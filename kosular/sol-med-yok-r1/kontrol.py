# yazan: codex · gpt-6
from pathlib import Path
import bpy
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'sonuc.blend'))
collection=bpy.data.collections["Molly's Nightstand"]
meshes=[o for o in collection.objects if o.type=='MESH']
assert len(meshes)==12
assert all(len(o.data.materials)==0 for o in meshes)
print('REOPEN VERIFIED',len(meshes),'parts;',bpy.context.scene['Dimensions metres'])
print('PREVIEW SETTINGS',[p.identifier for p in bpy.context.preferences.filepaths.bl_rna.properties if 'preview' in p.identifier])
