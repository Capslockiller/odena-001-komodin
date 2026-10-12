import bpy
import bmesh
import math
from mathutils import Vector

def body_width(z):
    z_min = 0.095
    z_max = 0.755
    h = z_max - z_min
    u = max(0.0, min(1.0, (z - z_min) / h))
    w_bot = 0.165
    w_mid = 0.200
    w_top = 0.185
    if u <= 0.60:
        s = u / 0.60
        return w_bot + (w_mid - w_bot) * math.sin(s * 0.5 * math.pi)
    else:
        s = (u - 0.60) / 0.40
        return w_mid - (w_mid - w_top) * (math.sin(s * 0.5 * math.pi) ** 2)

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes):
    bpy.data.meshes.remove(mesh)

def create_panel_mesh(name, z_min, z_max, nx=16, nz=20, side_margin=0.038, front_proud=0.008, back_embed=0.004):
    bm = bmesh.new()
    verts_front = []
    verts_back = []
    
    for j in range(nz):
        t = j / (nz - 1)
        z = z_min + t * (z_max - z_min)
        bw = body_width(z)
        wp = bw - side_margin
        
        row_f = []
        row_b = []
        for i in range(nx):
            u = -1.0 + 2.0 * (i / (nx - 1))
            x = u * wp
            yf = -bw - front_proud
            yb = -bw + back_embed
            vf = bm.verts.new((x, yf, z))
            vb = bm.verts.new((x, yb, z))
            row_f.append(vf)
            row_b.append(vb)
        verts_front.append(row_f)
        verts_back.append(row_b)
        
    bm.verts.ensure_lookup_table()
    
    for j in range(nz - 1):
        for i in range(nx - 1):
            v00 = verts_front[j][i]
            v10 = verts_front[j][i+1]
            v11 = verts_front[j+1][i+1]
            v01 = verts_front[j+1][i]
            bm.faces.new((v00, v01, v11, v10))
            
    for j in range(nz - 1):
        for i in range(nx - 1):
            v00 = verts_back[j][i]
            v10 = verts_back[j][i+1]
            v11 = verts_back[j+1][i+1]
            v01 = verts_back[j+1][i]
            bm.faces.new((v00, v10, v11, v01))
            
    for i in range(nx - 1):
        vf0 = verts_front[0][i]
        vf1 = verts_front[0][i+1]
        vb0 = verts_back[0][i]
        vb1 = verts_back[0][i+1]
        bm.faces.new((vf0, vf1, vb1, vb0))
        
    for i in range(nx - 1):
        vf0 = verts_front[nz-1][i]
        vf1 = verts_front[nz-1][i+1]
        vb0 = verts_back[nz-1][i]
        vb1 = verts_back[nz-1][i+1]
        bm.faces.new((vf0, vb0, vb1, vf1))
        
    for j in range(nz - 1):
        vf0 = verts_front[j][0]
        vf1 = verts_front[j+1][0]
        vb0 = verts_back[j][0]
        vb1 = verts_back[j+1][0]
        bm.faces.new((vf0, vb0, vb1, vf1))
        
    for j in range(nz - 1):
        vf0 = verts_front[j][nx-1]
        vf1 = verts_front[j+1][nx-1]
        vb0 = verts_back[j][nx-1]
        vb1 = verts_back[j+1][nx-1]
        bm.faces.new((vf0, vf1, vb1, vb0))
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    non_m = [e for e in bm.edges if not e.is_manifold]
    print(f"{name} non-manifold edges: {len(non_m)}")
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    mesh.shade_smooth()
    
    bev = obj.modifiers.new("Bevel", type='BEVEL')
    bev.width = 0.005
    bev.segments = 4
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(45)
    
    wn = obj.modifiers.new("WeightedNormal", type='WEIGHTED_NORMAL')
    return obj

d_obj = create_panel_mesh("DrawerFront", 0.525, 0.700, nx=16, nz=16)
