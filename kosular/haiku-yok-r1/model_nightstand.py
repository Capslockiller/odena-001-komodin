import bpy
import bmesh
from mathutils import Vector
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new collection
collection = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(collection)

# Parameters (in meters)
base_width = 0.4
base_depth = 0.4
body_height = 0.65
top_height = 0.15
total_height = body_height + top_height

# Helper function to create object from bmesh
def bmesh_to_object(bm, name):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj, mesh, bm

# Create main body with bulging sides
def create_body():
    bm = bmesh.new()

    # Create a subdivided cube that we'll shape
    verts = []

    # Base loop (bottom)
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            bm.verts.new((x * base_width/2, y * base_depth/2, 0))

    # Mid-bulge loop (1/3 height)
    bulge_height = body_height * 0.35
    bulge_amount = 0.08
    for x in [-1.2, 0, 1.2]:
        for y in [-1.2, 0, 1.2]:
            x_pos = x * base_width/2 if x != 0 else 0
            y_pos = y * base_depth/2 if y != 0 else 0
            if x != 0:
                x_pos = x_pos + (bulge_amount if x > 0 else -bulge_amount)
            if y != 0:
                y_pos = y_pos + (bulge_amount if y > 0 else -bulge_amount)
            bm.verts.new((x_pos, y_pos, bulge_height))

    # Top loop (body height)
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            bm.verts.new((x * base_width/2, y * base_depth/2, body_height))

    bm.verts.ensure_lookup_table()

    # Create faces to connect the loops
    # This is simplified - bmesh will help with topology

    obj, mesh, bm = bmesh_to_object(bm, "Body")

    # Add Subdivision Surface modifier
    subsurf = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return obj

# Create top surface (tabla)
def create_top():
    bm = bmesh.new()

    overhang = 0.05
    top_width = base_width + 2 * overhang
    top_depth = base_depth + 2 * overhang
    top_z = body_height

    # Create a simple box for the top surface
    verts = []
    # Bottom face
    v0 = bm.verts.new((-top_width/2, top_depth/2, top_z))
    v1 = bm.verts.new((top_width/2, top_depth/2, top_z))
    v2 = bm.verts.new((top_width/2, -top_depth/2, top_z))
    v3 = bm.verts.new((-top_width/2, -top_depth/2, top_z))

    # Top face
    v4 = bm.verts.new((-top_width/2, top_depth/2, top_z + top_height))
    v5 = bm.verts.new((top_width/2, top_depth/2, top_z + top_height))
    v6 = bm.verts.new((top_width/2, -top_depth/2, top_z + top_height))
    v7 = bm.verts.new((-top_width/2, -top_depth/2, top_z + top_height))

    # Create faces
    bm.faces.new((v0, v1, v2, v3))  # Bottom
    bm.faces.new((v4, v7, v6, v5))  # Top
    bm.faces.new((v0, v3, v7, v4))  # Left
    bm.faces.new((v1, v5, v6, v2))  # Right
    bm.faces.new((v0, v4, v5, v1))  # Front
    bm.faces.new((v3, v2, v6, v7))  # Back

    obj, mesh, bm = bmesh_to_object(bm, "Top")

    # Add Bevel modifier for rounded edges
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.015
    bevel.segments = 2

    return obj

# Create drawer (top front panel)
def create_drawer():
    bm = bmesh.new()

    drawer_height = body_height * 0.25
    drawer_y_offset = 0.01
    drawer_z_start = body_height - drawer_height
    padding = 0.02

    v0 = bm.verts.new((-base_width/2 + padding, base_depth/2 + drawer_y_offset, drawer_z_start))
    v1 = bm.verts.new((base_width/2 - padding, base_depth/2 + drawer_y_offset, drawer_z_start))
    v2 = bm.verts.new((base_width/2 - padding, base_depth/2 - padding + drawer_y_offset, drawer_z_start))
    v3 = bm.verts.new((-base_width/2 + padding, base_depth/2 - padding + drawer_y_offset, drawer_z_start))

    v4 = bm.verts.new((-base_width/2 + padding, base_depth/2 + drawer_y_offset, drawer_z_start + drawer_height))
    v5 = bm.verts.new((base_width/2 - padding, base_depth/2 + drawer_y_offset, drawer_z_start + drawer_height))
    v6 = bm.verts.new((base_width/2 - padding, base_depth/2 - padding + drawer_y_offset, drawer_z_start + drawer_height))
    v7 = bm.verts.new((-base_width/2 + padding, base_depth/2 - padding + drawer_y_offset, drawer_z_start + drawer_height))

    bm.faces.new((v0, v1, v2, v3))  # Back
    bm.faces.new((v4, v7, v6, v5))  # Front
    bm.faces.new((v0, v3, v7, v4))  # Left
    bm.faces.new((v1, v5, v6, v2))  # Right
    bm.faces.new((v0, v4, v5, v1))  # Top
    bm.faces.new((v3, v2, v6, v7))  # Bottom

    obj, mesh, bm = bmesh_to_object(bm, "Drawer")
    return obj

