import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import os

def clear_all():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def ensure_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def body_width_at(z):
    """
    Smooth width profile along Z:
    z from 0.080 to 0.758 (height 0.678m).
    u in [0, 1].
    Bottom (u=0): 0.325m (distinct taper downwards).
    Middle (u=0.494): 0.405m (swollen in the middle).
    Top (u=1.0): 0.380m (meets tabletop gracefully with gentle slope).
    """
    u = (z - 0.080) / 0.678
    u = max(0.0, min(1.0, u))
    w = 0.325 + 0.380 * u - 0.555 * (u ** 2) + 0.230 * (u ** 3)
    return w

def make_filleted_rectangle_ring(hx, hy, r_corner, z, n_corner=6, n_edge=4, barrel=0.003, front_indent=0.0):
    r_c = min(r_corner, hx * 0.45, hy * 0.45)
    cx = hx - r_c
    cy = hy - r_c
    
    verts = []
    
    # 1. Front edge (-Y face): from (+cx, -hy) to (-cx, -hy)
    for i in range(n_edge):
        t = i / float(n_edge)
        x = cx * (1.0 - 2.0 * t)
        y = -hy - barrel * math.sin(math.pi * t) + front_indent
        verts.append(Vector((x, y, z)))
        
    # Front-Left corner: center (-cx, -cy), angle from 3pi/2 to pi
    for i in range(n_corner):
        ang = math.pi * 1.5 - (math.pi * 0.5) * (i / float(n_corner))
        x = -cx + r_c * math.cos(ang)
        y = -cy + r_c * math.sin(ang)
        verts.append(Vector((x, y, z)))
        
    # Left edge (-X face): from (-hx, -cy) to (-hx, +cy)
    for i in range(n_edge):
        t = i / float(n_edge)
        y = -cy + 2.0 * cy * t
        x = -hx - barrel * math.sin(math.pi * t)
        verts.append(Vector((x, y, z)))
        
    # Back-Left corner: center (-cx, +cy), angle from pi to pi/2
    for i in range(n_corner):
        ang = math.pi - (math.pi * 0.5) * (i / float(n_corner))
        x = -cx + r_c * math.cos(ang)
        y = cy + r_c * math.sin(ang)
        verts.append(Vector((x, y, z)))
        
    # Back edge (+Y face): from (-cx, +hy) to (+cx, +hy)
    for i in range(n_edge):
        t = i / float(n_edge)
        x = -cx + 2.0 * cx * t
        y = hy + barrel * math.sin(math.pi * t)
        verts.append(Vector((x, y, z)))
        
    # Back-Right corner: center (+cx, +cy), angle from pi/2 to 0
    for i in range(n_corner):
        ang = math.pi * 0.5 - (math.pi * 0.5) * (i / float(n_corner))
        x = cx + r_c * math.cos(ang)
        y = cy + r_c * math.sin(ang)
        verts.append(Vector((x, y, z)))
        
    # Right edge (+X face): from (+hx, +cy) to (+hx, -cy)
    for i in range(n_edge):
        t = i / float(n_edge)
        y = cy * (1.0 - 2.0 * t)
        x = hx + barrel * math.sin(math.pi * t)
        verts.append(Vector((x, y, z)))
        
    # Front-Right corner: center (+cx, -cy), angle from 0 to -pi/2
    for i in range(n_corner):
        ang = 0.0 - (math.pi * 0.5) * (i / float(n_corner))
        x = cx + r_c * math.cos(ang)
        y = -cy + r_c * math.sin(ang)
        verts.append(Vector((x, y, z)))
        
    return verts

def bridge_rings(bm, ring1_bmverts, ring2_bmverts):
    n = len(ring1_bmverts)
    faces = []
    for i in range(n):
        i_next = (i + 1) % n
        v1 = ring1_bmverts[i]
        v2 = ring1_bmverts[i_next]
        v3 = ring2_bmverts[i_next]
        v4 = ring2_bmverts[i]
        f = bm.faces.new([v1, v2, v3, v4])
        faces.append(f)
    return faces

