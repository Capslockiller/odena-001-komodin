"""Molly's Nightstand - procedural build (Blender 5.x, headless).

Units: metres. Origin at floor centre, front faces -Y.
"""
import bpy, bmesh, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- dimensions
LEG_H      = 0.10          # floor -> body bottom
BODY_Z0    = LEG_H
TOP_T      = 0.045         # top slab thickness
TOTAL_H    = 0.80
BODY_Z1    = TOTAL_H - TOP_T            # body top = underside of top slab
BODY_CR    = 0.030         # vertical corner radius of carcass

W_BOTTOM, W_MAX, W_TOP = 0.34, 0.40, 0.385
T_PEAK = 0.62              # bulge peak, as fraction of body height

TOP_W  = 0.44              # top slab, square
TOP_CR = 0.05

PANEL_PROT  = 0.010        # how far panels stand proud of the carcass
PANEL_EMBED = 0.003
PANEL_SIDE  = 0.042        # side margin from carcass outline to panel edge
PANEL_Z1    = BODY_Z1 - 0.030
GAP         = 0.008
H_UNIT      = 0.18                               # drawer = 1, door = 2
PANEL_Z0    = PANEL_Z1 - 3 * H_UNIT - GAP         # leaves a plain apron below the door
DOOR  = (PANEL_Z0, PANEL_Z0 + 2 * H_UNIT)
DRAWER = (DOOR[1] + GAP, PANEL_Z1)


def body_w(z):
    """Carcass width (= depth, square plan) at height z."""
    t = (z - BODY_Z0) / (BODY_Z1 - BODY_Z0)
    t = min(max(t, 0.0), 1.0)
    if t < T_PEAK:
        a = (W_MAX - W_BOTTOM) / T_PEAK ** 2
    else:
        a = (W_MAX - W_TOP) / (1 - T_PEAK) ** 2
    return W_MAX - a * (t - T_PEAK) ** 2


def body_dw(z, h=1e-4):
    return (body_w(z + h) - body_w(z - h)) / (2 * h)


# ---------------------------------------------------------------- helpers
def rrect(hx, hy, r, z, seg=8):
    """Rounded rectangle ring, CCW, starting at +X/-Y corner."""
    pts = []
    corners = [(hx - r, -(hy - r), -90), (hx - r, hy - r, 0),
               (-(hx - r), hy - r, 90), (-(hx - r), -(hy - r), 180)]
    for cx, cy, a0 in corners:
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    return pts


def loft(name, rings, cap_bottom=True, cap_top=True):
    bm = bmesh.new()
    vrings = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(rings[0])
    for a, b in zip(vrings[:-1], vrings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap_bottom:
        bm.faces.new(list(reversed(vrings[0])))
    if cap_top:
        bm.faces.new(vrings[-1])
    return finish(name, bm)


def finish(name, bm):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    COLL.objects.link(ob)
    return ob


def smooth(ob, angle=35):
    for p in ob.data.polygons:
        p.use_smooth = True
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.view_layer.objects:
        o.select_set(o == ob)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))


def bevel(ob, width, segs=3, angle=30):
    m = ob.modifiers.new("Bevel", 'BEVEL')
    m.width = width
    m.segments = segs
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.harden_normals = False
    return m


def weighted(ob):
    m = ob.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
    m.keep_sharp = True


# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
COLL = bpy.data.collections.new("Molly's Nightstand")
scene.collection.children.link(COLL)

# ---------------------------------------------------------------- carcass
N_RINGS = 40
rings = []
for k in range(N_RINGS + 1):
    z = BODY_Z0 + (BODY_Z1 - BODY_Z0) * k / N_RINGS
    h = body_w(z) / 2
    rings.append(rrect(h, h, BODY_CR, z))
body = loft("Body", rings)
bevel(body, 0.006, segs=3, angle=30)      # soften bottom/top rim
smooth(body)
weighted(body)

# ---------------------------------------------------------------- top slab
# profile: (inset from outline, z) bottom -> top
prof = [(0.008, 0.0), (0.0, 0.007), (0.0, TOP_T - 0.022)]
R_ROUND = 0.022
for i in range(1, 9):
    a = math.radians(90 * i / 8)
    prof.append((R_ROUND * (1 - math.cos(a)), TOP_T - R_ROUND + R_ROUND * math.sin(a)))
rings = [rrect(TOP_W / 2 - d, TOP_W / 2 - d, TOP_CR - d, BODY_Z1 + z, seg=10) for d, z in prof]
top = loft("Top", rings)
smooth(top, 40)
weighted(top)


