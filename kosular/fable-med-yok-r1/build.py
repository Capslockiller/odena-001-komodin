"""Molly's Nightstand (Toy Story) - headless Blender build script.
Units: metres. Geometry only, no materials.
"""
import bpy, bmesh, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_BLEND = os.path.join(HERE, "sonuc.blend")
COLL_NAME = "Molly's Nightstand"

# ---------------------------------------------------------------- dimensions
FOOT_H = 0.06          # foot height
BODY_Z0 = FOOT_H       # body bottom
BODY_Z1 = 0.765        # body top
TOP_T = 0.035          # top slab thickness  -> total height 0.80
TOP_HW = 0.215         # top slab half width (0.43 m square)
PANEL_PROTRUDE = 0.008
GAP = 0.008

def body_hw(z):
    """Body half width at height z: bulges around 63 % of height, narrows markedly downward."""
    t = (z - BODY_Z0) / (BODY_Z1 - BODY_Z0)
    t = min(max(t, 0.0), 1.0)
    return 0.17 + 0.095 * t - 0.075 * t * t   # 0.17 bottom, 0.200 max, 0.19 top

def body_r(z):
    """Vertical corner radius of the body, scales with width."""
    return 0.05 * body_hw(z) / 0.2

# ---------------------------------------------------------------- helpers
def clean_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def get_coll():
    c = bpy.data.collections.get(COLL_NAME)
    if c is None:
        c = bpy.data.collections.new(COLL_NAME)
        bpy.context.scene.collection.children.link(c)
    return c

def new_obj(name, bm, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    get_coll().objects.link(ob)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob

def rounded_square_ring(bm, z, hw, r, n_corner=8):
    """Verts of a rounded square at height z, half width hw, corner radius r."""
    r = max(min(r, hw * 0.999), 0.0005)
    verts = []
    centers = [(hw - r, hw - r), (-(hw - r), hw - r), (-(hw - r), -(hw - r)), (hw - r, -(hw - r))]
    for ci, (cx, cy) in enumerate(centers):
        a0 = math.radians(90 * ci)
        for k in range(n_corner):
            a = a0 + (math.pi / 2) * k / n_corner
            verts.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z)))
    return verts

def loft(rings, bm, cap_bottom=True, cap_top=True):
    for a, b in zip(rings[:-1], rings[1:]):
        n = len(a)
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    if cap_bottom:
        bm.faces.new(list(reversed(rings[0])))
    if cap_top:
        bm.faces.new(rings[-1])

