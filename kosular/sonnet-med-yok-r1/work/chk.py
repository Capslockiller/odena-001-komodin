import bpy
from mathutils import Vector
c=bpy.data.collections["Molly's Nightstand"]
mn=Vector((9,9,9));mx=-mn
for o in c.objects:
    for v in o.bound_box:
        w=o.matrix_world@Vector(v); mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
print("DIM",mx-mn,len(c.objects),len(bpy.data.materials))
