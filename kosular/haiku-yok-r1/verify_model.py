import bpy
import os

os.chdir("<tezgah>\\kosular\\test-v2\\haiku-yok-r1")

# Load the model
bpy.ops.wm.open_mainfile(filepath="sonuc.blend")

# Check collection and objects
collection = bpy.data.collections.get("Molly's Nightstand")
print(f"Collection: {collection.name}")
print(f"Objects in collection:")
for obj in collection.all_objects:
    print(f"  - {obj.name} ({obj.type})")
    if obj.type == 'MESH':
        modifiers = [m.name for m in obj.modifiers]
        print(f"    Modifiers: {modifiers if modifiers else 'None'}")
        print(f"    Vertices: {len(obj.data.vertices)}")

print("\n✓ Model structure verified")
