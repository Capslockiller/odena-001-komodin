import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def clear_all():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

def get_nightstand_collection():
    col_name = "Molly's Nightstand"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    return col

def body_width(z):
    z_min = 0.095
    z_max = 0.755
    h = z_max - z_min
    u = max(0.0, min(1.0, (z - z_min) / h))
    w_bot = 0.165
    w_mid = 0.200
    w_top = 0.185
    if u <= 0.60:
        s = u / 0.60
        return w_bot + (w_mid - w_bot) * math.sin(s * 0.5 * math.pi)
    else:
        s = (u - 0.60) / 0.40
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
    """Fills a ring of 32 vertices with a clean quad grid."""
    # Create an inset ring first, then center quad
    n = len(ring_verts)
    center_co = sum((v.co for v in ring_verts), Vector()) / n
    # Inset vertices
    inset_verts = []
    for v in ring_verts:
        iv = bm.verts.new(center_co + 0.4 * (v.co - center_co))
        inset_verts.append(iv)
    bm.verts.ensure_lookup_table()
    
    # Quad strip between outer and inset
    for i in range(n):
        v0 = ring_verts[i]
        v1 = ring_verts[(i + 1) % n]
        i0 = inset_verts[i]
        i1 = inset_verts[(i + 1) % n]
        if normal_up:
            bm.faces.new((v0, v1, i1, i0))
        else:
            bm.faces.new((v0, i0, i1, v1))
            
    # Center vertex and triangle fan, or quads
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
        
        v_row = []
        for x, y in ring_2d:
            v_row.append(bm.verts.new((x, y, z)))
        rings_verts.append(v_row)
        
    bm.verts.ensure_lookup_table()
    n_verts_ring = len(rings_verts[0])
    
    # Bridge rings
    for k in range(n_rings - 1):
        for i in range(n_verts_ring):
            v00 = rings_verts[k][i]
            v10 = rings_verts[k][(i + 1) % n_verts_ring]
            v11 = rings_verts[k + 1][(i + 1) % n_verts_ring]
            v01 = rings_verts[k + 1][i]
            bm.faces.new((v00, v10, v11, v01))
            
    # Cap bottom (normal down)
    cap_ring(bm, rings_verts[0], normal_up=False)
    # Cap top (normal up)
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
    
    wn = obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

def build_table_top(col):
    bm = bmesh.new()
    n_seg_corner = 8
    
    # Table top parameters
    z_bot = 0.755
    z_chamfer_top = 0.763
    z_fillet_bot = 0.780
    z_top = 0.800
    
    w_full = 0.215
    w_bot = w_full - 0.008
    r_plan_full = 0.040
    
    # Edge profile rings
    # 1. Bottom chamfer base (z = 0.755, w = w_bot)
    # 2. Chamfer top / straight wall bottom (z = 0.763, w = w_full)
    # 3. Straight wall top / fillet bottom (z = 0.780, w = w_full)
    # 4.. Fillet arc up to z = 0.800
    
    profile_levels = [
        (z_bot, w_bot, r_plan_full * (w_bot / w_full)),
        (z_chamfer_top, w_full, r_plan_full),
        (z_fillet_bot, w_full, r_plan_full),
    ]
    
    n_fillet_steps = 8
    r_fillet = z_top - z_fillet_bot  # 0.020
    w_fillet_center = w_full - r_fillet  # 0.195
    
    for i in range(1, n_fillet_steps + 1):
        ang = (i / n_fillet_steps) * (0.5 * math.pi)
        z = z_fillet_bot + r_fillet * math.sin(ang)
        w = w_fillet_center + r_fillet * math.cos(ang)
        profile_levels.append((z, w, r_plan_full * (w / w_full)))
        
    rings_verts = []
    for z, w, r_c in profile_levels:
        ring_2d = rounded_square_ring(w, r_c, n_seg_corner)
        v_row = []
        for x, y in ring_2d:
            v_row.append(bm.verts.new((x, y, z)))
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
    
    wn = obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

