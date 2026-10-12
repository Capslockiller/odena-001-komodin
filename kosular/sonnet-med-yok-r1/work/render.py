import bpy, math
from mathutils import Vector
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=700; sc.render.resolution_y=900
cam=bpy.data.objects.new("c",bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera=cam
cam.data.type='ORTHO'; cam.data.ortho_scale=1.0
views={'front':((0,-3,.4),(math.pi/2,0,0)),'side':((3,0,.4),(math.pi/2,0,math.pi/2)),'iso':((1.4,-1.8,1.1),(math.radians(70),0,math.radians(38)))}
for n,(l,r) in views.items():
    cam.location=l; cam.rotation_euler=r
    sc.render.filepath=bpy.path.abspath(f"//prev_{n}.png"); bpy.ops.render.render(write_still=True)
