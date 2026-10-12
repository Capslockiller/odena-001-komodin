import bpy, math, os, sys
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'
sc.display.shading.show_cavity = True
sc.display.shading.show_object_outline = True
sc.render.resolution_x = sc.render.resolution_y = 900
sc.world = sc.world or bpy.data.worlds.new("W")
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
tgt = Vector((0, 0, 0.40))
views = {"front": (0, -1, 0), "side": (1, 0, 0), "persp": (0.8, -1.2, 0.55),
         "low": (-0.9, -1.1, -0.05), "topview": (0, -0.0001, 1)}
for name, d in views.items():
    d = Vector(d).normalized()
    if name in ("front", "side", "topview"):
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = 0.95
    else:
        cam.data.type = 'PERSP'; cam.data.lens = 50
    cam.location = tgt + d * 3.0
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)
