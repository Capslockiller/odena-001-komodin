"""Molly's Nightstand (Toy Story) -- headless Blender builder.

Run:
  blender.exe -b --factory-startup --python yap.py
Produces sonuc.blend next to this script and preview renders in onizleme/.
"""
import math
import os
import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
COLL_NAME = "Molly's Nightstand"

# ------------------------------------------------------------------ dimensions (m)
LEG_H = 0.09          # floor -> body underside
BODY_Z0 = LEG_H
BODY_Z1 = 0.745       # body top (hidden under slab)
TOP_T = 0.055         # slab thickness
TOP_Z1 = BODY_Z1 + TOP_T   # 0.80 overall

W_BOT, W_MAX, W_TOP = 0.325, 0.40, 0.385   # body width: bottom / belly / top
T_PEAK = 0.62                               # where the belly sits (0..1 of body height)
BODY_R = 0.042                              # vertical corner radius of the body

TOP_HW = 0.22                               # slab half width (0.44 overall)
TOP_R = 0.055                               # slab plan corner radius

PANEL_W = 0.26
PANEL_R = 0.022                             # panel corner radius (plan view of front)
PANEL_OUT = 0.008                           # how far panels stand proud of the body
PANEL_IN = 0.012                            # how far they sink into the body
PANEL_MARGIN_TOP = 0.03
PANEL_MARGIN_BOT = 0.035
PANEL_GAP = 0.012

LEG_R_TOP, LEG_R_BOT = 0.032, 0.023
LEG_OFF = 0.115                             # leg centre offset from axis


def body_w(z):
    """Body width as a function of height: belly in the upper-middle, clear taper downward."""
    t = (z - BODY_Z0) / (BODY_Z1 - BODY_Z0)
    t = min(max(t, 0.0), 1.0)
    if t < T_PEAK:
        a = (W_MAX - W_BOT) / T_PEAK ** 2
        return W_MAX - a * (t - T_PEAK) ** 2
    a = (W_MAX - W_TOP) / (1.0 - T_PEAK) ** 2
    return W_MAX - a * (t - T_PEAK) ** 2


def front_y(z):
    return -body_w(z) / 2.0


# ------------------------------------------------------------------ helpers
def rounded_rect(hw, hh, r, segs):
    """CCW outline of a rounded rectangle in a 2D plane, returned as (u, v) pairs."""
    pts = []
    cx, cy = hw - r, hh - r
    corners = [(cx, cy, 0.0), (-cx, cy, 90.0), (-cx, -cy, 180.0), (cx, -cy, 270.0)]
    for ox, oy, a0 in corners:
        for i in range(segs + 1):
            a = math.radians(a0 + 90.0 * i / segs)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def new_object(name, bm, coll):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def add_bevel(ob, name, width, segments, limit='ANGLE', vgroup=None, profile=0.5, angle=30.0):
    m = ob.modifiers.new(name, 'BEVEL')
    m.width = width
    m.segments = segments
    m.profile = profile
    m.limit_method = limit
    if limit == 'VGROUP':
        m.vertex_group = vgroup
    elif limit == 'ANGLE':
        m.angle_limit = math.radians(angle)
    m.harden_normals = True
    m.miter_outer = 'MITER_ARC'
    return m


def vgroup_from_indices(ob, name, indices):
    vg = ob.vertex_groups.new(name=name)
    vg.add(list(indices), 1.0, 'REPLACE')
    return vg


# ------------------------------------------------------------------ parts
def build_body(coll):
    """Lofted rounded-square rings: belly in the middle, tapering downward."""
    n_rings = 26
    segs = 8
    bm = bmesh.new()
    rings = []
    for i in range(n_rings):
        z = BODY_Z0 + (BODY_Z1 - BODY_Z0) * i / (n_rings - 1)
        hw = body_w(z) / 2.0
        ring = [bm.verts.new((u, v, z)) for u, v in rounded_rect(hw, hw, BODY_R, segs)]
        rings.append(ring)
    n = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.faces.new(list(reversed(rings[0])))   # bottom cap
    bm.faces.new(rings[-1])                  # top cap (under the slab)
    bm.verts.index_update()
    bot_idx = [v.index for v in rings[0]]
    ob = new_object("Body", bm, coll)
    vgroup_from_indices(ob, "bot", bot_idx)
    add_bevel(ob, "Bevel Bottom", 0.012, 3, limit='VGROUP', vgroup="bot")
    return ob