# ---------------------------------------------------------------- panels
def panel(name, z0, z1, nx=16, nz=24):
    bm = bmesh.new()

    def surf(u, v, front):
        z = z0 + (z1 - z0) * v
        hw = body_w(z) / 2 - PANEL_SIDE
        x = -hw + 2 * hw * u
        y = -body_w(z) / 2 + (-PANEL_PROT if front else PANEL_EMBED)
        return (x, y, z)

    F = [[bm.verts.new(surf(i / nx, j / nz, True)) for i in range(nx + 1)] for j in range(nz + 1)]
    B = [[bm.verts.new(surf(i / nx, j / nz, False)) for i in range(nx + 1)] for j in range(nz + 1)]
    for j in range(nz):
        for i in range(nx):
            bm.faces.new((F[j][i], F[j][i + 1], F[j + 1][i + 1], F[j + 1][i]))
            bm.faces.new((B[j][i], B[j + 1][i], B[j + 1][i + 1], B[j][i + 1]))
    # rim: walk the perimeter of the grid
    per = ([(0, i) for i in range(nx)] + [(j, nx) for j in range(nz)] +
           [(nz, i) for i in range(nx, 0, -1)] + [(j, 0) for j in range(nz, 0, -1)])
    for k in range(len(per)):
        (j0, i0), (j1, i1) = per[k], per[(k + 1) % len(per)]
        bm.faces.new((F[j0][i0], B[j0][i0], B[j1][i1], F[j1][i1]))
    ob = finish(name, bm)
    bevel(ob, 0.005, segs=4, angle=30)
    smooth(ob, 30)
    weighted(ob)
    return ob


door = panel("Door", *DOOR)
drawer = panel("Drawer_Front", *DRAWER)


# ---------------------------------------------------------------- knobs
# lathe profile (radius, distance along axis from base)
KNOB_PROF = [(0.0, 0.0), (0.0062, 0.0), (0.0062, 0.009), (0.0075, 0.0115),
             (0.0150, 0.0135), (0.0200, 0.0160), (0.0222, 0.0195),
             (0.0215, 0.0235), (0.0180, 0.0265), (0.0110, 0.0285), (0.0, 0.0292)]


def knob(name, zc):
    seg = 40
    bm = bmesh.new()
    rings = []
    for r, a in KNOB_PROF:
        if r == 0.0:
            rings.append([bm.verts.new((0, -a, 0))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * s / seg), -a,
                                        r * math.sin(2 * math.pi * s / seg))) for s in range(seg)])
    for ra, rb in zip(rings[:-1], rings[1:]):
        for s in range(seg):
            t = (s + 1) % seg
            if len(ra) == 1:
                bm.faces.new((ra[0], rb[t], rb[s]))
            elif len(rb) == 1:
                bm.faces.new((ra[s], ra[t], rb[0]))
            else:
                bm.faces.new((ra[s], ra[t], rb[t], rb[s]))
    ob = finish(name, bm)
    # place on the panel face, axis along the local surface normal
    y_face = -body_w(zc) / 2 - PANEL_PROT
    tilt = math.atan(body_dw(zc) / 2)   # front face leans as width changes
    ob.location = (0, y_face + 0.002, zc)
    ob.rotation_euler = (tilt, 0, 0)
    sub = ob.modifiers.new("Subdivision", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2
    smooth(ob, 60)
    return ob


knob("Knob_Door", (DOOR[0] + DOOR[1]) / 2)
knob("Knob_Drawer", (DRAWER[0] + DRAWER[1]) / 2)

# ---------------------------------------------------------------- legs
LEG_TOP, LEG_BOT, LEG_CR = 0.060, 0.044, 0.014
leg_c = W_BOTTOM / 2 - LEG_TOP / 2 - 0.006
for sx, sy, nm in [(-1, -1, "FL"), (1, -1, "FR"), (-1, 1, "BL"), (1, 1, "BR")]:
    rings = []
    n = 8
    for k in range(n + 1):
        t = k / n
        z = t * (LEG_H + 0.006)          # leg top sinks 6 mm into the carcass
        h = (LEG_BOT + (LEG_TOP - LEG_BOT) * t) / 2
        rings.append(rrect(h, h, LEG_CR * (0.8 + 0.2 * t), z, seg=6))
    leg = loft(f"Leg_{nm}", rings)
    leg.location = (sx * leg_c, sy * leg_c, 0)
    bevel(leg, 0.004, segs=3, angle=30)
    smooth(leg)
    weighted(leg)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "sonuc.blend"))
print("DOOR", DOOR, "DRAWER", DRAWER, "H_UNIT", H_UNIT)
