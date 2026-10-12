"""Preview renders of sonuc.blend (Workbench, no materials)."""
import bpy, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "onizleme")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "sonuc.blend"))
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.show_cavity = True
sc.display.shading.cavity_type = 'BOTH'
sc.display.shading.color_type = 'SINGLE'
sc.render.resolution_x = 900
sc.render.resolution_y = 1100
sc.render.film_transparent = False

cam_data = bpy.data.cameras.new("PreviewCam")
cam = bpy.data.objects.new("PreviewCam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
target = Vector((0, 0, 0.40))

views = {
    "on":      ((0, -3, 0.40), True),
    "yan":     ((3, 0, 0.40), True),
    "ust":     ((0, 0, 3), True),
    "persp":   ((1.3, -1.7, 1.05), False),
    "alt_persp": ((-1.1, -1.5, 0.15), False),
}
for name, (loc, ortho) in views.items():
    cam.location = loc
    d = target - Vector(loc)
    if name == "ust":
        cam.rotation_euler = (0, 0, 0)
    else:
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam_data.type = 'ORTHO' if ortho else 'PERSP'
    cam_data.ortho_scale = 0.95
    cam_data.lens = 60
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)

# remove helper camera so it never ends up in the deliverable (file not saved anyway)
