"""
protrude_front_b.py

Single-file solution that spawns a topmost overlay (click-through) and a main draggable window.
Overlay draws the protruding cube lines outside the main window; it clips so it doesn't draw
over the main window interior (so the main window's front face remains visible).
Works on Windows. Requires pygame.
"""
import os
import sys
import subprocess
import time
import ctypes
from ctypes import wintypes
import math
import pygame
import numpy as np

# ---------- CONFIG ----------
MAIN_W = 520
MAIN_H = 520
OVERLAY_PADDING = 0   # overlay covers entire screen
LAYERS = 12
DEPTH_SPACING = 20
FRONT_SIZE = 260
LINE_COLOR = (0, 230, 0)
LINE_WIDTH = 2
# ----------------------------

def run_overlay_process(script_path):
    python_exe = sys.executable
    return subprocess.Popen([python_exe, script_path, "--overlay"])

# ---------- Overlay mode ----------
if "--overlay" in sys.argv:
    pygame.init()

    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0)
    screen_h = user32.GetSystemMetrics(1)

    # create full-screen borderless overlay
    screen = pygame.display.set_mode((screen_w, screen_h), pygame.NOFRAME)
    pygame.display.set_caption("OverlayCube")

    hwnd_overlay = pygame.display.get_wm_info().get("window", 0)
    if not hwnd_overlay:
        print("Overlay: cannot get HWND, exiting.")
        sys.exit(1)

    # Make overlay layered, transparent, topmost, click-through
    GWL_EXSTYLE = -20
    WS_EX_LAYERED   = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    WS_EX_TOPMOST   = 0x00000008
    LWA_COLORKEY = 0x00000001

    ex = user32.GetWindowLongW(hwnd_overlay, GWL_EXSTYLE)
    ex |= (WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST)
    user32.SetWindowLongW(hwnd_overlay, GWL_EXSTYLE, ex)

    # Use color key (pure black) as transparent color
    color_key = (0,0,0)
    user32.SetLayeredWindowAttributes(hwnd_overlay,
                                      (color_key[2]<<16)|(color_key[1]<<8)|color_key[0],
                                      255, LWA_COLORKEY)

    # Helper: find main window by title
    MAIN_TITLE = "MainCubeWindow"

    def find_main_hwnd():
        return user32.FindWindowW(None, MAIN_TITLE)

    # Liang-Barsky algorithm to clip a line segment to rectangle.
    # We want segments OUTSIDE the rectangle, so we compute the inside interval and subtract.
    def liang_barsky_clip(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
        # returns (t0, t1, accept) for portion inside the rect parametric t in [0,1]
        dx = x1 - x0
        dy = y1 - y0
        p = [-dx, dx, -dy, dy]
        q = [x0 - xmin, xmax - x0, y0 - ymin, ymax - y0]
        u1, u2 = 0.0, 1.0
        for pi, qi in zip(p, q):
            if abs(pi) < 1e-9:
                if qi < 0:
                    return (0,0,False)
                else:
                    continue
            t = qi / pi
            if pi < 0:
                if t > u2:
                    return (0,0,False)
                if t > u1:
                    u1 = t
            else:
                if t < u1:
                    return (0,0,False)
                if t < u2:
                    u2 = t
        return (u1, u2, True)

    clock = pygame.time.Clock()
    print("Overlay started. Waiting for main window...")

    # main loop
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # attempt to locate main window
        hwnd_main = find_main_hwnd()
        if not hwnd_main:
            # draw nothing until main appears
            screen.fill(color_key)
            pygame.display.flip()
            time.sleep(0.05)
            continue

        # get main window rect
        rect = wintypes.RECT()
        ok = user32.GetWindowRect(hwnd_main, ctypes.byref(rect))
        if not ok:
            screen.fill(color_key)
            pygame.display.flip()
            time.sleep(0.01)
            continue

        main_left, main_top, main_right, main_bottom = rect.left, rect.top, rect.right, rect.bottom
        main_w = main_right - main_left
        main_h = main_bottom - main_top

        # compute front face center in screen coords (we anchor front to monitor center)
        sx = user32.GetSystemMetrics(0)
        sy = user32.GetSystemMetrics(1)
        screen_cx = sx // 2
        screen_cy = sy // 2
        front_cx = screen_cx
        front_cy = screen_cy
        front_half = FRONT_SIZE / 2

        # compute back origin center in screen coords (this is main window center)
        back_cx = main_left + main_w/2
        back_cy = main_top  + main_h/2

        # clear using colorkey (transparent)
        screen.fill(color_key)

        # draw layered rectangles as wireframes, but clipped so overlay does NOT draw inside main window rect
        for i in range(1, LAYERS+1):
            t = i / (LAYERS + 1.0)   # 0..1
            # interpolate center between front (anchored) and back (main window center)
            layer_cx = front_cx*(1-t) + back_cx*t
            layer_cy = front_cy*(1-t) + back_cy*t
            size = FRONT_SIZE + t * 380

            left = layer_cx - size/2
            top = layer_cy - size/2
            right = layer_cx + size/2
            bottom = layer_cy + size/2

            # draw four edges as line segments, but clip portions that lie inside main rect
            edges = [
                (left, top, right, top),
                (right, top, right, bottom),
                (right, bottom, left, bottom),
                (left, bottom, left, top)
            ]
            for (x0,y0,x1,y1) in edges:
                # compute inside interval for this segment wrt main rect
                u1,u2,accept = liang_barsky_clip(x0,y0,x1,y1, main_left, main_top, main_right, main_bottom)
                segments = []
                if not accept:
                    # entire segment is outside -> draw full
                    segments.append((x0,y0,x1,y1))
                else:
                    # inside portion is t in [u1,u2]; outside parts are [0,u1] and [u2,1]
                    if u1 > 1e-6:
                        ax0 = x0; ay0 = y0
                        ax1 = x0 + (x1-x0)*u1
                        ay1 = y0 + (y1-y0)*u1
                        segments.append((ax0,ay0,ax1,ay1))
                    if u2 < 1 - 1e-6:
                        bx0 = x0 + (x1-x0)*u2
                        by0 = y0 + (y1-y0)*u2
                        bx1 = x1; by1 = y1
                        segments.append((bx0,by0,bx1,by1))
                # draw outside segments
                for (sx0,sy0,sx1,sy1) in segments:
                    pygame.draw.line(screen, LINE_COLOR, (sx0, sy0), (sx1, sy1), LINE_WIDTH)

        # draw small connector lines that meet the front face edge (optional)
        # you can add small rays connecting the last layer to the front face corners
        last_t = LAYERS / (LAYERS + 1.0)
        last_size = FRONT_SIZE + last_t * 380
        last_cx = front_cx*(1-last_t) + back_cx*last_t
        last_cy = front_cy*(1-last_t) + back_cy*last_t
        # corners of last layer
        corners = [
            (last_cx - last_size/2, last_cy - last_size/2),
            (last_cx + last_size/2, last_cy - last_size/2),
            (last_cx + last_size/2, last_cy + last_size/2),
            (last_cx - last_size/2, last_cy + last_size/2)
        ]
        # front face corners
        fcorners = [
            (front_cx - front_half, front_cy - front_half),
            (front_cx + front_half, front_cy - front_half),
            (front_cx + front_half, front_cy + front_half),
            (front_cx - front_half, front_cy + front_half)
        ]
        # draw connector rays but clip so they don't draw inside main window
        for (sx0,sy0),(fx0,fy0) in zip(corners, fcorners):
            u1,u2,accept = liang_barsky_clip(sx0,sy0,fx0,fy0, main_left, main_top, main_right, main_bottom)
            segments = []
            if not accept:
                segments.append((sx0,sy0,fx0,fy0))
            else:
                if u1 > 1e-6:
                    ax0 = sx0; ay0 = sy0
                    ax1 = sx0 + (fx0 - sx0)*u1
                    ay1 = sy0 + (fy0 - sy0)*u1
                    segments.append((ax0,ay0,ax1,ay1))
                if u2 < 1 - 1e-6:
                    bx0 = sx0 + (fx0 - sx0)*u2
                    by0 = sy0 + (fy0 - sy0)*u2
                    bx1 = fx0; by1 = fy0
                    segments.append((bx0,by0,bx1,by1))
            for (sx0,sy0,sx1,sy1) in segments:
                pygame.draw.line(screen, LINE_COLOR, (sx0,sy0), (sx1,sy1), LINE_WIDTH)

        pygame.display.flip()
        clock.tick(60)

# ---------- Main process ----------
else:
    # launch overlay subprocess first
    script = os.path.abspath(__file__)
    overlay_proc = run_overlay_process(script)
    time.sleep(0.12)  # give overlay a moment

    pygame.init()
    user32 = ctypes.windll.user32
    sx = user32.GetSystemMetrics(0)
    sy = user32.GetSystemMetrics(1)

    # create main borderless window (we will move it manually)
    screen = pygame.display.set_mode((MAIN_W, MAIN_H), pygame.NOFRAME)
    pygame.display.set_caption("MainCubeWindow")
    hwnd_main = pygame.display.get_wm_info().get("window", 0)

    # initial position near center but slightly offset so protrusion is visible
    win_x = sx // 2 - MAIN_W // 2 + 80
    win_y = sy // 2 - MAIN_H // 2 + 30
    SWP_NOSIZE = 0x0001
    SWP_SHOWWINDOW = 0x0040
    user32.SetWindowPos(hwnd_main, 0, win_x, win_y, 0, 0, SWP_NOSIZE | SWP_SHOWWINDOW)

    clock = pygame.time.Clock()
    dragging = False
    drag_offset = (0,0)

    # draw function for main window interior (draw front face and a clipped interior)
    def draw_main(surface):
        surface.fill((10,10,10))
        cx = MAIN_W//2
        cy = MAIN_H//2
        size = FRONT_SIZE
        rect = pygame.Rect(cx - size//2, cy - size//2, size, size)
        # filled front face (window interior)
        pygame.draw.rect(surface, (0,180,0), rect)
        pygame.draw.rect(surface, (0,230,0), rect, 3)

        # small inner wireframe to show continuation
        inner_size = size - 40
        inner_rect = pygame.Rect(cx - inner_size//2, cy - inner_size//2, inner_size, inner_size)
        pygame.draw.rect(surface, (0,160,0), inner_rect, 2)

    print("Main window running. Drag it; overlay draws protruding lines in front (B).")

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                dragging = True
                pt = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(pt))
                drag_offset = (pt.x - win_x, pt.y - win_y)
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                dragging = False

        if dragging:
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            win_x = pt.x - drag_offset[0]
            win_y = pt.y - drag_offset[1]
            # move main window (manual move so position updates live)
            user32.SetWindowPos(hwnd_main, 0, win_x, win_y, 0, 0, SWP_NOSIZE | SWP_SHOWWINDOW)

        # draw main interior
        draw_main(screen)
        pygame.display.flip()
        clock.tick(60)

    # cleanup
    try:
        overlay_proc.terminate()
    except Exception:
        pass
    pygame.quit()
    sys.exit(0)
