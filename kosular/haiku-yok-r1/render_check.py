import bpy
import os
import math

os.chdir("<tezgah>\\kosular\\test-v2\\haiku-yok-r1")

# Load the model
bpy.ops.wm.open_mainfile(filepath="sonuc.blend")

scene = bpy.context.scene

# Set render settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
render_file = os.path.join(os.getcwd(), "render_preview.png")
scene.render.filepath = render_file

# Clear all existing objects except in our collection
collection = bpy.data.collections.get("Molly's Nightstand")

# Delete all cameras and lights
for obj in list(bpy.data.objects):
    if obj.type in ['CAMERA', 'LIGHT']:
        bpy.data.objects.remove(obj, do_unlink=True)

# Add camera with better positioning
bpy.ops.object.camera_add(location=(0.55, 0.55, 0.55))
camera = bpy.context.active_object
camera.name = "Preview_Camera"

# Look at center of model (around 0,0,0.4)
from mathutils import Vector
direction = Vector((0, 0, 0.4)) - Vector(camera.location)
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(2, 2, 3))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3

# Add area light for fill
bpy.ops.object.light_add(type='AREA', location=(-1, -1, 1))
area = bpy.context.active_object
area.name = "Fill"
area.data.energy = 1

# Enable ambient light in world
world = scene.world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[1].default_value = 0.8

print(f"Rendering to {render_file}...")
print(f"Camera at {camera.location}")
bpy.ops.render.render(write_still=True)
print(f"Preview rendered")
