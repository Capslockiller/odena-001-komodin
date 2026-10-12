"""Load sonuc.blend and render workbench previews (does not save the blend)."""
import bpy, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "sonuc.blend"))
OUTDIR = os.path.join(HERE, "preview")
os.makedirs(OUTDIR, exist_ok=True)

sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.color_type = 'SINGLE'
sc.display.shading.show_cavity = True
sc.display.shading.show_object_outline = True
sc.render.resolution_x = 900
sc.render.resolution_y = 1100
sc.render.film_transparent = False

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
target = Vector((0, 0, 0.40))

views = {
    "front": (Vector((0, -3.0, 0.40)), 'ORTHO'),
    "side": (Vector((3.0, 0, 0.40)), 'ORTHO'),
    "persp34": (Vector((1.35, -1.75, 1.05)), 'PERSP'),
    "low34": (Vector((-1.2, -1.5, 0.25)), 'PERSP'),
    "top": (Vector((0, -0.001, 3.0)), 'ORTHO'),
}
for name, (loc, kind) in views.items():
    cam.location = loc
    cam.rotation_euler = (target - loc).to_track_quat('-Z', 'Y').to_euler()
    cam_data.type = kind
    cam_data.ortho_scale = 0.95
    cam_data.lens = 50
    sc.render.filepath = os.path.join(OUTDIR, name + ".png")
    bpy.ops.render.render(write_still=True)
print("DONE")
