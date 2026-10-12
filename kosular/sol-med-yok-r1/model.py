# yazan: codex · gpt-6
import bpy
import math
import bmesh
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
collection = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(collection)

def adopt(obj, name):
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def mesh_obj(name, vertices, faces):
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for face in mesh.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj

def bevel(obj, width):
    mod = obj.modifiers.new('Soft edge finishing', 'BEVEL')
    mod.width = width
    mod.segments = 3
    mod = obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    mod.weight = 30

def outline(hx, hy, r, samples=12):
    points = []
    for cx, cy, angle in [(hx-r, hy-r, 0), (-hx+r, hy-r, 90),
                           (-hx+r, -hy+r, 180), (hx-r, -hy+r, 270)]:
        for j in range(samples + 1):
            a = math.radians(angle + 90*j/samples)
            points.append((cx+r*math.cos(a), cy+r*math.sin(a)))
    # Add straight-span samples so the front curvature has real geometry.
    result = []
    for i, p in enumerate(points):
        result.append(p)
        q = points[(i+1) % len(points)]
        if (i+1) % (samples+1) == 0:
            for j in range(1, 13):
                result.append((p[0]+(q[0]-p[0])*j/13,
                               p[1]+(q[1]-p[1])*j/13))
    return result

def loft(name, rings, front_bulge=False):
    verts = []
    for z, hx, hy, radius in rings:
        for x, y in outline(hx, hy, radius):
            if front_bulge:
                # A restrained convex face, symmetric on the back.
                y += math.copysign(.006*(x/hx)**2, -y) * (abs(y)/hy)**8
            verts.append((x, y, z))
    n = len(verts)//len(rings)
    assert all(len(outline(hx,hy,r)) == n for _,hx,hy,r in rings)
    faces = [tuple(reversed(range(n)))]
    for k in range(len(rings)-1):
        for i in range(n):
            j=(i+1)%n
            faces.append((k*n+i, k*n+j, (k+1)*n+j, (k+1)*n+i))
    faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
    return mesh_obj(name, verts, faces)

def halfwidth(z):
    t = max(0, min(1, (z-.105)/.632))
    return .145 + .027*t + .022*math.sin(math.pi*t)

body_rings = []
for i in range(49):
    z = .105 + .632*i/48
    h = halfwidth(z)
    body_rings.append((z,h,h,.031))
body=loft('01 Cabinet - gently bowed tapered body',body_rings,True)
bevel(body,.0025)

# Thick top: small chamfer below, generous rolled edge above.
top_rings = [(.731,.187,.187,.036),(.737,.196,.196,.038),
             (.742,.200,.200,.040),(.779,.200,.200,.040)]
for i in range(1,13):
    a=(math.pi/2)*i/12
    h=.179+.021*math.cos(a)
    top_rings.append((.779+.021*math.sin(a),h,h,.040))
top=loft('02 Overhanging thick top - rolled upper edge',top_rings)

def panel(name, zlow, zhigh):
    center=(zlow+zhigh)/2
    hh=(zhigh-zlow)/2
    # The outline is mapped onto the cabinet's bowed front, including its taper.
    boundary=outline(1,1,.13,16)
    n=len(boundary)
    vertices=[]
    # Rear perimeter -> edge crown -> front perimeter -> concentric face rings.
    rings=[(1,.001),(1,.006),(.990,.011),(.974,.014),
           (.94,.0155),(.80,.0155),(.60,.0155),(.40,.0155),(.20,.0155)]
    def coord(u,v,depth):
        z=center+v*hh
        x=u*(halfwidth(z)-.022)
        y=-halfwidth(z)+.006*(x/halfwidth(z))**2-depth
        return x,y,z
    for scale,depth in rings:
        for u,v in boundary:
            vertices.append(coord(u*scale,v*scale,depth))
    # Viewed from the front, the x/z outline needs reversed winding.
    faces=[tuple(range(n))]
    for k in range(len(rings)-1):
        for i in range(n):
            j=(i+1)%n
            faces.append((k*n+j,k*n+i,(k+1)*n+i,(k+1)*n+j))
    ci=len(vertices)
    vertices.append(coord(0,0,.0155))
    for i in range(n):
        faces.append(((len(rings)-1)*n+(i+1)%n,
                      (len(rings)-1)*n+i,ci))
    obj=mesh_obj(name,vertices,faces)
    for p in obj.data.polygons:
        p.use_smooth=True
    return obj,center