def add_bevel(ob, width, segments, angle_deg=None, name="Bevel"):
    m = ob.modifiers.new(name, 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE' if angle_deg else 'NONE'
    if angle_deg:
        m.angle_limit = math.radians(angle_deg)
    m.harden_normals = False
    return m

# ---------------------------------------------------------------- parts
def make_body():
    bm = bmesh.new()
    rings = []
    N = 28
    # tiny inset at bottom/top rings so the horizontal edges read as soft chamfers
    zs = [BODY_Z0 + (BODY_Z1 - BODY_Z0) * i / N for i in range(N + 1)]
    for i, z in enumerate(zs):
        hw, r = body_hw(z), body_r(z)
        rings.append(rounded_square_ring(bm, z, hw, r))
    loft(rings, bm)
    ob = new_obj("Body", bm)
    add_bevel(ob, 0.006, 3, angle_deg=35)
    return ob

def make_top():
    bm = bmesh.new()
    z0, z1 = BODY_Z1, BODY_Z1 + TOP_T
    hw, r = TOP_HW, 0.04
    rings = []
    # bottom chamfer: small 45° step
    ch = 0.005
    rings.append(rounded_square_ring(bm, z0, hw - ch, r - ch, 10))
    rings.append(rounded_square_ring(bm, z0 + ch, hw, r, 10))
    # vertical side up to the start of the top round
    rr = 0.016                       # top round-over radius (full, plump)
    rings.append(rounded_square_ring(bm, z1 - rr, hw, r, 10))
    # quarter round
    K = 8
    for k in range(1, K + 1):
        a = (math.pi / 2) * k / K
        inset = rr * (1 - math.cos(a))
        rings.append(rounded_square_ring(bm, z1 - rr + rr * math.sin(a), hw - inset, max(r - inset, 0.002), 10))
    loft(rings, bm)
    ob = new_obj("Top", bm)
    return ob

def make_panel(name, z0, z1, x_hw):
    """Front panel following the body's bulge. Front face protrudes PANEL_PROTRUDE out of the body."""
    bm = bmesh.new()
    N = 12
    front, back = [], []
    for i in range(N + 1):
        z = z0 + (z1 - z0) * i / N
        yf = -(body_hw(z) + PANEL_PROTRUDE)
        yb = -(body_hw(z) - 0.012)       # sinks slightly into the body so no gap shows
        front.append((bm.verts.new((-x_hw, yf, z)), bm.verts.new((x_hw, yf, z))))
        back.append((bm.verts.new((-x_hw, yb, z)), bm.verts.new((x_hw, yb, z))))
    for i in range(N):
        fl0, fr0 = front[i]; fl1, fr1 = front[i + 1]
        bl0, br0 = back[i];  bl1, br1 = back[i + 1]
        bm.faces.new((fl0, fr0, fr1, fl1))            # front
        bm.faces.new((br0, bl0, bl1, br1))            # back
        bm.faces.new((bl0, fl0, fl1, bl1))            # left side
        bm.faces.new((fr0, br0, br1, fr1))            # right side
    bm.faces.new((back[0][0], back[0][1], front[0][1], front[0][0]))        # bottom
    bm.faces.new((front[-1][0], front[-1][1], back[-1][1], back[-1][0]))    # top
    bm.normal_update()
    ob = new_obj(name, bm)
    add_bevel(ob, 0.006, 4, angle_deg=30)
    return ob

def make_knob(name, z):
    y_face = -(body_hw(z) + PANEL_PROTRUDE)
    # stem
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.006, radius2=0.006, depth=0.016,
                          matrix=__import__("mathutils").Matrix.Rotation(math.radians(90), 4, 'X'))
    for v in bm.verts:
        v.co.y += y_face - 0.005
        v.co.z += z
    stem = new_obj(name + " Stem", bm)
    # knob: squashed sphere
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.022)
    for v in bm.verts:
        v.co.y *= 0.55
        v.co.y += y_face - 0.016 - 0.0105
        v.co.z += z
    knob = new_obj(name, bm)
    return knob, stem

def make_foot(name, x, y):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=0.031, radius2=0.025, depth=FOOT_H + 0.01)
    # create_cone: radius1 at -depth/2 ... actually radius1 is bottom, radius2 is top in bmesh; fix orientation
    for v in bm.verts:
        v.co.z = -v.co.z            # flip so wider end is on top
        v.co.z += (FOOT_H + 0.01) / 2 - 0.0   # bottom at z=0, top sinks 1 cm into body
        v.co.x += x
        v.co.y += y
    ob = new_obj(name, bm)
    add_bevel(ob, 0.004, 3, angle_deg=40)
    return ob

# ---------------------------------------------------------------- build
clean_scene()
get_coll()

body = make_body()
top = make_top()

# front layout
margin_top, margin_bot, margin_side = 0.03, 0.035, 0.03
avail = (BODY_Z1 - margin_top) - (BODY_Z0 + margin_bot) - GAP
drawer_h = avail / 3.0
door_h = avail - drawer_h
door_z0 = BODY_Z0 + margin_bot
door_z1 = door_z0 + door_h
drawer_z0 = door_z1 + GAP
drawer_z1 = drawer_z0 + drawer_h
x_hw = body_hw(drawer_z0) - margin_side   # panels share one width (slightly narrower than body)

drawer = make_panel("Drawer Front", drawer_z0, drawer_z1, x_hw)
door = make_panel("Door", door_z0, door_z1, x_hw)
make_knob("Drawer Knob", (drawer_z0 + drawer_z1) / 2)
make_knob("Door Knob", (door_z0 + door_z1) / 2)

fx = body_hw(BODY_Z0) - 0.045
for nm, (x, y) in {"Foot FL": (-fx, -fx), "Foot FR": (fx, -fx), "Foot BL": (-fx, fx), "Foot BR": (fx, fx)}.items():
    make_foot(nm, x, y)

# tidy
for ob in get_coll().objects:
    ob.select_set(False)

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print("SAVED", OUT_BLEND)
print("drawer", drawer_z0, drawer_z1, "door", door_z0, door_z1, "panel hw", x_hw)
