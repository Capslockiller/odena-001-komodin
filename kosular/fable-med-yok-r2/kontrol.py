import bpy
from mathutils import Vector
print("LIBS:", [l.filepath for l in bpy.data.libraries])
print("COLLS:", [c.name for c in bpy.data.collections])
print("MATS:", len(bpy.data.materials))
c = bpy.data.collections.get("Molly's Nightstand")
dg = bpy.context.evaluated_depsgraph_get()
lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
for ob in c.objects:
    ev = ob.evaluated_get(dg)
    for v in ev.data.vertices:
        p = ev.matrix_world @ v.co
        lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    print(ob.name, [(m.name, m.type) for m in ob.modifiers], len(ob.data.materials))
print("BOUNDS", tuple(round(x, 3) for x in lo), tuple(round(x, 3) for x in hi))
print("SIZE", tuple(round(x, 3) for x in (hi - lo)))
