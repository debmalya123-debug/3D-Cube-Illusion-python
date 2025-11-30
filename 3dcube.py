import pygame
import ctypes
from ctypes import wintypes
import numpy as np

pygame.init()

WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
clock = pygame.time.Clock()

user32 = ctypes.windll.user32
SetWindowPos = user32.SetWindowPos
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004

# Monitor center
sw = user32.GetSystemMetrics(0)
sh = user32.GetSystemMetrics(1)
SCX = sw//2
SCY = sh//2

# Start window centered
win_x = SCX - WIDTH//2
win_y = SCY - HEIGHT//2

hwnd = pygame.display.get_wm_info()["window"]
SetWindowPos(hwnd, 0, win_x, win_y, 0,0, SWP_NOSIZE | SWP_NOZORDER)

dragging = False
drag_offset = (0,0)

# Cube parameters
FRONT = 250
LAYERS = 12
GREEN = (0,255,0)

def draw_perspective_cube(surface, win_x, win_y):
    cx = WIDTH//2
    cy = HEIGHT//2

    # Position of window center in global space
    wx_center = win_x + WIDTH//2
    wy_center = win_y + HEIGHT//2

    # Offset of window center from screen center
    dx = wx_center - SCX
    dy = wy_center - SCY

    # ------------------------------
    # 1. Compute the anchored front face
    # ------------------------------
    Fx = cx - dx   # screen-anchored position
    Fy = cy - dy
    front = pygame.Rect(Fx - FRONT//2, Fy - FRONT//2, FRONT, FRONT)

    # ------------------------------
    # 2. Compute back origin (position relative to window center)
    # ------------------------------
    back_cx = cx
    back_cy = cy

    # ------------------------------
    # 3. Draw perspective back layers
    # ------------------------------
    for i in range(LAYERS):
        t = (i+1)/LAYERS  # depth factor (0 front → 1 back)

        # target size decreases with depth
        size = FRONT + (t * 350)

        # linearly blend from front face origin to window-centered back origin
        layer_cx = Fx*(1-t) + back_cx*t
        layer_cy = Fy*(1-t) + back_cy*t

        layer_rect = pygame.Rect(
            layer_cx - size/2,
            layer_cy - size/2,
            size, size
        )

        pygame.draw.rect(surface, GREEN, layer_rect, 2)

    # ------------------------------
    # 4. Draw the FRONT face on top
    # ------------------------------
    pygame.draw.rect(surface, (0,200,0), front)
    pygame.draw.rect(surface, GREEN, front, 4)


running = True
while running:
    screen.fill((20,20,20))

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
        SetWindowPos(hwnd, 0, win_x, win_y, 0,0, SWP_NOSIZE | SWP_NOZORDER)

    draw_perspective_cube(screen, win_x, win_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
