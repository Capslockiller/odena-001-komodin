# yazan: codex
# model: gpt-6
"""Metre units; geometry only. Run with Blender in background mode."""
import bpy
import math
import json
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection':
        bpy.data.collections.remove(c)
parts = bpy.data.collections.get('Collection')
parts.name = "Molly's Nightstand"
studio = bpy.data.collections.new('Preview Studio')
bpy.context.scene.collection.children.link(studio)

def mesh(name, verts, faces):
    data = bpy.data.meshes.new(name + ' Mesh')
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    parts.objects.link(obj)
    for f in data.polygons:
        f.use_smooth = True
    return obj

def bevel(obj, width, segments=4):
    m = obj.modifiers.new('Soft crafted edges', 'BEVEL')
    m.width = width
    m.segments = segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(35)
    m = obj.modifiers.new('Area weighted normals', 'WEIGHTED_NORMAL')
    m.keep_sharp = True
    m.weight = 40

def rr(half, radius, n=12):
    # Begins at front-right tangent; traverses sides/back to front-left.
    pts = []
    for cx, cy, start in [(half-radius,-half+radius,-90),
                           (half-radius,half-radius,0),
                           (-half+radius,half-radius,90),
                           (-half+radius,-half+radius,180)]:
        for j in range(n+1):
            a = math.radians(start + 90*j/n)
            pts.append((cx + radius*math.cos(a),cy + radius*math.sin(a)))
    return pts

def loft(name, rings, closed=True, caps=True):
    verts = [v for ring in rings for v in ring]
    n = len(rings[0])
    faces = []
    for k in range(len(rings)-1):
        for j in range(n if closed else n-1):
            jj = (j+1)%n
            faces.append((k*n+j,k*n+jj,(k+1)*n+jj,(k+1)*n+j))
    if caps:
        faces += [tuple(reversed(range(n))),tuple((len(rings)-1)*n+j for j in range(n))]
    return mesh(name,verts,faces)

def half(z):
    t = (z-.105)/.645
    # Pronounced lower taper; soft belly above the middle.
    return .148 + .029*t + .020*math.sin(math.pi*t)

def u_ring(z):
    outer = rr(half(z),.032)
    inner = rr(half(z)-.016,.016)
    return [(x,y,z) for x,y in outer + list(reversed(inner))]

body = loft('Carcass - curved sides and back', [u_ring(.105+.645*i/64) for i in range(65)])
bevel(body,.0025,3)

def slab(name,z0,z1):
    obj = loft(name,[[(x,y,z) for x,y in rr(half(z),.032)] for z in [z0,(z0+z1)/2,z1]])
    bevel(obj,.003,3)
    return obj

slab('Bottom plinth and cabinet floor',.105,.143)
slab('Upper carcass rail',.724,.750)

def panel(name, z0,z1):
    verts=[]
    rows=24
    cols=16
    for back in [False,True]:
        for iz in range(rows+1):
            z=z0+(z1-z0)*iz/rows
            w=half(z)-.023
            for ix in range(cols+1):
                u=-1+2*ix/cols
                # Broad shallow transverse bow; exact body bow vertically.
                verts.append((u*w,-half(z)-.010+.005*u*u+(.019 if back else 0),z))
    N=(rows+1)*(cols+1)
    faces=[]
    for iz in range(rows):
        for ix in range(cols):
            a=iz*(cols+1)+ix
            faces.append((a,a+1,a+cols+2,a+cols+1))
            faces.append((a+N+cols+1,a+N+cols+2,a+N+1,a+N))
    border=list(range(cols+1))
    border += [iz*(cols+1)+cols for iz in range(1,rows+1)]
    border += [rows*(cols+1)+ix for ix in range(cols-1,-1,-1)]
    border += [iz*(cols+1) for iz in range(rows-1,0,-1)]
    for j,a in enumerate(border):
        b=border[(j+1)%len(border)]
        faces.append((a,a+N,b+N,b))
    obj=mesh(name,verts,faces)
    bevel(obj,.004,5)
    obj.modifiers[0].use_clamp_overlap=True
    return obj

panel('Lower door - bowed panel',.150,.526)
panel('Upper drawer - bowed front',.534,.722)

# Top profile: 4 mm lower chamfer, full rounded upper lip, flat usable top.
profiles=[(.750,.195,.032),(.754,.200,.037),(.782,.200,.037)]
for i in range(1,13):
    a=math.pi*.5*i/12
    profiles.append((.782+.018*math.sin(a),.182+.018*math.cos(a),.019+.018*math.cos(a)))
