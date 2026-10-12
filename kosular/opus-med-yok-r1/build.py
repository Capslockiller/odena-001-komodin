"""Molly's Nightstand - headless build script.
Units: metres. Front of the piece faces -Y. Floor at Z=0.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sonuc.blend")

# ---------------------------------------------------------------- dimensions
LEG_H = 0.085          # legs: floor -> body underside (+ 1 cm buried in body)
BODY_Z0 = 0.080        # body underside
BODY_Z1 = 0.757        # body top (hidden under the top slab)
TOP_Z0 = 0.755         # top slab underside
TOP_Z1 = 0.800         # overall height 80 cm
TOP_HALF = 0.215       # top slab 43 x 43 cm
TOP_R = 0.045          # plan corner radius of top slab
BODY_R = 0.030         # plan corner radius of body (soft vertical corners)

# body half-width profile: narrow at the bottom, widest a bit above the middle
W_BOT, W_MAX, W_TOP, T_PEAK = 0.163, 0.195, 0.189, 0.62


def body_half(z):
    t = (z - BODY_Z0) / (BODY_Z1 - BODY_Z0)
    t = min(max(t, 0.0), 1.0)
    if t < T_PEAK:
        a = (W_MAX - W_BOT) / T_PEAK ** 2
    else:
        a = (W_MAX - W_TOP) / (1 - T_PEAK) ** 2
    return W_MAX - a * (t - T_PEAK) ** 2


def body_half_slope(z, e=1e-4):
    return (body_half(z + e) - body_half(z - e)) / (2 * e)


# ---------------------------------------------------------------- helpers
def rounded_square(half, r, seg=12, cx=0.0, cy=0.0):
    """CCW ring of a rounded square, constant point count."""
    r = max(min(r, half), 1e-4)
    pts = []
    c = half - r
    for k, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        a0 = k * math.pi / 2
        for i in range(seg + 1):
            a = a0 + (math.pi / 2) * i / seg
            pts.append((cx + sx * c + r * math.cos(a), cy + sy * c + r * math.sin(a)))
    return pts


def loft(name, rings, cap_bottom=True, cap_top=True):
    """rings: list of (z, [(x, y), ...]) bottom -> top, equal point counts."""
    bm = bmesh.new()
    vrings = [[bm.verts.new((x, y, z)) for x, y in pts] for z, pts in rings]
    n = len(vrings[0])
    for a, b in zip(vrings[:-1], vrings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap_bottom:
        bm.faces.new(list(reversed(vrings[0])))
    if cap_top:
        bm.faces.new(vrings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def link(name, me, coll):
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def smooth_by_angle(ob, deg=35):
    for p in ob.data.polygons:
        p.use_smooth = True
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(deg))
    ob.select_set(False)


# ---------------------------------------------------------------- scene
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
coll = bpy.data.collections.new("Molly's Nightstand")
scene.collection.children.link(coll)

# ---------------------------------------------------------------- body
# bulging carcass lofted from rounded-square sections; small round on the bottom edge
EDGE_R = 0.008
rings = []
for i in range(7):                           # bottom edge round (quarter circle)
    a = (math.pi / 2) * i / 6
    z = BODY_Z0 + EDGE_R * (1 - math.cos(a))
    inset = EDGE_R * (1 - math.sin(a))
    h = body_half(z) - inset
    rings.append((z, rounded_square(h, BODY_R - inset)))
N = 48
for i in range(1, N + 1):
    z = BODY_Z0 + EDGE_R + (BODY_Z1 - BODY_Z0 - EDGE_R) * i / N
    rings.append((z, rounded_square(body_half(z), BODY_R)))
body = link("Body", loft("Body", rings), coll)
smooth_by_angle(body, 40)

# ---------------------------------------------------------------- top slab
TOP_ROUND = 0.022     # full round on the upper edge
CHAMFER = 0.008       # light chamfer on the lower edge
rings = [(TOP_Z0, rounded_square(TOP_HALF - CHAMFER, TOP_R - CHAMFER)),
         (TOP_Z0 + CHAMFER, rounded_square(TOP_HALF, TOP_R))]
zc = TOP_Z1 - TOP_ROUND
for i in range(0, 13):
    a = (math.pi / 2) * i / 12
    z = zc + TOP_ROUND * math.sin(a)
    inset = TOP_ROUND * (1 - math.cos(a))
    rings.append((z, rounded_square(TOP_HALF - inset, TOP_R - inset)))
top = link("Top", loft("Top", rings), coll)
smooth_by_angle(top, 30)
bv = top.modifiers.new("Bevel", 'BEVEL')          # soften the two chamfer edges
bv.limit_method = 'ANGLE'
bv.angle_limit = math.radians(30)
bv.width = 0.0015
bv.segments = 2
bv.harden_normals = False

# ---------------------------------------------------------------- legs
LEG_C = 0.127
LEG_TOP_HALF, LEG_BOT_HALF = 0.029, 0.022
LEG_TOP_Z = BODY_Z0 + 0.010
for sx, sy, tag in ((1, 1, "BR"), (-1, 1, "BL"), (1, -1, "FR"), (-1, -1, "FL")):
    rings = []
    fr = 0.004
    for i in range(5):                       # small round at the foot
        a = (math.pi / 2) * i / 4
        z = fr * (1 - math.cos(a))
        inset = fr * (1 - math.sin(a))
        h = LEG_BOT_HALF + (LEG_TOP_HALF - LEG_BOT_HALF) * z / LEG_TOP_Z - inset
        rings.append((z, rounded_square(h, h * 0.55, 10, sx * LEG_C, sy * LEG_C)))
    for i in range(1, 6):
        z = fr + (LEG_TOP_Z - fr) * i / 5
        h = LEG_BOT_HALF + (LEG_TOP_HALF - LEG_BOT_HALF) * z / LEG_TOP_Z
        rings.append((z, rounded_square(h, h * 0.55, 10, sx * LEG_C, sy * LEG_C)))
    leg = link(f"Leg_{tag}", loft(f"Leg_{tag}", rings), coll)
    smooth_by_angle(leg, 40)

# ---------------------------------------------------------------- front panels
PANEL_PROUD = 0.008    # how far the panel face stands off the body front
PANEL_T = 0.011        # panel thickness (buried 3 mm into the body)
SIDE_MARGIN = 0.034    # panel edge -> body side (clears the 3 cm corner round)
PANEL_R = 0.016        # panel corner radius in its own plane
GAP = 0.006
P_TOP, P_BOT = 0.727, 0.112
unit = (P_TOP - P_BOT - GAP) / 3.0
DRAWER = (P_TOP - unit, P_TOP)              # low drawer
DOOR = (P_BOT, P_TOP - unit - GAP)          # door, twice the drawer height
U_REF = 0.150


def front_y(z):
    return -body_half(z)


def panel_mesh(name, z0, z1, rows=40):
    """Rounded-rect outline in (u, z), filled, sliced into rows, then wrapped
    onto the bulging front: width follows the body, depth follows the bulge."""
    hz = (z1 - z0) / 2
    zm = (z0 + z1) / 2
    outline = []
    # build rounded rect (U_REF x hz) with radius PANEL_R
    seg = 8
    corners = ((U_REF - PANEL_R, hz - PANEL_R, 0), (-(U_REF - PANEL_R), hz - PANEL_R, 1),
               (-(U_REF - PANEL_R), -(hz - PANEL_R), 2), (U_REF - PANEL_R, -(hz - PANEL_R), 3))
    for cx, cz, k in corners:
        for i in range(seg + 1):
            a = k * math.pi / 2 + (math.pi / 2) * i / seg
            outline.append((cx + PANEL_R * math.cos(a), zm + cz + PANEL_R * math.sin(a)))
    bm = bmesh.new()
    # face lies in XZ with normal -Y: order so that normal faces front
    verts = [bm.verts.new((u, 0.0, z)) for u, z in outline]
    f = bm.faces.new(verts)
    bm.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    # horizontal slices so the face can bend with the bulge
    for i in range(1, rows):
        z = z0 + (z1 - z0) * i / rows
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z), plane_no=(0, 0, 1))
    # vertical slices too, keeps n-gons small and evenly shaded
    for u in (-0.1, -0.05, 0.0, 0.05, 0.1):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(u, 0, 0), plane_no=(1, 0, 0))
    for v in bm.verts:
        u, _, z = v.co
        half = body_half(z) - SIDE_MARGIN
        v.co = Vector((u * half / U_REF, front_y(z) - PANEL_PROUD, z))
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


panels = {}
for pname, (z0, z1) in (("Drawer_Front", DRAWER), ("Door", DOOR)):
    ob = link(pname, panel_mesh(pname, z0, z1), coll)
    for p in ob.data.polygons:
        p.use_smooth = True
    so = ob.modifiers.new("Solidify", 'SOLIDIFY')
    so.thickness = PANEL_T
    so.offset = -1.0                 # grow backwards into the carcass
    so.use_even_offset = True
    so.use_quality_normals = True
    bv = ob.modifiers.new("Bevel", 'BEVEL')
    bv.limit_method = 'ANGLE'
    bv.angle_limit = math.radians(50)
    bv.width = 0.0035
    bv.segments = 3
    bv.profile = 0.5
    panels[pname] = ((z0 + z1) / 2, ob)

# ---------------------------------------------------------------- knobs
# lathe profile (radius, height along axis) -> Screw modifier
KNOB_PROFILE = [
    (0.0000, -0.004),
    (0.0055, -0.004),
    (0.0055, 0.008),      # short spindle
    (0.0060, 0.0105),
    (0.0095, 0.0120),
    (0.0140, 0.0135),
    (0.0168, 0.0160),
    (0.0178, 0.0190),     # widest
    (0.0172, 0.0215),
    (0.0150, 0.0240),
    (0.0110, 0.0257),
    (0.0060, 0.0265),
    (0.0000, 0.0268),     # flattish domed face
]


def knob_mesh(name):
    me = bpy.data.meshes.new(name)
    # x1.1 radius, spindle shortened by 3 mm
    verts = [(r * 1.1, 0.0, h if h <= 0.0 else max(h - 0.003, 0.004)) for r, h in KNOB_PROFILE]
    edges = [(i, i + 1) for i in range(len(verts) - 1)]
    me.from_pydata(verts, edges, [])
    return me


for pname, (zc, pob) in panels.items():
    kname = "Knob_" + pname.split("_")[0]
    kob = link(kname, knob_mesh(kname), coll)
    sc = kob.modifiers.new("Screw", 'SCREW')
    sc.axis = 'Z'
    sc.angle = math.radians(360)
    sc.steps = 40
    sc.render_steps = 40
    sc.screw_offset = 0.0
    sc.use_merge_vertices = True
    sc.merge_threshold = 1e-5
    sc.use_smooth_shade = True
    sc.use_normal_calculate = True
    # orient along the outward normal of the bulging front at this height
    slope = body_half_slope(zc)
    n = Vector((0.0, -1.0, -slope)).normalized()
    rot = Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4()
    base = Vector((0.0, front_y(zc) - PANEL_PROUD, zc))
    kob.matrix_world = Matrix.Translation(base) @ rot
    kob.parent = pob
    kob.matrix_parent_inverse = pob.matrix_world.inverted()

# panels/legs/top hang off the body for easy handling
for ob in coll.objects:
    if ob is not body and ob.parent is None:
        ob.parent = body
        ob.matrix_parent_inverse = body.matrix_world.inverted()

for m in list(bpy.data.materials):          # geometry only: drop factory material
    bpy.data.materials.remove(m)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
for ob in coll.objects:
    print(ob.name, [m.type for m in ob.modifiers], tuple(round(d, 3) for d in ob.dimensions))
