"""Molly's Nightstand - headless Blender build script (geometry only, metres)."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sonuc.blend")
COLL_NAME = "Molly's Nightstand"

# ---------------- key dimensions (m) ----------------
LEG_H = 0.075          # legs 0 .. 0.075 (body starts at 0.07 -> 5 mm overlap)
BODY_Z0, BODY_Z1 = 0.07, 0.74
TOP_Z0, TOP_Z1 = 0.74, 0.80
BODY_R = 0.035         # vertical corner radius of body
TOP_HALF, TOP_R = 0.20, 0.045
W_BOT, W_MAX, W_TOP = 0.14, 0.185, 0.17   # body half-widths: bottom / belly / top
T_PEAK = 0.58          # belly position (0=bottom,1=top of body)

PANEL_PROUD, PANEL_SINK, PANEL_R = 0.008, 0.012, 0.02
PANEL_INSET = 0.045    # panel edge inset from body half-width
GAP = 0.008
DRAWER_Z1 = BODY_Z1 - 0.03
DRAWER_Z0 = DRAWER_Z1 - 0.20
DOOR_Z1 = DRAWER_Z0 - GAP
DOOR_Z0 = DOOR_Z1 - 0.40


def body_half(z):
    """Half-width of the body at height z: belly in the middle, clear taper to the bottom."""
    t = (z - BODY_Z0) / (BODY_Z1 - BODY_Z0)
    t = min(max(t, 0.0), 1.0)
    if t < T_PEAK:
        k = (W_MAX - W_BOT) / T_PEAK ** 2
        return W_MAX - k * (T_PEAK - t) ** 2
    k = (W_MAX - W_TOP) / (1 - T_PEAK) ** 2
    return W_MAX - k * (t - T_PEAK) ** 2


# ---------------- helpers ----------------
def rounded_square(half, r, z, seg=8):
    pts = []
    c = half - r
    for cx, cy, a0 in ((c, c, 0.0), (-c, c, math.pi / 2), (-c, -c, math.pi), (c, -c, 1.5 * math.pi)):
        for i in range(seg + 1):
            a = a0 + (math.pi / 2) * i / seg
            pts.append(Vector((cx + r * math.cos(a), cy + r * math.sin(a), z)))
    return pts


def loft(bm, rings, groups=None):
    """rings: list of equal-length point lists. Returns list of vert rings."""
    vrings = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(rings[0])
    for a, b in zip(vrings[:-1], vrings[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(list(reversed(vrings[0])))   # bottom cap
    bm.faces.new(vrings[-1])                  # top cap
    return vrings


def finish(bm, name, coll, sharp_deg=35.0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle() > math.radians(sharp_deg):
            e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def bevel(ob, name, width, segments, limit="ANGLE", vgroup=None, angle=60.0):
    m = ob.modifiers.new(name, "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = limit
    m.harden_normals = True
    if limit == "ANGLE":
        m.angle_limit = math.radians(angle)
    if vgroup:
        m.vertex_group = vgroup
    return m


def smooth_by_angle(ob, deg=35.0):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob],
                                   selected_editable_objects=[ob]):
        try:
            bpy.ops.object.shade_auto_smooth(angle=math.radians(deg))
        except Exception as ex:  # fallback: plain smooth, sharp edges already marked
            print("shade_auto_smooth failed:", ex)
            ob.data.shade_smooth()


def assign_group(bm, ob, verts, gname):
    vg = ob.vertex_groups.new(name=gname)
    dl = bm.verts.layers.deform.verify()
    for v in verts:
        v[dl][vg.index] = 1.0


# ---------------- scene ----------------
scene = bpy.context.scene
for ob in list(bpy.data.objects):            # default Cube / Light / Camera
    bpy.data.objects.remove(ob, do_unlink=True)
for c in list(bpy.data.collections):          # default "Collection"
    bpy.data.collections.remove(c)
for blk in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights, bpy.data.materials):
    for d in list(blk):
        if d.users == 0:
            blk.remove(d)
coll = bpy.data.collections.new(COLL_NAME)
scene.collection.children.link(coll)
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"

# ---------------- body (govde) ----------------
bm = bmesh.new()
dl = bm.verts.layers.deform.verify()   # create layer BEFORE verts so references stay valid
me = bpy.data.meshes.new("Govde")
ob_body = bpy.data.objects.new("Govde", me)
N = 28
rings = []
for i in range(N + 1):
    z = BODY_Z0 + (BODY_Z1 - BODY_Z0) * i / N
    rings.append(rounded_square(body_half(z), BODY_R, z))
vr = loft(bm, rings)
vg = ob_body.vertex_groups.new(name="alt")
for v in vr[0]:
    v[dl][vg.index] = 1.0
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
for f in bm.faces:
    f.smooth = True
for e in bm.edges:
    if len(e.link_faces) == 2 and e.calc_face_angle() > math.radians(35):
        e.smooth = False
bm.to_mesh(me)
bm.free()
coll.objects.link(ob_body)
bevel(ob_body, "Alt_pah", 0.006, 3, limit="VGROUP", vgroup="alt")
smooth_by_angle(ob_body)

# ---------------- top slab (tabla) ----------------
bm = bmesh.new()
bm.verts.layers.deform.verify()
me = bpy.data.meshes.new("Tabla")
ob_top = bpy.data.objects.new("Tabla", me)
vr = loft(bm, [rounded_square(TOP_HALF, TOP_R, TOP_Z0, seg=10),
               rounded_square(TOP_HALF, TOP_R, TOP_Z1, seg=10)])
assign_group(bm, ob_top, vr[0], "alt")
assign_group(bm, ob_top, vr[1], "ust")
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
for f in bm.faces:
    f.smooth = True
for e in bm.edges:
    if len(e.link_faces) == 2 and e.calc_face_angle() > math.radians(35):
        e.smooth = False
bm.to_mesh(me)
bm.free()
coll.objects.link(ob_top)
bevel(ob_top, "Ust_yuvarlak", 0.024, 12, limit="VGROUP", vgroup="ust")
bevel(ob_top, "Alt_pah", 0.007, 1, limit="VGROUP", vgroup="alt")
smooth_by_angle(ob_top)


# ---------------- front panels (cekmece / kapak) ----------------
def panel(name, z0, z1):
    levels = []  # (z, inset)
    A = 7
    for i in range(A + 1):                      # bottom arc
        phi = (math.pi / 2) * (1 - i / A)
        levels.append((z0 + PANEL_R - PANEL_R * math.sin(phi), PANEL_R - PANEL_R * math.cos(phi)))
    M = 8
    for i in range(1, M):                       # straight part
        levels.append((z0 + PANEL_R + (z1 - z0 - 2 * PANEL_R) * i / M, 0.0))
    for i in range(A + 1):                      # top arc
        phi = (math.pi / 2) * (i / A)
        levels.append((z1 - PANEL_R + PANEL_R * math.sin(phi), PANEL_R - PANEL_R * math.cos(phi)))
    rings = []
    for z, d in levels:
        w = body_half(z)
        xh = w - PANEL_INSET - d
        yf, yb = -(w + PANEL_PROUD), -(w - PANEL_SINK)
        rings.append([Vector((-xh, yf, z)), Vector((xh, yf, z)), Vector((xh, yb, z)), Vector((-xh, yb, z))])
    bm = bmesh.new()
    loft(bm, rings)
    ob = finish(bm, name, coll, sharp_deg=35)
    bevel(ob, "Yumusak_kenar", 0.0045, 4, limit="ANGLE", angle=60)
    smooth_by_angle(ob, 35)
    return ob


ob_drawer = panel("Cekmece_Paneli", DRAWER_Z0, DRAWER_Z1)
ob_door = panel("Kapak_Paneli", DOOR_Z0, DOOR_Z1)


# ---------------- knobs (topuz kulp) ----------------
def knob(name, zc):
    w = body_half(zc)
    yf = -(w + PANEL_PROUD)
    # stem
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=0.0055, radius2=0.0055, depth=0.026,
                          matrix=Matrix.Translation((0, yf - 0.007, zc)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    ob_s = finish(bm, name + "_Mil", coll, sharp_deg=35)
    bevel(ob_s, "Pah", 0.0012, 2, limit="ANGLE", angle=60)
    smooth_by_angle(ob_s)
    # squat knob
    bm = bmesh.new()
    R = 0.017
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=R,
                              matrix=Matrix.Translation((0, yf - 0.014 - R * 0.55 + 0.004, zc))
                              @ Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Diagonal((1, 1, 0.55, 1)))
    ob_k = finish(bm, name, coll, sharp_deg=35)
    smooth_by_angle(ob_k)
    return ob_s, ob_k


knob("Cekmece_Kulp", (DRAWER_Z0 + DRAWER_Z1) / 2)
knob("Kapak_Kulp", (DOOR_Z0 + DOOR_Z1) / 2)

# ---------------- legs (ayak) ----------------
LEG_OFF = 0.095
for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32,
                          radius1=0.025, radius2=0.032, depth=LEG_H,
                          matrix=Matrix.Translation((sx * LEG_OFF, sy * LEG_OFF, LEG_H / 2)))
    ob_l = finish(bm, f"Ayak_{i + 1}", coll, sharp_deg=35)
    bevel(ob_l, "Pah", 0.006, 4, limit="ANGLE", angle=60)
    smooth_by_angle(ob_l)

# ---------------- make "Smooth by Angle" node group local (no external library dependency) ----------------
for ng in list(bpy.data.node_groups):
    if ng.library:
        ng.make_local()
try:
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
except Exception as ex:
    print("purge:", ex)
print("libraries left:", [l.filepath for l in bpy.data.libraries])
print("node groups:", [(ng.name, bool(ng.library)) for ng in bpy.data.node_groups])

# ---------------- save ----------------
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("SAVED", OUT)
print("objects:", [o.name for o in coll.objects])
