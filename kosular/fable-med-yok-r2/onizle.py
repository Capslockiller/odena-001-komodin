"""Render Workbench previews of sonuc.blend (run: blender -b sonuc.blend --python onizle.py)."""
import bpy, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "onizleme")
os.makedirs(OUTDIR, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "SINGLE"
sh.single_color = (0.8, 0.75, 0.65)
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.show_shadows = True
sh.show_object_outline = True
scene.display.render_aa = "8"
scene.view_settings.view_transform = "Standard"

cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
target = Vector((0, 0, 0.40))


def shoot(name, loc, ortho=None):
    cam.location = loc
    cam.rotation_euler = (target - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho
    else:
        cam_data.type = "PERSP"
        cam_data.lens = 60
    scene.render.filepath = os.path.join(OUTDIR, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", scene.render.filepath)


shoot("uc_ceyrek", (1.3, -1.6, 0.95))
shoot("on", (0, -3, 0.40), ortho=0.95)
shoot("yan", (3, 0, 0.40), ortho=0.95)
shoot("alt_ceyrek", (1.2, -1.5, -0.35))
shoot("detay_kulp", (0.35, -0.55, 0.62))
