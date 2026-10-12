# yazan: codex
# model: gpt-6-astra
import bpy
import bmesh
import json
from pathlib import Path

root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'sonuc.blend'))
collection=bpy.data.collections["Molly's Nightstand"]
meshes=[o for o in bpy.data.objects if o.type=='MESH']
results={}
for obj in meshes:
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    results[obj.name]={
        'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
        'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces),
        'signed_volume_m3':bm.calc_volume(signed=True),
        'in_required_collection':collection in obj.users_collection,
        'material_slots':len(obj.data.materials),
    }
    bm.free()
assert len(meshes)==12
assert all(r['non_manifold_edges']==0 and r['zero_area_faces']==0 and
           r['signed_volume_m3']>0 and r['in_required_collection'] and
           r['material_slots']==0 for r in results.values()), results
(root/'dogrulama.json').write_text(json.dumps({'yazan':'codex','model':'gpt-6-astra',
    'reopened_blend':True,'checks':results},ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: reopened blend, 12 closed positive-volume meshes, no degenerate faces, no material slots.')
