# yazan: codex
# model: gpt-6-astra
import bpy, math, os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
parts = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(parts)
stage = bpy.data.collections.new('Preview cameras')
bpy.context.scene.collection.children.link(stage)

def mesh_obj(name, verts, faces):
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    parts.objects.link(obj)
    for p in mesh.polygons:
        p.use_smooth = len(p.vertices) == 4
    return obj

def rounded_rect(hx, hy, r, n=12):
    pts=[]
    for cx,cy,start in [(hx-r,hy-r,0),(-hx+r,hy-r,90),(-hx+r,-hy+r,180),(hx-r,-hy+r,270)]:
        for i in range(n+1):
            a=math.radians(start+i*90/n)
            pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return pts

def loft(name, rings):
    n=len(rings[0]); verts=[v for ring in rings for v in ring]
    faces=[tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        for i in range(n):
            a=j*n+i; b=j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    return mesh_obj(name,verts,faces)

def bevel(obj, width):
    mod=obj.modifiers.new('Soft edge finishing','BEVEL')
    mod.width=width; mod.segments=4
    mod.limit_method='ANGLE'
    mod=obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    mod.keep_sharp=True; mod.weight=30

def halfwidth(z):
    t=max(0,min(1,(z-.12)/.625))
    return .146 + .036*math.sin(math.pi*.70*t) + .001*t

rings=[]
for i in range(65):
    z=.12+.625*i/64
    h=halfwidth(z)
    rings.append([(x,y,z) for x,y in rounded_rect(h,h,.033)])
body=loft('Cabinet - bowed tapered body',rings)
bevel(body,.004)

profile=[(.738,.188,.035),(.741,.191,.038),(.749,.198,.044),(.756,.2,.046),(.771,.2,.046),(.781,.1985,.045),(.790,.195,.042),(.796,.190,.039),(.800,.183,.034)]
top=loft('Top - full rounded lip and lower chamfer', [[(x,y,z) for x,y in rounded_rect(h,h,r)] for z,h,r in profile])

def panel(name,zmin,zmax):
    nx, nz = 32, 96
    verts=[]
    for depth in [.002,.014]:
        for j in range(nz+1):
            z=zmin+(zmax-zmin)*j/nz
            edge=min(z-zmin,zmax-z)
            r=.014
            inset=r-math.sqrt(max(0,r*r-(r-min(r,edge))**2))
            w=halfwidth(z)-.023-inset
            for i in range(nx+1):
                x=w*(2*i/nx-1)
                y=-halfwidth(z)-depth-.002*(1-(x/(halfwidth(z)-.023))**2)
                verts.append((x,y,z))
    faces=[]; stride=nx+1; sheet=stride*(nz+1)
    for layer in range(2):
        for j in range(nz):
            for i in range(nx):
                a=layer*sheet+j*stride+i
                faces.append((a,a+1,a+1+stride,a+stride))
    perimeter=list(range(nx+1))
    perimeter += [j*stride+nx for j in range(1,nz+1)]
    perimeter += [nz*stride+i for i in range(nx-1,-1,-1)]
    perimeter += [j*stride for j in range(nz-1,0,-1)]
    for k,a in enumerate(perimeter):
        b=perimeter[(k+1)%len(perimeter)]
        faces.append((a,b,b+sheet,a+sheet))
    obj=mesh_obj(name,verts,faces)
    import bmesh
    bm=bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data); bm.free()
    mod=obj.modifiers.new('Soft continuous panel surface','SUBSURF')
    mod.subdivision_type='CATMULL_CLARK'; mod.levels=2; mod.render_levels=2
    return obj

panel('Lower door - curved soft panel',.168,.529)
panel('Upper drawer - curved soft panel',.540,.720)

for sx in [-1,1]:
    for sy in [-1,1]:
        rings=[]
        for z,h in [(0,.023),(.004,.026),(.018,.027),(.13,.032),(.145,.032)]:
            cx=sx*(.125+.004*(1-z/.145)); cy=sy*(.125+.004*(1-z/.145))
            rings.append([(x+cx,y+cy,z) for x,y in rounded_rect(h,h,.011)])
        obj=loft(('Left' if sx<0 else 'Right')+' '+('front' if sy<0 else 'rear')+' tapered foot',rings)
        bevel(obj,.002)

def move_to_parts(obj,name):
    obj.name=name
    for col in list(obj.users_collection): col.objects.unlink(obj)
    parts.objects.link(obj)
    for p in obj.data.polygons: p.use_smooth=True

for label,z in [('Drawer',.63),('Door',(.168+.529)/2)]:
    front=-halfwidth(z)-.019
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.007,depth=.013,location=(0,front-.005,z),rotation=(math.pi/2,0,0))
    obj=bpy.context.object; move_to_parts(obj,label+' knob - short stem'); bevel(obj,.0015)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(0,front-.016,z))
    obj=bpy.context.object; move_to_parts(obj,label+' knob - flattened round grip')
    obj.scale=(.016,.010,.016)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.length_unit='METERS'
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1000; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.world.color=(.25,.25,.25)
shade=scene.display.shading
shade.light='STUDIO'; shade.studiolight_rotate_z=.4
shade.color_type='SINGLE'; shade.single_color=(.72,.72,.72)
shade.show_shadows=True; shade.show_cavity=True
shade.cavity_type='BOTH'; shade.curvature_ridge_factor=1.3; shade.curvature_valley_factor=1.1
shade.show_specular_highlight=True
shade.background_type='WORLD'
scene.render.image_settings.file_format='PNG'

def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data); stage.objects.link(obj)
    obj.location=loc; obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'; data.ortho_scale=scale
    return obj

cam=camera('Three-quarter inspection',(1.35,-2,1.15),(0,0,.40),1.02)
front=camera('Front inspection',(0,-2,.40),(0,0,.40),.98)
scene.camera=cam
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True); bpy.context.view_layer.objects.active=body
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'sonuc.blend'))
for c,filename in [(cam,'preview-perspective.png'),(front,'preview-front.png')]:
    scene.camera=c; scene.render.filepath=os.path.join(ROOT,filename)
    bpy.ops.render.render(write_still=True)

# Exact geometry diagnostics, independent of rendered appearance.
deps=bpy.context.evaluated_depsgraph_get()
coords=[]
for obj in parts.objects:
    evaluated=obj.evaluated_get(deps)
    coords.extend([evaluated.matrix_world@Vector(c) for c in evaluated.bound_box])
mins=[min(v[i] for v in coords) for i in range(3)]
maxs=[max(v[i] for v in coords) for i in range(3)]
print('MODEL_AUDIT', {'parts':len(parts.objects),'dimensions_m':[maxs[i]-mins[i] for i in range(3)],'materials':sum(len(o.data.materials) for o in parts.objects),'collection':parts.name})
