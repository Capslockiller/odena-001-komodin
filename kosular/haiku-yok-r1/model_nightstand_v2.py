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

def create_body_mesh():
    bm = bmesh.new()

    # Create the body as a box with tapered bottom using scale
    # Base of body (will be wider due to bulge)
    # We'll create multiple height rings to define the bulging shape

    # Number of subdivisions around the body
    sides = 8
    height_steps = 5  # Bottom, bulge, middle, upper, top

    # Define height positions
    heights = [0, 0.15, 0.35, 0.52, 0.65]  # body_height positions

    # For each height, define the xy scale factor
    # At bottom: 1.0, bulge out to 1.2 at 1/3 height, taper back to 1.0 at top
    scales = [0.85, 1.15, 1.2, 1.1, 1.0]  # X scale (Y scale derived from keeping square)

    verts_per_ring = []

    for h_idx, (height, scale) in enumerate(zip(heights, scales)):
        ring_verts = []
        for i in range(sides):
            angle = (i / sides) * 2 * math.pi
            x = math.cos(angle) * (base_width / 2) * scale
            y = math.sin(angle) * (base_depth / 2) * scale
            v = bm.verts.new((x, y, height))
            ring_verts.append(v)
        verts_per_ring.append(ring_verts)

    # Create faces between rings
    for ring_idx in range(len(verts_per_ring) - 1):
        for vert_idx in range(sides):
            next_vert_idx = (vert_idx + 1) % sides

            v0 = verts_per_ring[ring_idx][vert_idx]
            v1 = verts_per_ring[ring_idx][next_vert_idx]
            v2 = verts_per_ring[ring_idx + 1][next_vert_idx]
            v3 = verts_per_ring[ring_idx + 1][vert_idx]

            bm.faces.new((v0, v1, v2, v3))

    # Create top and bottom caps
    bottom_verts = verts_per_ring[0]
    bm.faces.new(bottom_verts)

    top_verts = verts_per_ring[-1]
    bm.faces.new(top_verts)

    return bm

# Create the body
print("Creating body...")
bm_body = create_body_mesh()
mesh_body = bpy.data.meshes.new("Body")
bm_body.to_mesh(mesh_body)
mesh_body.update()
obj_body = bpy.data.objects.new("Body", mesh_body)
collection.objects.link(obj_body)

# Add smooth shading and subdivision surface
for face in mesh_body.polygons:
    face.use_smooth = True
subsurf = obj_body.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Create top surface (tabla)
print("Creating top surface...")
def create_top_mesh():
    bm = bmesh.new()

    overhang = 0.05
    top_width = base_width + 2 * overhang
    top_depth = base_depth + 2 * overhang
    top_z = body_height
    top_thickness = top_height

    # Create a simple rounded top surface
    # We'll use a box with beveled edges
    v0 = bm.verts.new((-top_width/2, top_depth/2, top_z))
    v1 = bm.verts.new((top_width/2, top_depth/2, top_z))
    v2 = bm.verts.new((top_width/2, -top_depth/2, top_z))
    v3 = bm.verts.new((-top_width/2, -top_depth/2, top_z))

    v4 = bm.verts.new((-top_width/2, top_depth/2, top_z + top_thickness))
    v5 = bm.verts.new((top_width/2, top_depth/2, top_z + top_thickness))
    v6 = bm.verts.new((top_width/2, -top_depth/2, top_z + top_thickness))
    v7 = bm.verts.new((-top_width/2, -top_depth/2, top_z + top_thickness))

    bm.faces.new((v0, v1, v2, v3))
    bm.faces.new((v4, v7, v6, v5))
    bm.faces.new((v0, v3, v7, v4))
    bm.faces.new((v1, v5, v6, v2))
    bm.faces.new((v0, v4, v5, v1))
    bm.faces.new((v3, v2, v6, v7))

    return bm

bm_top = create_top_mesh()
mesh_top = bpy.data.meshes.new("Top")
bm_top.to_mesh(mesh_top)
mesh_top.update()
obj_top = bpy.data.objects.new("Top", mesh_top)
collection.objects.link(obj_top)
for face in mesh_top.polygons:
    face.use_smooth = True

bevel = obj_top.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.012
bevel.segments = 2

