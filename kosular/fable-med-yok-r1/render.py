"""Render preview images of sonuc.blend (Workbench, headless). Does not modify sonuc.blend."""
import bpy, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "sonuc.blend"))
scene = bpy.context.scene

scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.show_cavity = True
scene.display.shading.show_shadows = True
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.film_transparent = False
scene.world = scene.world or bpy.data.worlds.new("W")
scene.world.color = (0.9, 0.9, 0.9)

cam_data = bpy.data.cameras.new("PreviewCam")
cam = bpy.data.objects.new("PreviewCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
target = Vector((0, 0, 0.42))

def shoot(name, pos, ortho=False, scale=1.0):
    cam.location = pos
    d = target - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam_data.type = 'ORTHO' if ortho else 'PERSP'
    cam_data.ortho_scale = scale
    cam_data.lens = 50
    scene.render.filepath = os.path.join(HERE, f"preview_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", scene.render.filepath)

shoot("front34", Vector((1.3, -1.7, 0.95)))
shoot("front", Vector((0, -3, 0.42)), ortho=True, scale=1.0)
shoot("side", Vector((3, 0, 0.42)), ortho=True, scale=1.0)
shoot("low34", Vector((-1.2, -1.6, 0.25)))
