import bpy
from mathutils import Vector

print('=== VERIFYING sonuc.blend ===')
print('Collections in file:', [c.name for c in bpy.data.collections])
target_col = bpy.data.collections.get("Molly's Nightstand")
if not target_col:
    print("ERROR: Collection Molly's Nightstand NOT FOUND!")
else:
    print('Found collection:', target_col.name)
    print(f'Total objects in collection: {len(target_col.objects)}')
    for obj in target_col.objects:
        mods = [f'{m.name} ({m.type})' for m in obj.modifiers]
        mats = [m.name for m in obj.data.materials if m] if hasattr(obj.data, 'materials') else []
        dim = obj.dimensions
        loc = obj.location
        print(f'  Object: {obj.name:18} | Type: {obj.type} | Modifiers: {mods} | Materials: {mats} | Dims: ({dim.x:.3f}, {dim.y:.3f}, {dim.z:.3f})')

# Check total bounds across all objects in Molly's Nightstand
min_corner = [float('inf')]*3
max_corner = [float('-inf')]*3
for obj in target_col.objects:
    for v in obj.bound_box:
        w_co = obj.matrix_world @ Vector(v)
        for i in range(3):
            min_corner[i] = min(min_corner[i], w_co[i])
            max_corner[i] = max(max_corner[i], w_co[i])

print('Overall Bounding Box:')
print(f'  X: [{min_corner[0]:.4f}, {max_corner[0]:.4f}] -> Width  = {max_corner[0]-min_corner[0]:.4f} m ({(max_corner[0]-min_corner[0])*100:.1f} cm)')
print(f'  Y: [{min_corner[1]:.4f}, {max_corner[1]:.4f}] -> Depth  = {max_corner[1]-min_corner[1]:.4f} m ({(max_corner[1]-min_corner[1])*100:.1f} cm)')
print(f'  Z: [{min_corner[2]:.4f}, {max_corner[2]:.4f}] -> Height = {max_corner[2]-min_corner[2]:.4f} m ({(max_corner[2]-min_corner[2])*100:.1f} cm)')

# Check if any objects exist outside the collection
other_objs = [obj.name for obj in bpy.data.objects if obj.name not in target_col.objects]
print(f"Objects outside Molly's Nightstand: {other_objs}")

# Check materials in file
print(f'Total materials in blend file: {len(bpy.data.materials)}')
