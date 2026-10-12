import bpy
import os
from mathutils import Vector

blend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sonuc.blend")
bpy.ops.wm.open_mainfile(filepath=blend_path)

print("=== VERIFYING SONUC.BLEND ===")

# 1. Collection check
col_name = "Molly's Nightstand"
assert col_name in bpy.data.collections, f"Collection '{col_name}' not found!"
col = bpy.data.collections[col_name]
print(f"Collection '{col_name}' found with {len(col.objects)} objects.")

# 2. Objects check
print("Objects in collection:")
for obj in col.objects:
    print(f"  - {obj.name}: type={obj.type}, verts={len(obj.data.vertices)}, polys={len(obj.data.polygons)}")
    mods = [f"{m.name} ({m.type})" for m in obj.modifiers]
    print(f"    Modifiers: {mods}")
    # Scale check
    scale_tuple = (round(obj.scale.x, 5), round(obj.scale.y, 5), round(obj.scale.z, 5))
    assert scale_tuple == (1.0, 1.0, 1.0), f"Object {obj.name} scale is not (1,1,1)! Got {scale_tuple}"

# 3. Check for any loose objects in Scene collection
scene_loose = [o.name for o in bpy.context.scene.collection.objects]
print(f"Loose objects in root Scene collection: {scene_loose}")
assert len(scene_loose) == 0, f"Found loose objects in root: {scene_loose}"

all_scene_objs = list(bpy.context.scene.objects)
for o in all_scene_objs:
    assert o.name in col.objects, f"Object {o.name} is in scene but not in '{col_name}'!"
print("All scene objects are in 'Molly\\'s Nightstand'!")

# 4. Materials check
mats = list(bpy.data.materials)
print(f"Total materials in blend: {len(mats)}")
for o in col.objects:
    if hasattr(o.data, "materials"):
        assert len(o.data.materials) == 0, f"Object {o.name} has materials assigned!"
print("Zero materials check PASSED!")

# 5. Dimensions check
min_z = min((o.matrix_world @ v.co).z for o in col.objects for v in o.data.vertices)
max_z = max((o.matrix_world @ v.co).z for o in col.objects for v in o.data.vertices)
min_x = min((o.matrix_world @ v.co).x for o in col.objects for v in o.data.vertices)
max_x = max((o.matrix_world @ v.co).x for o in col.objects for v in o.data.vertices)
min_y = min((o.matrix_world @ v.co).y for o in col.objects for v in o.data.vertices)
max_y = max((o.matrix_world @ v.co).y for o in col.objects for v in o.data.vertices)

print(f"Bounding Box:")
print(f"  X: {max_x - min_x:.4f} m (span [{min_x:.4f}, {max_x:.4f}])")
print(f"  Y: {max_y - min_y:.4f} m (span [{min_y:.4f}, {max_y:.4f}])")
print(f"  Z: {max_z - min_z:.4f} m (span [{min_z:.4f}, {max_z:.4f}])")

assert abs(max_z - min_z - 0.8000) < 1e-3, f"Height is not 0.80 m! Got {max_z - min_z}"
assert abs(min_z - 0.0) < 1e-3, f"Base is not at Z = 0! Got {min_z}"
print("Real-world scale (0.80 m height) check PASSED!")
print("=== ALL VERIFICATION CHECKS PASSED ===")