# Create drawer (top front panel)
print("Creating drawer...")
def create_drawer_mesh():
    bm = bmesh.new()

    drawer_height = body_height * 0.22
    drawer_y_offset = 0.012
    drawer_z_start = body_height - drawer_height - 0.003
    padding = 0.018
    thickness = 0.008

    # Front panel
    x0 = -base_width/2 + padding
    x1 = base_width/2 - padding
    y0 = base_depth/2 - thickness
    y1 = base_depth/2 + drawer_y_offset
    z0 = drawer_z_start
    z1 = drawer_z_start + drawer_height

    v0 = bm.verts.new((x0, y0, z0))
    v1 = bm.verts.new((x1, y0, z0))
    v2 = bm.verts.new((x1, y1, z0))
    v3 = bm.verts.new((x0, y1, z0))

    v4 = bm.verts.new((x0, y0, z1))
    v5 = bm.verts.new((x1, y0, z1))
    v6 = bm.verts.new((x1, y1, z1))
    v7 = bm.verts.new((x0, y1, z1))

    bm.faces.new((v0, v1, v2, v3))
    bm.faces.new((v4, v7, v6, v5))
    bm.faces.new((v0, v3, v7, v4))
    bm.faces.new((v1, v5, v6, v2))
    bm.faces.new((v0, v4, v5, v1))
    bm.faces.new((v3, v2, v6, v7))

    return bm

bm_drawer = create_drawer_mesh()
mesh_drawer = bpy.data.meshes.new("Drawer")
bm_drawer.to_mesh(mesh_drawer)
mesh_drawer.update()
obj_drawer = bpy.data.objects.new("Drawer", mesh_drawer)
collection.objects.link(obj_drawer)

# Create door (bottom front panel)
print("Creating door...")
def create_door_mesh():
    bm = bmesh.new()

    door_height = body_height * 0.62
    door_y_offset = 0.012
    door_z_start = 0.025
    padding = 0.018
    thickness = 0.008

    x0 = -base_width/2 + padding
    x1 = base_width/2 - padding
    y0 = base_depth/2 - thickness
    y1 = base_depth/2 + door_y_offset
    z0 = door_z_start
    z1 = door_z_start + door_height

    v0 = bm.verts.new((x0, y0, z0))
    v1 = bm.verts.new((x1, y0, z0))
    v2 = bm.verts.new((x1, y1, z0))
    v3 = bm.verts.new((x0, y1, z0))

    v4 = bm.verts.new((x0, y0, z1))
    v5 = bm.verts.new((x1, y0, z1))
    v6 = bm.verts.new((x1, y1, z1))
    v7 = bm.verts.new((x0, y1, z1))

    bm.faces.new((v0, v1, v2, v3))
    bm.faces.new((v4, v7, v6, v5))
    bm.faces.new((v0, v3, v7, v4))
    bm.faces.new((v1, v5, v6, v2))
    bm.faces.new((v0, v4, v5, v1))
    bm.faces.new((v3, v2, v6, v7))

    return bm

bm_door = create_door_mesh()
mesh_door = bpy.data.meshes.new("Door")
bm_door.to_mesh(mesh_door)
mesh_door.update()
obj_door = bpy.data.objects.new("Door", mesh_door)
collection.objects.link(obj_door)

# Create knobs as UV spheres
print("Creating knobs...")
def add_knob(x, y, z, name):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.008, location=(x, y, z))
    knob = bpy.context.active_object
    knob.name = name
    for coll in knob.users_collection:
        coll.objects.unlink(knob)
    collection.objects.link(knob)
    return knob

knob1 = add_knob(0, base_depth/2 + 0.018, body_height - 0.05, "Drawer_Knob")
knob2 = add_knob(0, base_depth/2 + 0.018, 0.15, "Door_Knob")

# Create legs as tapered cylinders
print("Creating legs...")
def add_leg(x, y, name):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.08, location=(x, y, 0.04))
    leg = bpy.context.active_object
    leg.name = name
    for coll in leg.users_collection:
        coll.objects.unlink(leg)
    collection.objects.link(leg)
    leg.scale.z = 0.9
    return leg

leg_dist = base_width * 0.32
leg1 = add_leg(-leg_dist, -leg_dist, "Leg_FL")
leg2 = add_leg(leg_dist, -leg_dist, "Leg_FR")
leg3 = add_leg(-leg_dist, leg_dist, "Leg_BL")
leg4 = add_leg(leg_dist, leg_dist, "Leg_BR")

# Save the file
import os
os.chdir("<tezgah>\\kosular\\test-v2\\haiku-yok-r1")
bpy.ops.wm.save_as_mainfile(filepath="sonuc.blend")
print("Model saved to sonuc.blend")
