import bpy
import os

os.chdir("<tezgah>\\kosular\\test-v2\\haiku-yok-r1")

# Load the model
bpy.ops.wm.open_mainfile(filepath="sonuc.blend")

scene = bpy.context.scene

# Set render settings to use viewport shading
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
render_file = os.path.join(os.getcwd(), "render_preview.png")
scene.render.filepath = render_file

# Delete existing cameras
for obj in list(bpy.data.objects):
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Add a simple camera
bpy.ops.object.camera_add(location=(0.6, 0.6, 0.5))
camera = bpy.context.active_object
camera.name = "PreviewCam"

# Orient camera
from mathutils import Vector
direction = Vector((0, 0, 0.32)) - Vector(camera.location)
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

scene.camera = camera

print(f"Rendering with WORKBENCH engine...")
print(f"Camera location: {camera.location}")
bpy.ops.render.render(write_still=True)
print(f"Saved to {render_file}")
