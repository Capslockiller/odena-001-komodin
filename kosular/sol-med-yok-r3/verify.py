# yazan: codex
# model: gpt-6.1-sol
import bpy
import os
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'sonuc.blend'))
scene=bpy.context.scene
parts=bpy.data.collections["Molly's Nightstand"]
assert len(parts.objects)==12
assert all(o.type=='MESH' for o in parts.objects)
assert all(len(o.data.materials)==0 for o in parts.objects)
assert all(o in parts.objects.values() for o in scene.objects if o.type=='MESH')
points=[o.matrix_world@Vector(p) for o in parts.objects for p in o.bound_box]
size=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
assert abs(size[0]-.4)<1e-6 and abs(size[2]-.8)<1e-6
drawer=parts.objects['03 Shallow drawer front']
door=parts.objects['04 Lower door front']
assert abs(door.dimensions.z/drawer.dimensions.z-2)<1e-5
assert scene.unit_settings.system=='METRIC'
assert scene['yazan']=='codex'
print('SAVED FILE VERIFIED: 12 meshes; exact collection; no assigned materials; metric units;')
print('overall dimensions (m):',size,'door/drawer:',door.dimensions.z/drawer.dimensions.z)
