import bpy
import bmesh
import math
from mathutils import Vector

def create_rounded_square_ring(w, r_c, n_seg_per_corner=8):
    """Returns a list of 2D (x, y) coordinates for a rounded square centered at origin."""
    d = w - r_c
    coords = []
    # 4 corners: (+, +), (-, +), (-, -), (+, -)
    corners = [
        (d, d, 0.0),
        (-d, d, 0.5 * math.pi),
        (-d, -d, 1.0 * math.pi),
        (d, -d, 1.5 * math.pi),
    ]
    for cx, cy, start_angle in corners:
        for i in range(n_seg_per_corner):
            ang = start_angle + (i / n_seg_per_corner) * (0.5 * math.pi)
            x = cx + r_c * math.cos(ang)
            y = cy + r_c * math.sin(ang)
            coords.append((x, y))
    return coords

print("Ring coords generated:", len(create_rounded_square_ring(0.20, 0.035)))
