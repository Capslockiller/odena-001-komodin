# yazan: codex
# model: gpt-6
"""Headless, metre-scale construction and geometry-only preview rendering."""
import bpy
import math
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
bpy.context.preferences.filepaths.save_version = 0
if hasattr(bpy.context.preferences.filepaths, 'save_preview_images'):
    bpy.context.preferences.filepaths.save_preview_images = False
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    bpy.data.collections.remove(collection)
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)
parts = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(parts)
scene = bpy.context.scene
scene['yazan'] = 'codex'
scene['model'] = 'gpt-6'
parts['yazan'] = 'codex'
parts['model'] = 'gpt-6'
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'
scene.unit_settings.scale_length = 1.0


def mesh_object(name, vertices, faces):
    mesh = bpy.data.meshes.new(name + ' Mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    parts.objects.link(obj)
    for face in mesh.polygons:
        face.use_smooth = True
    return obj


def bevel(obj, width, segments=4):
    mod = obj.modifiers.new('Soft edge fillets', 'BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(28)
    mod = obj.modifiers.new('Balanced face normals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    mod.weight = 40


def rounded_loop(width, depth, radius, arc_steps=12, straight_steps=12):
    # CCW polygon with sampling along both the arcs and straight edges.
    corners = [(width/2-radius, depth/2-radius, 0),
               (-width/2+radius, depth/2-radius, 90),
               (-width/2+radius, -depth/2+radius, 180),
               (width/2-radius, -depth/2+radius, 270)]
    points = []
    for i, (cx, cy, a) in enumerate(corners):
        for j in range(arc_steps):
            angle = math.radians(a + j*90/arc_steps)
            points.append((cx + radius*math.cos(angle), cy + radius*math.sin(angle)))
        angle = math.radians(a+90)
        start = (cx+radius*math.cos(angle), cy+radius*math.sin(angle))
        nx, ny, na = corners[(i+1)%4]
        end = (nx+radius*math.cos(math.radians(na)), ny+radius*math.sin(math.radians(na)))
        for j in range(straight_steps):
            t = j/straight_steps
            points.append((start[0]*(1-t)+end[0]*t, start[1]*(1-t)+end[1]*t))
    return points


def loft(name, rings, cap=True):
    n = len(rings[0])
    vertices = [p for ring in rings for p in ring]
    faces = []
    for k in range(len(rings)-1):
        for j in range(n):
            a = k*n+j
            b = k*n+(j+1)%n
            faces.append((a,b,b+n,a+n))
    if cap:
        faces += [tuple(reversed(range(n))), tuple(range((len(rings)-1)*n, len(rings)*n))]
    return mesh_object(name, vertices, faces)


def body_size(z):
    t = max(0, min(1, (z-.085)/.655))
    return .302 + .044*t + .038*math.sin(math.pi*t)


def front_y(x, z):
    w = body_size(z)
    return -w/2 - .003*(1-(2*x/w)**2)


def body_ring(z, inset=0):
    w = body_size(z)-2*inset
    ring = []
    for x,y in rounded_loop(w,w,.033-inset):
        y += math.copysign(.003*(1-(2*x/w)**2),y)
        ring.append((x,y,z))
    return ring


# A hollow carcass with 15 mm walls, integral bottom and open top under the lid.
outer = [body_ring(.085+.655*i/60) for i in range(61)]
inner = [body_ring(.74-(.74-.103)*i/60,.015) for i in range(61)]
body = loft('01 Carcass - bowed sides and tapered base', outer+inner)
bevel(body,.004,4)

# The top is a shaped solid. Its profile explicitly models a small lower chamfer
# and a large, convex upper roll; the widest ring is exactly 400 mm square.
top_profile = [(.735,.390,.039),(.739,.398,.043),(.742,.400,.044),
               (.782,.400,.044)]
for i in range(1,13):
    a = (math.pi/2)*i/12
    top_profile.append((.782+.018*math.sin(a), .364+.036*math.cos(a),
                        .026+.018*math.cos(a)))
top = loft('02 Thick overhanging top - rolled upper edge',
           [[(x,y,z) for x,y in rounded_loop(w,w,r)] for z,w,r in top_profile])
bevel(top,.0012,3)


def panel(name, low, high):
    center = (low+high)/2
    # Build a dense planar rounded outline, then warp each sampled height to
    # the carcass profile. Closed concentric face rings prevent giant warped ngons.
    outline = rounded_loop(1.0,high-low,.013,16,16)
    n = len(outline)
    vertices = []
    scales = [1.0,.8,.6,.4,.2]
    for back in [False,True]:
        for s in scales:
            for ox,oz in outline:
                z = center+oz*s
                x = ox*s*(body_size(z)-.050)
                y = front_y(x,z) - (.011 if not back else .001)
                vertices.append((x,y,z))
        vertices.append((0,front_y(0,center)-(.011 if not back else .001),center))
    stride = len(scales)*n+1
    faces = []
    for side in range(2):
        off = side*stride
        for ring in range(len(scales)-1):
            for j in range(n):
                f=(off+ring*n+j,off+ring*n+(j+1)%n,
                   off+(ring+1)*n+(j+1)%n,off+(ring+1)*n+j)
                faces.append(f if side==0 else tuple(reversed(f)))
        for j in range(n):
            f=(off+(len(scales)-1)*n+j,off+(len(scales)-1)*n+(j+1)%n,off+stride-1)
            faces.append(f if side==0 else tuple(reversed(f)))
    for j in range(n):
        faces.append((j,stride+j,stride+(j+1)%n,(j+1)%n))
    obj=mesh_object(name,vertices,faces)
    # Recalculate winding after the x/z to front-face coordinate mapping.
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    bevel(obj,.0035,4)
    return obj


panel('03 Lower door - curved soft panel',.152,.488)
panel('04 Upper drawer - curved soft panel',.496,.664)


def move_to_parts(obj,name):
    obj.name=name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    parts.objects.link(obj)
    for p in obj.data.polygons:
        p.use_smooth=True
    return obj


for label,z in [('Door',.320),('Drawer',.580)]:
    y=front_y(0,z)-.011
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.006,depth=.014,
                                       location=(0,y-.006,z),rotation=(math.pi/2,0,0))
    stem=move_to_parts(bpy.context.object, label+' knob - short stem')
    bevel(stem,.0015,3)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,
                                        location=(0,y-.017,z))
    knob=move_to_parts(bpy.context.object,label+' knob - flattened round head')
    knob.scale=(.017,.010,.017)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)


