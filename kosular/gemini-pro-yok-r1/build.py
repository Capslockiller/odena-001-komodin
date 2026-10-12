import bpy
import bmesh
import math
from mathutils import Vector

def run():
    # Clear all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    col_name = "Molly's Nightstand"
    col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(col)

    def link_obj(obj):
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)

    # Dimensions
    total_h = 0.8
    leg_h = 0.1
    top_h = 0.04
    body_h = total_h - leg_h - top_h # 0.66
    body_z_start = leg_h
    body_z_end = leg_h + body_h

    # 1. Body
    # Create base mesh
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, leg_h + body_h/2))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (0.36, 0.36, body_h)
    bpy.ops.object.transform_apply(scale=True)
    link_obj(body)

    # Subdivide body for deformation
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=10)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Deform function
    def get_bulge_factor(z):
        # z is global Z
        nz = (z - leg_h) / body_h # 0 to 1
        # Bulge: mid is widest. Top is wider than bottom.
        # Top: 0.36, Mid: 0.38, Bottom: 0.30
        if nz < 0.5:
            return 0.30 + (0.38 - 0.30) * (nz / 0.5)
        else:
            return 0.38 - (0.38 - 0.36) * ((nz - 0.5) / 0.5)

    for v in body.data.vertices:
        f = get_bulge_factor(v.co.z)
        # normalize x, y from -0.18..0.18 to -0.5..0.5
        nx = v.co.x / 0.18
        ny = v.co.y / 0.18
        v.co.x = nx * (f / 2)
        v.co.y = ny * (f / 2)

    # Add Bevel for vertical corners
    bevel = body.modifiers.new("Bevel", 'BEVEL')
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(45)
    bevel.width = 0.03
    bevel.segments = 4

    subsurf = body.modifiers.new("Subsurf", 'SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 2

    for p in body.data.polygons:
        p.use_smooth = True

    # 2. Drawer and Door (Panels)
    # They should sit on the front face (y = -front_y).
    # The front face itself has the bulge.
    # Let's create panels by duplicating front faces of body before modifiers? No, better use a simple grid and shrinkwrap, or duplicate after applying bulge.
    
    # We can create a dense grid, deform it with the same bulge function, and solidify.
    # Door: takes up bottom 2/3 of body front.
    # Drawer: takes up top 1/3 of body front.
    # Gap between them.
    
    door_z_start = leg_h + 0.05
    door_z_end = leg_h + body_h * 0.65
    drawer_z_start = door_z_end + 0.02
    drawer_z_end = leg_h + body_h - 0.05

    def create_panel(name, z_start, z_end):
        # Create a grid
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10, size=1, location=(0, 0, 0))
        panel = bpy.context.active_object
        panel.name = name
        
        # We'll map x from -0.15 to 0.15, z from z_start to z_end
        # y will be calculated from bulge + offset
        w = 0.32
        h = z_end - z_start
        panel.scale = (w, h, 1)
        # rotate to stand up facing -y
        panel.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        panel.location.z = z_start + h/2
        bpy.ops.object.transform_apply(location=True)
        
        for v in panel.data.vertices:
            f = get_bulge_factor(v.co.z)
            # The body front y at this z and x is roughly -f/2.
            # But the body front is flat in X before bevel.
            v.co.y = - (f / 2) - 0.005 # slightly outside body
            
            # shrink width to fit inside bevels
            v.co.x *= (f / 0.36) * 0.9

        # Add Solidify
        solid = panel.modifiers.new("Solidify", 'SOLIDIFY')
        solid.thickness = 0.015
        solid.offset = 1 # grow outwards (-y is out, but normal is +y? grid faces +Z initially, rotated 90 on X, so normal is +Y. offset 1 goes to +Y. Wait, let's just check normals.)
        
        # Let's fix normals and direction
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        solid.thickness = 0.015
        solid.offset = -1 # Grow outward
        
        bevel = panel.modifiers.new("Bevel", 'BEVEL')
        bevel.width = 0.008
        bevel.segments = 5
        
        subsurf = panel.modifiers.new("Subsurf", 'SUBSURF')
        subsurf.levels = 2

        for p in panel.data.polygons:
            p.use_smooth = True
            
        link_obj(panel)
        return panel

    door = create_panel("Door", door_z_start, door_z_end)
    drawer = create_panel("Drawer", drawer_z_start, drawer_z_end)

    # 3. Knobs
    def create_knob(name, z_center):
        # find the y position on the panel
        f = get_bulge_factor(z_center)
        y_pos = - (f / 2) - 0.005 - 0.015 # body face + panel gap + panel thickness
        
        # shaft
        bpy.ops.mesh.primitive_cylinder_add(radius=0.007, depth=0.015, location=(0, y_pos - 0.0075, z_center), rotation=(math.radians(90), 0, 0))
        shaft = bpy.context.active_object
        shaft.name = f"{name}_Shaft"
        link_obj(shaft)
        
        # head (basık topuz)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(0, y_pos - 0.02, z_center))
        head = bpy.context.active_object
        head.name = f"{name}_Head"
        head.scale.y = 0.5
        bpy.ops.object.transform_apply(scale=True)
        link_obj(head)
        
        for p in head.data.polygons:
            p.use_smooth = True
        for p in shaft.data.polygons:
            p.use_smooth = True

    create_knob("DoorKnob", (door_z_start + door_z_end)/2 + 0.1) # place door knob slightly above center or center
    create_knob("DrawerKnob", (drawer_z_start + drawer_z_end)/2)

    # 4. Top Board
    # 40x40 cm base, top is larger? "gövdeden her yönden biraz taşan kalın bir tabla"
    # base is 0.30 at bottom, mid is 0.38, top is 0.36. 
    # Let's make top board 0.40 x 0.40
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, leg_h + body_h + top_h/2))
    top = bpy.context.active_object
    top.name = "TopBoard"
    top.scale = (0.40, 0.40, top_h)
    bpy.ops.object.transform_apply(scale=True)
    link_obj(top)

    # "üst kenarı yuvarlak ve dolgun, alt kenarı hafif pahlı. Köşeleri yuvarlatılmış."
    # To do this exactly:
    # Subdivide top a bit, or use Bevel modifier.
    # Bevel on Z edges for rounded corners.
    # Bevel on top edge for round/full.
    # Bevel on bottom edge for chamfer.
    # We can do this destructively in edit mode using bmesh.
    
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(top.data)
    
    # 1. Round the 4 vertical corners
    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.01]
    bmesh.ops.bevel(bm, geom=vertical_edges, offset=0.04, segments=6, profile=0.5, affect='EDGES')
    
    # 2. Top edge (yuvarlak ve dolgun)
    # top edges are those where both vertices have z > top_z_center
    top_z = leg_h + body_h + top_h/2
    top_edges = [e for e in bm.edges if e.verts[0].co.z > top_z - 0.001 and e.verts[1].co.z > top_z - 0.001]
    bmesh.ops.bevel(bm, geom=top_edges, offset=0.015, segments=5, profile=0.5, affect='EDGES')
    
    # 3. Bottom edge (hafif pahlı)
    bottom_edges = [e for e in bm.edges if e.verts[0].co.z < top_z - 0.001 and e.verts[1].co.z < top_z - 0.001]
    bmesh.ops.bevel(bm, geom=bottom_edges, offset=0.005, segments=1, profile=0.5, affect='EDGES')
    
    bmesh.update_edit_mesh(top.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for p in top.data.polygons:
        p.use_smooth = True

    # 5. Legs
    # "Altta dört kısa, kalın, aşağı doğru hafif daralan ayak; köşelere yakın."
    for i, (x_sign, y_sign) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.035, depth=leg_h, location=(x_sign * 0.12, y_sign * 0.12, leg_h/2))
        leg = bpy.context.active_object
        leg.name = f"Leg_{i}"
        
        # Taper
        for v in leg.data.vertices:
            if v.co.z < 0:
                v.co.x *= 0.6
                v.co.y *= 0.6
                
        link_obj(leg)
        for p in leg.data.polygons:
            p.use_smooth = True

    # Check normals
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Save
    bpy.ops.wm.save_as_mainfile(filepath="<tezgah>/kosular/test-v2/gemini-pro-yok-r1/sonuc.blend")

    # Render prep
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.camera_add(location=(1.0, -1.5, 0.8), rotation=(math.radians(75), 0, math.radians(35)))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    # Add lighting
    bpy.ops.object.light_add(type='AREA', location=(1.5, -2, 2))
    light = bpy.context.active_object
    light.data.energy = 500
    light.data.size = 2.0
    
    bpy.ops.object.light_add(type='AREA', location=(-1.5, 0, 1))
    light2 = bpy.context.active_object
    light2.data.energy = 100
    light2.data.size = 2.0

    # Add a floor
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    floor = bpy.context.active_object
    
    # Material for better contrast
    mat = bpy.data.materials.new(name="Clay")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
    bsdf.inputs["Roughness"].default_value = 0.5
    for obj in col.objects:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024

    bpy.context.scene.render.filepath = '<tezgah>/kosular/test-v2/gemini-pro-yok-r1/render_front.png'
    bpy.ops.render.render(write_still=True)

    cam.location = (1.5, -1.0, 1.2)
    cam.rotation_euler = (math.radians(60), 0, math.radians(50))
    bpy.context.scene.render.filepath = '<tezgah>/kosular/test-v2/gemini-pro-yok-r1/render_side.png'
    bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    run()
