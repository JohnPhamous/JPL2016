import bpy, random
from random import randint

context = bpy.context
scene = context.scene

def base_object():
    #Creates base cylinder
    bpy.ops.mesh.primitive_cylinder_add()
    return

def clear_scene(scene):
    #Clears the current scene
    for obj in scene.objects:
        scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    return

def object_creation(scene, clouds):
    base_object()
    obj = scene.objects.active
    mesh = obj.data
    nummats = 10
    random_mats = create_material_list(nummats) # create 10 random materials
    for attempts in range(clouds):
        x = round(random.uniform(-4.0, 4.0), 10)
        y = round(random.uniform(-4.0, 4.0), 10)
        z = round(random.uniform(-4.0, 4.0), 10)
        obj.location = (x, y, z)
        obj.scale = 0.1 * obj.location

        red = random.uniform(0.0, 1.0)    #Used for random color scale, need to adjust later for color mapping
        green = random.uniform(0.0, 1.0)
        blue = random.uniform(0.0, 1.0)
        obj.show_transparent = True
        obj.active_material = random_mats[random.randint(0, nummats-1)] # random pick of random mats

        obj.color = (red, green, blue, 1)  #Changes objects color(RGB Opacity)

        # copy the next one
        obj = obj.copy()
        obj.data = mesh.copy() # a new mesh for each object.
        scene.objects.link(obj) # link it to the scene
    return

def create_material_list(len):
    #for attempts in range(scale):
    mats = []
    for i in range(len):
        material = bpy.data.materials.new("Material")    #Material properties
        material.alpha = round(random.uniform(0.1, 1.0), 10)    #Opacity
        material.use_transparency = True
        material.use_object_color = True
        mats.append(material)

    return mats

clear_scene(scene)
object_creation(scene, 1000)
