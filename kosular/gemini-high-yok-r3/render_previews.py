import bpy
import math
import os
from mathutils import Vector

# Open sonuc.blend
blend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sonuc.blend")
bpy.ops.wm.open_mainfile(filepath=blend_path)

preview_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "onizleme")
os.makedirs(preview_dir, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.88, 0.86, 0.82)
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.cavity_ridge_factor = 1.5
scene.display.shading.cavity_valley_factor = 1.5

scene.render.resolution_x = 1280
scene.render.resolution_y = 1280
scene.render.film_transparent = False

# Create Camera
cam_data = bpy.data.cameras.new("PreviewCamera")
cam_obj = bpy.data.objects.new("PreviewCamera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

def setup_camera(pos, look_at, ortho=False, ortho_scale=1.0):
    cam_obj.location = Vector(pos)
    direction = Vector(look_at) - Vector(pos)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    if ortho:
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.type = 'PERSP'
        cam_data.lens = 50

views = [
    ("preview_persp_front.png", (0.85, -1.25, 0.95), (0.0, 0.0, 0.42), False, 1.0),
    ("preview_front.png",       (0.0, -1.4, 0.42), (0.0, 0.0, 0.42), True, 0.95),
    ("preview_side.png",        (1.4, 0.0, 0.42), (0.0, 0.0, 0.42), True, 0.95),
    ("preview_top.png",         (0.0, 0.0, 1.5), (0.0, 0.0, 0.42), True, 0.65),
    ("preview_persp_back.png",  (-0.95, 1.15, 0.85), (0.0, 0.0, 0.42), False, 1.0),
    ("preview_knob_detail.png", (0.28, -0.55, 0.62), (0.0, -0.21, 0.61), False, 1.0),
    ("preview_tabletop_detail.png", (0.45, -0.45, 0.95), (0.15, -0.15, 0.78), False, 1.0),
]

for filename, pos, look, ortho, scale in views:
    setup_camera(pos, look, ortho, scale)
    out_path = os.path.join(preview_dir, filename)
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print("Rendered:", out_path)

print("All preview renders finished successfully!")