for x in [-.116,.116]:
    for y in [-.116,.116]:
        foot=loft(('Front' if y<0 else 'Rear')+(' left' if x<0 else ' right')+' short tapered foot',
                  [[(px+x,py+y,z) for px,py in rounded_loop(w,w,r,10,4)]
                   for z,w,r in [(0,.047,.013),(.008,.048,.014),(.088,.058,.018),(.103,.058,.018)]])
        bevel(foot,.005,4)

# Clear selection and save the deliverable without preview cameras or lights.
for obj in parts.objects:
    obj['yazan'] = 'codex'
    obj['model'] = 'gpt-6'
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'sonuc.blend'))

# Structural audit is computed on the evaluated geometry, including modifiers.
depsgraph=bpy.context.evaluated_depsgraph_get()
bounds=[]
audit=[]
for obj in parts.objects:
    evaluated=obj.evaluated_get(depsgraph)
    mesh=evaluated.to_mesh()
    bounds.extend([obj.matrix_world @ v.co for v in mesh.vertices])
    edge_counts={}
    for p in mesh.polygons:
        for e in p.edge_keys:
            edge_counts[e]=edge_counts.get(e,0)+1
    audit.append({'part':obj.name,'vertices':len(mesh.vertices),
                  'nonmanifold_edges':sum(c!=2 for c in edge_counts.values()),
                  'materials':len(obj.data.materials),
                  'modifiers':[m.type for m in obj.modifiers]})
    evaluated.to_mesh_clear()
dimensions=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
(ROOT/'kontrol.json').write_text(json.dumps({'yazan':'codex','model':'gpt-6',
    'dimensions_m':dimensions,'parts':audit},ensure_ascii=False,indent=2),encoding='utf-8')

scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1000
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO'
scene.display.shading.studiolight_rotate_z=math.radians(25)
scene.display.shading.color_type='SINGLE'
scene.display.shading.single_color=(.72,.72,.72)
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.1
scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.show_specular_highlight=True
scene.display.shading.background_type='WORLD'
scene.world.color=(.17,.17,.17)
camera_data=bpy.data.cameras.new('Preview camera')
camera=bpy.data.objects.new('Preview camera',camera_data)
scene.collection.objects.link(camera)
scene.camera=camera
camera_data.type='ORTHO'
camera_data.ortho_scale=1.02
for name,position in [('on_capraz',(1.15,-1.8,1.15)),
                      ('on',(0,-2,.47)),('yan',(2,0,.47))]:
    camera.location=position
    camera.rotation_euler=(Vector((0,0,.405))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(ROOT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
print('AUDIT_DIMENSIONS_METRES',dimensions)
print('AUDIT_PARTS',len(audit),'NONMANIFOLD_EDGES',sum(a['nonmanifold_edges'] for a in audit))
