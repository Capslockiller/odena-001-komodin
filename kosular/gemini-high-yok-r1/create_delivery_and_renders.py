"""
Molly's Nightstand - Final Delivery Generator and Cycles Clay Renderer
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import os
import sys

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

def look_at(obj, target):
    direction = Vector(target) - obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()

def body_half_width(u):
    """
    Normalized height u in [0, 1] for carcass:
    Z_bot = 0.090, Z_top = 0.762 (H = 0.672)
    Bottom: w = 0.160 (32 cm width/depth)
    Top: w = 0.180 (36 cm width/depth)
    Mid bulge: w_max ~ 0.193 (38.6 cm width/depth at u ~ 0.55)
    """
    return 0.160 + 0.020 * u + 0.0225 * 4.0 * u * (1.0 - u)

def ray_intersect_rounded_rect(theta, W, D, R):
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    sx = 1.0 if cos_t >= 0 else -1.0
    sy = 1.0 if sin_t >= 0 else -1.0
    cx = max(0.0005, W - R)
    cy = max(0.0005, D - R)
    if abs(sin_t) > 1e-6:
        t_h = (sy * D) / sin_t
        x_h = t_h * cos_t
        if abs(x_h) <= cx:
            return (x_h, sy * D)
    if abs(cos_t) > 1e-6:
        t_v = (sx * W) / cos_t
        y_v = t_v * sin_t
        if abs(y_v) <= cy:
            return (sx * W, y_v)
    b = -2.0 * (sx * cx * cos_t + sy * cy * sin_t)
    c = cx*cx + cy*cy - R*R
    disc = b*b - 4.0*c
    if disc >= 0:
        t_c = (-b + math.sqrt(disc)) / 2.0
        return (t_c * cos_t, t_c * sin_t)
    return (sx * W, sy * D)

# --- 1. TABLETOP ---
def build_tabletop(col):
    mesh = bpy.data.meshes.new("Tabletop")
    obj = bpy.data.objects.new("Tabletop", mesh)
    col.objects.link(obj)
    bm = bmesh.new()

    N = 48
    thetas = [2.0 * math.pi * i / N for i in range(N)]
    W = 0.205
    D = 0.205
    R = 0.035

    profiles = []
    # Bottom chamfer (45 deg, 4mm)
    profiles.append((0.762, 0.004))
    profiles.append((0.766, 0.000))
    profiles.append((0.787, 0.000))
    # Top fillet (plump rounding, 13mm radius)
    r_fillet = 0.013
    for k in range(1, 7):
        ang = (math.pi / 2.0) * (k / 6.0)
        zk = 0.787 + r_fillet * math.sin(ang)
        ik = r_fillet * (1.0 - math.cos(ang))
        profiles.append((zk, ik))

    rings = []
    for zk, ik in profiles:
        w_k = W - ik
        d_k = D - ik
        r_k = max(0.005, R - ik)
        loop = []
        for th in thetas:
            px, py = ray_intersect_rounded_rect(th, w_k, d_k, r_k)
            v = bm.verts.new((px, py, zk))
            loop.append(v)
        rings.append(loop)

    for r in range(len(rings) - 1):
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])

    # Bottom cap
    bot_ring = rings[0]
    for frac in [0.7, 0.4, 0.1]:
        w_k = (W - 0.004) * frac
        d_k = (D - 0.004) * frac
        r_k = max(0.002, (R - 0.004) * frac)
        new_loop = []
        for th in thetas:
            px, py = ray_intersect_rounded_rect(th, w_k, d_k, r_k)
            v = bm.verts.new((px, py, 0.762))
            new_loop.append(v)
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([bot_ring[i], new_loop[i], new_loop[ni], bot_ring[ni]])
        bot_ring = new_loop
    v_bot_center = bm.verts.new((0, 0, 0.762))
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([bot_ring[i], v_bot_center, bot_ring[ni]])

    # Top cap
    top_ring = rings[-1]
    for frac in [0.7, 0.4, 0.1]:
        w_k = (W - r_fillet) * frac
        d_k = (D - r_fillet) * frac
        r_k = max(0.002, (R - r_fillet) * frac)
        new_loop = []
        for th in thetas:
            px, py = ray_intersect_rounded_rect(th, w_k, d_k, r_k)
            v = bm.verts.new((px, py, 0.800))
            new_loop.append(v)
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([top_ring[i], top_ring[ni], new_loop[ni], new_loop[i]])
        top_ring = new_loop
    v_top_center = bm.verts.new((0, 0, 0.800))
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([top_ring[i], top_ring[ni], v_top_center])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    sub = obj.modifiers.new('Subdivision', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    return obj

# --- 2. CABINET BODY ---
def build_cabinet_body(col):
    mesh = bpy.data.meshes.new("Cabinet_Body")
    obj = bpy.data.objects.new("Cabinet_Body", mesh)
    col.objects.link(obj)
    bm = bmesh.new()

    N = 48
    thetas = [2.0 * math.pi * i / N for i in range(N)]

    z_levels = [
        0.090, 0.093, 0.120, 0.169, 0.230, 0.300, 0.370,
        0.440, 0.510, 0.529, 0.537, 0.600, 0.670, 0.717,
        0.758, 0.762
    ]

    rings = []
    for zk in z_levels:
        u = (zk - 0.090) / 0.672
        w_k = body_half_width(u)
        d_k = w_k
        r_k = 0.030 * (w_k / 0.180)
        loop = []
        for th in thetas:
            px, py = ray_intersect_rounded_rect(th, w_k, d_k, r_k)
            v = bm.verts.new((px, py, zk))
            loop.append(v)
        rings.append(loop)

    for r in range(len(rings) - 1):
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([rings[r][i], rings[r][ni], rings[r+1][ni], rings[r+1][i]])

    # Bottom cap at 0.090
    bot_ring = rings[0]
    w_bot = body_half_width(0.0)
    r_bot = 0.030 * (w_bot / 0.180)
    for frac in [0.7, 0.4, 0.1]:
        new_loop = []
        for th in thetas:
            px, py = ray_intersect_rounded_rect(th, w_bot * frac, w_bot * frac, r_bot * frac)
            v = bm.verts.new((px, py, 0.090))
            new_loop.append(v)
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([bot_ring[i], new_loop[i], new_loop[ni], bot_ring[ni]])
        bot_ring = new_loop
    v_bot_center = bm.verts.new((0, 0, 0.090))
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([bot_ring[i], v_bot_center, bot_ring[ni]])

    # Top cap at 0.762
    top_ring = rings[-1]
    w_top = body_half_width(1.0)
    r_top = 0.030 * (w_top / 0.180)
    for frac in [0.7, 0.4, 0.1]:
        new_loop = []
        for th in thetas:
            px, py = ray_intersect_rounded_rect(th, w_top * frac, w_top * frac, r_top * frac)
            v = bm.verts.new((px, py, 0.762))
            new_loop.append(v)
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([top_ring[i], top_ring[ni], new_loop[ni], new_loop[i]])
        top_ring = new_loop
    v_top_center = bm.verts.new((0, 0, 0.762))
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([top_ring[i], top_ring[ni], v_top_center])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    sub = obj.modifiers.new('Subdivision', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    return obj

# --- 3. FRONT PANELS ---
def generate_panel_perimeter_2d(z_bot, z_top, margin=0.022, r_corner=0.012, inset=0.0, n_corner=6, n_horiz=8, n_vert=10):
    z_top_in = z_top - inset
    z_bot_in = z_bot + inset
    r_c = max(0.002, r_corner - inset)
    
    u_top = (z_top_in - 0.090) / 0.672
    u_bot = (z_bot_in - 0.090) / 0.672
    
    w_top = body_half_width(u_top) - margin - inset
    w_bot = body_half_width(u_bot) - margin - inset
    
    cx_top = max(0.005, w_top - r_c)
    cx_bot = max(0.005, w_bot - r_c)
    
    pts = []
    # 1. Top horizontal edge (from -cx to +cx)
    for i in range(n_horiz):
        frac = i / n_horiz
        x = -cx_top + 2.0 * cx_top * frac
        pts.append((x, z_top_in))
    # 2. Top-right corner (pi/2 to 0)
    for i in range(n_corner):
        ang = (math.pi / 2.0) - (math.pi / 2.0) * (i / n_corner)
        x = cx_top + r_c * math.cos(ang)
        z = (z_top_in - r_c) + r_c * math.sin(ang)
        pts.append((x, z))
    # 3. Right vertical edge (downward)
    z_start_r = z_top_in - r_c
    z_end_r = z_bot_in + r_c
    for i in range(n_vert):
        frac = i / n_vert
        z = z_start_r - (z_start_r - z_end_r) * frac
        u = (z - 0.090) / 0.672
        w_cur = body_half_width(u) - margin - inset
        pts.append((w_cur, z))
    # 4. Bottom-right corner (0 to -pi/2)
    for i in range(n_corner):
        ang = 0.0 - (math.pi / 2.0) * (i / n_corner)
        x = cx_bot + r_c * math.cos(ang)
        z = (z_bot_in + r_c) + r_c * math.sin(ang)
        pts.append((x, z))
    # 5. Bottom horizontal edge (+cx to -cx)
    for i in range(n_horiz):
        frac = i / n_horiz
        x = cx_bot - 2.0 * cx_bot * frac
        pts.append((x, z_bot_in))
    # 6. Bottom-left corner (-pi/2 to -pi)
    for i in range(n_corner):
        ang = -math.pi / 2.0 - (math.pi / 2.0) * (i / n_corner)
        x = -cx_bot + r_c * math.cos(ang)
        z = (z_bot_in + r_c) + r_c * math.sin(ang)
        pts.append((x, z))
    # 7. Left vertical edge (upward)
    for i in range(n_vert):
        frac = i / n_vert
        z = z_end_r + (z_start_r - z_end_r) * frac
        u = (z - 0.090) / 0.672
        w_cur = body_half_width(u) - margin - inset
        pts.append((-w_cur, z))
    # 8. Top-left corner (pi to pi/2)
    for i in range(n_corner):
        ang = math.pi - (math.pi / 2.0) * (i / n_corner)
        x = -cx_top + r_c * math.cos(ang)
        z = (z_top_in - r_c) + r_c * math.sin(ang)
        pts.append((x, z))
    return pts

def build_panel(name, z_bot, z_top, col, margin=0.022, r_corner=0.012):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()

    z_mid = (z_top + z_bot) / 2.0
    r_edge = 0.0035

    profiles = [
        (0.002, r_edge),       # back face cap rim
        (0.001, 0.0),          # back outer rim
        (-0.0045, 0.0),        # front outer rim
        (-0.0065, r_edge*0.5), # front fillet
        (-0.008, r_edge),      # front face perimeter
    ]

    rings = []
    for y_loc, inset in profiles:
        pts_2d = generate_panel_perimeter_2d(z_bot, z_top, margin=margin, r_corner=r_corner, inset=inset)
        loop = []
        for px, pz in pts_2d:
            u = max(0.0, min(1.0, (pz - 0.090) / 0.672))
            w_carcass = body_half_width(u)
            crown = 0.0015 * (1.0 - (px / (w_carcass - margin))**2) if y_loc < 0 else 0.0
            y_world = -w_carcass + y_loc - crown
            v = bm.verts.new((px, y_world, pz))
            loop.append(v)
        rings.append(loop)

    N_pts = len(rings[0])
    for r in range(len(rings) - 1):
        for i in range(N_pts):
            ni = (i + 1) % N_pts
            bm.faces.new([rings[r][i], rings[r+1][i], rings[r+1][ni], rings[r][ni]])

    # Back cap
    back_ring = rings[0]
    for frac in [0.7, 0.4]:
        new_loop = []
        for i, v_orig in enumerate(back_ring):
            pz = z_mid + (v_orig.co.z - z_mid) * frac
            px = v_orig.co.x * frac
            u = max(0.0, min(1.0, (pz - 0.090) / 0.672))
            w_carcass = body_half_width(u)
            y_world = -w_carcass + 0.002
            v = bm.verts.new((px, y_world, pz))
            new_loop.append(v)
        for i in range(N_pts):
            ni = (i + 1) % N_pts
            bm.faces.new([back_ring[i], new_loop[i], new_loop[ni], back_ring[ni]])
        back_ring = new_loop
    u_mid = (z_mid - 0.090) / 0.672
    v_back_center = bm.verts.new((0.0, -body_half_width(u_mid) + 0.002, z_mid))
    for i in range(N_pts):
        ni = (i + 1) % N_pts
        bm.faces.new([back_ring[i], v_back_center, back_ring[ni]])

    # Front cap
    front_ring = rings[-1]
    for frac in [0.7, 0.4]:
        new_loop = []
        for i, v_orig in enumerate(front_ring):
            pz = z_mid + (v_orig.co.z - z_mid) * frac
            px = v_orig.co.x * frac
            u = max(0.0, min(1.0, (pz - 0.090) / 0.672))
            w_carcass = body_half_width(u)
            crown = 0.0015 * (1.0 - (px / (w_carcass - margin))**2)
            y_world = -w_carcass - 0.008 - crown
            v = bm.verts.new((px, y_world, pz))
            new_loop.append(v)
        for i in range(N_pts):
            ni = (i + 1) % N_pts
            bm.faces.new([front_ring[i], front_ring[ni], new_loop[ni], new_loop[i]])
        front_ring = new_loop
    v_front_center = bm.verts.new((0.0, -body_half_width(u_mid) - 0.0095, z_mid))
    for i in range(N_pts):
        ni = (i + 1) % N_pts
        bm.faces.new([front_ring[i], front_ring[ni], v_front_center])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    sub = obj.modifiers.new('Subdivision', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    return obj

# --- 4. KNOBS ---
def build_knob(name, loc, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()

    profile = [
        (0.000, 0.0065),  # base collar
        (-0.002, 0.0050), # stem start
        (-0.010, 0.0050), # stem end
        (-0.012, 0.0070), # flare into head
        (-0.014, 0.0120), # back of head
        (-0.017, 0.0165), # widest head rim (diameter 33mm)
        (-0.020, 0.0160), # dome start
        (-0.023, 0.0130), # dome mid
        (-0.025, 0.0080), # dome front
        (-0.026, 0.0000), # front tip
    ]
    N = 24
    rings = []
    for y_val, r_val in profile[:-1]:
        ring = []
        for i in range(N):
            th = 2.0 * math.pi * i / N
            x = r_val * math.cos(th)
            z = r_val * math.sin(th)
            v = bm.verts.new((x, y_val, z))
            ring.append(v)
        rings.append(ring)
    v_tip = bm.verts.new((0.0, profile[-1][0], 0.0))
    for r in range(len(rings) - 1):
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([rings[r][i], rings[r+1][i], rings[r+1][ni], rings[r][ni]])
    last_ring = rings[-1]
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([last_ring[i], v_tip, last_ring[ni]])
    v_base = bm.verts.new((0.0, 0.0, 0.0))
    first_ring = rings[0]
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([first_ring[i], first_ring[ni], v_base])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    sub = obj.modifiers.new('Subdivision', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    obj.location = loc
    return obj

# --- 5. LEGS ---
def build_leg(name, loc, col):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    bm = bmesh.new()

    r_fillet = 0.0035
    r_bot = 0.020
    r_top = 0.028
    H = 0.090

    profile = []
    for k in range(5):
        ang = (math.pi / 2.0) * (k / 4.0)
        zk = r_fillet * (1.0 - math.cos(ang))
        rk = (r_bot - r_fillet) + r_fillet * math.sin(ang)
        profile.append((zk, rk))

    for frac in [0.25, 0.5, 0.75, 0.95, 1.0]:
        zk = frac * H
        rk = r_bot + (r_top - r_bot) * frac
        profile.append((zk, rk))

    N = 24
    rings = []
    for zk, rk in profile:
        ring = []
        for i in range(N):
            th = 2.0 * math.pi * i / N
            x = rk * math.cos(th)
            y = rk * math.sin(th)
            v = bm.verts.new((x, y, zk))
            ring.append(v)
        rings.append(ring)

    for r in range(len(rings) - 1):
        for i in range(N):
            ni = (i + 1) % N
            bm.faces.new([rings[r][i], rings[r+1][i], rings[r+1][ni], rings[r][ni]])

    v_bot = bm.verts.new((0.0, 0.0, 0.0))
    first_ring = rings[0]
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([first_ring[i], v_bot, first_ring[ni]])

    # Top cap with holding ring to keep it flat
    top_ring = rings[-1]
    new_loop = []
    for i in range(N):
        th = 2.0 * math.pi * i / N
        v = bm.verts.new((0.5 * r_top * math.cos(th), 0.5 * r_top * math.sin(th), H))
        new_loop.append(v)
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([top_ring[i], top_ring[ni], new_loop[ni], new_loop[i]])
    v_top = bm.verts.new((0.0, 0.0, H))
    for i in range(N):
        ni = (i + 1) % N
        bm.faces.new([new_loop[i], new_loop[ni], v_top])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    sub = obj.modifiers.new('Subdivision', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    obj.location = loc
    return obj

def assemble_model():
    clear_scene()
    col = bpy.data.collections.new("Molly's Nightstand")
    bpy.context.scene.collection.children.link(col)

    # 1. Tabletop
    tabletop = build_tabletop(col)

    # 2. Cabinet Body
    body = build_cabinet_body(col)

    # 3. Front Panels
    drawer = build_panel("Drawer_Front", 0.537, 0.717, col, margin=0.022, r_corner=0.012)
    door = build_panel("Door_Front", 0.169, 0.529, col, margin=0.022, r_corner=0.012)

    # 4. Knobs
    u_draw = (0.627 - 0.090) / 0.672
    w_draw = body_half_width(u_draw)
    y_knob_draw = -w_draw - 0.0095
    drawer_knob = build_knob("Drawer_Knob", (0.0, y_knob_draw, 0.627), col)

    u_door = (0.349 - 0.090) / 0.672
    w_door = body_half_width(u_door)
    y_knob_door = -w_door - 0.0095
    door_knob = build_knob("Door_Knob", (0.0, y_knob_door, 0.349), col)

    # 5. Legs
    leg_offset = 0.106
    legs = [
        build_leg("Leg_Front_Left", (-leg_offset, -leg_offset, 0.0), col),
        build_leg("Leg_Front_Right", (leg_offset, -leg_offset, 0.0), col),
        build_leg("Leg_Back_Left", (-leg_offset, leg_offset, 0.0), col),
        build_leg("Leg_Back_Right", (leg_offset, leg_offset, 0.0), col),
    ]

    # Verify no materials exist
    for obj in col.objects:
        obj.data.materials.clear()

    return col

def save_deliverable_blend(filepath):
    # Save the blend file with only the model and collection
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"Saved deliverable blend file to: {filepath}")

def setup_studio_and_render(output_dir):
    # Setup Cycles CPU renderer
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.cycles.use_adaptive_sampling = True
    bpy.context.scene.cycles.adaptive_threshold = 0.02

    # World: clean neutral studio ambient
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("StudioWorld")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.92, 0.92, 0.94, 1.0)
        bg_node.inputs["Strength"].default_value = 0.7

    # Studio Collection outside Molly's Nightstand
    studio_col = bpy.data.collections.new("Studio_Environment")
    bpy.context.scene.collection.children.link(studio_col)

    # Key light: soft area light
    key_data = bpy.data.lights.new("KeyLight", 'AREA')
    key_data.energy = 80.0
    key_data.size = 1.2
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    studio_col.objects.link(key_obj)
    key_obj.location = (1.4, -1.8, 1.8)
    look_at(key_obj, (0.0, -0.05, 0.40))

    # Fill light: soft cooler area light
    fill_data = bpy.data.lights.new("FillLight", 'AREA')
    fill_data.energy = 35.0
    fill_data.size = 1.5
    fill_data.color = (0.92, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    studio_col.objects.link(fill_obj)
    fill_obj.location = (-1.8, -1.2, 1.4)
    look_at(fill_obj, (0.0, -0.05, 0.40))

    # Rim light: crisp top/back rim
    rim_data = bpy.data.lights.new("RimLight", 'AREA')
    rim_data.energy = 60.0
    rim_data.size = 1.0
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    studio_col.objects.link(rim_obj)
    rim_obj.location = (0.8, 1.8, 2.0)
    look_at(rim_obj, (0.0, 0.0, 0.40))

    # Shadow catcher floor
    mesh_floor = bpy.data.meshes.new("FloorMesh")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=5.0)
    bm.to_mesh(mesh_floor)
    bm.free()
    floor_obj = bpy.data.objects.new("ShadowFloor", mesh_floor)
    studio_col.objects.link(floor_obj)
    floor_obj.location = (0.0, 0.0, 0.0)
    floor_obj.is_shadow_catcher = True

    # Camera
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    studio_col.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    def render_shot(loc, target, filename, res=(1200, 900), lens=60.0):
        cam_obj.location = loc
        cam_data.lens = lens
        look_at(cam_obj, target)
        path = os.path.join(output_dir, filename)
        bpy.context.scene.render.filepath = os.path.abspath(path)
        bpy.context.scene.render.resolution_x = res[0]
        bpy.context.scene.render.resolution_y = res[1]
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {path}")

    # 1. Perspective 3/4
    render_shot((1.1, -1.6, 1.15), (0.0, -0.05, 0.42), "render_perspective.png", (1200, 900), lens=60.0)

    # 2. Front elevation
    render_shot((0.0, -2.1, 0.42), (0.0, -0.05, 0.42), "render_front.png", (1000, 1000), lens=75.0)

    # 3. Side profile
    render_shot((2.1, 0.0, 0.42), (0.0, 0.0, 0.42), "render_side.png", (1000, 1000), lens=75.0)

    # 4. Top view
    render_shot((0.0, -0.01, 2.0), (0.0, 0.0, 0.40), "render_top.png", (1000, 1000), lens=65.0)

    # 5. Detail: Panels closeup
    render_shot((0.45, -0.9, 0.55), (0.0, -0.19, 0.48), "render_detail_panels.png", (1200, 900), lens=70.0)

    # 6. Detail: Tabletop closeup
    render_shot((0.45, -0.65, 0.90), (0.16, -0.16, 0.78), "render_detail_tabletop.png", (1200, 900), lens=85.0)

    # 7. Detail: Legs closeup
    render_shot((0.55, -0.85, 0.20), (0.0, -0.10, 0.07), "render_detail_legs.png", (1200, 900), lens=75.0)

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    blend_path = os.path.join(folder, "sonuc.blend")

    # Step 1: Assemble clean model
    col = assemble_model()

    # Step 2: Save sonuc.blend (clean, without lights/cameras)
    save_deliverable_blend(blend_path)

    # Step 3: Setup studio and render previews
    setup_studio_and_render(folder)
    print("All tasks completed successfully!")

if __name__ == "__main__":
    main()
