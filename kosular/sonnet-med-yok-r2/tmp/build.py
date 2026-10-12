import bpy, bmesh, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
COL = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(COL)

def rrect(h, r, n=6):
    """rounded square ring, half-size h, corner radius r, CCW; n arc segs/corner"""
    r = max(min(r, h - 1e-4), 1e-4)
    pts = []
    for (cx, cy, a0) in ((h-r, h-r, 0), (-(h-r), h-r, 90), (-(h-r), -(h-r), 180), (h-r, -(h-r), 270)):
        for i in range(n+1):
            a = math.radians(a0 + 90*i/n)
            pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    return pts

def loft(name, rings, cap_bottom=True, cap_top=True, smooth=True):
    """rings: list of (z, pointlist[(x,y)]), same vertex count"""
    bm = bmesh.new()
    vr = [[bm.verts.new((x, y, z)) for (x, y) in pts] for z, pts in rings]
    n = len(vr[0])
    for k in range(len(vr)-1):
        for i in range(n):
            bm.faces.new((vr[k][i], vr[k][(i+1) % n], vr[k+1][(i+1) % n], vr[k+1][i]))
    if cap_bottom: bm.faces.new(vr[0][::-1])
    if cap_top: bm.faces.new(vr[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); COL.objects.link(ob)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return ob

# ---- profile ----
Z0, ZM, Z1 = 0.08, 0.50, 0.74
def hw(z):
    if z <= ZM:
        t = (z-Z0)/(ZM-Z0); return 0.135 + 0.040*(1-(1-t)**2)
    u = (z-ZM)/(Z1-ZM); return 0.175 - 0.013*u*u
CR = 0.04

# body
rings = []
N = 28
for i in range(N+1):
    z = Z0 + (Z1-Z0)*i/N
    rings.append((z, rrect(hw(z), CR)))
body = loft("Govde", rings)

# tabla (top slab)
T0, T1, TH = 0.74, 0.80, 0.20
rings = [(T0, rrect(TH-0.010, 0.035)), (T0+0.008, rrect(TH, 0.045))]
zs = T0+0.008
rings.append((T0+0.034, rrect(TH, 0.045)))
R = 0.022; zc = T1 - R
for k in range(1, 7):
    a = math.radians(90*k/6)
    d = R*(1-math.cos(a)); z = zc + R*math.sin(a)
    rings.append((z, rrect(TH-d, 0.045-d*0.9)))
tabla = loft("Tabla", rings)
bm = bpy.context.view_layer
m = tabla.modifiers.new("Bevel_ust_kenar", 'BEVEL'); m.width = 0.0015; m.segments = 2; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(60)

# feet
feet = []
for sx in (-1, 1):
    for sy in (-1, 1):
        rs = [(0.0, rrect(0.026, 0.016)), (0.004, rrect(0.0285, 0.017)), (0.02, rrect(0.0315, 0.018)), (0.08, rrect(0.037, 0.02))]
        rs = [(z, rrect(0.026, 0.016)) for z in [0.0]] + [(0.003, rrect(0.0275,0.0165)), (0.012, rrect(0.029, 0.017)), (0.045, rrect(0.0335, 0.019)), (0.081, rrect(0.037, 0.02))]
        f = loft("Ayak_%s%s" % ('+' if sx > 0 else '-', '+' if sy > 0 else '-'), rs)
        f.location = (sx*0.103, sy*0.103, 0)
        feet.append(f)

# front panels
def panel(name, zlo, zhi, w=0.18, r=0.022, proud=0.004, thick=0.012):
    bm = bmesh.new()
    nx = 18; nz = int(round(18*(zhi-zlo)/w)) + 2
    g = []
    for j in range(nz+1):
        row = []
        for i in range(nx+1):
            x = -w/2 + w*i/nx; zz = zlo + (zhi-zlo)*j/nz
            hh = (zhi-zlo)/2; zr = zz - (zlo+zhi)/2
            # round corners
            cx = abs(x) - (w/2 - r); cz = abs(zr) - (hh - r)
            if cx > 0 and cz > 0:
                d = math.hypot(cx, cz)
                if d > r:
                    x = math.copysign(w/2 - r + cx*r/d, x)
                    zr = math.copysign(hh - r + cz*r/d, zr); zz = (zlo+zhi)/2 + zr
            row.append(bm.verts.new((x, -(hw(zz)+proud), zz)))
        g.append(row)
    for j in range(nz):
        for i in range(nx):
            try: bm.faces.new((g[j][i], g[j][i+1], g[j+1][i+1], g[j+1][i]))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); COL.objects.link(ob)
    # ensure normals point -Y
    if sum(p.normal.y for p in me.polygons) > 0:
        for p in me.polygons: p.flip()
        me.update()
    for p in me.polygons: p.use_smooth = True
    s = ob.modifiers.new("Solidify", 'SOLIDIFY'); s.thickness = thick; s.offset = -1
    b = ob.modifiers.new("Bevel", 'BEVEL'); b.width = 0.0035; b.segments = 3; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(30)
    return ob

