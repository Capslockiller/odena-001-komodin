import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

def clear_all():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

def body_width(z):
    z_min = 0.095
    z_max = 0.755
    h = z_max - z_min
    u = max(0.0, min(1.0, (z - z_min) / h))
    
    # Let's refine the body profile:
    # Top: w = 0.190 (38 cm width)
    # Mid bulge: w = 0.200 (40 cm width) at u = 0.65
    # Bottom: w = 0.165 (33 cm width) at u = 0.0
    w_bot = 0.165
    w_mid = 0.200
    w_top = 0.190
    
    if u <= 0.65:
        s = u / 0.65
        return w_bot + (w_mid - w_bot) * math.sin(s * 0.5 * math.pi)
    else:
        s = (u - 0.65) / 0.35
        return w_mid - (w_mid - w_top) * (math.sin(s * 0.5 * math.pi) ** 2)

def body_slope(z):
    dz = 0.001
    return (body_width(z + dz) - body_width(z - dz)) / (2.0 * dz)

def rounded_square_ring(w, r_c, n_seg_per_corner=8):
    d = w - r_c
    coords = []
    corners = [
        (d, d, 0.0),
        (-d, d, 0.5 * math.pi),
        (-d, -d, 1.0 * math.pi),
        (d, -d, 1.5 * math.pi),
    ]
    for cx, cy, start_ang in corners:
        for i in range(n_seg_per_corner):
            ang = start_ang + (i / n_seg_per_corner) * (0.5 * math.pi)
            coords.append((cx + r_c * math.cos(ang), cy + r_c * math.sin(ang)))
    return coords

def cap_ring(bm, ring_verts, normal_up=True):
    n = len(ring_verts)
    center_co = sum((v.co for v in ring_verts), Vector()) / n
    inset_verts = []
    for v in ring_verts:
        iv = bm.verts.new(center_co + 0.4 * (v.co - center_co))
        inset_verts.append(iv)
    bm.verts.ensure_lookup_table()
    
    for i in range(n):
        v0 = ring_verts[i]
        v1 = ring_verts[(i + 1) % n]
        i0 = inset_verts[i]
        i1 = inset_verts[(i + 1) % n]
        if normal_up:
            bm.faces.new((v0, v1, i1, i0))
        else:
            bm.faces.new((v0, i0, i1, v1))
            
    c_v = bm.verts.new(center_co)
    bm.verts.ensure_lookup_table()
    for i in range(n):
        i0 = inset_verts[i]
        i1 = inset_verts[(i + 1) % n]
        if normal_up:
            bm.faces.new((i0, i1, c_v))
        else:
            bm.faces.new((i0, c_v, i1))

