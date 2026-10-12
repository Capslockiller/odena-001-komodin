# yazan: codex
# model: gpt-6.1-sol
"""Metre-scale, material-free nightstand; Blender headless entry point."""
import bpy
import math
import os
import json
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    if collection.name == 'Collection':
        bpy.data.collections.remove(collection)
parts = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(parts)
stage = bpy.data.collections.new('Preview cameras')
bpy.context.scene.collection.children.link(stage)

def mesh_object(name, vertices, faces, smooth=True):
    mesh = bpy.data.meshes.new(name + ' geometry')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    parts.objects.link(obj)
    for p in mesh.polygons:
        p.use_smooth = smooth
    return obj

def outline(hx, hy, r, arc=12, straight=8):
    points = []
    for i in range(4):
        angle = i * math.pi / 2
        cx = (hx-r) * (1 if i in (0, 3) else -1)
        cy = (hy-r) * (1 if i in (0, 1) else -1)
        # Start at right edge of top-right corner; walk counterclockwise.
        for j in range(arc):
            a = angle + j / arc * math.pi / 2
            points.append((cx+r*math.cos(a), cy+r*math.sin(a)))
        a = angle + math.pi / 2
        end = (cx+r*math.cos(a), cy+r*math.sin(a))
        ni = (i+1) % 4
        ncx = (hx-r) * (1 if ni in (0, 3) else -1)
        ncy = (hy-r) * (1 if ni in (0, 1) else -1)
        target = (ncx+r*math.cos(a), ncy+r*math.sin(a))
        for j in range(straight):
            t = j / straight
            points.append((end[0]*(1-t)+target[0]*t, end[1]*(1-t)+target[1]*t))
    return points

def loft(name, rings):
    verts = []
    for z, hx, hy, r in rings:
        verts.extend((x,y,z) for x,y in outline(hx,hy,r))
    n = len(outline(*rings[0][1:]))
    faces = [tuple(reversed(range(n)))]
    for k in range(len(rings)-1):
        for j in range(n):
            a=k*n+j; b=k*n+(j+1)%n
            faces.append((a,b,b+n,a+n))
    faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    obj = mesh_object(name,verts,faces)
    obj.data.polygons[0].use_smooth=False
    obj.data.polygons[-1].use_smooth=False
    return obj

def halfwidth(z):
    # Smooth bowed sides with a pronounced lower taper.
    t = max(0,min(1,(z-.104)/.646))
    if t <= .5:
        return .146 + .038 * math.sin(math.pi * t)
    return .184 - .014 * (1-math.cos(2*math.pi*(t-.5))) / 2

body_rings=[]
for z,inset in [(.100,.004),(.1006,.002),(.102,.0006)]:
    h=halfwidth(z)-inset
    body_rings.append((z,h,h,.033))
for i in range(49):
    z=.104+(.642*i/48)
    h=halfwidth(z)
    body_rings.append((z,h,h,.036))
body_rings += [(.748,halfwidth(.748)-.0006,halfwidth(.748)-.0006,.036),
               (.75,halfwidth(.75)-.003,halfwidth(.75)-.003,.034)]
body=loft('01 Bowed cabinet body',body_rings)
body['construction']='Rounded square sections; continuous lower taper and mid-height bow'

# Thick top: small lower chamfer, broad rounded upper edge.
top_rings=[(.75,.195,.195,.034),(.754,.2,.2,.039),(.784,.2,.2,.039)]
for i in range(1,13):
    a=i/12*math.pi/2
    h=.184+.016*math.cos(a)
    top_rings.append((.784+.016*math.sin(a),h,h,.023+.016*math.cos(a)))
top=loft('02 Thick rounded overhanging top',top_rings)

def body_front(x,z):
    h=halfwidth(z); r=.036
    d=max(0,abs(x)-(h-r))
    return -h+r-math.sqrt(max(0,r*r-d*d))

def panel(name,zlo,zhi):
    zc=(zlo+zhi)/2; hz=(zhi-zlo)/2
    hw=halfwidth(zc)-.019
    base=outline(hw,hz,.013)
    n=len(base); verts=[]; faces=[]
    # Back edge, rounded perimeter, and dense concentric front surface rings.
    settings=[(1,.001),(1,.004),(.994,.0065),(.981,.0085)]
    settings += [(s,.009) for s in [.95,.88,.80,.72,.64,.56,.48,.40,.32,.24,.16,.08]]
    for scale,depth in settings:
        for x,dz in base:
            z=zc+dz*scale
            x=x*scale*(halfwidth(z)-.019)/hw
            verts.append((x,body_front(x,z)-depth,z))
    for k in range(len(settings)-1):
        for j in range(n):
            a=k*n+j; b=k*n+(j+1)%n
            faces.append((a,a+n,b+n,b))
    center=len(verts); verts.append((0,body_front(0,zc)-.009,zc))
    for j in range(n):
        faces.append(((len(settings)-1)*n+j,center,(len(settings)-1)*n+(j+1)%n))
    # Back follows the same bow; concentric rings give a closed manifold panel.
    back_start=len(verts)
    for scale in [.9,.7,.5,.3,.1]:
        for x,dz in base:
            z=zc+dz*scale; x=x*scale*(halfwidth(z)-.019)/hw
            verts.append((x,body_front(x,z)-.001,z))
    previous=0
    for k in range(5):
        cur=back_start+k*n
        for j in range(n):
            faces.append((previous+j,previous+(j+1)%n,cur+(j+1)%n,cur+j))
        previous=cur
    center=len(verts); verts.append((0,body_front(0,zc)-.001,zc))
    for j in range(n):
        faces.append((previous+j,previous+(j+1)%n,center))
    obj=mesh_object(name,verts,faces)
    obj['height_m']=zhi-zlo
    return zc