DR = (0.502, 0.682); DO = (0.130, 0.490)
drawer = panel("Cekmece_On", *DR)
door = panel("Kapak_On", *DO)

# knobs (lathe)
def knob(name, z):
    bm = bmesh.new()
    prof = [(0, 0.0), (0.0055, 0.0), (0.0055, 0.014), (0.011, 0.015), (0.0165, 0.019), (0.0185, 0.0235),
            (0.0165, 0.0285), (0.010, 0.0315), (0, 0.032)]
    vs = [bm.verts.new((r, -d, 0)) for r, d in prof]
    es = [bm.edges.new((vs[i], vs[i+1])) for i in range(len(vs)-1)]
    bmesh.ops.spin(bm, geom=vs+es, cent=(0, 0, 0), axis=(0, 1, 0), angle=2*math.pi, steps=28, use_merge=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); COL.objects.link(ob)
    ob.location = (0, -(hw(z)+0.004), z)
    return ob
k1 = knob("Topuz_Cekmece", sum(DR)/2)
k2 = knob("Topuz_Kapak", sum(DO)/2)

# normals sanity: make sure each closed mesh points outward
for ob in COL.objects:
    bm = bmesh.new(); bm.from_mesh(ob.data)
    if ob.name.startswith(("Govde", "Tabla", "Ayak", "Topuz")):
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(ob.data)
    bm.free()

# units
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0

# report dims
mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
dg = bpy.context.evaluated_depsgraph_get()
for ob in COL.objects:
    e = ob.evaluated_get(dg)
    for c in e.bound_box:
        w = ob.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
print("BBOX", mn, mx, mx-mn)

# preview rig (not saved into collection; removed before save)
import os
D = os.path.dirname(bpy.data.filepath) or os.getcwd()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, "sonuc.blend"))

sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'SINGLE'
sc.display.shading.single_color = (0.8, 0.8, 0.8)
sc.render.resolution_x = 700; sc.render.resolution_y = 700
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'
def shot(name, loc, rot, scale=1.1, tgt=(0,0,0.4)):
    cam.data.ortho_scale = scale
    cam.location = loc; cam.rotation_euler = rot
    sc.render.filepath = os.path.join(D, "tmp", name + ".png"); bpy.ops.render.render(write_still=True)
shot("front", (0,-3,0.4), (math.pi/2,0,0), 1.0)
shot("side", (3,0,0.4), (math.pi/2,0,math.pi/2), 1.0)
shot("persp", (1.6,-1.6,1.2), (math.radians(65),0,math.radians(45)), 1.1)
cam.data.type='PERSP'; cam.data.lens=60
shot("persp2", (-1.5,-1.9,1.3), (math.radians(68),0,math.radians(-38)))
shot("under", (1.3,-1.3,-0.5), (math.radians(115),0,math.radians(45)))
