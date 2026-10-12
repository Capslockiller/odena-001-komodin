# yazan: codex
# model: gpt-6-astra
"""Metre units, geometry only. Run using Blender in background mode."""
import bpy
import math
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name == 'Collection':
        bpy.data.collections.remove(c)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
col = bpy.data.collections.new("Molly's Nightstand")
scene.collection.children.link(col)

def move(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    obj['yazan'] = 'codex'
    obj['model'] = 'gpt-6-astra'
    return obj

def mesh_object(name, vertices, faces, subdiv=0):
    mesh = bpy.data.meshes.new(name + '_Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    obj['yazan'] = 'codex'
    obj['model'] = 'gpt-6-astra'
    for p in mesh.polygons:
        p.use_smooth = True
    if subdiv:
        mod = obj.modifiers.new('Yumusak yuzey', 'SUBSURF')
        mod.levels = subdiv
        mod.render_levels = subdiv
    return obj

def rounded_rect(w, h, r, samples=16):
    points = []
    corners = [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),
               (-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]
    for index,(cx,cy,start) in enumerate(corners):
        for i in range(samples):
            a = math.radians(start + 90*i/samples)
            points.append((cx+r*math.cos(a), cy+r*math.sin(a)))
        a = math.radians(start+90)
        end = (cx+r*math.cos(a),cy+r*math.sin(a))
        nx,ny,angle = corners[(index+1)%4]
        a = math.radians(angle)
        nxt = (nx+r*math.cos(a),ny+r*math.sin(a))
        for i in range(20):
            f=i/20
            points.append((end[0]*(1-f)+nxt[0]*f,end[1]*(1-f)+nxt[1]*f))
    return points

def loft(name, rings, subdiv=2):
    n = len(rings[0])
    verts = [p for ring in rings for p in ring]
    faces = [tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        for i in range(n):
            k = (i+1) % n
            faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
    faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    return mesh_object(name, verts, faces, subdiv)

def halfwidth(z):
    t = min(1, max(0, (z-.115)/.635))
    return (.278 + .072*math.sin(t*math.pi*.75) + .003*t)/2

def front(x, z):
    a = halfwidth(z)
    return -a * max(.00001, 1-(abs(x)/a)**6)**(1/6)

# Continuous superellipse cross sections: gently curved sides and rounded corners.
rings = []
zs = [.115,.117,.122] + [.13+i*.02 for i in range(31)] + [.742,.748,.75]
for z in sorted(set(zs)):
    a = halfwidth(z)
    # Soft lower and upper rim; these supports keep the cabinet volume legible.
    inset = .003 if z in (.115,.75) else 0
    ring = []
    for i in range(96):
        t = 2*math.pi*i/96
        x = (a-inset)*math.copysign(abs(math.cos(t))**(1/3), math.cos(t))
        y = (a-inset)*math.copysign(abs(math.sin(t))**(1/3), math.sin(t))
        ring.append((x,y,z))
    rings.append(ring)
body = loft('01_Govde_bombeli', rings, 2)

# Asymmetric slab profile: small chamfer below, broad rolled upper edge.
profile = [(.747,.378,.042),(.749,.382,.043),(.755,.396,.049),
           (.758,.400,.051),(.778,.400,.051),(.785,.398,.050),
           (.792,.391,.047),(.797,.381,.043),(.799,.369,.039),
           (.800,.357,.035),(.800,.345,.031)]
top = loft('02_Tabla_dolgun_ust_hafif_pah_alti',
           [[(x,y,z) for x,y in rounded_rect(w,w,r)] for z,w,r in profile], 2)

def panel(name, low, high):
    center = (low+high)/2
    height = high-low
    width = .288
    r = .018
    bevel = .005
    depth = .016
    # Rings cover front/back faces as well as their rolled perimeter, avoiding
    # large nonplanar ngons on the visible curved surface.
    sections = []
    for f in [.04,.15,.3,.5,.7,.85,1]:
        sections.append(((width-2*bevel)*f,(height-2*bevel)*f,(r-bevel)*f,-.002))
    for i in range(1,7):
        t = math.pi/2*i/6
        s = bevel*(1-math.cos(t))
        sections.append((width-2*bevel+2*s,height-2*bevel+2*s,r-bevel+s,
                         -.002+bevel*math.sin(t)))
    sections.append((width,height,r,depth-bevel))
    for i in range(1,7):
        t = math.pi/2*i/6
        s = bevel*(1-math.cos(t))
        sections.append((width-2*s,height-2*s,r-s,depth-bevel+bevel*math.sin(t)))
    for f in [.85,.7,.5,.3,.15,.04]:
        sections.append(((width-2*bevel)*f,(height-2*bevel)*f,(r-bevel)*f,depth))
    rings = []
    for w,h,rad,offset in sections:
        ring=[]
        for u,v in rounded_rect(w,h,rad):
            z = center+v
            x = u*halfwidth(z)/.175
            ring.append((x,front(x,z)-offset,z))
        rings.append(ring)
    obj = loft(name,rings,1)
    obj['construction'] = 'Closed curved relief panel; integrated edge rounding'
    return center

door_z = panel('03_Alt_kapak',.192,.534)
drawer_z = panel('04_Ust_cekmece',.545,.716)

for idx,z in enumerate([door_z,drawer_z],1):
    surface = front(0,z)-.016
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=.0065, depth=.009,
                                      location=(0,surface-.0025,z), rotation=(math.pi/2,0,0))
    stem = move(bpy.context.object)
    stem.name = f'05_{idx}_Kulp_kisa_mil'
    bevel = stem.modifiers.new('Mil kenar yumusatma','BEVEL')
    bevel.width=.0015
    bevel.segments=3
    for p in stem.data.polygons: p.use_smooth=True
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24,
                                       location=(0,surface-.013,z))
    knob=move(bpy.context.object)
    knob.name=f'06_{idx}_Basik_yuvarlak_topuz'
    knob.scale=(.015,.010,.015)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in knob.data.polygons: p.use_smooth=True

for i,(x,y) in enumerate([(-.112,-.112),(.112,-.112),(-.112,.112),(.112,.112)],1):
    foot_rings=[]
    for z,w,r in [(0,.039,.011),(.003,.045,.013),(.008,.046,.014),
                  (.105,.058,.016),(.128,.060,.017),(.132,.056,.015)]:
        foot_rings.append([(u+x,v+y,z) for u,v in rounded_rect(w,w,r,10)])
    loft(f'07_{i}_Kisa_kalin_ayak',foot_rings,2)

# Technical checks on evaluated meshes; render cameras are also in the collection.
depsgraph=bpy.context.evaluated_depsgraph_get()
geo=[o for o in col.objects if o.type=='MESH']
allpts=[o.matrix_world @ v.co for o in geo for v in o.evaluated_get(depsgraph).data.vertices]
bounds={axis: [min(p[i] for p in allpts),max(p[i] for p in allpts)] for i,axis in enumerate('xyz')}
checks={'yazan':'codex','model':'gpt-6-astra','mesh_parts':len(geo),
        'bounds_m':bounds,'dimensions_m':{a:b[1]-b[0] for a,b in bounds.items()},
        'material_slots':sum(len(o.data.materials) for o in geo),
        'panel_height_ratio':.342/.171,
        'parts':{o.name:[m.type for m in o.modifiers] for o in geo}}
assert len(geo)==12
assert checks['material_slots']==0
assert all(o.users_collection[0]==col for o in geo)
(ROOT/'kontrol.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')

scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1000
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
sh=scene.display.shading
sh.light='STUDIO'
sh.studiolight_rotate_z=.35
sh.color_type='SINGLE'
sh.show_shadows=True
sh.show_cavity=True
sh.cavity_type='BOTH'
sh.curvature_ridge_factor=1.3
sh.curvature_valley_factor=1.0
sh.show_specular_highlight=True
sh.background_type='WORLD'
scene.world.color=(.16,.16,.16)
scene.render.film_transparent=False

def camera(name, location, ortho):
    data=bpy.data.cameras.new(name)
    obj=bpy.data.objects.new(name,data)
    col.objects.link(obj)
    obj['yazan']='codex'
    obj['model']='gpt-6-astra'
    obj.location=location
    obj.rotation_euler=(Vector((0,0,.4))-obj.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'
    data.ortho_scale=ortho
    return obj

cam3=camera('Kontrol_Capraz',(1.15,-1.7,1.10),1.05)
camf=camera('Kontrol_On',(0,-2,.4),.97)
cams=camera('Kontrol_Yan',(2,0,.4),.97)
for cam,filename in [(cam3,'onizleme_capraz.png'),(camf,'onizleme_on.png'),(cams,'onizleme_yan.png')]:
    scene.camera=cam
    scene.render.filepath=str(ROOT/filename)
    if '--skip-render' not in sys.argv:
        bpy.ops.render.render(write_still=True)
scene.camera=cam3
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True)
bpy.context.view_layer.objects.active=body
scene['yazan']='codex'
scene['model']='gpt-6-astra'
scene['brief']='tarif.md; verbal-only interpretation, metres, geometry only'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'sonuc.blend'))
print('CHECKS',json.dumps(checks,ensure_ascii=False))
