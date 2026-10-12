import bpy
import os

# Load the model
blend_file = r"<tezgah>\kosular\test-v2\haiku-yok-r3\sonuc.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Set up render settings for a quick preview
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 800

# Set camera position for good view
camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
bpy.context.collection.objects.link(camera)
bpy.context.scene.camera = camera

# Position camera to see the piece nicely
camera.location = (0.5, 0.5, 0.6)
camera.rotation_euler = (1.1, 0, 0.785)  # Look down at an angle

# Add a light
light_data = bpy.data.lights.new(name="Light", type='SUN')
light_object = bpy.data.objects.new(name="Light", object_data=light_data)
bpy.context.collection.objects.link(light_object)
light_object.location = (0.5, 0.5, 1.0)
light_data.energy = 2

# Set render engine and settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.cycles.use_denoising = True

# Render
output_path = r"<tezgah>\kosular\test-v2\haiku-yok-r3\preview.png"
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)

print(f"Preview rendered to: {output_path}")
