"""Molly's Nightstand — headless build script.

Method: every part is a loft of rounded-rectangle rings (or a lathe for the
knobs) generated from explicit profile functions, so the bulge, taper and
edge roundings are baked into clean quad geometry. Units: metres, -Y = front.
"""
import bpy, bmesh, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- dimensions
H_TOTAL   = 0.80
LEG_H     = 0.08
TOP_T     = 0.045
Z_BODY0   = LEG_H
Z_BODY1   = H_TOTAL - TOP_T          # 0.755
BODY_H    = Z_BODY1 - Z_BODY0

W_BOT, W_MAX, T_PEAK, TOP_FRAC = 0.335, 0.400, 0.60, 0.75
BODY_R    = 0.035                    # vertical corner radius

TOP_W     = 0.44
TOP_R     = 0.045                    # plan corner radius of top
TOP_ROUND = 0.020                    # upper edge round-over
TOP_CHAMF = 0.007                    # lower edge chamfer

PANEL_T, PANEL_EMBED, PANEL_SIDE = 0.016, 0.002, 0.040
PANEL_EDGE = 0.006
MARGIN_TOP, MARGIN_BOT, GAP = 0.050, 0.060, 0.008

CS = 8                               # segments per rounded corner


def body_w(z):
    """Full width (=depth, square plan) of the carcass at height z."""
    t = min(max((z - Z_BODY0) / BODY_H, 0.0), 1.0)
    if t <= T_PEAK:
        f = 1 - ((t - T_PEAK) / T_PEAK) ** 2
    else:
        f = 1 - (1 - TOP_FRAC) * ((t - T_PEAK) / (1 - T_PEAK)) ** 2
    return W_BOT + (W_MAX - W_BOT) * f


def front_y(z):
    return -body_w(z) / 2


# ---------------------------------------------------------------- helpers
def rrect(cx, cy, hx, hy, r, z):
    r = max(min(r, hx - 1e-5, hy - 1e-5), 1e-4)
    pts = []
    corners = [(hx - r, hy - r, 0), (-hx + r, hy - r, 90),
               (-hx + r, -hy + r, 180), (hx - r, -hy + r, 270)]
    for ox, oy, a0 in corners:
        for i in range(CS + 1):
            a = math.radians(a0 + 90 * i / CS)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a), z))
    return pts


def edge_round_rings(z0, z1, rr_bot, rr_top, steps=6, mid=None, chamfer_bot=False):
    """(z, inset) samples for a slab/solid whose bottom/top edges are rounded
    (quarter circle) or chamfered. mid: extra intermediate z samples."""
    out = []
    if rr_bot > 0:
        if chamfer_bot:
            out += [(z0, rr_bot), (z0 + rr_bot, 0.0)]
        else:
            for i in range(steps + 1):
                th = math.pi / 2 * i / steps
                out.append((z0 + rr_bot - rr_bot * math.cos(th), rr_bot - rr_bot * math.sin(th)))
    else:
        out.append((z0, 0.0))
    for z in (mid or []):
        if out[-1][0] + 1e-4 < z < z1 - rr_top - 1e-4:
            out.append((z, 0.0))
    if rr_top > 0:
        for i in range(steps + 1):
            th = math.pi / 2 * i / steps
            out.append((z1 - rr_top + rr_top * math.sin(th), rr_top - rr_top * math.cos(th)))
    else:
        out.append((z1, 0.0))
    # drop duplicates
    clean = []
    for s in out:
        if not clean or abs(s[0] - clean[-1][0]) > 1e-6 or abs(s[1] - clean[-1][1]) > 1e-6:
            clean.append(s)
    return clean


def mesh_from_rings(name, rings, coll, sharp_angle=35):
    verts, faces = [], []
    n = len(rings[0])
    for ring in rings:
        verts += ring
    for k in range(len(rings) - 1):
        a, b = k * n, (k + 1) * n
        for i in range(n):
            j = (i + 1) % n
            faces.append((a + i, a + j, b + j, b + i))
    faces.append(tuple(reversed(range(n))))                       # bottom cap
    last = (len(rings) - 1) * n
    faces.append(tuple(range(last, last + n)))                    # top cap
    return finish(name, verts, faces, coll, sharp_angle)