top=loft('Overhanging top - rolled upper edge and lower chamfer',
         [[(x,y,z) for x,y in rr(h,r,16)] for z,h,r in profiles])
norm=top.modifiers.new('Area weighted normals','WEIGHTED_NORMAL')
norm.keep_sharp=True

for xside in [-1,1]:
    for yside in [-1,1]:
        rings=[]
        for z,h,r in [(0,.022,.010),(.004,.025,.012),(.099,.032,.014),(.114,.032,.014)]:
            t=z/.114
            # Very slight outward stance, broad rounded square feet.
            cx=xside*(.111+.004*(1-t))
            cy=yside*(.111+.004*(1-t))
            rings.append([(x+cx,y+cy,z) for x,y in rr(h,r)])
        obj=loft(('Front' if yside<0 else 'Rear')+(' left' if xside<0 else ' right')+' tapered foot',rings)
        bevel(obj,.0025,3)

def to_parts(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    parts.objects.link(obj)

for label,z in [('Door',.338),('Drawer',.628)]:
    surf=-half(z)-.010
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.009,depth=.014,
                                      location=(0,surf-.004,z),rotation=(math.pi/2,0,0))
    stem=bpy.context.object
    stem.name=label+' knob - short stem'
    to_parts(stem)
    for p in stem.data.polygons:p.use_smooth=True
    bevel(stem,.002,3)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(0,surf-.015,z))
    knob=bpy.context.object
    knob.name=label+' knob - flattened round grip'
    knob.scale=(.020,.012,.020)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    to_parts(knob)
    for p in knob.data.polygons:p.use_smooth=True

scene=bpy.context.scene
scene['yazan']='codex'
scene['model']='gpt-6'
scene.unit_settings.system='METRIC'
scene.unit_settings.length_unit='METERS'
scene.unit_settings.scale_length=1
bpy.context.preferences.filepaths.save_version=0
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=900
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.world.color=(.25,.25,.25)
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False

def studio_obj(obj):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    studio.objects.link(obj)

def aim(obj,pt):
    obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()

bpy.ops.object.camera_add(location=(1.12,-1.7,1.15))
cam=bpy.context.object
cam.name='Preview camera'
studio_obj(cam)
cam.data.type='ORTHO'
cam.data.ortho_scale=1.03
scene.camera=cam
aim(cam,(0,0,.405))
for name,loc,power,size in [('Large key',(-1,-1.4,2),110,1.4),('Fill',(1.3,-.4,1.1),55,1),('Rim',(0,1.4,1.6),95,1.1)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=bpy.context.object
    light.name=name
    light.data.energy=power
    light.data.shape='DISK'
    light.data.size=size
    aim(light,(0,0,.4))
    studio_obj(light)

# Ground is preview-only; no auxiliary mesh is left in the delivered asset.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001))
ground=bpy.context.object
ground.name='Temporary preview ground'
studio_obj(ground)
for name,loc in [('onizleme-perspektif',(1.12,-1.7,1.15)),('onizleme-on',(0,-2,.43)),('onizleme-arka',(-1.15,1.65,1.0))]:
    cam.location=loc
    aim(cam,(0,0,.40))
    scene.render.filepath=str(ROOT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(ground,do_unlink=True)
cam.location=(1.12,-1.7,1.15)
aim(cam,(0,0,.405))

# Deliver an easy-to-inspect viewport with the furniture selected.
bpy.ops.object.select_all(action='DESELECT')
for o in parts.objects:o.select_set(True)
bpy.context.view_layer.objects.active=body
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=1.45
            area.spaces.active.region_3d.view_location=(0,0,.4)

deps=bpy.context.evaluated_depsgraph_get()
coords=[]
validation=[]
import bmesh
for obj in parts.objects:
    ev=obj.evaluated_get(deps)
    coords.extend([obj.matrix_world@Vector(v) for v in ev.bound_box])
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    validation.append({'part':obj.name,'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
                       'materials':len(obj.data.materials),'modifiers':[m.type for m in obj.modifiers]})
    bm.free()
size=[max(v[i] for v in coords)-min(v[i] for v in coords) for i in range(3)]
report={'yazan':'codex','model':'gpt-6','dimensions_m':size,'parts':validation}
(ROOT/'kontrol.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(x['non_manifold_edges']==0 and x['materials']==0 for x in validation)
assert len(parts.objects)==14
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'sonuc.blend'))
print('COMPLETE',json.dumps(report))
