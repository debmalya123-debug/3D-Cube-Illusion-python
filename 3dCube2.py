import pygame
import numpy as np
import math
import ctypes
from ctypes import wintypes

pygame.init()

WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("3D Illusion Cube")
clock = pygame.time.Clock()

# windows api setup
user32 = ctypes.windll.user32
SetWindowPos = user32.SetWindowPos
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004

# screen center
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)
center_x = screen_w // 2
center_y = screen_h // 2

# Start window in center
win_x = center_x - WIDTH // 2
win_y = center_y - HEIGHT // 2
hwnd = pygame.display.get_wm_info()["window"]
SetWindowPos(hwnd, None, win_x, win_y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)

# dragging state
dragging = False
drag_offset = (0,0)

# cube points
cube_points = np.array([
    [-1,-1,-1],
    [ 1,-1,-1],
    [ 1, 1,-1],
    [-1, 1,-1],
    [-1,-1, 1],
    [ 1,-1, 1],
    [ 1, 1, 1],
    [-1, 1, 1]
], float)

# faces
faces = [
    (0,1,2,3), # back
    (4,5,6,7), # front
    (0,1,5,4), # bottom
    (2,3,7,6), # top
    (1,2,6,5), # right
    (0,3,7,4)  # left
]

# light direction
light_dir = np.array([0.4, -1, -0.6])
light_dir /= np.linalg.norm(light_dir)

def rotate(points, ax, ay, az):
    Rx = np.array([
        [1,0,0],
        [0, math.cos(ax), -math.sin(ax)],
        [0, math.sin(ax),  math.cos(ax)]
    ])
    Ry = np.array([
        [ math.cos(ay),0, math.sin(ay)],
        [0,1,0],
        [-math.sin(ay),0, math.cos(ay)]
    ])
    Rz = np.array([
        [math.cos(az), -math.sin(az), 0],
        [math.sin(az),  math.cos(az), 0],
        [0,0,1]
    ])
    return points @ (Rx @ Ry @ Rz)

def project(points):
    out = []
    for x,y,z in points:
        f = 280 / (z + 4)
        px = x*f + WIDTH/2
        py = y*f + HEIGHT/2
        out.append((px, py, z))
    return np.array(out)

def face_normal(p1, p2, p3):
    u = p2 - p1
    v = p3 - p1
    n = np.cross(u, v)
    if np.linalg.norm(n) == 0: 
        return n
    return n / np.linalg.norm(n)

ax = ay = az = 0



running = True
while running:
    screen.fill((15,15,15))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            mouse = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(mouse))
            drag_offset = (mouse.x - win_x, mouse.y - win_y)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False

    # move the window
    if dragging:
        mouse = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(mouse))
        win_x = mouse.x - drag_offset[0]
        win_y = mouse.y - drag_offset[1]
        SetWindowPos(hwnd, None, win_x, win_y, 0,0, SWP_NOSIZE | SWP_NOZORDER)

    # calculate rotation based on position
    dx = win_x + WIDTH//2 - center_x
    dy = win_y + HEIGHT//2 - center_y

    target_ax = dy / 350.0
    target_ay = dx / 350.0
    target_az = (dx + dy) / 700.0

    ax += (target_ax - ax) * 0.15
    ay += (target_ay - ay) * 0.15
    az += (target_az - az) * 0.15

    # rotate and project
    rotated = rotate(cube_points, ax, ay, az)
    projected = project(rotated)

    # sort faces by depth
    face_depths = []
    for i, f in enumerate(faces):
        z_sum = sum(projected[j][2] for j in f)
        face_depths.append((z_sum, i))
    face_depths.sort(reverse=True)  # farthest first

    # draw
    for _, fi in face_depths:
        f = faces[fi]

        pts_3d = np.array([rotated[i] for i in f])
        pts_2d = np.array([[projected[i][0], projected[i][1]] for i in f])

        # Calculate face normal
        n = face_normal(pts_3d[0], pts_3d[1], pts_3d[2])

        # lighting
        intensity = max(0.1, np.dot(n, -light_dir))
        color = np.array([0, 255, 0]) * intensity
        color = color.clip(0,255).astype(int)

        # transparency
        surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(surface, (*color, 180), pts_2d)
        screen.blit(surface, (0,0))

        # draw edges
        pygame.draw.polygon(screen, (0,255,0), pts_2d, 2)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