def cap_ring_quads(bm, ring_bmverts, center_z, is_top=True):
    n = len(ring_bmverts)
    current_ring = ring_bmverts
    for step in [0.70, 0.40]:
        new_ring = []
        for v in current_ring:
            pos = v.co
            new_co = Vector((pos.x * step, pos.y * step, pos.z))
            new_v = bm.verts.new(new_co)
            new_ring.append(new_v)
        if is_top:
            bridge_rings(bm, current_ring, new_ring)
        else:
            bridge_rings(bm, new_ring, current_ring)
        current_ring = new_ring
    
    center_v = bm.verts.new(Vector((0.0, 0.0, center_z)))
    for i in range(n):
        i_next = (i + 1) % n
        if is_top:
            bm.faces.new([current_ring[i], current_ring[i_next], center_v])
        else:
            bm.faces.new([current_ring[i_next], current_ring[i], center_v])

def create_tabletop(col):
    mesh = bpy.data.meshes.new("Tabletop")
    obj = bpy.data.objects.new("Tabletop", mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    
    hx = 0.435 / 2.0
    hy = 0.435 / 2.0
    r_corner = 0.038
    
    ring_defs = [
        (hx - 0.0055, hy - 0.0055, 0.7580), # 0: bottom chamfer inner
        (hx - 0.0005, hy - 0.0005, 0.7630), # 1: bottom chamfer outer support
        (hx,          hy,          0.7650), # 2: bottom of rim
        (hx,          hy,          0.7810), # 3: top of rim / start of round bullnose
        (hx - 0.0030, hy - 0.0030, 0.7890), # 4: bullnose arc 1
        (hx - 0.0080, hy - 0.0080, 0.7950), # 5: bullnose arc 2
        (hx - 0.0145, hy - 0.0145, 0.7988), # 6: bullnose arc 3
        (hx - 0.0200, hy - 0.0200, 0.8000), # 7: bullnose top tangent
        (hx - 0.0240, hy - 0.0240, 0.8000), # 8: flat top inner support loop
    ]
    
    bm_rings = []
    for cur_hx, cur_hy, cur_z in ring_defs:
        pts = make_filleted_rectangle_ring(cur_hx, cur_hy, r_corner * (cur_hx / hx), cur_z, n_corner=6, n_edge=4, barrel=0.002)
        bm_ring = [bm.verts.new(p) for p in pts]
        bm_rings.append(bm_ring)
        
    for i in range(len(bm_rings) - 1):
        bridge_rings(bm, bm_rings[i], bm_rings[i+1])
        
    cap_ring_quads(bm, bm_rings[0], 0.7580, is_top=False)
    cap_ring_quads(bm, bm_rings[-1], 0.8000, is_top=True)
    
    bm.to_mesh(mesh)
    bm.free()
    
    sub = obj.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    return obj

def create_body(col, z_gap_low=0.520, z_gap_high=0.528):
    mesh = bpy.data.meshes.new("Body")
    obj = bpy.data.objects.new("Body", mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    
    z_min = 0.080
    z_max = 0.758
    
    z_ring_specs = [
        (0.0800, 0.0), # Bottom base edge
        (0.0830, 0.0), # Bottom base support loop
        (0.0950, 0.0),
        (0.1200, 0.0),
        (0.1800, 0.0),
        (0.2600, 0.0),
        (0.3500, 0.0),
        (0.4400, 0.0),
        (0.5050, 0.0),
        (0.5180, 0.0),
        (0.5200, 0.008), # Shadow groove bottom
        (0.5240, 0.010), # Shadow groove center
        (0.5280, 0.008), # Shadow groove top
        (0.5300, 0.0),
        (0.5800, 0.0),
        (0.6400, 0.0),
        (0.7000, 0.0),
        (0.7450, 0.0),
        (0.7550, 0.0), # Top rim support loop
        (0.7580, 0.0), # Top rim meeting tabletop
    ]
    
    bm_rings = []
    for cur_z, f_indent in z_ring_specs:
        w = body_width_at(cur_z)
        hx = w / 2.0
        hy = w / 2.0
        r_c = 0.16 * w
        pts = make_filleted_rectangle_ring(hx, hy, r_c, cur_z, n_corner=6, n_edge=4, barrel=0.003, front_indent=f_indent)
        bm_ring = [bm.verts.new(p) for p in pts]
        bm_rings.append(bm_ring)
        
    for i in range(len(bm_rings) - 1):
        bridge_rings(bm, bm_rings[i], bm_rings[i+1])
        
    cap_ring_quads(bm, bm_rings[0], z_min, is_top=False)
    cap_ring_quads(bm, bm_rings[-1], z_max, is_top=True)
    
    bm.to_mesh(mesh)
    bm.free()
    
    sub = obj.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    return obj

def create_panel_beveled(name, col, z_low, z_high, margin_x=0.024, thickness=0.015, protrusion=0.011, bevel_width=0.007):
    """
    Creates a clean quad block conforming to the body surface,
    with a multi-segment Bevel modifier (MITER_ARC) and Subdivision Surface
    for smooth, unpinched rounded edges.
    """
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    
    nz = 8
    nx = 10
    
    back_grid = []
    front_grid = []
    
    for iz in range(nz + 1):
        tz = iz / float(nz)
        z = z_low + tz * (z_high - z_low)
        w = body_width_at(z)
        panel_w = w - 2.0 * margin_x
        half_w = panel_w / 2.0
        y_body_center = -w / 2.0
        
        row_b = []
        row_f = []
        for ix in range(nx + 1):
            tx = (ix / float(nx)) * 2.0 - 1.0
            x = tx * half_w
            y_curve = y_body_center - 0.003 * math.cos(tx * math.pi * 0.5)
            
            # Back face embedded 3mm into cabinet face
            vb = bm.verts.new(Vector((x, y_curve + 0.003, z)))
            # Front face projecting forward by protrusion
            vf = bm.verts.new(Vector((x, y_curve - protrusion, z)))
            row_b.append(vb)
            row_f.append(vf)
        back_grid.append(row_b)
        front_grid.append(row_f)
        
    # Back faces (facing +Y)
    for iz in range(nz):
        for ix in range(nx):
            bm.faces.new([back_grid[iz][ix], back_grid[iz][ix+1], back_grid[iz+1][ix+1], back_grid[iz+1][ix]])
            
    # Front faces (facing -Y)
    for iz in range(nz):
        for ix in range(nx):
            bm.faces.new([front_grid[iz][ix], front_grid[iz+1][ix], front_grid[iz+1][ix+1], front_grid[iz][ix+1]])
            
    # Left edge
    for iz in range(nz):
        bm.faces.new([back_grid[iz][0], back_grid[iz+1][0], front_grid[iz+1][0], front_grid[iz][0]])
        
    # Right edge
    for iz in range(nz):
        bm.faces.new([back_grid[iz][nx], front_grid[iz][nx], front_grid[iz+1][nx], back_grid[iz+1][nx]])
        
    # Bottom edge
    for ix in range(nx):
        bm.faces.new([back_grid[0][ix], front_grid[0][ix], front_grid[0][ix+1], back_grid[0][ix+1]])
        
    # Top edge
    for ix in range(nx):
        bm.faces.new([back_grid[nz][ix], back_grid[nz][ix+1], front_grid[nz][ix+1], front_grid[nz][ix]])
        
    bm.to_mesh(mesh)
    bm.free()
    
    # Bevel Modifier for soft rounded edges
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = bevel_width
    bev.segments = 4
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(40)
    bev.miter_outer = 'MITER_ARC'
    
    # Subsurf Modifier
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    return obj

def create_knob(name, col, center_z, panel_y_front):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    
    # Knob revolved along Y axis, projecting towards -Y (front)
    # "küçük yuvarlak, basık topuz kulp (kısa bir mil üzerinde)"
    # Diameter = 40mm (r = 0.020m)
    profile = [
        (0.000, 0.0085), # Base flare against panel
        (0.002, 0.0055), # Base collar
        (0.008, 0.0055), # Stem / mil
        (0.012, 0.0075), # Stem neck flare
        (0.015, 0.0145), # Back curve of knob head
        (0.018, 0.0200), # Maximum radius (40mm diameter)
        (0.022, 0.0202), # Crest of flattened knob
        (0.027, 0.0175), # Front curvature
        (0.030, 0.0115), # Front dome
        (0.032, 0.0040), # Tip near-center
        (0.0325, 0.0000) # Tip center
    ]
    
    n_seg = 24
    bm_rings = []
    
    for dy, r in profile[:-1]:
        ring = []
        y = panel_y_front - dy
        for iseg in range(n_seg):
            ang = (iseg / float(n_seg)) * 2.0 * math.pi
            x = r * math.cos(ang)
            z = center_z + r * math.sin(ang)
            ring.append(bm.verts.new(Vector((x, y, z))))
        bm_rings.append(ring)
        
    for i in range(len(bm_rings) - 1):
        bridge_rings(bm, bm_rings[i+1], bm_rings[i])
        
    tip_y = panel_y_front - profile[-1][0]
    tip_v = bm.verts.new(Vector((0.0, tip_y, center_z)))
    for iseg in range(n_seg):
        i_next = (iseg + 1) % n_seg
        bm.faces.new([bm_rings[-1][i_next], bm_rings[-1][iseg], tip_v])
        
    base_v = bm.verts.new(Vector((0.0, panel_y_front, center_z)))
    for iseg in range(n_seg):
        i_next = (iseg + 1) % n_seg
        bm.faces.new([bm_rings[0][iseg], bm_rings[0][i_next], base_v])
        
    bm.to_mesh(mesh)
    bm.free()
    
    sub = obj.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    return obj

def create_legs(col):
    mesh = bpy.data.meshes.new("Legs")
    obj = bpy.data.objects.new("Legs", mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    
    # "Altta dört kısa, kalın, aşağı doğru hafif daralan ayak; köşelere yakın."
    leg_cx = 0.106
    leg_cy = 0.106
    
    leg_profile = [
        (0.000, 0.0000), # Bottom point
        (0.002, 0.0100), # Rounded bottom edge
        (0.006, 0.0200), # Rounded foot flare
        (0.012, 0.0238), # Bottom of tapered cylinder
        (0.040, 0.0275), # Mid-height taper
        (0.070, 0.0315), # Upper taper
        (0.078, 0.0330), # Support loop below cabinet plate
        (0.080, 0.0330), # Top rim flush against cabinet underside
    ]
    
    n_seg = 20
    bm_rings = []
    
    for z, r in leg_profile[1:]:
        ring = []
        for iseg in range(n_seg):
            ang = (iseg / float(n_seg)) * 2.0 * math.pi
            x = leg_cx + r * math.cos(ang)
            y = leg_cy + r * math.sin(ang)
            ring.append(bm.verts.new(Vector((x, y, z))))
        bm_rings.append(ring)
        
    tip_v = bm.verts.new(Vector((leg_cx, leg_cy, 0.000)))
    for iseg in range(n_seg):
        i_next = (iseg + 1) % n_seg
        bm.faces.new([bm_rings[0][i_next], bm_rings[0][iseg], tip_v])
        
    for i in range(len(bm_rings) - 1):
        bridge_rings(bm, bm_rings[i], bm_rings[i+1])
        
    top_v = bm.verts.new(Vector((leg_cx, leg_cy, 0.080)))
    for iseg in range(n_seg):
        i_next = (iseg + 1) % n_seg
        bm.faces.new([bm_rings[-1][i_next], bm_rings[-1][iseg], top_v])
        
    bm.to_mesh(mesh)
    bm.free()
    
    mir = obj.modifiers.new("Mirror", "MIRROR")
    mir.use_axis[0] = True # X
    mir.use_axis[1] = True # Y
    mir.use_axis[2] = False
    
    sub = obj.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 2
    
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    return obj

def build_scene():
    clear_all()
    col = ensure_collection("Molly's Nightstand")
    
    tabletop = create_tabletop(col)
    
    z_gap_low = 0.520
    z_gap_high = 0.528
    
    body = create_body(col, z_gap_low, z_gap_high)
    
    # Heights for drawer and door:
    # Drawer: z from 0.528 to 0.734 (h = 0.206)
    # Door: z from 0.106 to 0.520 (h = 0.414)
    # Door height is exactly 2.01x drawer height (~twice as high)
    z_drawer_low = z_gap_high
    z_drawer_high = 0.734
    z_door_low = 0.106
    z_door_high = z_gap_low
    
    drawer = create_panel_beveled("Drawer_Front", col, z_drawer_low, z_drawer_high, margin_x=0.024, thickness=0.015, protrusion=0.011, bevel_width=0.007)
    door = create_panel_beveled("Door_Front", col, z_door_low, z_door_high, margin_x=0.024, thickness=0.015, protrusion=0.011, bevel_width=0.007)
    
    # Knobs:
    z_drawer_mid = (z_drawer_low + z_drawer_high) / 2.0
    w_drawer_mid = body_width_at(z_drawer_mid)
    y_drawer_front = -(w_drawer_mid / 2.0) - 0.003 - 0.011
    drawer_knob = create_knob("Drawer_Knob", col, z_drawer_mid, y_drawer_front)
    
    z_door_mid = (z_door_low + z_door_high) / 2.0
    w_door_mid = body_width_at(z_door_mid)
    y_door_front = -(w_door_mid / 2.0) - 0.003 - 0.011
    door_knob = create_knob("Door_Knob", col, z_door_mid, y_door_front)
    
    legs = create_legs(col)
    
    return {
        "Tabletop": tabletop,
        "Body": body,
        "Drawer_Front": drawer,
        "Door_Front": door,
        "Drawer_Knob": drawer_knob,
        "Door_Knob": door_knob,
        "Legs": legs
    }

def setup_lighting_and_camera():
    for obj in list(bpy.data.objects):
        if obj.type in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
            
    key_light_data = bpy.data.lights.new(name="Key_Light", type='AREA')
    key_light_data.energy = 240.0
    key_light_data.size = 1.2
    key_light_obj = bpy.data.objects.new(name="Key_Light", object_data=key_light_data)
    bpy.context.scene.collection.objects.link(key_light_obj)
    key_light_obj.location = Vector((1.2, -1.6, 1.6))
    direction = Vector((0.0, 0.0, 0.42)) - key_light_obj.location
    key_light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    fill_light_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill_light_data.energy = 95.0
    fill_light_data.size = 1.5
    fill_light_obj = bpy.data.objects.new(name="Fill_Light", object_data=fill_light_data)
    bpy.context.scene.collection.objects.link(fill_light_obj)
    fill_light_obj.location = Vector((-1.4, -1.3, 0.9))
    direction = Vector((0.0, 0.0, 0.42)) - fill_light_obj.location
    fill_light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    rim_light_data = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim_light_data.energy = 170.0
    rim_light_data.size = 1.0
    rim_light_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_light_data)
    bpy.context.scene.collection.objects.link(rim_light_obj)
    rim_light_obj.location = Vector((-0.8, 1.4, 1.4))
    direction = Vector((0.0, 0.0, 0.42)) - rim_light_obj.location
    rim_light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    cam_data = bpy.data.cameras.new(name="Camera")
    cam_data.lens = 52.0
    cam_obj = bpy.data.objects.new(name="Camera", object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.07, 0.07, 0.08, 1.0)
        bg.inputs["Strength"].default_value = 0.5
        
    return cam_obj

def render_view(cam_obj, loc, target, filepath):
    cam_obj.location = Vector(loc)
    direction = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.abspath(filepath)
    print(f"Rendering {filepath}...")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered {filepath}.")

if __name__ == "__main__":
    parts = build_scene()
    cam_obj = setup_lighting_and_camera()
    
    # 1. Perspective 3/4 view
    render_view(cam_obj, (1.15, -1.35, 0.95), (0.0, 0.0, 0.42), "preview_perspective.png")
    
    # 2. Front view
    render_view(cam_obj, (0.0, -1.65, 0.42), (0.0, 0.0, 0.42), "preview_front.png")
    
    # 3. Side view
    render_view(cam_obj, (1.65, 0.0, 0.42), (0.0, 0.0, 0.42), "preview_side.png")
    
    # 4. Detail close-up
    render_view(cam_obj, (0.45, -0.75, 0.70), (0.0, -0.15, 0.62), "preview_closeup.png")
    
    # Remove camera and lights for clean geometry-only deliverable
    for obj in list(bpy.data.objects):
        if obj.type in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)
    
    # Save blend file
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("sonuc.blend"))
    print("Saved sonuc.blend successfully.")

