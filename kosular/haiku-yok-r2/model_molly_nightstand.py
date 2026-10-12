import bpy
import bmesh
from mathutils import Vector
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

collection = bpy.data.collections.new("Molly's Nightstand")
bpy.context.scene.collection.children.link(collection)

def add_to_collection(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

def apply_smooth_shading(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

def create_body():
    bm = bmesh.new()

    width = 0.40
    depth = 0.40
    height = 0.70

    num_height_segments = 8
    num_width_segments = 4
    bulge_max = 0.04

    vertices = []

    for h_idx in range(num_height_segments + 1):
        z = (h_idx / num_height_segments) * height
        progress = h_idx / num_height_segments

        if progress < 0.5:
            bulge_factor = progress * 2
        else:
            bulge_factor = (1 - progress) * 2

        bulge = bulge_max * bulge_factor
        taper_factor = 1.0 - (0.1 * (1 - progress))

        ring_verts = []

        for angle_idx in range(num_width_segments * 4):
            if angle_idx < num_width_segments:
                x = width / 2 * taper_factor
                y = -depth / 2 * taper_factor + (angle_idx / num_width_segments) * depth * taper_factor
            elif angle_idx < num_width_segments * 2:
                x = width / 2 * taper_factor - ((angle_idx - num_width_segments) / num_width_segments) * width * taper_factor
                y = depth / 2 * taper_factor
            elif angle_idx < num_width_segments * 3:
                x = -width / 2 * taper_factor
                y = depth / 2 * taper_factor - ((angle_idx - num_width_segments * 2) / num_width_segments) * depth * taper_factor
            else:
                x = -width / 2 * taper_factor + ((angle_idx - num_width_segments * 3) / num_width_segments) * width * taper_factor
                y = -depth / 2 * taper_factor

            dist = math.sqrt(x*x + y*y)
            if dist > 0:
                x = x + (x / dist) * bulge * 0.15
                y = y + (y / dist) * bulge * 0.15

            pos = Vector((x, y, z))
            vert = bm.verts.new(pos)
            ring_verts.append(vert)

        vertices.append(ring_verts)

    for h_idx in range(num_height_segments):
        for w_idx in range(num_width_segments * 4):
            v0 = vertices[h_idx][w_idx]
            v1 = vertices[h_idx][(w_idx + 1) % (num_width_segments * 4)]
            v2 = vertices[h_idx + 1][(w_idx + 1) % (num_width_segments * 4)]
            v3 = vertices[h_idx + 1][w_idx]
            bm.faces.new([v0, v1, v2, v3])

    bm.faces.new(reversed(vertices[0]))
    bm.faces.new(vertices[-1])

    mesh = bpy.data.meshes.new("Body")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new("Body", mesh)
    bpy.context.collection.objects.link(obj)
    add_to_collection(obj, collection)
    apply_smooth_shading(obj)

    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return obj, height

def create_top(body_obj, body_height):
    bm = bmesh.new()

    width = 0.40
    depth = 0.40
    top_thickness = 0.04
    overhang = 0.03

    base_width = width + overhang * 2
    base_depth = depth + overhang * 2

    num_segments = 12

    bottom_verts = []
    top_verts = []

    for i in range(num_segments * 4):
        angle_idx = i

        if angle_idx < num_segments:
            x = base_width / 2
            y = -base_depth / 2 + (angle_idx / num_segments) * base_depth
        elif angle_idx < num_segments * 2:
            x = base_width / 2 - ((angle_idx - num_segments) / num_segments) * base_width
            y = base_depth / 2
        elif angle_idx < num_segments * 3:
            x = -base_width / 2
            y = base_depth / 2 - ((angle_idx - num_segments * 2) / num_segments) * base_depth
        else:
            x = -base_width / 2 + ((angle_idx - num_segments * 3) / num_segments) * base_width
            y = -base_depth / 2

        bottom_verts.append(bm.verts.new(Vector((x, y, body_height))))
        top_verts.append(bm.verts.new(Vector((x, y, body_height + top_thickness))))

    for i in range(len(bottom_verts)):
        v0 = bottom_verts[i]
        v1 = bottom_verts[(i + 1) % len(bottom_verts)]
        v2 = top_verts[(i + 1) % len(top_verts)]
        v3 = top_verts[i]
        bm.faces.new([v0, v1, v2, v3])

    bm.faces.new(reversed(bottom_verts))
    bm.faces.new(top_verts)

    mesh = bpy.data.meshes.new("Top")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new("Top", mesh)
    bpy.context.collection.objects.link(obj)
    add_to_collection(obj, collection)
    apply_smooth_shading(obj)

    subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf.levels = 2
    subsurf.render_levels = 3

    return obj

def create_panel(is_drawer, body_height):
    bm = bmesh.new()

    panel_width = 0.34
    if is_drawer:
        panel_height = 0.095
        z_pos = body_height - 0.285
    else:
        panel_height = 0.17
        z_pos = body_height - 0.17

    panel_depth = 0.012
    panel_forward_pos = 0.23

    w_subdiv = 6
    h_subdiv = 6

    front_verts = []
    back_verts = []

    for h_idx in range(h_subdiv + 1):
        for w_idx in range(w_subdiv + 1):
            t_w = w_idx / w_subdiv
            t_h = h_idx / h_subdiv

            x = (t_w - 0.5) * panel_width
            z = z_pos + (t_h) * panel_height

            bulge = 0.001 * math.sin(t_w * math.pi) * math.sin(t_h * math.pi)

            # Front face (facing outward in positive Y direction)
            pos_front = Vector((x, panel_forward_pos + bulge, z))
            front_verts.append(bm.verts.new(pos_front))

            # Back face
            pos_back = Vector((x, panel_forward_pos - panel_depth + bulge, z))
            back_verts.append(bm.verts.new(pos_back))

    # Front face
    for h_idx in range(h_subdiv):
        for w_idx in range(w_subdiv):
            idx0 = h_idx * (w_subdiv + 1) + w_idx
            idx1 = h_idx * (w_subdiv + 1) + w_idx + 1
            idx2 = (h_idx + 1) * (w_subdiv + 1) + w_idx + 1
            idx3 = (h_idx + 1) * (w_subdiv + 1) + w_idx
            bm.faces.new([front_verts[idx0], front_verts[idx1], front_verts[idx2], front_verts[idx3]])

    # Back face
    for h_idx in range(h_subdiv):
        for w_idx in range(w_subdiv):
            idx0 = h_idx * (w_subdiv + 1) + w_idx
            idx1 = h_idx * (w_subdiv + 1) + w_idx + 1
            idx2 = (h_idx + 1) * (w_subdiv + 1) + w_idx + 1
            idx3 = (h_idx + 1) * (w_subdiv + 1) + w_idx
            bm.faces.new([back_verts[idx3], back_verts[idx2], back_verts[idx1], back_verts[idx0]])

    # Edges (sides and top/bottom)
    for w_idx in range(w_subdiv):
        bm.faces.new([front_verts[w_idx], front_verts[w_idx + 1], back_verts[w_idx + 1], back_verts[w_idx]])
        top_idx = h_subdiv * (w_subdiv + 1) + w_idx
        bm.faces.new([front_verts[top_idx], front_verts[top_idx + 1], back_verts[top_idx + 1], back_verts[top_idx]])

    mesh = bpy.data.meshes.new(f"{'Drawer' if is_drawer else 'Door'}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj_name = "Drawer" if is_drawer else "Door"
    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.collection.objects.link(obj)
    add_to_collection(obj, collection)
    apply_smooth_shading(obj)

    return obj

def create_handle(x_pos, z_pos):
    bm = bmesh.new()

    radius = 0.009
    segments = 8
    rings = 4
    y_pos = 0.242

    for ring_idx in range(rings + 1):
        for seg_idx in range(segments):
            angle = (seg_idx / segments) * 2 * math.pi

            ring_progress = ring_idx / rings
            r = radius * math.sin(ring_progress * math.pi)

            x = x_pos + r * math.cos(angle)
            y = y_pos + r * math.sin(angle) * 0.5
            z = z_pos + radius * math.cos(ring_progress * math.pi)

            bm.verts.new(Vector((x, y, z)))

    verts = bm.verts[:]

    for ring_idx in range(rings):
        for seg_idx in range(segments):
            v0 = verts[ring_idx * segments + seg_idx]
            v1 = verts[ring_idx * segments + (seg_idx + 1) % segments]
            v2 = verts[(ring_idx + 1) * segments + (seg_idx + 1) % segments]
            v3 = verts[(ring_idx + 1) * segments + seg_idx]
            bm.faces.new([v0, v1, v2, v3])

    mesh = bpy.data.meshes.new(f"Handle_{int(x_pos*100)}_{int(z_pos*100)}")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new(f"Handle_{int(x_pos*100)}_{int(z_pos*100)}", mesh)
    bpy.context.collection.objects.link(obj)
    add_to_collection(obj, collection)
    apply_smooth_shading(obj)

    return obj

def create_feet(body_height):
    feet_positions = [
        (-0.18, -0.18),
        (0.18, -0.18),
        (0.18, 0.18),
        (-0.18, 0.18),
    ]

    for idx, (x, y) in enumerate(feet_positions):
        bm = bmesh.new()

        foot_height = 0.06
        foot_width = 0.03
        foot_depth = 0.03

        bottom_verts = [
            bm.verts.new(Vector((x - foot_width/2, y - foot_depth/2, 0))),
            bm.verts.new(Vector((x + foot_width/2, y - foot_depth/2, 0))),
            bm.verts.new(Vector((x + foot_width/2, y + foot_depth/2, 0))),
            bm.verts.new(Vector((x - foot_width/2, y + foot_depth/2, 0))),
        ]

        taper = 0.8
        top_verts = [
            bm.verts.new(Vector((x - foot_width/2 * taper, y - foot_depth/2 * taper, foot_height))),
            bm.verts.new(Vector((x + foot_width/2 * taper, y - foot_depth/2 * taper, foot_height))),
            bm.verts.new(Vector((x + foot_width/2 * taper, y + foot_depth/2 * taper, foot_height))),
            bm.verts.new(Vector((x - foot_width/2 * taper, y + foot_depth/2 * taper, foot_height))),
        ]

        for i in range(4):
            bm.faces.new([bottom_verts[i], bottom_verts[(i+1)%4], top_verts[(i+1)%4], top_verts[i]])

        bm.faces.new(reversed(bottom_verts))
        bm.faces.new(top_verts)

        mesh = bpy.data.meshes.new(f"Foot_{idx}")
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        obj = bpy.data.objects.new(f"Foot_{idx}", mesh)
        bpy.context.collection.objects.link(obj)
        add_to_collection(obj, collection)

body_obj, body_height = create_body()
top_obj = create_top(body_obj, body_height)
drawer_obj = create_panel(is_drawer=True, body_height=body_height)
door_obj = create_panel(is_drawer=False, body_height=body_height)

drawer_z = body_height - 0.285 + 0.095/2
door_z = body_height - 0.17 + 0.17/2
create_handle(-0.11, drawer_z)
create_handle(-0.11, door_z)

create_feet(body_height)

filepath = bpy.path.abspath("//sonuc.blend")
bpy.ops.wm.save_as_mainfile(filepath=filepath)
print(f"Model saved to {filepath}")

bpy.ops.object.camera_add(location=(0.65, -0.65, 0.45))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera
camera.rotation_euler = (1.1, 0, 0.785)

bpy.ops.object.light_add(type='SUN', location=(2, 2, 2))
light = bpy.context.active_object
light.data.energy = 4

bpy.ops.object.light_add(type='SUN', location=(-1, -1, 1))
fill_light = bpy.context.active_object
fill_light.data.energy = 2

bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 960
bpy.context.scene.render.filepath = bpy.path.abspath("//preview.png")

bpy.ops.render.render(write_still=True)
print(f"Preview rendered to {bpy.context.scene.render.filepath}")

# Front view
camera.location = (0.0, -0.7, 0.4)
camera.rotation_euler = (1.3, 0, 0)

bpy.context.scene.render.filepath = bpy.path.abspath("//preview_front.png")
bpy.ops.render.render(write_still=True)
print(f"Front preview rendered to {bpy.context.scene.render.filepath}")
