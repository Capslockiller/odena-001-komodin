import bpy
import bmesh
import math
from mathutils import Vector

# Clear all
bpy.ops.wm.read_factory_settings(use_empty=True)

# Set scene scale to metric
bpy.context.scene.unit_settings.system = 'METRIC'

# Create collection
coll_name = "Molly's Nightstand"
coll = bpy.data.collections.new(coll_name)
bpy.context.scene.collection.children.link(coll)

def link_obj(obj):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)

# ---------------------------------------------------------
# Body
# ---------------------------------------------------------
bm_body = bmesh.new()
bmesh.ops.create_cube(bm_body, size=1.0)
# Subdivide so it bends nicely with Lattice
bmesh.ops.subdivide_edges(bm_body, edges=bm_body.edges, cuts=8)

for v in bm_body.verts:
    v.co.x *= 0.36
    v.co.y *= 0.36
    v.co.z = (v.co.z + 0.5) * 0.65 + 0.1

mesh_body = bpy.data.meshes.new("Body")
bm_body.to_mesh(mesh_body)
bm_body.free()
body = bpy.data.objects.new("Body", mesh_body)
link_obj(body)

# Bevel vertical corners of the body
# Since we subdivided, limit by angle will work on the 90-degree corners.
body_bevel = body.modifiers.new("Bevel", 'BEVEL')
body_bevel.limit_method = 'ANGLE'
body_bevel.angle_limit = math.radians(45)
body_bevel.width = 0.04
body_bevel.segments = 8

# ---------------------------------------------------------
# Top Board
# ---------------------------------------------------------
bm_top = bmesh.new()
bmesh.ops.create_cube(bm_top, size=1.0)
for v in bm_top.verts:
    v.co.x *= 0.42
    v.co.y *= 0.42
    v.co.z *= 0.05

# Bevel vertical corners
vert_edges = [e for e in bm_top.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.01]
bmesh.ops.bevel(bm_top, geom=vert_edges, offset=0.04, segments=6, profile=0.5, affect='EDGES')

# Bevel top edges
top_edges = [e for e in bm_top.edges if e.verts[0].co.z > 0.01 and e.verts[1].co.z > 0.01]
bmesh.ops.bevel(bm_top, geom=top_edges, offset=0.02, segments=6, profile=0.5, affect='EDGES')

# Bevel bottom edges
bottom_edges = [e for e in bm_top.edges if e.verts[0].co.z < -0.01 and e.verts[1].co.z < -0.01]
bmesh.ops.bevel(bm_top, geom=bottom_edges, offset=0.01, segments=2, profile=0.5, affect='EDGES')

mesh_top = bpy.data.meshes.new("TopBoard")
bm_top.to_mesh(mesh_top)
bm_top.free()
top = bpy.data.objects.new("TopBoard", mesh_top)
top.location = (0, 0, 0.775)
link_obj(top)

# ---------------------------------------------------------
# Drawer and Door
# ---------------------------------------------------------
def create_panel(name, width, height, thick, z_center, y_center):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=6)
    for v in bm.verts:
        v.co.x *= width
        v.co.y *= thick
        v.co.y += y_center
        v.co.z = (v.co.z + 0.5) * height + (z_center - height/2.0)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    link_obj(obj)
    
    bevel = obj.modifiers.new("Bevel", 'BEVEL')
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(45)
    bevel.width = 0.015
    bevel.segments = 4
    return obj

# Y front of body is -0.18. So center of panels is around -0.19 to protrude.
drawer = create_panel("Drawer", 0.30, 0.20, 0.02, 0.62, -0.19)
door = create_panel("Door", 0.30, 0.36, 0.02, 0.31, -0.19)

# ---------------------------------------------------------
# Knobs
# ---------------------------------------------------------
def create_knob(name, z_center):
    # Stem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.015, location=(0, -0.2075, z_center))
    stem = bpy.context.active_object
    stem.rotation_euler[0] = math.pi / 2
    
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018, location=(0, -0.215, z_center))
    head = bpy.context.active_object
    head.scale[1] = 0.5
    
    # Join
    bpy.ops.object.select_all(action='DESELECT')
    stem.select_set(True)
    head.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()
    
    head.name = name
    link_obj(head)
    return head

knob_drawer = create_knob("Knob_Drawer", 0.62)
knob_door = create_knob("Knob_Door", 0.31)

# ---------------------------------------------------------
# Legs
# ---------------------------------------------------------
for i, x in enumerate([-0.13, 0.13]):
    for j, y in enumerate([-0.13, 0.13]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.035, depth=0.1, location=(x, y, 0.05))
        leg = bpy.context.active_object
        leg.name = f"Leg_{i}_{j}"
        link_obj(leg)
        
        # Taper
        for v in leg.data.vertices:
            if v.co.z < 0:
                v.co.x *= 0.5
                v.co.y *= 0.5
                
        # Bevel bottom
        leg_bevel = leg.modifiers.new("Bevel", 'BEVEL')
        leg_bevel.limit_method = 'ANGLE'
        leg_bevel.angle_limit = math.radians(45)
        leg_bevel.width = 0.005
        leg_bevel.segments = 3

# ---------------------------------------------------------
# Lattice (Bulge and Taper)
# ---------------------------------------------------------
bpy.ops.object.add(type='LATTICE', location=(0, 0, 0.425))
lattice = bpy.context.active_object
lattice.name = "Body_Lattice"
link_obj(lattice)
lattice.scale = (0.40, 0.40, 0.65)

lat_data = lattice.data
lat_data.points_u = 3
lat_data.points_v = 3
lat_data.points_w = 3

for w in range(3):
    for v in range(3):
        for u in range(3):
            idx = u + v * 3 + w * 9
            pt = lat_data.points[idx]
            x, y, z = pt.co
            
            scale = 1.0
            if w == 0:
                scale = 0.85 # narrow bottom
            elif w == 1:
                scale = 1.08 # bulge middle
            elif w == 2:
                scale = 1.00 # match top
                
            pt.co_deform = (x * scale, y * scale, z)

# Apply Lattice Modifier to Body and Panels
for obj in [body, drawer, door, knob_drawer, knob_door]:
    mod = obj.modifiers.new("Bulge", 'LATTICE')
    mod.object = lattice

# ---------------------------------------------------------
# Smooth Shading
# ---------------------------------------------------------
for obj in coll.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = True
        # add auto smooth equivalent in 4.x/5.x
        if hasattr(obj.data, "use_auto_smooth"):
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(60)

# Save the blend file
bpy.ops.wm.save_as_mainfile(filepath="//sonuc.blend")

# ---------------------------------------------------------
# Render Preview
# ---------------------------------------------------------
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000

bpy.ops.object.camera_add(location=(1.0, -1.2, 0.9))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

bpy.ops.object.empty_add(location=(0, 0, 0.4))
target = bpy.context.active_object

cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.target = target
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'

# Add basic lighting
bpy.ops.object.light_add(type='SUN', location=(2, -2, 3))
sun1 = bpy.context.active_object
sun1.data.energy = 2.0
sun1.rotation_euler = (math.radians(45), 0, math.radians(45))

bpy.ops.object.light_add(type='SUN', location=(-2, -1, 2))
sun2 = bpy.context.active_object
sun2.data.energy = 0.5
sun2.rotation_euler = (math.radians(45), 0, math.radians(-45))

bpy.context.scene.render.filepath = "//preview.png"
bpy.ops.render.render(write_still=True)
