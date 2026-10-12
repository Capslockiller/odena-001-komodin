import bpy, bmesh, math
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("Molly's Nightstand"); bpy.context.scene.collection.children.link(col)

def rrect(hw, r, n=6):
    """rounded square ring, CCW, starting at +x side, returns list of (x,y)"""
    r = min(r, hw-1e-4); pts=[]
    for ci,(cx,cy) in enumerate([(1,1),(-1,1),(-1,-1),(1,-1)]):
        for k in range(n+1):
            a = math.radians(90*ci + 90*k/n)
            pts.append((cx*(hw-r)+r*math.cos(a), cy*(hw-r)+r*math.sin(a)))
    return pts

def loft(name, prof, n=6, smooth=True):
    """prof: list of (z, halfwidth, corner radius) bottom->top"""
    bm = bmesh.new(); rings=[]
    for z,hw,r in prof:
        rings.append([bm.verts.new((x,y,z)) for x,y in rrect(hw,r,n)])
    m=len(rings[0])
    for i in range(len(rings)-1):
        for j in range(m):
            bm.faces.new((rings[i][j],rings[i][(j+1)%m],rings[i+1][(j+1)%m],rings[i+1][j]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=smooth
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob

def add_mod(ob, kind, **kw):
    m=ob.modifiers.new(kind.title(), kind)
    for k,v in kw.items(): setattr(m,k,v)
    return m

Z_FOOT=0.075; Z_TOP=0.745; Z_TOP_END=0.80
# --- body: belly widest at ~65% height, narrows strongly downward
def hw_body(t):  # t 0..1 bottom..top
    return 0.150 + (0.190-0.150)*math.sin(min(t/0.62,1)*math.pi/2) - (0.190-0.178)*max(0,(t-0.62)/0.38)**2 if True else 0
N=14; body_prof=[]
for i in range(N+1):
    t=i/N; body_prof.append((Z_FOOT+t*(Z_TOP-Z_FOOT-0.004), hw_body(t), 0.032))
body=loft("Body", body_prof)
add_mod(body,'WEIGHTED_NORMAL', keep_sharp=True)
def zb(t): return Z_FOOT+t*(Z_TOP-Z_FOOT-0.004)

# --- top slab: rounded top edge, small chamfer under
zt0=Z_TOP-0.004; th=Z_TOP_END-zt0; HW=0.215; R=0.045
prof=[(zt0,HW-0.008,R-0.006),(zt0+0.006,HW,R)]
rt=0.020; zc=Z_TOP_END-rt
for k in range(1,6):
    a=math.radians(90*k/5); prof.append((zc+rt*math.sin(a), HW-rt+rt*math.cos(a), R-rt*(1-math.cos(a))*0.5))
top=loft("Top", prof)
add_mod(top,'WEIGHTED_NORMAL', keep_sharp=True)
# slab: widest 0.43 (a bit proud of body, 0.38) -> overhang

# --- front panels (follow belly) ---
def panel(name,t0,t1,half,ny=8):
    bm=bmesh.new(); nx=6; g=[]
    for j in range(ny+1):
        t=t0+(t1-t0)*j/ny; z=zb(t); y=-(hw_body(t)+0.0035)
        g.append([bm.verts.new((-half+2*half*i/nx,y,z)) for i in range(nx+1)])
    for j in range(ny):
        for i in range(nx): bm.faces.new((g[j][i],g[j][i+1],g[j+1][i+1],g[j+1][i]))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:p.use_smooth=True
    ob=bpy.data.objects.new(name,me); col.objects.link(ob)
    s=add_mod(ob,'SOLIDIFY',thickness=-0.010,offset=1.0)  # extrude toward body? (fixed below)
    ob.modifiers[0].thickness=0.012; ob.modifiers[0].offset=-1.0
    add_mod(ob,'BEVEL',width=0.004,segments=3,limit_method='ANGLE')
    return ob
T0,T1=0.07,0.94; g=0.008/(Z_TOP-Z_FOOT); dh=(T1-T0-g)/3
door=panel("Door",T0,T0+2*dh,0.150)
drawer=panel("Drawer Front",T0+2*dh+g,T1,0.150)
def knob(name,t):
    z=zb(t); y=-(hw_body(t)+0.0035)
    bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=20,radius1=0.007,radius2=0.007,depth=0.020)
    me=bpy.data.meshes.new(name+" Shaft"); bm.to_mesh(me); bm.free()
    s=bpy.data.objects.new(name+" Shaft",me); col.objects.link(s)
    s.rotation_euler=(math.pi/2,0,0); s.location=(0,y-0.010,z)
    bm=bmesh.new(); bmesh.ops.create_uvsphere(bm,u_segments=24,v_segments=12,radius=0.022)
    me=bpy.data.meshes.new(name+" Head"); bm.to_mesh(me); bm.free()
    for p in me.polygons:p.use_smooth=True
    h=bpy.data.objects.new(name+" Head",me); col.objects.link(h)
    h.scale=(1,0.5,1); h.location=(0,y-0.024,z)
knob("Door Knob",T0+dh); knob("Drawer Knob",T0+2*dh+g+dh/2)
# feet: tapering, near corners
for sx in(-1,1):
    for sy in(-1,1):
        bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=24,radius1=0.020,radius2=0.030,depth=Z_FOOT+0.01)
        me=bpy.data.meshes.new("Foot"); bm.to_mesh(me); bm.free()
        for p in me.polygons:p.use_smooth=True
        f=bpy.data.objects.new("Foot %s%s"%("R" if sx>0 else "L","B" if sy>0 else "F"),me); col.objects.link(f)
        f.location=(sx*0.135,sy*0.135,(Z_FOOT+0.01)/2)
        add_mod(f,'BEVEL',width=0.004,segments=3,limit_method='ANGLE')
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//../sonuc.blend"))
