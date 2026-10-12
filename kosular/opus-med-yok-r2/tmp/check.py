import bpy
from mathutils import Vector
c=bpy.data.collections["Molly's Nightstand"]
mn=Vector((9,9,9)); mx=-mn
for o in c.objects:
    for v in o.data.vertices:
        w=o.matrix_world@v.co; mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
    print("PART",o.name,len(o.data.polygons),[m.type for m in o.modifiers])
print("BBOX",tuple(round(x,3) for x in mn),tuple(round(x,3) for x in mx))
print("OUTSIDE",[o.name for o in bpy.data.objects if c not in o.users_collection])
