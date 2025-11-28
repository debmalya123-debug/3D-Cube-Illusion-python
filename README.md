# Python 3D Cube Illusions

Here are two python scripts that mess with 3D cube illusions using **Pygame** and **Windows API**. They both react to where the window is on your screen.

## The Scripts

### 1. `3dCube2.py` - Rotation

This one rotates the cube based on where you drag the window.

- **Effect**: Drag the window around and the cube rotates to face the center of the screen.
- **Visuals**: Flat shading, some transparency, glowing edges.
- **How it works**: Calculates rotation angles based on distance from screen center.
- **Run it**:
  ```bash
  python 3dCube2.py
  ```

### 2. `3dCube3.py` - Protrusion

This one makes the cube look like it's popping out of the monitor.

- **Effect**: The front face is in the window, but the rest of the cube is drawn on a transparent overlay so it looks like it's floating.
- **Visuals**: Wireframe style with depth fading.
- **How it works**: Uses two windows - one for the front face (that you drag) and a transparent one on top for the rest of the cube.
- **Run it**:
  ```bash
  python 3dCube3.py
  ```

## You need

- Windows (for the window management stuff)
- Python 3
- Pygame

## How to run

1.  Grab the code.
2.  Install pygame:
    ```bash
    pip install pygame
    ```
3.  Run one of the scripts.

## Controls

- **Move**: Drag the window around.
- **Exit**: Close the window.
