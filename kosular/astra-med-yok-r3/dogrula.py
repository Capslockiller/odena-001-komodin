# yazan: codex
# model: gpt-6
import bpy
import bmesh
from pathlib import Path

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'sonuc.blend'))
scene=bpy.context.scene
scene['yazan']='codex'
scene['model']='gpt-6'
parts=bpy.data.collections["Molly's Nightstand"]
assert len(parts.objects)==14
assert all(o.type!='MESH' or o.name in parts.objects for o in scene.objects)
deps=bpy.context.evaluated_depsgraph_get()
for obj in parts.objects:
    assert len(obj.data.materials)==0
    ev=obj.evaluated_get(deps)
    data=ev.to_mesh()
    bm=bmesh.new()
    bm.from_mesh(data)
    bad=sum(not e.is_manifold for e in bm.edges)
    assert bad==0,(obj.name,bad)
    bm.free()
    ev.to_mesh_clear()
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(root/'sonuc.blend'))
print('PASS: reopened blend; 14 parts; evaluated meshes manifold; no material assignments.')
