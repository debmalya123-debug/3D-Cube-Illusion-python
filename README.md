# Python 3D Cube Illusions

Here are three python scripts that create 3D cube illusions using **Pygame** and **Windows API**. They all react to where you drag the window on your screen.

## The Scripts

### 1. `3dcube.py` - Simple Perspective Cube

A clean, single-window perspective cube that expands as you drag it.

- **Effect**: Drag the window around and the cube layers expand/contract based on window position.
- **Visuals**: Green wireframe layers with a solid front face.
- **How it works**: Front face stays anchored to screen center while back layers follow the window, creating dynamic perspective.
- **Run it**:
  ```bash
  python 3dcube.py
  ```

### 2. `3dCube2.py` - Rotating Cube

This one rotates the cube based on where you drag the window.

- **Effect**: Drag the window around and the cube rotates to face the center of the screen.
- **Visuals**: 3D rendered cube with flat shading, transparency, and glowing edges.
- **How it works**: Calculates rotation angles based on distance from screen center, with smooth interpolation.
- **Run it**:
  ```bash
  python 3dCube2.py
  ```

### 3. `3dCube3.py` - Protruding Overlay Cube

Advanced dual-window system that makes the cube appear to protrude out of the screen.

- **Effect**: The cube appears anchored to screen center with layers protruding toward your draggable window.
- **Visuals**: Wireframe layers drawn on a transparent fullscreen overlay with Liang-Barsky line clipping.
- **How it works**: Spawns two processes - main draggable window and a topmost transparent overlay. The overlay clips lines to avoid drawing inside the main window, creating a clean protrusion effect.
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