# Create door (bottom front panel)
def create_door():
    bm = bmesh.new()

    door_height = body_height * 0.65
    door_y_offset = 0.01
    door_z_start = 0.02
    padding = 0.02

    v0 = bm.verts.new((-base_width/2 + padding, base_depth/2 + door_y_offset, door_z_start))
    v1 = bm.verts.new((base_width/2 - padding, base_depth/2 + door_y_offset, door_z_start))
    v2 = bm.verts.new((base_width/2 - padding, base_depth/2 - padding + door_y_offset, door_z_start))
    v3 = bm.verts.new((-base_width/2 + padding, base_depth/2 - padding + door_y_offset, door_z_start))

    v4 = bm.verts.new((-base_width/2 + padding, base_depth/2 + door_y_offset, door_z_start + door_height))
    v5 = bm.verts.new((base_width/2 - padding, base_depth/2 + door_y_offset, door_z_start + door_height))
    v6 = bm.verts.new((base_width/2 - padding, base_depth/2 - padding + door_y_offset, door_z_start + door_height))
    v7 = bm.verts.new((-base_width/2 + padding, base_depth/2 - padding + door_y_offset, door_z_start + door_height))

    bm.faces.new((v0, v1, v2, v3))  # Back
    bm.faces.new((v4, v7, v6, v5))  # Front
    bm.faces.new((v0, v3, v7, v4))  # Left
    bm.faces.new((v1, v5, v6, v2))  # Right
    bm.faces.new((v0, v4, v5, v1))  # Top
    bm.faces.new((v3, v2, v6, v7))  # Bottom

    obj, mesh, bm = bmesh_to_object(bm, "Door")
    return obj

# Create knob/handle
def create_knob(x_pos, z_pos, name):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.008,
        location=(x_pos, base_depth/2 + 0.015, z_pos)
    )
    knob = bpy.context.active_object
    knob.name = name
    # Move to custom collection
    for coll in knob.users_collection:
        coll.objects.unlink(knob)
    collection.objects.link(knob)
    return knob

# Create legs
def create_legs():
    leg_distance = base_width * 0.35
    leg_height = 0.08
    leg_radius = 0.015

    leg_positions = [
        (-leg_distance, -leg_distance, leg_height/2),
        (leg_distance, -leg_distance, leg_height/2),
        (-leg_distance, leg_distance, leg_height/2),
        (leg_distance, leg_distance, leg_height/2),
    ]

    legs = []
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=leg_radius,
            depth=leg_height,
            location=pos
        )
        leg = bpy.context.active_object
        leg.name = f"Leg_{i}"
        # Move to custom collection
        for coll in leg.users_collection:
            coll.objects.unlink(leg)
        collection.objects.link(leg)
        leg.scale.z = 0.85
        legs.append(leg)

    return legs

# Create all parts
print("Creating body...")
body = create_body()

print("Creating top surface...")
top = create_top()

print("Creating drawer...")
drawer = create_drawer()

print("Creating door...")
door = create_door()

print("Creating knobs...")
drawer_knob = create_knob(0, body_height - 0.05, "Drawer_Knob")
door_knob = create_knob(0, 0.15, "Door_Knob")

print("Creating legs...")
legs = create_legs()

# Save the file
import os
os.chdir("<tezgah>\\kosular\\test-v2\\haiku-yok-r1")
output_file = "sonuc.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_file)
print(f"Model saved to {output_file}")