door, door_z=panel('03 Lower door - curved soft panel',.178,.522)
drawer, drawer_z=panel('04 Upper drawer - curved soft panel',.534,.706)

for label,z in [('Door',door_z),('Drawer',drawer_z)]:
    surface=-halfwidth(z)-.0155
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.008,depth=.018,
        location=(0,surface-.008,z),rotation=(math.pi/2,0,0))
    stem=adopt(bpy.context.object,label+' knob - short stem')
    bevel(stem,.0015)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,
        location=(0,surface-.022,z))
    knob=adopt(bpy.context.object,label+' knob - flattened round head')
    knob.scale=(.020,.012,.020)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in knob.data.polygons:
        p.use_smooth=True

for ix in [-1,1]:
    for iy in [-1,1]:
        foot=loft('Foot '+('left' if ix<0 else 'right')+' '+('front' if iy<0 else 'rear'),
                  [(0,.022,.022,.010),(.008,.025,.025,.012),
                   (.102,.035,.035,.014),(.125,.035,.035,.014)])
        foot.location=(ix*.098,iy*.098,0)
        bevel(foot,.003)

scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.length_unit='METERS'
scene.unit_settings.scale_length=1
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studiolight_rotate_z=.35
scene.display.shading.color_type='SINGLE'
scene.display.shading.single_color=(.72,.72,.72)
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.25
scene.display.shading.curvature_valley_factor=1.15
scene.display.shading.show_object_outline=True
scene.display.shading.background_type='WORLD'
scene.world.color=(.20,.20,.20)
scene.render.resolution_x=1000
scene.render.resolution_y=1100
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add()
camera=adopt(bpy.context.object,'Preview camera')
camera.data.type='ORTHO'
camera.data.ortho_scale=1.02
scene.camera=camera

def preview(filename, position, target=(0,0,.405)):
    camera.location=position
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(ROOT/filename)
    bpy.ops.render.render(write_still=True)

preview('onizleme_capraz.png',(1.15,-1.65,1.04))
preview('onizleme_on.png',(0,-2,.43))
preview('onizleme_yan.png',(2,0,.43))
camera.location=(1.15,-1.65,1.04)
camera.rotation_euler=(Vector((0,0,.405))-camera.location).to_track_quat('-Z','Y').to_euler()

# Verify evaluated scale, closed edges and absence of material assignments.
geometry=[o for o in collection.objects if o.type=='MESH']
depsgraph=bpy.context.evaluated_depsgraph_get()
points=[]
for obj in geometry:
    ev=obj.evaluated_get(depsgraph)
    points.extend(ev.matrix_world@Vector(c) for c in ev.bound_box)
dimensions=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
assert abs(dimensions[0]-.4)<.001 and .4 <= dimensions[1] < .45
assert abs(dimensions[2]-.8)<.001
assert len(geometry)==12
assert all(len(o.data.materials)==0 for o in geometry)
for obj in geometry:
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    assert all(e.is_manifold for e in bm.edges),obj.name
    assert bm.calc_volume(signed=True)>0,obj.name
    bm.free()
scene['Brief source']='tarif.md; geometry only; no reference imagery'
scene['Author']='codex'
scene['Model']='gpt-6'
scene['Dimensions metres']=dimensions
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'sonuc.blend'))
print('VERIFIED: 12 closed mesh parts; dimensions',dimensions,'; no material slots')