def build_body(col):
    bm = bmesh.new()
    n_rings = 33
    n_seg_corner = 8
    rings_verts = []
    
    z_min = 0.095
    z_max = 0.755
    
    for k in range(n_rings):
        t = k / (n_rings - 1)
        z = z_min + t * (z_max - z_min)
        w = body_width(z)
        r_c = 0.035 * (w / 0.200)
        ring_2d = rounded_square_ring(w, r_c, n_seg_corner)
        v_row = [bm.verts.new((x, y, z)) for x, y in ring_2d]
        rings_verts.append(v_row)
        
    bm.verts.ensure_lookup_table()
    n_verts_ring = len(rings_verts[0])
    
    for k in range(n_rings - 1):
        for i in range(n_verts_ring):
            v00 = rings_verts[k][i]
            v10 = rings_verts[k][(i + 1) % n_verts_ring]
            v11 = rings_verts[k + 1][(i + 1) % n_verts_ring]
            v01 = rings_verts[k + 1][i]
            bm.faces.new((v00, v10, v11, v01))
            
    cap_ring(bm, rings_verts[0], normal_up=False)
    cap_ring(bm, rings_verts[-1], normal_up=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new("CabinetBodyMesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("CabinetBody", mesh)
    col.objects.link(obj)
    mesh.shade_smooth()
    
    bev = obj.modifiers.new("Bevel", type='BEVEL')
    bev.width = 0.005
    bev.segments = 3
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(40)
    obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

def build_table_top(col):
    bm = bmesh.new()
    n_seg_corner = 12
    
    z_bot = 0.755
    z_chamfer_top = 0.763
    z_fillet_bot = 0.780
    z_top = 0.800
    
    w_full = 0.215
    w_bot = w_full - 0.008
    r_plan_full = 0.040
    
    profile_levels = [
        (z_bot, w_bot, r_plan_full * (w_bot / w_full)),
        (z_chamfer_top, w_full, r_plan_full),
        (z_fillet_bot, w_full, r_plan_full),
    ]
    
    n_fillet_steps = 10
    r_fillet = z_top - z_fillet_bot
    w_fillet_center = w_full - r_fillet
    
    for i in range(1, n_fillet_steps + 1):
        ang = (i / n_fillet_steps) * (0.5 * math.pi)
        z = z_fillet_bot + r_fillet * math.sin(ang)
        w = w_fillet_center + r_fillet * math.cos(ang)
        profile_levels.append((z, w, r_plan_full * (w / w_full)))
        
    rings_verts = []
    for z, w, r_c in profile_levels:
        ring_2d = rounded_square_ring(w, r_c, n_seg_corner)
        v_row = [bm.verts.new((x, y, z)) for x, y in ring_2d]
        rings_verts.append(v_row)
        
    bm.verts.ensure_lookup_table()
    n_rings = len(rings_verts)
    n_verts_ring = len(rings_verts[0])
    
    for k in range(n_rings - 1):
        for i in range(n_verts_ring):
            v00 = rings_verts[k][i]
            v10 = rings_verts[k][(i + 1) % n_verts_ring]
            v11 = rings_verts[k + 1][(i + 1) % n_verts_ring]
            v01 = rings_verts[k + 1][i]
            bm.faces.new((v00, v10, v11, v01))
            
    cap_ring(bm, rings_verts[0], normal_up=False)
    cap_ring(bm, rings_verts[-1], normal_up=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new("TableTopMesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("TableTop", mesh)
    col.objects.link(obj)
    mesh.shade_smooth()
    obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

def build_panel(name, z_min, z_max, col, nx=16, nz=20, width_fn=None, front_proud=0.008, back_embed=0.004):
    bm = bmesh.new()
    verts_front = []
    verts_back = []
    
    for j in range(nz):
        t = j / (nz - 1)
        z = z_min + t * (z_max - z_min)
        bw = body_width(z)
        wp = width_fn(z)
        
        row_f = []
        row_b = []
        for i in range(nx):
            u = -1.0 + 2.0 * (i / (nx - 1))
            x = u * wp
            yf = -bw - front_proud
            yb = -bw + back_embed
            vf = bm.verts.new((x, yf, z))
            vb = bm.verts.new((x, yb, z))
            row_f.append(vf)
            row_b.append(vb)
        verts_front.append(row_f)
        verts_back.append(row_b)
        
    bm.verts.ensure_lookup_table()
    
    for j in range(nz - 1):
        for i in range(nx - 1):
            bm.faces.new((verts_front[j][i], verts_front[j+1][i], verts_front[j+1][i+1], verts_front[j][i+1]))
            bm.faces.new((verts_back[j][i], verts_back[j][i+1], verts_back[j+1][i+1], verts_back[j+1][i]))
            
    for i in range(nx - 1):
        bm.faces.new((verts_front[0][i], verts_front[0][i+1], verts_back[0][i+1], verts_back[0][i]))
        bm.faces.new((verts_front[nz-1][i], verts_back[nz-1][i], verts_back[nz-1][i+1], verts_front[nz-1][i+1]))
        
    for j in range(nz - 1):
        bm.faces.new((verts_front[j][0], verts_back[j][0], verts_back[j+1][0], verts_front[j+1][0]))
        bm.faces.new((verts_front[j][nx-1], verts_front[j+1][nx-1], verts_back[j+1][nx-1], verts_back[j][nx-1]))
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new(f"{name}Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mesh.shade_smooth()
    
    bev = obj.modifiers.new("Bevel", type='BEVEL')
    bev.width = 0.005
    bev.segments = 4
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(45)
    obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

def build_knob(name, z_center, col):
    profile = [
        (0.000, 0.008),
        (0.003, 0.0065),
        (0.012, 0.0065),
        (0.016, 0.013),
        (0.021, 0.021),   # 42 mm diameter
        (0.026, 0.020),
        (0.029, 0.015),
        (0.031, 0.000),
    ]
    bm = bmesh.new()
    n_radial = 24
    rings = []
    for y_ax, r in profile:
        row = []
        if r < 1e-5:
            v = bm.verts.new((0.0, y_ax, 0.0))
            row = [v] * n_radial
        else:
            for i in range(n_radial):
                ang = (i / n_radial) * 2.0 * math.pi
                row.append(bm.verts.new((r * math.cos(ang), y_ax, r * math.sin(ang))))
        rings.append(row)
    bm.verts.ensure_lookup_table()
    
    base_center = bm.verts.new((0.0, 0.0, 0.0))
    bm.verts.ensure_lookup_table()
    for i in range(n_radial):
        bm.faces.new((base_center, rings[0][(i + 1) % n_radial], rings[0][i]))
        
    for k in range(len(profile) - 2):
        for i in range(n_radial):
            bm.faces.new((rings[k][i], rings[k][(i + 1) % n_radial], rings[k + 1][(i + 1) % n_radial], rings[k + 1][i]))
            
    tip_v = rings[-1][0]
    last_ring = rings[-2]
    for i in range(n_radial):
        bm.faces.new((last_ring[i], last_ring[(i + 1) % n_radial], tip_v))
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mesh.shade_smooth()
    
    sub = obj.modifiers.new("Subdivision", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    
    bw = body_width(z_center)
    y_pos = -bw - 0.008
    z_pos = z_center
    slope = body_slope(z_center)
    no_y = -1.0
    no_z = -slope
    mag = math.sqrt(no_y**2 + no_z**2)
    no_y /= mag
    no_z /= mag
    
    rot_mat = Matrix([
        [1.0, 0.0, 0.0],
        [0.0, no_y, -no_z],
        [0.0, no_z,  no_y]
    ]).to_4x4()
    obj.matrix_world = Matrix.Translation((0.0, y_pos, z_pos)) @ rot_mat
    return obj

def build_leg(name, x_pos, y_pos, col):
    bm = bmesh.new()
    n_radial = 24
    levels = [
        (0.000, 0.016),
        (0.005, 0.021),
        (0.100, 0.029),
    ]
    rings = []
    for z_lvl, r in levels:
        row = []
        for i in range(n_radial):
            ang = (i / n_radial) * 2.0 * math.pi
            row.append(bm.verts.new((r * math.cos(ang), r * math.sin(ang), z_lvl)))
        rings.append(row)
    bm.verts.ensure_lookup_table()
    
    bot_center = bm.verts.new((0.0, 0.0, 0.000))
    bm.verts.ensure_lookup_table()
    for i in range(n_radial):
        bm.faces.new((bot_center, rings[0][(i + 1) % n_radial], rings[0][i]))
    for k in range(len(levels) - 1):
        for i in range(n_radial):
            bm.faces.new((rings[k][i], rings[k][(i + 1) % n_radial], rings[k + 1][(i + 1) % n_radial], rings[k + 1][i]))
    top_center = bm.verts.new((0.0, 0.0, 0.100))
    bm.verts.ensure_lookup_table()
    for i in range(n_radial):
        bm.faces.new((top_center, rings[-1][i], rings[-1][(i + 1) % n_radial]))
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    mesh.shade_smooth()
    obj.location = (x_pos, y_pos, 0.0)
    
    bev = obj.modifiers.new("Bevel", type='BEVEL')
    bev.width = 0.003
    bev.segments = 3
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(45)
    obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

def render_comparison(style_name, width_fn_drawer, width_fn_door, z_drawer_min, z_drawer_max, z_door_min, z_door_max):
    clear_all()
    col = bpy.data.collections.new("Molly's Nightstand")
    bpy.context.scene.collection.children.link(col)
    
    build_body(col)
    build_table_top(col)
    build_panel("DrawerFront", z_drawer_min, z_drawer_max, col, nx=16, nz=16, width_fn=width_fn_drawer)
    build_panel("DoorFront", z_door_min, z_door_max, col, nx=16, nz=24, width_fn=width_fn_door)
    build_knob("KnobDrawer", (z_drawer_min + z_drawer_max) / 2.0, col)
    build_knob("KnobDoor", (z_door_min + z_door_max) / 2.0, col)
    
    # Closer to corners: leg_dist = 0.122
    leg_dist = 0.122
    build_leg("Leg_FL", -leg_dist, -leg_dist, col)
    build_leg("Leg_FR",  leg_dist, -leg_dist, col)
    build_leg("Leg_BL", -leg_dist,  leg_dist, col)
    build_leg("Leg_BR",  leg_dist,  leg_dist, col)
    
    # Render front view
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'SINGLE'
    scene.display.shading.single_color = (0.88, 0.86, 0.82)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = 'BOTH'
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    
    cam_data = bpy.data.cameras.new("Cam")
    cam_obj = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    cam_obj.location = Vector((0.0, -1.4, 0.42))
    direction = Vector((0, 0, 0.42)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 0.95
    
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "onizleme")
    scene.render.filepath = os.path.join(out_dir, f"compare_{style_name}.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered:", scene.render.filepath)

# Test 1: Rectangular panels (constant width = 29 cm, perfectly aligned edges)
# Z ranges:
# Door: z 0.145 to 0.515 (37 cm)
# Gap: 5 mm (0.515 to 0.520)
# Drawer: z 0.520 to 0.705 (18.5 cm) - exactly 1:2 ratio!
render_comparison(
    "rectangular",
    lambda z: 0.148, # 29.6 cm width
    lambda z: 0.148, # 29.6 cm width
    0.520, 0.705,
    0.145, 0.515
)

# Test 2: Unified subtle taper (both drawer and door follow a smooth straight-line taper from top to bottom)
# At top (z = 0.705): half-width 0.155 (31 cm)
# At bottom (z = 0.145): half-width 0.138 (27.6 cm)
def unified_taper(z):
    t = (z - 0.145) / (0.705 - 0.145)
    return 0.138 + t * (0.155 - 0.138)

render_comparison(
    "unified_taper",
    unified_taper,
    unified_taper,
    0.520, 0.705,
    0.145, 0.515
)