def build_top(coll):
    """Thick slab, rounded plan corners, fat round top edge, light chamfer underneath."""
    segs = 10
    bm = bmesh.new()
    out = rounded_rect(TOP_HW, TOP_HW, TOP_R, segs)
    bot = [bm.verts.new((u, v, BODY_Z1)) for u, v in out]
    top = [bm.verts.new((u, v, TOP_Z1)) for u, v in out]
    n = len(out)
    for k in range(n):
        bm.faces.new((bot[k], bot[(k + 1) % n], top[(k + 1) % n], top[k]))
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    bm.verts.index_update()
    top_idx = [v.index for v in top]
    bot_idx = [v.index for v in bot]
    ob = new_object("Top", bm, coll)
    vgroup_from_indices(ob, "top", top_idx)
    vgroup_from_indices(ob, "bot", bot_idx)
    add_bevel(ob, "Bevel Top Round", 0.024, 8, limit='VGROUP', vgroup="top")
    add_bevel(ob, "Chamfer Bottom", 0.005, 1, limit='VGROUP', vgroup="bot")
    return ob


def build_panel(coll, name, z0, z1):
    """Front panel: all-quad row grid whose outer columns trace the rounded corners,
    then sheared in Y so the whole panel rides on the body's belly."""
    hw, r = PANEL_W / 2.0, PANEL_R
    cx = hw - r
    arc = 6
    rows = []                                   # (z, half width)
    for i in range(arc + 1):                    # bottom corner arc
        a = math.radians(90.0 * i / arc)
        rows.append((z0 + r * (1.0 - math.cos(a)), cx + r * math.sin(a)))
    n_mid = max(2, int(round((z1 - z0 - 2 * r) / 0.014)))
    for i in range(1, n_mid):                   # straight part
        rows.append((z0 + r + (z1 - z0 - 2 * r) * i / n_mid, hw))
    for i in range(arc, -1, -1):                # top corner arc
        a = math.radians(90.0 * i / arc)
        rows.append((z1 - r * (1.0 - math.cos(a)), cx + r * math.sin(a)))

    bm = bmesh.new()
    F, B = [], []                               # per row: (left, right) verts
    for z, xh in rows:
        F.append((bm.verts.new((-xh, -PANEL_OUT, z)), bm.verts.new((xh, -PANEL_OUT, z))))
        B.append((bm.verts.new((-xh, PANEL_IN, z)), bm.verts.new((xh, PANEL_IN, z))))
    for (fl0, fr0), (fl1, fr1), (bl0, br0), (bl1, br1) in zip(F[:-1], F[1:], B[:-1], B[1:]):
        bm.faces.new((fl0, fr0, fr1, fl1))      # front strip
        bm.faces.new((br0, bl0, bl1, br1))      # back strip
        bm.faces.new((fr0, br0, br1, fr1))      # right band
        bm.faces.new((bl0, fl0, fl1, bl1))      # left band
    bm.faces.new((B[0][0], B[0][1], F[0][1], F[0][0]))        # bottom
    bm.faces.new((F[-1][0], F[-1][1], B[-1][1], B[-1][0]))    # top
    # shear: every vertex rides on the body's front face at its own height
    for v in bm.verts:
        v.co.y += front_y(v.co.z)
    ob = new_object(name, bm, coll)
    add_bevel(ob, "Soft Edges", 0.0055, 3, limit='ANGLE', angle=40.0)
    return ob


