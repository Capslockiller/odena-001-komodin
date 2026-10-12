import bpy
import math
from mathutils import Vector

# Load the model
blend_file = r"<tezgah>\kosular\test-v2\haiku-yok-r3\sonuc.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Clear existing camera and lights
for obj in bpy.data.objects:
    if obj.type in ['CAMERA', 'LIGHT']:
        bpy.data.objects.remove(obj, do_unlink=True)

# Set render settings
scene = bpy.context.scene
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.engine = 'BLENDER_EEVEE'

# Create camera
camera_data = bpy.data.cameras.new("Camera")
camera = bpy.data.objects.new("Camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera

# Position camera for good 3/4 view
camera.location = (0.6, 0.6, 0.5)
# Point at the center of the piece
direction = Vector((0, 0, 0.4)) - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Add key light
light_data_key = bpy.data.lights.new("KeyLight", type='SUN')
light_data_key.energy = 3
light_obj_key = bpy.data.objects.new("KeyLight", light_data_key)
scene.collection.objects.link(light_obj_key)
light_obj_key.location = (0.7, 0.7, 1.2)

# Add fill light
light_data_fill = bpy.data.lights.new("FillLight", type='SUN')
light_data_fill.energy = 1.5
light_obj_fill = bpy.data.objects.new("FillLight", light_data_fill)
scene.collection.objects.link(light_obj_fill)
light_obj_fill.location = (-0.5, -0.5, 0.8)

# Add world background light
world = bpy.data.worlds["World"]
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 0.5, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

# Render
output_path = r"<tezgah>\kosular\test-v2\haiku-yok-r3\preview.png"
scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)

print(f"Preview rendered successfully to: {output_path}")
