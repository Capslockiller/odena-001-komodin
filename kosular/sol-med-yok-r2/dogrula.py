# yazan: codex
# model: gpt-6
from pathlib import Path
import bpy

bpy.ops.wm.open_mainfile(filepath=str(Path(__file__).resolve().parent / 'sonuc.blend'))
collection = bpy.data.collections.get("Molly's Nightstand")
assert collection is not None
assert len(collection.objects) == 12
assert all(obj.type == 'MESH' and len(obj.data.materials) == 0 for obj in collection.objects)
assert len(bpy.data.objects) == 12
assert len(bpy.data.materials) == 0
assert bpy.context.scene.unit_settings.system == 'METRIC'
assert bpy.context.scene['yazan'] == 'codex'
print('SAVED_FILE_VERIFIED: 12 meshes, required collection, metric units, zero materials')
