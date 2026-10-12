import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import os

# --- Setup ---
bpy.ops.wm.read_factory_settings(use_empty=True)

# Remove all existing collections to be safe
for col in bpy.data.collections:
    bpy.data.collections.remove(col)

collection_name = "Molly's Nightstand"
collection = bpy.data.collections.new(collection_name)
bpy.context.scene.collection.children.link(collection)

# --- Helpers ---
def apply_modifiers(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(obj_eval)
    obj.data = mesh
    obj.modifiers.clear()

# --- 1. Body ---
bpy.ops.mesh.primitive_cube_add(size=1)
body = bpy.context.active_object
body.name = "Body"
collection.objects.link(body)
bpy.context.scene.collection.objects.unlink(body)

mod = body.modifiers.new("Subsurf", 'SUBSURF')
mod.subdivision_type = 'SIMPLE'
mod.levels = 5
apply_modifiers(body)

bm = bmesh.new()
bm.from_mesh(body.data)
for v in bm.verts:
    z = (v.co.z + 0.5) * 0.65 + 0.1
    nz = (z - 0.1) / 0.65
    profile_scale = -0.8 * (nz**2) + 1.0 * nz + 0.75
    
    x = v.co.x * 0.36 * profile_scale
    y = v.co.y * 0.36 * profile_scale
    
    v.co.x = x
    v.co.y = y
    v.co.z = z

bm.to_mesh(body.data)
bm.free()

bevel = body.modifiers.new("Bevel", 'BEVEL')
bevel.width = 0.04
bevel.segments = 6
bevel.limit_method = 'ANGLE'
bevel.angle_limit = math.radians(45)

for p in body.data.polygons:
    p.use_smooth = True

# --- 2. Top Plate ---
top_mesh = bpy.data.meshes.new("TopPlate")
top = bpy.data.objects.new("TopPlate", top_mesh)
collection.objects.link(top)

bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.40
    v.co.y *= 0.40
    v.co.z *= 0.05
    v.co.z += 0.775

edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.01]
bmesh.ops.bevel(bm, geom=edges, offset=0.04, segments=8, profile=0.5, affect='EDGES')

edges = [e for e in bm.edges if e.verts[0].co.z > 0.79 and e.verts[1].co.z > 0.79]
bmesh.ops.bevel(bm, geom=edges, offset=0.015, segments=6, profile=0.5, affect='EDGES')

edges = [e for e in bm.edges if e.verts[0].co.z < 0.76 and e.verts[1].co.z < 0.76]
bmesh.ops.bevel(bm, geom=edges, offset=0.008, segments=1, affect='EDGES')

bm.to_mesh(top.data)
bm.free()

for p in top.data.polygons:
    p.use_smooth = True

# --- 3. Front Panels ---
def create_panel(name, z_start, z_end):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.name = name
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    
    mod = obj.modifiers.new("Subsurf", 'SUBSURF')
    mod.subdivision_type = 'SIMPLE'
    mod.levels = 4
    apply_modifiers(obj)
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    height_z = z_end - z_start
    
    for v in bm.verts:
        z = (v.co.z + 0.5) * height_z + z_start
        nz = (z - 0.1) / 0.65
        profile_scale = -0.8 * (nz**2) + 1.0 * nz + 0.75
        
        panel_width = 0.36 * profile_scale - 0.04
        x = v.co.x * panel_width
        
        body_front_y = -0.18 * profile_scale
        protrusion = 0.015
        front_y = body_front_y - protrusion
        back_y = body_front_y + 0.02
        
        y = (v.co.y + 0.5) * (back_y - front_y) + front_y
        
        v.co.x = x
        v.co.y = y
        v.co.z = z
        
    bm.to_mesh(obj.data)
    bm.free()
    
    bevel = obj.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.008
    bevel.segments = 4
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(45)
    
    for p in obj.data.polygons:
        p.use_smooth = True

create_panel("Door", 0.15, 0.49)
create_panel("Drawer", 0.50, 0.70)

# --- 4. Handles ---
def get_front_y_at_z(z):
    nz = (z - 0.1) / 0.65
    profile_scale = -0.8 * (nz**2) + 1.0 * nz + 0.75
    return -0.18 * profile_scale - 0.015

def create_handle(name, z):
    front_y = get_front_y_at_z(z)
    
    shaft_mesh = bpy.data.meshes.new(name + "_shaft")
    shaft = bpy.data.objects.new(name + "_shaft", shaft_mesh)
    collection.objects.link(shaft)
    
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.008, radius2=0.008, depth=0.02)
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, front_y - 0.01, z), verts=bm.verts)
    bm.to_mesh(shaft.data)
    bm.free()
    for p in shaft.data.polygons:
        p.use_smooth = True
        
    knob_mesh = bpy.data.meshes.new(name + "_knob")
    knob = bpy.data.objects.new(name + "_knob", knob_mesh)
    collection.objects.link(knob)
    
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    for v in bm.verts:
        v.co.x *= 0.025
        v.co.y *= 0.015
        v.co.z *= 0.025
    bmesh.ops.translate(bm, vec=(0, front_y - 0.02 - 0.0075, z), verts=bm.verts)
    bm.to_mesh(knob.data)
    bm.free()
    for p in knob.data.polygons:
        p.use_smooth = True

create_handle("Door_Handle", 0.32)
create_handle("Drawer_Handle", 0.60)

# --- 5. Legs ---
def create_leg(name, x_sign, y_sign):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=0.02, radius2=0.035, depth=0.1)
    bmesh.ops.translate(bm, vec=(x_sign * 0.09, y_sign * 0.09, 0.05), verts=bm.verts)
    bm.to_mesh(obj.data)
    bm.free()
    for p in obj.data.polygons:
        p.use_smooth = True
        
    bevel = obj.modifiers.new("Bevel", 'BEVEL')
    bevel.width = 0.005
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(45)

create_leg("Leg_FL", -1, -1)
create_leg("Leg_FR", 1, -1)
create_leg("Leg_BL", -1, 1)
create_leg("Leg_BR", 1, 1)

# --- Save and Render ---
output_path = os.path.join(os.getcwd(), "sonuc.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_path)

cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (1.2, -1.2, 0.8)
direction = Vector((0, 0, 0.4)) - cam_obj.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

light_data = bpy.data.lights.new(name="Light", type='AREA')
light_data.energy = 500
light_data.size = 2.0
light_obj = bpy.data.objects.new(name="Light", object_data=light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.location = (1, -1, 1.5)
light_obj.rotation_euler = rot_quat.to_euler()

light2_data = bpy.data.lights.new(name="Light2", type='AREA')
light2_data.energy = 200
light2_data.size = 2.0
light2_obj = bpy.data.objects.new(name="Light2", object_data=light2_data)
bpy.context.scene.collection.objects.link(light2_obj)
light2_obj.location = (-1, -1, 1.0)
direction2 = Vector((0, 0, 0.4)) - light2_obj.location
light2_obj.rotation_euler = direction2.to_track_quat('-Z', 'Y').to_euler()

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 800
bpy.context.scene.render.filepath = os.path.join(os.getcwd(), "preview.png")
bpy.ops.render.render(write_still=True)
