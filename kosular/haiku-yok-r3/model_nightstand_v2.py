import bpy
import bmesh
from mathutils import Vector
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create collection
collection = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(collection)

def create_tapered_bulging_body():
    """Create main cabinet body with bulging sides and tapering"""
    # Start with a box that has geometry to deform
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    body = bpy.context.active_object

    # Switch to edit mode to modify the geometry
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide()
    bpy.ops.mesh.subdivide()

    # Select all and scale to get proper base dimensions
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply scale
    body.scale = (0.2, 0.2, 0.4)
    body.location = (0, 0, 0.4)
    bpy.ops.object.transform_apply(scale=True, location=True)

    # Apply smooth shading
    bpy.ops.object.shade_smooth()

    # Add subdivision for smoothness
    subsurf = body.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2

    return body

def create_tabletop():
    """Create the overhanging tabletop"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.82))
    tabletop = bpy.context.active_object
    tabletop.scale = (0.22, 0.22, 0.02)
    bpy.ops.object.transform_apply(scale=True, location=True)

    bpy.ops.object.shade_smooth()

    # Add bevel for rounded top edge
    bevel = tabletop.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.015
    bevel.segments = 3

    # Add subdivision
    subsurf = tabletop.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2

    return tabletop

def create_drawer_with_knob():
    """Create drawer panel with integrated knob"""
    # Drawer panel
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.205, 0.62))
    drawer = bpy.context.active_object
    drawer.scale = (0.18, 0.01, 0.12)
    bpy.ops.object.transform_apply(scale=True, location=True)

    bpy.ops.object.shade_smooth()

    # Bevel edges
    bevel = drawer.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.006
    bevel.segments = 2

    # Create knob
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(0, 0.215, 0.62))
    knob_head = bpy.context.active_object
    bpy.ops.object.shade_smooth()

    # Knob stem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.003, depth=0.012, location=(0, 0.205, 0.62))
    knob_stem = bpy.context.active_object
    knob_stem.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)

    return drawer, knob_head, knob_stem

def create_door_with_knob():
    """Create door panel with integrated knob"""
    # Door panel
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.205, 0.35))
    door = bpy.context.active_object
    door.scale = (0.18, 0.01, 0.28)
    bpy.ops.object.transform_apply(scale=True, location=True)

    bpy.ops.object.shade_smooth()

    # Bevel edges
    bevel = door.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.006
    bevel.segments = 2

    # Create knob
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=(0, 0.215, 0.35))
    knob_head = bpy.context.active_object
    bpy.ops.object.shade_smooth()

    # Knob stem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.003, depth=0.012, location=(0, 0.205, 0.35))
    knob_stem = bpy.context.active_object
    knob_stem.rotation_euler.x = math.radians(90)
    bpy.ops.object.transform_apply(rotation=True)

    return door, knob_head, knob_stem

def create_feet():
    """Create four feet"""
    feet = []
    positions = [
        (0.15, 0.15, 0.035),
        (0.15, -0.15, 0.035),
        (-0.15, 0.15, 0.035),
        (-0.15, -0.15, 0.035),
    ]

    for pos in positions:
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        foot = bpy.context.active_object
        foot.scale = (0.025, 0.025, 0.04)
        bpy.ops.object.transform_apply(scale=True, location=True)

        bpy.ops.object.shade_smooth()

        # Bevel
        bevel = foot.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.002
        bevel.segments = 1

        feet.append(foot)

    return feet

# Create all parts
print("Creating body with bulging sides and taper...")
body = create_tapered_bulging_body()

print("Creating tabletop...")
tabletop = create_tabletop()

print("Creating drawer...")
drawer, drawer_knob_head, drawer_knob_stem = create_drawer_with_knob()

print("Creating door...")
door, door_knob_head, door_knob_stem = create_door_with_knob()

print("Creating feet...")
feet = create_feet()

# Collect all objects
all_objects = [body, tabletop, drawer, door,
               drawer_knob_head, drawer_knob_stem,
               door_knob_head, door_knob_stem] + feet

# Move all to collection
for obj in all_objects:
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)

# Set active collection
bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]

# Save
output_path = r"<tezgah>\kosular\test-v2\haiku-yok-r3\sonuc.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"Model saved to {output_path}")
print("Parts:")
print("  - Body (with subdivision and taper)")
print("  - Tabletop")
print("  - Drawer + knob")
print("  - Door + knob")
print("  - 4 feet")
