import bpy, random, argparse, sys, time
from random import randint
import numpy as np
from math import pi

#Short hands for common calls
scene = bpy.context.scene
selected = bpy.context.selected_objects
mesh = bpy.ops.mesh
context = bpy.context
object = bpy.ops.object
selected_object = bpy.context.active_object

#General Parameters
clouds = 1000
#Used to track how much time elapsed
startTime = time.time()
#Different lighting types: sun, area
lightType = "area"

parser = argparse.ArgumentParser('Display AIRS clouds in 3D')
parser.add_argument('--date', action = 'store', dest = 'date', default = '20020906', help = 'date yyyymmdd')
parser.add_argument('--gran', action = 'store', dest = 'gran', default = 50, type = int, help = 'granule number [1-240]')
parser.add_argument('--sub', action = 'store', dest = 'subsample', default = 1, type = int, help = 'subsampling factor for horizontal decimation [1-5]')
parser.add_argument('--cirrus', action = 'store_true', default = False, help='Plot Kahn cirrus cloud results')
parser.add_argument('--colorby', action = 'store', default = '', help = 'field by which to color clouds')

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat

#Color Paremeters
blue = makeMaterial('BlueSemi', (0,0,1), (0.5,0.5,0), 0.5)

def setMaterial(obj, mat):
    obj.data.materials.append(mat)
    return

def setup():
    #Light source setup
    if lightType == "sun":
        print("Creating sun light")
        object.lamp_add(type = 'SUN', radius = 1, view_align = False, location = (-1, -32, 18))
    elif lightType == "area":
        print("Creating area light")
        object.lamp_add(type = 'AREA', radius = 1, view_align = False, location = (-1, -32, 18))
    #Camera initialized
    object.camera_add(view_align = True, enter_editmode = False, location = (0, -20, 10))
    #Sets camera rotation
    bpy.ops.transform.rotate(value = 1.06299, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL', mirror = False, proportional = 'DISABLED', proportional_edit_falloff = 'SMOOTH', proportional_size = 1)
    #Earth plane created
    mesh.primitive_plane_add(radius = 30, view_align = False, enter_editmode = False, location = (0, 0, 0))
    setMaterial(context.object, blue)
    return

def baseObject(x,y,z):
    #Creates base cylinder
    mesh.primitive_cylinder_add(location=(x,y,z))
    return

def clearScene():
    #Clears the current scene
    for obj in scene.objects:
        scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    return

def ObjectCreation(clouds):
    counter = 0
    for attempts in range(clouds):
        print("Generating cloud #" + str(attempts + 1))
        x = round(random.uniform(-5.0, 5.0), 10)
        y = round(random.uniform(-5.0, 5.0), 10)
        z = round(random.uniform(0, 4.0), 10)
        baseObject(x,y,z)
        #X Scale
        context.object.scale[0] = x/100
        #Y Scale
        context.object.scale[1] = y/100
        #Z Scale
        context.object.scale[2] = z/100

        #Alternating cloud types
        #0 =  status, 1 = cumulous, 2 = cirrus
        if counter == 0:
            counter = 1
            scene.cloud_type = '0'
            #Converts primitive objects into clouds
            bpy.ops.cloud.generate_cloud()
        elif counter == 1:
            counter = 2
            scene.cloud_type = '1'
            bpy.ops.cloud.generate_cloud()
        elif counter == 2:
            counter = 0
            scene.cloud_type = '2'
            bpy.ops.cloud.generate_cloud()

        if z > 3:   #Testing color conversion
            context.object.active_material.volume.transmission_color = (3, 0.628163, 0)

        else:
            context.object.active_material.volume.transmission_color = (0, 1, 1)
    return

'''def materialCreation():
    #Used to color primitive objects, won't work for clouds
    #for attempts in range(scale):
    randomRed = random.uniform(0.0, 1.0)    #Used for random color scale, need to adjust later for color mapping
    randomGreen = random.uniform(0.0, 1.0)
    randomBlue = random.uniform(0.0, 1.0)

    material = bpy.data.materials.new("Material")    #Material properties
    material.alpha = round(random.uniform(0.1, 1.0), 10)    #Opacity
    material.use_transparency = True
    context.object.show_transparent = True
    context.object.data.materials.append(material)  #Applies material properties
    context.object.color = (randomRed, randomGreen, randomBlue, 1)  #Changes objects color(RGB Opacity)
    context.object.active_material.use_object_color = True
    return'''

print("Starting visualizer...")
clearScene()
setup()
ObjectCreation(clouds)
print("Visualizer took " + str((time.time() - startTime)) + " seconds for " + str(clouds) + " clouds using " + lightType + " lighting.")
