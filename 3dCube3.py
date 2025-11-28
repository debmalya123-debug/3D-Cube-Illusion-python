# Protruding 3D Cube Effect
# Uses a transparent overlay window to draw the sides of the cube

import os
import sys
import subprocess
import time
import ctypes
from ctypes import wintypes
import pygame

# Config
MAIN_W = 520
MAIN_H = 520
LAYERS = 12
DEPTH_SPACING = 20
FRONT_SIZE = 260


def run_overlay(script_path):
    return subprocess.Popen([sys.executable, script_path, "--overlay"])

# Overlay process
if "--overlay" in sys.argv:
    pygame.init()

    user32 = ctypes.windll.user32
    sx = user32.GetSystemMetrics(0)
    sy = user32.GetSystemMetrics(1)

    screen = pygame.display.set_mode((sx, sy), pygame.NOFRAME)
    pygame.display.set_caption("OverlayCube")

    hwnd_overlay = pygame.display.get_wm_info()["window"]

    # Make overlay topmost + clickthrough + transparent
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x80000
    WS_EX_TRANSPARENT = 0x20
    WS_EX_TOPMOST = 0x8
    LWA_COLORKEY = 0x1

    ex = user32.GetWindowLongW(hwnd_overlay, GWL_EXSTYLE)
    ex |= (WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST)
    user32.SetWindowLongW(hwnd_overlay, GWL_EXSTYLE, ex)

    # Pure black = transparent
    user32.SetLayeredWindowAttributes(hwnd_overlay, 0x000000, 255, LWA_COLORKEY)

    MAIN_TITLE = "MainCubeWindow"

    def get_main_hwnd():
        return user32.FindWindowW(None, MAIN_TITLE)

    def get_rect(hwnd):
        r = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        return r.left, r.top, r.right, r.bottom

    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        hwnd_main = get_main_hwnd()
        screen.fill((0,0,0))

        if not hwnd_main:
            pygame.display.flip()
            continue

        left, top, right, bottom = get_rect(hwnd_main)
        mw = right - left
        mh = bottom - top

        # Window center, screen center
        win_cx = left + mw/2
        win_cy = top + mh/2
        screen_cx = sx/2
        screen_cy = sy/2

        # Shear effect
        shear_x = (win_cx - screen_cx) * 0.0018
        shear_y = (win_cy - screen_cy) * 0.0018

        # Anchored front face world position
        front_x = screen_cx
        front_y = screen_cy

        back_x = win_cx
        back_y = win_cy

        overlay = pygame.Surface((sx, sy), pygame.SRCALPHA)

        # Draw layers
        for i in range(1, LAYERS+1):
            t = i / (LAYERS + 1.0)
            cx = front_x*(1-t) + back_x*t
            cy = front_y*(1-t) + back_y*t

            size = FRONT_SIZE + t * 380

            # Shear by depth z
            z = i * DEPTH_SPACING
            cx += shear_x * z
            cy += shear_y * z

            rect = pygame.Rect(cx - size/2, cy - size/2, size, size)

            alpha = int(200 * (1 - t))
            pygame.draw.rect(overlay, (0,255,0,alpha), rect, 2)

        # Connector lines
        last_t = LAYERS/(LAYERS+1.0)
        last_size = FRONT_SIZE + last_t*380
        last_cx = front_x*(1-last_t) + back_x*last_t
        last_cy = front_y*(1-last_t) + back_y*last_t

        back_corners = [
            (last_cx - last_size/2, last_cy - last_size/2),
            (last_cx + last_size/2, last_cy - last_size/2),
            (last_cx + last_size/2, last_cy + last_size/2),
            (last_cx - last_size/2, last_cy + last_size/2)
        ]
        front_corners = [
            (front_x - FRONT_SIZE/2, front_y - FRONT_SIZE/2),
            (front_x + FRONT_SIZE/2, front_y - FRONT_SIZE/2),
            (front_x + FRONT_SIZE/2, front_y + FRONT_SIZE/2),
            (front_x - FRONT_SIZE/2, front_y + FRONT_SIZE/2)
        ]

        for (bx,by),(fx,fy) in zip(back_corners, front_corners):
            pygame.draw.line(overlay, (0,255,0,150), (bx,by), (fx,fy), 2)

        # Clear overlay inside main window area (so lines do not cover front face)
        overlay.fill((0,0,0,0), pygame.Rect(left, top, mw, mh))

        # Blit overlay
        screen.blit(overlay, (0,0))
        pygame.display.flip()
        clock.tick(60)

# Main process
else:
    script = os.path.abspath(__file__)
    overlay_proc = run_overlay(script)
    time.sleep(0.15)

    pygame.init()
    user32 = ctypes.windll.user32
    sx = user32.GetSystemMetrics(0)
    sy = user32.GetSystemMetrics(1)

    screen = pygame.display.set_mode((MAIN_W, MAIN_H), pygame.NOFRAME)
    pygame.display.set_caption("MainCubeWindow")

    hwnd = pygame.display.get_wm_info()["window"]

    # Initial window position
    win_x = sx//2 - MAIN_W//2 + 80
    win_y = sy//2 - MAIN_H//2 + 30
    user32.SetWindowPos(hwnd, 0, win_x, win_y, 0,0, 0x0001|0x0040)

    dragging = False
    drag_offset = (0,0)
    clock = pygame.time.Clock()

    # Draw the front face
    def draw_main(surface, win_x, win_y, hwnd):
        surface.fill((10,10,10))

        # REAL window draw offset (Windows shadow/margins)
        r = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        offset_x = r.left - win_x
        offset_y = r.top  - win_y

        # World front-face position
        screen_cx = sx//2
        screen_cy = sy//2

        # Convert world → window-local coordinates
        local_fx = (screen_cx - win_x) - offset_x
        local_fy = (screen_cy - win_y) - offset_y

        size = FRONT_SIZE
        rect = pygame.Rect(int(local_fx - size/2), int(local_fy - size/2), size, size)

        pygame.draw.rect(surface, (0,180,0), rect)
        pygame.draw.rect(surface, (0,255,0), rect, 3)

        # Inner highlight
        inner_s = size - 40
        inner_r = pygame.Rect(int(local_fx-inner_s/2), int(local_fy-inner_s/2), inner_s, inner_s)
        pygame.draw.rect(surface, (0,160,0), inner_r, 2)

    # Main loop
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                try: overlay_proc.terminate()
                except: pass
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                dragging = True
                pt = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(pt))
                drag_offset = (pt.x - win_x, pt.y - win_y)
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                dragging = False

        if dragging:
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            win_x = pt.x - drag_offset[0]
            win_y = pt.y - drag_offset[1]
            user32.SetWindowPos(hwnd, 0, win_x, win_y, 0,0, 0x0001)

        draw_main(screen, win_x, win_y, hwnd)
        pygame.display.flip()
        clock.tick(60)