def finish(name, verts, faces, coll, sharp_angle):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if e.is_manifold and e.calc_face_angle() > math.radians(sharp_angle):
            e.smooth = False
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def lathe(name, profile, coll, segs=48):
    """profile: (radius, d) pairs, revolved around local -Y (d grows toward -Y)."""
    verts, faces = [], []
    idx = []
    for r, d in profile:
        if r < 1e-7:
            idx.append([len(verts)] * segs)
            verts.append((0, -d, 0))
        else:
            row = []
            for s in range(segs):
                a = 2 * math.pi * s / segs
                row.append(len(verts))
                verts.append((r * math.cos(a), -d, r * math.sin(a)))
            idx.append(row)
    for k in range(len(idx) - 1):
        A, B = idx[k], idx[k + 1]
        for s in range(segs):
            t = (s + 1) % segs
            q = [A[s], A[t], B[t], B[s]]
            q2 = []
            for v in q:
                if v not in q2:
                    q2.append(v)
            if len(q2) >= 3:
                faces.append(tuple(q2))
    return finish(name, verts, faces, coll, 40)


# ---------------------------------------------------------------- scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
coll = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(coll)

# --- carcass: bulged, tapering down, rounded vertical corners, soft bottom edge
BODY_BOT_ROUND = 0.008
zs = [Z_BODY0 + BODY_H * i / 60 for i in range(61)]
samples = edge_round_rings(Z_BODY0, Z_BODY1 + 0.003, BODY_BOT_ROUND, 0, mid=zs)
rings = []
for z, ins in samples:
    h = body_w(min(z, Z_BODY1)) / 2 - ins
    rings.append(rrect(0, 0, h, h, BODY_R - ins, z))
mesh_from_rings("Body", rings, coll)

# --- top: overhanging slab, full round-over on top edge, chamfer underneath
samples = edge_round_rings(Z_BODY1, H_TOTAL, TOP_CHAMF, TOP_ROUND, steps=8, chamfer_bot=True)
rings = [rrect(0, 0, TOP_W / 2 - ins, TOP_W / 2 - ins, TOP_R - ins, z) for z, ins in samples]
mesh_from_rings("Top", rings, coll)

# --- front panels: drawer (upper, squat) and door (2x drawer height)
avail = BODY_H - MARGIN_TOP - MARGIN_BOT - GAP
drawer_h = avail / 3
door_z0 = Z_BODY0 + MARGIN_BOT
door_z1 = door_z0 + 2 * drawer_h
drawer_z0 = door_z1 + GAP
drawer_z1 = drawer_z0 + drawer_h


def panel(name, z0, z1):
    zs = [z0 + (z1 - z0) * i / 30 for i in range(31)]
    rings = []
    for z, ins in edge_round_rings(z0, z1, PANEL_EDGE, PANEL_EDGE, mid=zs):
        cy = front_y(z) - PANEL_T / 2 + PANEL_EMBED
        hx = body_w(z) / 2 - PANEL_SIDE - ins
        hy = PANEL_T / 2 - ins * 0.5          # front face pulls back at the round-over
        cy += ins * 0.5
        rings.append(rrect(0, cy, hx, hy, PANEL_EDGE, z))
    return mesh_from_rings(name, rings, coll)


panel("Drawer_Front", drawer_z0, drawer_z1)
panel("Door", door_z0, door_z1)

# --- knobs: short shaft + squat round mushroom cap, centred on each panel
KNOB = [(0.0, -0.003), (0.0065, -0.003), (0.0065, 0.0055), (0.0085, 0.0075),
        (0.0160, 0.0080), (0.0195, 0.0098), (0.0213, 0.0130), (0.0215, 0.0155),
        (0.0205, 0.0185), (0.0178, 0.0212), (0.0130, 0.0232), (0.0065, 0.0242),
        (0.0, 0.0245)]
for name, z0, z1 in (("Knob_Drawer", drawer_z0, drawer_z1), ("Knob_Door", door_z0, door_z1)):
    zc = (z0 + z1) / 2
    ob = lathe(name, KNOB, coll)
    ob.location = (0, front_y(zc) - PANEL_T + PANEL_EMBED, zc)

# --- legs: short, thick, tapering downward, near the corners
LEG_TOP, LEG_BOT, LEG_R = 0.064, 0.048, 0.015
off = W_BOT / 2 - 0.050
for nm, sx, sy in (("Leg_FL", -1, -1), ("Leg_FR", 1, -1), ("Leg_BL", -1, 1), ("Leg_BR", 1, 1)):
    rings = []
    for z, ins in edge_round_rings(0, LEG_H + 0.004, 0.005, 0, mid=[LEG_H * i / 8 for i in range(9)]):
        t = min(z / LEG_H, 1)
        h = (LEG_BOT + (LEG_TOP - LEG_BOT) * t) / 2 - ins
        rings.append(rrect(sx * off, sy * off, h, h, LEG_R - ins, z))
    mesh_from_rings(nm, rings, coll)

print("drawer h %.3f  door h %.3f" % (drawer_h, 2 * drawer_h))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "sonuc.blend"))
