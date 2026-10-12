import bpy
import bmesh
from mathutils import Vector, Matrix
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create collection
collection = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(collection)

# Helper function to create a smooth cube with modifiers
def create_body_mesh():
    """Create the main cabinet body with curved sides"""
    # Create base cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.4))
    body = bpy.context.active_object
    body.scale = (0.4, 0.4, 0.8)  # 40x40cm base, 80cm height
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(scale=True)

    # Apply smooth shading
    bpy.ops.object.shade_smooth()

    # Add subdivision surface for smooth curves
    subsurf = body.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 3
    subsurf.render_levels = 3

    # Add simple deform to create the bulging sides and tapering
    # We'll use lattice deform instead for more control
    return body

def create_tabletop():
    """Create the tabletop that overhangs slightly"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.82))
    tabletop = bpy.context.active_object
    tabletop.scale = (0.42, 0.42, 0.04)  # Slightly larger, thin
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.object.shade_smooth()

    # Add bevel to edges
    bevel = tabletop.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.02
    bevel.segments = 3

    # Add subdivision for smooth corners
    subsurf = tabletop.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2

    return tabletop

def create_drawer_front():
    """Create the shallow drawer front panel"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.195, 0.62))
    drawer = bpy.context.active_object
    drawer.scale = (0.38, 0.01, 0.15)  # Wide, thin, short height
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.object.shade_smooth()

    # Add bevel for soft edges
    bevel = drawer.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.008
    bevel.segments = 2

    return drawer

def create_door_front():
    """Create the larger door panel below drawer"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.195, 0.35))
    door = bpy.context.active_object
    door.scale = (0.38, 0.01, 0.32)  # Wide, thin, taller
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.object.shade_smooth()

    # Add bevel for soft edges
    bevel = door.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.008
    bevel.segments = 2

    return door

def create_knob(x, y, z):
    """Create a small round knob"""
    # Create a small sphere for the knob head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(x, y, z))
    knob_head = bpy.context.active_object

    # Create a small cylinder for the stem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.015, location=(x, y-0.012, z))
    knob_stem = bpy.context.active_object
    knob_stem.rotation_euler.x = math.radians(90)

    return knob_head, knob_stem

def create_feet():
    """Create four feet at corners"""
    feet = []
    foot_positions = [
        (0.16, 0.16, 0.04),
        (0.16, -0.16, 0.04),
        (-0.16, 0.16, 0.04),
        (-0.16, -0.16, 0.04),
    ]

    for pos in foot_positions:
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        foot = bpy.context.active_object
        foot.scale = (0.04, 0.04, 0.06)  # Thick, short, tapering
        foot.scale.z = 0.05  # Slightly smaller for taper effect
        bpy.ops.object.transform_apply(scale=True)

        bpy.ops.object.shade_smooth()

        # Add bevel
        bevel = foot.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.003
        bevel.segments = 1

        feet.append(foot)

    return feet

def apply_lattice_deform(obj, scale_factors):
    """Apply lattice deform to create bulging effect"""
    # Create lattice
    lattice_data = bpy.data.lattices.new(name="Lattice")
    lattice_data.points_u = 3
    lattice_data.points_v = 3
    lattice_data.points_w = 4

    lattice_obj = bpy.data.objects.new(name="Lattice", object_data=lattice_data)
    bpy.context.collection.objects.link(lattice_obj)

    # Scale lattice to fit object
    lattice_obj.scale = (0.5, 0.5, 1)
    lattice_obj.location = obj.location

    # Apply lattice modifier
    lat_mod = obj.modifiers.new(name="Lattice", type='LATTICE')
    lat_mod.object = lattice_obj

    return lattice_obj

# Create all parts
print("Creating body...")
body = create_body_mesh()

print("Creating tabletop...")
tabletop = create_tabletop()

print("Creating drawer front...")
drawer = create_drawer_front()

print("Creating door...")
door = create_door_front()

print("Creating knobs...")
drawer_knob_head, drawer_knob_stem = create_knob(0, 0.195, 0.62)
door_knob_head, door_knob_stem = create_knob(0, 0.195, 0.35)

print("Creating feet...")
feet = create_feet()

# Move all objects to collection
objects_to_add = [body, tabletop, drawer, door,
                  drawer_knob_head, drawer_knob_stem,
                  door_knob_head, door_knob_stem] + feet

for obj in objects_to_add:
    # Remove from default collection
    for col in obj.users_collection:
        col.objects.unlink(obj)
    # Add to our collection
    collection.objects.link(obj)

# Set active collection
bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]

# Save the file
output_path = r"<tezgah>\kosular\test-v2\haiku-yok-r3\sonuc.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"Model saved to {output_path}")
print(f"Parts created:")
print(f"  - Body (with subdivision)")
print(f"  - Tabletop (with bevel)")
print(f"  - Drawer front")
print(f"  - Door front")
print(f"  - 2x Knobs (heads and stems)")
print(f"  - 4x Feet")