drawer_z=panel('03 Shallow drawer front',.551,.736)
door_z=panel('04 Lower door front',.174,.544)

def relocate(obj,name):
    obj.name=name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    parts.objects.link(obj)
    for face in obj.data.polygons: face.use_smooth=True

for label,z in [('Drawer',drawer_z),('Door',door_z)]:
    y=body_front(0,z)-.009
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.007,depth=.012,
        location=(0,y-.006,z),rotation=(math.pi/2,0,0))
    stem=bpy.context.object; relocate(stem,label+' knob short stem')
    bevel=stem.modifiers.new('Soft stem rims','BEVEL'); bevel.width=.0015; bevel.segments=3
    normal=stem.modifiers.new('Stem normals','WEIGHTED_NORMAL')
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(0,y-.016,z))
    knob=bpy.context.object; relocate(knob,label+' flattened round knob')
    knob.scale=(.018,.010,.018)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

for label,x,y in [('FL',-.104,-.104),('FR',.104,-.104),('BL',-.104,.104),('BR',.104,.104)]:
    foot=loft('Foot '+label,[(0,.020,.020,.006),(.002,.023,.023,.008),
        (.006,.024,.024,.009),(.101,.030,.030,.011),(.112,.028,.028,.010)])
    foot.location.x=x; foot.location.y=y
    bevel=foot.modifiers.new('Rounded foot ends','BEVEL'); bevel.width=.002; bevel.segments=3
    bevel.limit_method='ANGLE'
    normal=foot.modifiers.new('Foot normals','WEIGHTED_NORMAL'); normal.keep_sharp=True

scene=bpy.context.scene
scene['yazan']='codex'
scene['model']='gpt-6.1-sol'
scene['source']='tarif.md: verbal brief only'
scene.unit_settings.system='METRIC'; scene.unit_settings.length_unit='METERS'
scene.unit_settings.scale_length=1
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1000; scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.use_stamp_note=True
scene.render.stamp_note_text='yazan: codex | model: gpt-6.1-sol'
display=scene.display.shading
display.light='STUDIO'; display.studiolight_rotate_z=.3
display.color_type='SINGLE'; display.single_color=(.72,.72,.72)
display.show_shadows=True; display.show_cavity=True
display.cavity_type='BOTH'; display.curvature_ridge_factor=1.3
display.curvature_valley_factor=1.1
display.background_type='WORLD'
scene.world.color=(.18,.18,.18)
scene.view_settings.view_transform='Standard'

def camera(name,pos,scale):
    data=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,data)
    stage.objects.link(obj); obj.location=pos
    obj.rotation_euler=(Vector((0,0,.40))-obj.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO'; data.ortho_scale=scale
    return obj

cam=camera('Three quarter inspection',(1.15,-1.6,1.08),1.04)
front=camera('Front inspection',(0,-2,.42),.98)
side=camera('Side inspection',(2,0,.42),.98)
scene.camera=cam
bpy.context.preferences.filepaths.save_version=0
bpy.context.preferences.filepaths.file_preview_type='NONE'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'sonuc.blend'))
for camera_obj,filename in [(cam,'onizleme_capraz.png'),(front,'onizleme_on.png'),(side,'onizleme_yan.png')]:
    scene.camera=camera_obj
    scene.render.filepath=os.path.join(ROOT,filename)
    bpy.ops.render.render(write_still=True)
scene.camera=cam
# Save exactly once to avoid creating a backup deliverable.
depsgraph=bpy.context.evaluated_depsgraph_get()
audit={'yazan':'codex','model':'gpt-6.1-sol','parts':[]}
for obj in parts.objects:
    evaluated=obj.evaluated_get(depsgraph)
    mesh=evaluated.to_mesh()
    coords=[obj.matrix_world@v.co for v in mesh.vertices]
    edge_use={}
    for poly in mesh.polygons:
        for edge in poly.edge_keys: edge_use[tuple(sorted(edge))]=edge_use.get(tuple(sorted(edge)),0)+1
    audit['parts'].append({'name':obj.name,'modifiers':[m.type for m in obj.modifiers],
        'materials':len(obj.data.materials),'nonmanifold_edges':sum(v!=2 for v in edge_use.values()),
        'bounds_min':[min(v[i] for v in coords) for i in range(3)],
        'bounds_max':[max(v[i] for v in coords) for i in range(3)]})
    evaluated.to_mesh_clear()
with open(os.path.join(ROOT,'kontrol.json'),'w',encoding='utf-8') as f:
    json.dump(audit,f,ensure_ascii=False,indent=2)
print('AUDIT: parts=',len(audit['parts']),'materials=',sum(p['materials'] for p in audit['parts']),
      'nonmanifold=',sum(p['nonmanifold_edges'] for p in audit['parts']))