def build_panel(name, z_min, z_max, col, nx=16, nz=20, side_margin=0.038, front_proud=0.008, back_embed=0.004):
    bm = bmesh.new()
    verts_front = []
    verts_back = []
    
    for j in range(nz):
        t = j / (nz - 1)
        z = z_min + t * (z_max - z_min)
        bw = body_width(z)
        wp = bw - side_margin
        
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
            
    # Connect borders
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
    
    wn = obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

def build_knob(name, z_center, col):
    """Creates a turned knob aligned to the panel surface normal."""
    # Profile along local axis Y (0 to length)
    # y: axial distance, r: radius
    profile = [
        (0.000, 0.008),   # base collar at panel
        (0.003, 0.0065),  # stem start
        (0.012, 0.0065),  # stem end
        (0.016, 0.012),   # neck flare
        (0.021, 0.020),   # max diameter (40 mm)
        (0.026, 0.019),   # dome curve
        (0.029, 0.014),   # dome front
        (0.031, 0.000),   # front center tip
    ]
    
    bm = bmesh.new()
    n_radial = 24
    rings = []
    
    for y_ax, r in profile:
        row = []
        if r < 1e-5:
            # Tip vertex
            v = bm.verts.new((0.0, y_ax, 0.0))
            row = [v] * n_radial
        else:
            for i in range(n_radial):
                ang = (i / n_radial) * 2.0 * math.pi
                x = r * math.cos(ang)
                z = r * math.sin(ang)
                row.append(bm.verts.new((x, y_ax, z)))
        rings.append(row)
        
    bm.verts.ensure_lookup_table()
    
    # Cap base (y = 0)
    base_center = bm.verts.new((0.0, 0.0, 0.0))
    bm.verts.ensure_lookup_table()
    for i in range(n_radial):
        v0 = rings[0][i]
        v1 = rings[0][(i + 1) % n_radial]
        bm.faces.new((base_center, v1, v0))
        
    # Bridge rings
    for k in range(len(profile) - 2):
        for i in range(n_radial):
            v00 = rings[k][i]
            v10 = rings[k][(i + 1) % n_radial]
            v11 = rings[k + 1][(i + 1) % n_radial]
            v01 = rings[k + 1][i]
            bm.faces.new((v00, v10, v11, v01))
            
    # Last ring to tip
    tip_v = rings[-1][0]
    last_ring = rings[-2]
    for i in range(n_radial):
        v0 = last_ring[i]
        v1 = last_ring[(i + 1) % n_radial]
        bm.faces.new((v0, v1, tip_v))
        
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
    
    # Position and orient the knob
    bw = body_width(z_center)
    # Front of panel is at y = -bw - 0.008
    y_pos = -bw - 0.008
    x_pos = 0.0
    z_pos = z_center
    
    # Surface normal
    slope = body_slope(z_center)
    # Vector along surface tangent in YZ: (0, -slope, 1)
    # Outward normal pointing mostly in -Y: (0, -1, -slope) normalized
    no_y = -1.0
    no_z = -slope
    mag = math.sqrt(no_y**2 + no_z**2)
    no_y /= mag
    no_z /= mag
    
    # In local knob space, axis points along +Y.
    # We want local +Y to align with world normal (0, no_y, no_z).
    # Since normal is in YZ plane:
    # Local Z maps to tangent: (0, -no_z, no_y)
    # Local X remains (1, 0, 0)
    rot_mat = Matrix([
        [1.0, 0.0, 0.0],
        [0.0, no_y, -no_z],
        [0.0, no_z,  no_y]
    ]).to_4x4()
    
    obj.matrix_world = Matrix.Translation((x_pos, y_pos, z_pos)) @ rot_mat
    
    return obj

