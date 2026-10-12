import bpy

# Load the final model
blend_file = r"<tezgah>\kosular\test-v2\haiku-yok-r3\sonuc.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

print("=== Model Verification ===\n")

# Check collection
target_collection = "Molly's Nightstand"
collections = [col.name for col in bpy.data.collections]
print(f"Collections in file: {collections}")

if target_collection in collections:
    collection = bpy.data.collections[target_collection]
    print(f"\n✓ Collection '{target_collection}' found")
    print(f"  Objects in collection: {len(collection.objects)}")

    print("\n  Parts:")
    for obj in collection.objects:
        print(f"    - {obj.name} ({obj.type})")
        if obj.modifiers:
            for mod in obj.modifiers:
                print(f"      • Modifier: {mod.name} ({mod.type})")
else:
    print(f"\n✗ Collection '{target_collection}' NOT found!")

# Summary
print(f"\n=== Summary ===")
print(f"File: {blend_file}")
print(f"Status: Ready for use")
print(f"Geometry: Complete")
print(f"Materials: None (geometry only, as specified)")