def build_knob(coll, name, zc):
    """Small squat round knob on a short stem, centred on a panel."""
    y_face = front_y(zc) - PANEL_OUT
    stem_len = 0.012
    knob_r = 0.019
    knob_depth = 0.6          # Y-squash of the sphere
    bm = bmesh.new()
    # stem
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=0.0065, radius2=0.0065,
                                depth=stem_len + 0.004)
    for v in res['verts']:
        v.co = Vector((v.co.x, v.co.z, v.co.y))          # axis -> Y
        v.co.y += y_face - (stem_len + 0.004) / 2.0 + 0.004
        v.co.z += zc
    # knob head
    res = bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=knob_r)
    for v in res['verts']:
        v.co = Vector((v.co.x, v.co.z * knob_depth, v.co.y))
        v.co.y += y_face - stem_len - knob_r * knob_depth * 0.85
        v.co.z += zc
    ob = new_object(name, bm, coll)
    return ob


def build_leg(coll, name, x, y):
    """Short, thick, slightly tapered leg; pokes a little into the body."""
    depth = LEG_H + 0.012
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=LEG_R_BOT, radius2=LEG_R_TOP, depth=depth)
    for v in bm.verts:
        v.co.z += depth / 2.0
        v.co.x += x
        v.co.y += y
    ob = new_object(name, bm, coll)
    add_bevel(ob, "Foot Round", 0.007, 3, limit='ANGLE', angle=40.0)
    return ob


# ------------------------------------------------------------------ scene
def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def build():
    clear_scene()
    coll = bpy.data.collections.new(COLL_NAME)
    bpy.context.scene.collection.children.link(coll)

    build_body(coll)
    build_top(coll)

    avail = (BODY_Z1 - PANEL_MARGIN_TOP) - (BODY_Z0 + PANEL_MARGIN_BOT) - PANEL_GAP
    drawer_h = avail / 3.0
    door_h = avail - drawer_h
    drawer_z1 = BODY_Z1 - PANEL_MARGIN_TOP
    drawer_z0 = drawer_z1 - drawer_h
    door_z1 = drawer_z0 - PANEL_GAP
    door_z0 = door_z1 - door_h
    build_panel(coll, "Drawer Front", drawer_z0, drawer_z1)
    build_panel(coll, "Door", door_z0, door_z1)
    build_knob(coll, "Knob Drawer", (drawer_z0 + drawer_z1) / 2.0)
    build_knob(coll, "Knob Door", (door_z0 + door_z1) / 2.0)

    for nm, sx, sy in (("FL", -1, -1), ("FR", 1, -1), ("BL", -1, 1), ("BR", 1, 1)):
        build_leg(coll, f"Leg {nm}", sx * LEG_OFF, sy * LEG_OFF)

    return dict(drawer=(drawer_z0, drawer_z1), door=(door_z0, door_z1))


def save():
    path = os.path.join(HERE, "sonuc.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    return path


def render_previews():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'SINGLE'
    sh.single_color = (0.75, 0.72, 0.68)
    sh.show_cavity = True
    sh.show_shadows = True
    scene.display.render_aa = '8'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1000
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("W") if not bpy.data.worlds else bpy.data.worlds[0]

    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = 60
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    target = Vector((0, 0, 0.40))
    out_dir = os.path.join(HERE, "onizleme")
    os.makedirs(out_dir, exist_ok=True)
    views = {
        "34": Vector((1.0, -1.35, 0.75)),
        "front": Vector((0.0, -1.0, 0.05)),
        "side": Vector((1.0, 0.0, 0.05)),
        "low34": Vector((0.9, -1.2, -0.25)),
        "close": Vector((0.6, -1.0, 0.35)),
    }
    for name, d in views.items():
        dist = 1.2 if name == "close" else 2.3
        cam.location = target + d.normalized() * dist
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = os.path.join(out_dir, f"{name}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    info = build()
    p = save()
    print("SAVED", p, info)
    render_previews()
    print("RENDERED")