def build_leg(name, x_pos, y_pos, col):
    """Creates a short, thick, slightly tapering round leg."""
    bm = bmesh.new()
    n_radial = 24
    
    # Leg spans z = 0.0 to z = 0.100 (overlaps into body base at z = 0.095)
    # Radius profile:
    # z = 0.000: floor pad r = 0.016
    # z = 0.005: rounded rim r = 0.021
    # z = 0.100: top r = 0.028
    levels = [
        (0.000, 0.016),
        (0.005, 0.021),
        (0.100, 0.028),
    ]
    
    rings = []
    for z_lvl, r in levels:
        row = []
        for i in range(n_radial):
            ang = (i / n_radial) * 2.0 * math.pi
            x = r * math.cos(ang)
            y = r * math.sin(ang)
            row.append(bm.verts.new((x, y, z_lvl)))
        rings.append(row)
        
    bm.verts.ensure_lookup_table()
    
    # Cap bottom (z = 0, normal down)
    bot_center = bm.verts.new((0.0, 0.0, 0.000))
    bm.verts.ensure_lookup_table()
    for i in range(n_radial):
        v0 = rings[0][i]
        v1 = rings[0][(i + 1) % n_radial]
        bm.faces.new((bot_center, v1, v0))
        
    # Bridge rings
    for k in range(len(levels) - 1):
        for i in range(n_radial):
            v00 = rings[k][i]
            v10 = rings[k][(i + 1) % n_radial]
            v11 = rings[k + 1][(i + 1) % n_radial]
            v01 = rings[k + 1][i]
            bm.faces.new((v00, v10, v11, v01))
            
    # Cap top (z = 0.100, normal up)
    top_center = bm.verts.new((0.0, 0.0, 0.100))
    bm.verts.ensure_lookup_table()
    for i in range(n_radial):
        v0 = rings[-1][i]
        v1 = rings[-1][(i + 1) % n_radial]
        bm.faces.new((top_center, v0, v1))
        
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
    
    wn = obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

clear_all()
col = get_nightstand_collection()

# Build all parts
body = build_body(col)
top = build_table_top(col)
drawer = build_panel("DrawerFront", 0.525, 0.700, col, nx=16, nz=16)
door = build_panel("DoorFront", 0.169, 0.519, col, nx=16, nz=24)

knob_d = build_knob("KnobDrawer", (0.525 + 0.700) / 2.0, col)
knob_p = build_knob("KnobDoor", (0.169 + 0.519) / 2.0, col)

leg_dist = 0.115
leg_fl = build_leg("Leg_FL", -leg_dist, -leg_dist, col)
leg_fr = build_leg("Leg_FR",  leg_dist, -leg_dist, col)
leg_bl = build_leg("Leg_BL", -leg_dist,  leg_dist, col)
leg_br = build_leg("Leg_BR",  leg_dist,  leg_dist, col)

print("--- NIGHTSTAND BUILD SUMMARY ---")
print("Total objects in scene:", len(bpy.data.objects))
print("Objects in collection:", [o.name for o in col.objects])
for obj in col.objects:
    mods = [f"{m.name} ({m.type})" for m in obj.modifiers]
    print(f"  {obj.name}: {len(obj.data.vertices)} verts, {len(obj.data.polygons)} polys, modifiers: {mods}")

# Check total bounding box
all_coords = []
for obj in col.objects:
    mw = obj.matrix_world
    for corner in obj.bound_box:
        all_coords.append(mw @ Vector(corner))

min_x = min(c.x for c in all_coords)
max_x = max(c.x for c in all_coords)
min_y = min(c.y for c in all_coords)
max_y = max(c.y for c in all_coords)
min_z = min(c.z for c in all_coords)
max_z = max(c.z for c in all_coords)

print(f"Overall Dimensions (m):")
print(f"  X: {max_x - min_x:.4f} m (span {min_x:.4f} to {max_x:.4f})")
print(f"  Y: {max_y - min_y:.4f} m (span {min_y:.4f} to {max_y:.4f})")
print(f"  Z: {max_z - min_z:.4f} m (span {min_z:.4f} to {max_z:.4f})")
