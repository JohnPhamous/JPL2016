#Adds in Manning's pickle reader

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
#Used to track how much time elapsed
startTime = time.time()
#Different lighting types: sun, area
lightType = "sun"
objectsToClouds = False
merge = True
render = True
date = "20020906"
granule = "50"
#1 all, 2 every other, 3 skips 2/3
horizontal_decimation = 3
satHeight_km = 715
kmPerBlend = 300
verticalMag = 10
colorScheme = 'cloud_phase_3x3'
pickleLocation = "/Users/John/Desktop/JPL"
layers_tfff=(True, False, False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False, False, False)

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
        object.lamp_add(type = 'SUN', radius = 1, view_align = False, location = (-1, -32, 18))
    elif lightType == "area":
        object.lamp_add(type = 'AREA', radius = 1, view_align = False, location = (-1, -32, 18))
    #Camera initialized
    object.camera_add(view_align = True, enter_editmode = False, location = (0, -10, 10))
    #Sets camera rotation
    ops.transform.rotate(value = 1.16299, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL', mirror = False, proportional = 'DISABLED', proportional_edit_falloff = 'SMOOTH', proportional_size = 1)
    #Earth plane created
    '''mesh.primitive_plane_add(radius = 5, view_align = False, enter_editmode = False, location = (0, 0, -1), layers = layers_tfff)
    setMaterial(context.object, blue)
    bpy.context.object.active_material.use_raytrace = False
    bpy.context.object.active_material.use_mist = False
    bpy.context.object.active_material.use_cast_shadows = False
    bpy.context.object.active_material.use_cast_buffer_shadows = False
    bpy.context.object.active_material.use_cast_approximate = False'''
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
    #Used for test cases
    num = round(random.uniform(min, max), 10)
    return num

def joinObjects():
    #Merges all of the created objects
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
        bpy.ops.object.join()
    return

def ObjectCreation():
    #Makes clouds
    counter = 0
    obj = scene.objects.active
    os.chdir(pickleLocation)
    pkl_file=open('clouds.20020906G050.pkl', 'rb')
    CldFrcTot = pickle.load(pkl_file,fix_imports=True,encoding='bytes')
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

    for isc in range(horizontal_decimation // 2, 135, horizontal_decimation):
    #for isc in range(1):
        cloudTime = time.time()
        ysc_km = (isc - 135.0/2.0) * 15.0
        ysc = ysc_km / kmPerBlend

        for ifp in range(horizontal_decimation // 2, 90, horizontal_decimation):
        #for ifp in range(100):
            # align the "footprint" (cross-track or xtrack) dimension with the x axis.
            # The instrument scans at a constant rate taking an observation every 1.1 degrees,
            # centered on nadir (pointing straight down)
            scanang_deg = (ifp - 44.5) * 1.1
            # convert scan angle to radians for trig
            scanang_rad = np.radians(scanang_deg)
            # get the position of each footprint center using simple trig (flat Earth approximation)
            xfp_km = satHeight_km * np.tan(scanang_rad)
            # convert x position in km to blender units
            xfp = xfp_km / kmPerBlend
            # are there 0, 1 or 2 clouds in this spot?
            numCloud = int(nCld[isc, ifp])

            for icl in range(numCloud):
                # input field PCldTop gives cloud pressure heights in hPa, but we want km
                # NOAA formula to convert pressure in hPa to altitude in feet
                # (1-(hPa/1013.25)^{.190284})*145366.45
                # This is for a standard atmosphere, but good enough!
                zcl_feet = (1 - np.power(PCldTop[isc, ifp, icl] / 1013.25, 0.190284)) * 145366.45
                zcl_km = zcl_feet * 0.3048 * 0.001
                zcl = (verticalMag * zcl_km) / kmPerBlend

                if cl == 0:
                    # the cloud fraction of the first (top) cloud layer can be used as-is
                    frac = CldFrcStd[isc, ifp, icl]
                else:
                    # the cloud fraction of the second (bottom) cloud layer is only what fraction
               	    # of the scene as seen by the instrument is covered by this cloud layer, so that
               	    # the two cloud fractions never add up to more than 1.0.  But we can assume
               	    # there is a similar amount of the lower cloud under the parts of the scene covered
               	    # by the upper cloud.
                    frac = CldFrcStd[isc,ifp,icl] / (1.0 - CldFrcStd[isc,ifp,0])

                # express cloud fraction as optical depth
                if frac > 0.9999546:
                    opticalDepth = 10
                else:
                    opticalDepth = np.log(1.0 / (1.0 - frac))

                # assume cloud thickness relates to optical depth
                thickness = 0.02 * optical_depth

                xsmear = 1.25
                hmag = 1.0 / np.cos(scanang_rad)
                xelong = 1.0 / np.cos(scanang_rad)
                radius = (horizontal_decimation * xsmear * hmag * xelong) / 30

                #Radius = horizontal_decimation * xsmear * hmag * xelong
                mesh.primitive_cylinder_add(radius = radius, view_align=False, enter_editmode=False, location=(xfp, ysc, zcl))

                if merge == True:
                    for ob in bpy.context.scene.objects:
                        if ob.type == 'MESH':
                            ob.select = True
                            bpy.context.scene.objects.active = ob
                        else:
                            ob.select = False
                        bpy.ops.object.join()

                if objectsToClouds == True:
                    bpy.ops.cloud.generate_cloud()


        print("****** \nIt took " + str((time.time()) - cloudTime) + " to generate clouds #", + (isc + 1))

clearScene()
setup()
ObjectCreation()
