"""
Render multi-angle previews of Molly's Nightstand.
"""

import bpy
import bmesh
import math
from mathutils import Vector
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import assembly
import assemble_nightstand as ans

def setup_lighting():
    # World background: clean neutral studio grey
    world = bpy.data.worlds.new("StudioWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.85, 0.85, 0.87, 1.0)
        bg_node.inputs["Strength"].default_value = 0.6

    # Key light: warm key
    key_data = bpy.data.lights.new("KeyLight", 'SUN')
    key_data.energy = 2.8
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.location = (2.0, -3.0, 3.5)
    ans.look_at(key_obj, (0, 0, 0.40))

    # Fill light: soft cool fill
    fill_data = bpy.data.lights.new("FillLight", 'SUN')
    fill_data.energy = 1.2
    fill_data.color = (0.92, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.location = (-3.0, -2.0, 2.5)
    ans.look_at(fill_obj, (0, 0, 0.40))

    # Rim / Back light: edge definition
    rim_data = bpy.data.lights.new("RimLight", 'SUN')
    rim_data.energy = 1.8
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.location = (1.5, 3.0, 3.0)
    ans.look_at(rim_obj, (0, 0, 0.40))

    # Shadow floor
    bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0, 0, 0))
    floor_obj = bpy.context.active_object
    floor_obj.name = "Floor_Plane"
    # Make sure floor is not in Molly's Nightstand collection
    col = bpy.data.collections.get("Molly's Nightstand")
    if floor_obj.name in col.objects:
        col.objects.unlink(floor_obj)
    if floor_obj.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(floor_obj)

def create_camera():
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.clip_start = 0.01
    cam_data.clip_end = 100.0
    cam_data.lens = 55.0
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    return cam_obj

def render_view(cam_obj, loc, target, filename, res=(1200, 900), lens=55.0):
    cam_obj.location = loc
    cam_obj.data.lens = lens
    ans.look_at(cam_obj, target)
    out_path = os.path.abspath(filename)
    bpy.context.scene.render.filepath = out_path
    bpy.context.scene.render.resolution_x = res[0]
    bpy.context.scene.render.resolution_y = res[1]
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {filename}")

def main():
    ans.assemble_model()
    setup_lighting()
    cam = create_camera()

    # 1. Perspective 3/4 front view
    render_view(cam, (1.1, -1.6, 1.15), (0.0, -0.05, 0.42), "render_perspective.png", (1200, 900), lens=60.0)

    # 2. Front elevation view
    render_view(cam, (0.0, -2.1, 0.42), (0.0, -0.05, 0.42), "render_front.png", (1000, 1000), lens=75.0)

    # 3. Side profile view (to see bulge, taper, tabletop overhang, proud panels)
    render_view(cam, (2.1, 0.0, 0.42), (0.0, 0.0, 0.42), "render_side.png", (1000, 1000), lens=75.0)

    # 4. Top-down view (to see square plan, rounded corners, overhang)
    render_view(cam, (0.0, -0.01, 2.0), (0.0, 0.0, 0.40), "render_top.png", (1000, 1000), lens=65.0)

    # 5. Detail: Panels & Knobs closeup
    render_view(cam, (0.45, -0.9, 0.55), (0.0, -0.19, 0.48), "render_detail_panels.png", (1200, 900), lens=70.0)

    # 6. Detail: Tabletop edge profile closeup (bullnose + chamfer)
    render_view(cam, (0.45, -0.65, 0.90), (0.16, -0.16, 0.78), "render_detail_tabletop.png", (1200, 900), lens=85.0)

    # 7. Detail: Legs closeup
    render_view(cam, (0.55, -0.85, 0.20), (0.0, -0.10, 0.07), "render_detail_legs.png", (1200, 900), lens=75.0)

    print("All renders complete!")

if __name__ == "__main__":
    main()
