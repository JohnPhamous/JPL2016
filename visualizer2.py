#Different than original,copies objects for new instances rather than creating new ones

import bpy, random, argparse, sys, time, pickle, os
from random import randint
import numpy as np
from math import pi

#Short hands for common calls
scene = bpy.context.scene
selected = bpy.context.selected_objects
mesh = bpy.ops.mesh
context = bpy.context
object = bpy.ops.object
ops = bpy.ops
selected_object = bpy.context.active_object

#General Parameters
clouds = 25
#Used to track how much time elapsed
startTime = time.time()
#Different lighting types: sun, area
lightType = "sun"
objectsToClouds = False
render = True
date = "20020906"
granule = "50"
horizontal_decimation = 1
satHeight_km = 715
kmPerBlend = 300
verticleMag = 10
colorScheme = "cloud_phase_3x3"
pickleLocation = "/Users/John/Desktop/JPL"

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
        print("Creating sun light...")
        object.lamp_add(type = 'SUN', radius = 1, view_align = False, location = (-1, -32, 18))
    elif lightType == "area":
        print("Creating area light...")
        object.lamp_add(type = 'AREA', radius = 1, view_align = False, location = (-1, -32, 18))
    #Camera initialized
    object.camera_add(view_align = True, enter_editmode = False, location = (0, -20, 10))
    #Sets camera rotation
    ops.transform.rotate(value = 1.16299, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL', mirror = False, proportional = 'DISABLED', proportional_edit_falloff = 'SMOOTH', proportional_size = 1)
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
def randomNum(min, max):
    num = round(random.uniform(min, max), 10)
    return num

def ObjectCreation(clouds):
    counter = 0
    baseObject(0, 0, 0)
    obj = scene.objects.active
    meshCopy = obj.data
    os.chdir(pickleLocation)

    print("Reading pickle file...")
    pkl_file=open('clouds.20020906G050.pkl', 'rb')
    CldFrcTot = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    # print(CldFrcTot[0,0])
    CldFrcTot_QC = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    Latitude = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    Longitude = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    latAIRS = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    lonAIRS = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    nCld = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    CldFrcStd = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    CldFrcStd_QC = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    CldFrcStdErr = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    PCldTop = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    PCldTop_QC = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    PCldTopErr = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    TCldTop = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    TCldTop_QC = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    TCldTopErr = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    cloud_phase_3x3 = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    cloud_phase_bits = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_opt_dpth = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_opt_dpth_QC = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_opt_dpth_ave_kern = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_eff_diam = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_eff_diam_QC = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_eff_diam_ave_kern = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_temp_eff = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_temp_eff_QC = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_temp_eff_ave_kern = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    ice_cld_fit_reduced_chisq = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
    pkl_file.close()
    print("Pickle filed closed.")

    if colorScheme == 'cloud_phase_3x3':
        global phase_m9999_color, phase_m2_color, phase_m1_color, phase_00_color
        global phase_p1_color, phase_p2_color, phase_p3_color, phase_p4_color
        phase_m9999_color = makeMaterial('Phase-9999', (0.5,0.5,0.5), (0.0,0.0,0.0), 0.25)
        phase_m2_color = makeMaterial('Phase-2', (1.0,0.0,0.0), (0.0,0.0,0.0), 0.25)
        phase_m1_color = makeMaterial('Phase-1', (0.8,0.2,0.0), (0.0,0.0,0.0), 0.25)
        phase_00_color = makeMaterial('Phase+0', (0.5,0.5,0.0), (0.0,0.0,0.0), 0.25)
        phase_p1_color = makeMaterial('Phase+1', (0.3,0.7,0.0), (0.0,0.0,0.0), 0.25)
        phase_p2_color = makeMaterial('Phase+2', (0.2,0.8,0.0), (0.0,0.0,0.0), 0.25)
        phase_p3_color = makeMaterial('Phase+3', (0.1,0.9,0.0), (0.0,0.0,0.0), 0.25)
        phase_p4_color = makeMaterial('Phase+4', (0.0,1.0,0.0), (0.0,0.0,0.0), 0.25)

    for attempts in range(clouds):
        cloudTime = time.time()
        print("Generating cloud #" + str(attempts + 1))

        '''
        #Demo Coordinates
        x = randomNum(-5.0, 5.0)
        y = randomNum(-5.0, 5.0)
        z = randomNum(0.0, 5.0)
        '''
        ysc_km = (attempts - 135/2.) * 15.
        ysc = ysc_km / kmPerBlend
        for ifp in range(horizontal_decimation // 2, 135, horizontal_decimation):

        obj.location = (x, y, z)
        obj.scale = 0.1 * obj.location

        if objectsToClouds == True:
            #0 =  status, 1 = cumulous, 2 = cirrus
            if counter == 0:
                counter = 1
                scene.cloud_type = '0'
                #Converts primitive objects into clouds
                ops.cloud.generate_cloud()
            elif counter == 1:
                counter = 2
                scene.cloud_type = '1'
                ops.cloud.generate_cloud()
            elif counter == 2:
                counter = 0
                scene.cloud_type = '2'
                ops.cloud.generate_cloud()

        obj = obj.copy()
        obj.data = meshCopy.copy()
        scene.objects.link(obj)
        print("****** \nIt took " + str((time.time()) - cloudTime) + " to generate clouds " + str(attempts + 1))
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

print("\n|||||||||||||\nStarting visualizer for displaying AIRS clouds in 3D...")
clearScene()
setup()
ObjectCreation(clouds)

if objectsToClouds == True:
    print("------------- \nVisualizer took " + str((time.time() - startTime)) + " seconds for " + str(clouds) + " clouds using " + lightType + " lighting.")
elif objectsToClouds == False:
    print("------------- \nVisualizer took " + str((time.time() - startTime)) + " seconds for " + str(clouds) + " objects using " + lightType + " lighting.")
