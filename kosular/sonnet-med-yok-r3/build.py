import bpy, bmesh, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(col)
NC = 7  # points per corner

def mk(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob); return ob

def loft(name, rings, cx=0, cy=0):
    """rings: list of (z, halfwidth, corner_radius)"""
    bm = bmesh.new(); R = []
    for z, hw, r in rings:
        r = min(r, hw*0.98); ring = []
        for k, (sx, sy) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
            for i in range(NC):
                a = math.radians(90*k + 90*i/(NC-1))
                ring.append(bm.verts.new((cx + sx*0+ (hw-r)*sx*(1 if True else 1) + 0, 0, 0)))
        bm.verts.ensure_lookup_table()
        # rewrite coordinates properly
        idx = 0
        for k, (sx, sy) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
            for i in range(NC):
                a = math.radians(90*k + 90*i/(NC-1))
                ring[idx].co = (cx + (hw-r)*sx + r*math.cos(a), cy + (hw-r)*sy + r*math.sin(a), z); idx += 1
        R.append(ring)
    n = len(R[0])
    for a, b in zip(R, R[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i+1)%n], b[(i+1)%n], b[i]))
    bm.faces.new(R[0][::-1]); bm.faces.new(R[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mk(name, bm)

ZB0, ZB1 = 0.09, 0.75
def w(z):
    t = (z-ZB0)/(ZB1-ZB0)
    if t <= 0.72: return 0.15 + 0.04*math.sin(math.pi/2*t/0.72)
    return 0.19 - 0.012*((t-0.72)/0.28)**2

# body
zs = [ZB0 + (ZB1-ZB0)*i/24 for i in range(25)]
rings = [(ZB0, w(ZB0)-0.008, 0.04), (ZB0+0.006, w(ZB0+0.006)-0.003, 0.042)]
rings += [(z, w(z), 0.045) for z in zs[1:]]
rings.append((ZB1+0.006, w(ZB1), 0.045))
body = loft("Body", rings)

# top slab: chamfered underside, full round upper edge
H = 0.22; T0, T1 = 0.75, 0.80; rt = 0.05
rg = [(T0, H-0.008, rt-0.008), (T0+0.008, H, rt)]
rad = 0.02
for i in range(1, 9):
    a = math.radians(90*i/8)
    rg.append((T1-rad + rad*math.sin(a), H-rad + rad*math.cos(a), rt))
rg[2:] = [(z, h, max(rt-(H-h), 0.015)) for z, h, _ in rg[2:]]
top = loft("Top", rg)

# legs
legs = []
for sx in (1, -1):
    for sy in (1, -1):
        lr = [(0.0, 0.020, 0.016), (0.006, 0.023, 0.018), (0.04, 0.0275, 0.022), (0.10, 0.032, 0.024)]
        legs.append(loft("Leg", lr, cx=sx*0.118, cy=sy*0.118))
for i, l in enumerate(legs): l.name = f"Leg.{i+1}"

# panels
def panel(name, z0, z1, hw, rc):
    bm = bmesh.new(); pts = []
    for k, (sx, sz) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
        for i in range(NC):
            a = math.radians(90*k + 90*i/(NC-1))
            pts.append(bm.verts.new(((hw-rc)*sx + rc*math.cos(a), 0, (z0+z1)/2 + ((z1-z0)/2-rc)*sz + rc*math.sin(a))))
    f = bm.faces.new(pts)
    bmesh.ops.triangulate(bm, faces=[f])
    for _ in range(3):
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
    OFF, TH = 0.008, 0.018
    for v in bm.verts:
        v.co.y = -(w(v.co.z) + OFF)
    ex = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    for v in [g for g in ex["geom"] if isinstance(g, bmesh.types.BMVert)]:
        v.co.y += TH
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = mk(name, bm)
    m = ob.modifiers.new("Bevel", 'BEVEL'); m.width = 0.0045; m.segments = 3; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(40)
    return ob
drawer = panel("Drawer Front", 0.535, 0.725, 0.10, 0.025)
door = panel("Door", 0.13, 0.515, 0.10, 0.03)

# knobs
def knob(name, zc):
    yf = -(w(zc) + 0.008)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.022)
    for v in bm.verts: v.co.y *= 0.55; v.co.y += yf - 0.020 - 0.006
    sh = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.007, radius2=0.007, depth=0.022,
                          matrix=__import__('mathutils').Matrix.Translation((0, yf-0.009, zc)) @ __import__('mathutils').Matrix.Rotation(math.pi/2, 4, 'X'))
    for v in bm.verts:
        if abs(v.co.z) < 0.03 and v.co.y < yf-0.015 and False: pass
    ob = mk(name, bm); return ob
# sphere centred at zc: fix z after creation
def knob2(name, zc):
    yf = -(w(zc) + 0.008)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.022)
    for v in bm.verts:
        v.co.y = v.co.y*0.5 + yf - 0.018 - 0.011; v.co.z += zc
    from mathutils import Matrix
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.007, radius2=0.007, depth=0.026,
                          matrix=Matrix.Translation((0, yf-0.008, zc)) @ Matrix.Rotation(math.pi/2, 4, 'X'))
    return mk(name, bm)
k1 = knob2("Drawer Knob", 0.63); k2 = knob2("Door Knob", 0.322)

bpy.ops.object.select_all(action='DESELECT')
for ob in col.objects: ob.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
bpy.ops.wm.save_as_mainfile(filepath="sonuc.blend")

# previews
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = 700; sc.render.resolution_y = 900
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'SINGLE'
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
def shot(fn, loc, tgt=(0,0,0.4), ortho=False):
    cam.location = loc
    d = Vector(tgt) - Vector(loc); cam.rotation_euler = d.to_track_quat('-Z','Y').to_euler()
    cam.data.type = 'ORTHO' if ortho else 'PERSP'; cam.data.ortho_scale = 1.0
    sc.render.filepath = "//prev_"+fn+".png"; bpy.ops.render.render(write_still=True)
shot("persp", (0.9,-1.2,0.9)); shot("front", (0,-3,0.4), ortho=True); shot("side", (3,0,0.4), ortho=True)
shot("back", (-0.9,1.2,0.9))
