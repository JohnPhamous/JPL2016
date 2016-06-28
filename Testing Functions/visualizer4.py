# Different than 3: Renders cylinders as clouds, this speeds up the creation by cloning each object rather than creating a new one

import bpy, random, argparse, sys, time, pickle, os
from random import randint
import numpy as np
from math import pi
from tqdm import *

# Used to track how much time elapsed
startTime = time.time()

merge = False
camera1 = True
camera2 = False
camera3 = False
colorObjects = True
testingObject = False

date = "20020906"
granule = "50"
# 1 all, 2 every other, 3 skips 2/3
horizontal_decimation = 3
satHeight_km = 715
kmPerBlend = 300
verticalMag = 10
colorScheme = 'cloud_phase_3x3'
pickleLocation = "/Users/John/GitHub/JPL2016"
layers_tfff = (True, False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False, False)


def makeMaterial(name, diffuse, specular, thickness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.alpha = thickness
    mat.ambient = 1
    return mat


# Color Paremeters
blue = makeMaterial('BlueSemi', (0, 0, 1), (0.5, 0.5, 0.5), 1)


def setMaterial(obj, mat):
    obj.data.materials.append(mat)
    return


def setup():
    # Light source setup
    bpy.ops.object.lamp_add(type='SUN', radius=1, view_align=False,
                    location=(-1, 20, 18))

    # Camera setup
    if camera1:
        # Front down angle
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(0, -15, 5))
        bpy.ops.transform.rotate(value=1.16299, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL',
                             mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    if camera2:
        # 45 down angle
        bpy.ops.object.camera_add(
            view_align=True, enter_editmode=False, location=(8, -8, 3))
        bpy.ops.transform.rotate(value=1.36011, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL',
                                 mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        bpy.ops.transform.rotate(value=0.8, axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL',
                                 mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
    if camera3:
        # Side
        bpy.ops.object.camera_add(view_align=True, enter_editmode=False,
                          location=(12.5, -.3, 4))
        bpy.ops.transform.rotate(value=1.5, axis=(0, 1, 0), constraint_axis=(False, False, True), constraint_orientation='GLOBAL',
                                 mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        bpy.ops.transform.rotate(value=1.25489, axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL',
                                 mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
        bpy.ops.transform.rotate(value=0.0840454, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL',
                                 mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
    return


def earthSetup():
    # TODO: Add Earth texture
    mesh.primitive_plane_add(radius=50, view_align=False, enter_editmode=False, location=(
        0, 0, -1), layers=layers_tfff)
    setMaterial(context.object, blue)
    bpy.context.object.active_material.use_raytrace = False
    bpy.context.object.active_material.use_mist = False
    bpy.context.object.active_material.use_cast_shadows = False
    bpy.context.object.active_material.use_cast_buffer_shadows = False
    bpy.context.object.active_material.use_cast_approximate = False
    return


def clearScene():
    # Clears the current scene
    for obj in bpy.context.scene.objects:
        bpy.context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    return


def randomNum(min, max):
    # Used for test cases
    num = round(random.uniform(min, max), 10)
    return num


def joinObjects():
    # Merges all of the created objects
    for ob in context.scene.objects:
        if ob.type == 'MESH':
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
        ops.object.join()
    return


def testObject():
    bpy.ops.mesh.primitive_cylinder_add(radius=(1), depth=(
        1), view_align=False, enter_editmode=False, location=(0, 0, 0))
    matProperties = makeMaterial(
        'BlueSemi', (0, .25, 1), (0.5, 0.5, 0.5), (10))
    setMaterial(bpy.context.object, matProperties)
    bpy.context.object.active_material.use_transparency = True
    bpy.context.object.active_material.transparency_method = 'RAYTRACE'
    bpy.context.object.active_material.raytrace_transparency.fresnel = 2
    bpy.context.object.active_material.raytrace_transparency.depth = 50
    bpy.context.object.active_material.raytrace_transparency.ior = 1.3
    bpy.context.object.active_material.raytrace_transparency.fresnel_factor = 1.25
    bpy.context.object.active_material.subsurface_scattering.use = True
    return

def copyObject():
    
def ObjectCreation():
    # can't currently read AIRS HDF files from python 3, so get them from a
    # pickle file created using python 2.7
    os.chdir(pickleLocation)
    # Pickle stuff by Evan Manning
    pkl_file = open('clouds.20020906G050.pkl', 'rb')
    CldFrcTot = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    CldFrcTot_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    Latitude = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    Longitude = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    latAIRS = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    lonAIRS = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    nCld = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    CldFrcStd = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    CldFrcStd_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    CldFrcStdErr = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    PCldTop = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    PCldTop_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    PCldTopErr = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    TCldTop = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    TCldTop_QC = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    TCldTopErr = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    cloud_phase_3x3 = pickle.load(pkl_file, fix_imports=True, encoding='bytes')
    cloud_phase_bits = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_opt_dpth = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_opt_dpth_QC = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_opt_dpth_ave_kern = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_eff_diam = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_eff_diam_QC = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_eff_diam_ave_kern = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_temp_eff = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_temp_eff_QC = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_temp_eff_ave_kern = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    ice_cld_fit_reduced_chisq = pickle.load(
        pkl_file, fix_imports=True, encoding='bytes')
    pkl_file.close()

    for isc in tqdm(range(horizontal_decimation // 2, 135, horizontal_decimation), desc='Creating objects', leave=True):
        # for isc in range(1):
        cloudTime = time.time()
        ysc_km = (isc - 135.0 / 2.0) * 15.0
        ysc = ysc_km / kmPerBlend

        for ifp in range(horizontal_decimation // 2, 90, horizontal_decimation):
            # for ifp in range(10):
            # align the "footprint" (cross-track or xtrack) dimension with the x axis.
            # The instrument scans at a constant rate taking an observation every 1.1 degrees,
            # centered on nadir (pointing straight down)
            scanang_deg = (ifp - 44.5) * 1.1
            # convert scan angle to radians for trig
            scanang_rad = np.radians(scanang_deg)
            # get the position of each footprint center using simple trig (flat
            # Earth approximation)
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
                zcl_feet = (
                    1 - np.power(PCldTop[isc, ifp, icl] / 1013.25, 0.190284)) * 145366.45
                zcl_km = zcl_feet * 0.3048 * 0.001
                zcl = (verticalMag * zcl_km) / kmPerBlend

                if icl == 0:
                    # the cloud fraction of the first (top) cloud layer can be
                    # used as-is
                    frac = CldFrcStd[isc, ifp, icl]
                else:
                    # the cloud fraction of the second (bottom) cloud layer is only what fraction
                    # of the scene as seen by the instrument is covered by this cloud layer, so that
                    # the two cloud fractions never add up to more than 1.0.  But we can assume
                    # there is a similar amount of the lower cloud under the parts of the scene covered
                    # by the upper cloud.
                    frac = CldFrcStd[isc, ifp, icl] / \
                        (1.0 - CldFrcStd[isc, ifp, 0])

                # express cloud fraction as optical depth
                if frac > 0.9999546:
                    opticalDepth = 10
                else:
                    opticalDepth = np.log(1.0 / (1.0 - frac))

                # assume cloud thickness relates to optical depth
                thickness = 0.02 * opticalDepth
                smallFactor = 1
                #Radius = horizontal_decimation * xsmear * hmag * xelong
                bpy.ops.mesh.primitive_cylinder_add(radius=(0.02 / smallFactor), depth=(thickness / smallFactor),
                                            view_align=False, enter_editmode=False, location=(xfp, ysc, (zcl - thickness / 2.0)))

                if colorObjects:
                    if thickness < .01:
                        thickness * 100
                    matProperties = makeMaterial(
                        'BlueSemi', (0, .25, 1), (0.5, 0.5, 0.5), (thickness * 10))
                    setMaterial(bpy.context.object, matProperties)
                    bpy.context.object.active_material.use_transparency = True
                    bpy.context.object.active_material.transparency_method = 'RAYTRACE'
                    bpy.context.object.active_material.raytrace_transparency.fresnel = 2
                    bpy.context.object.active_material.raytrace_transparency.depth = 50
                    bpy.context.object.active_material.raytrace_transparency.ior = 1.3
                    bpy.context.object.active_material.raytrace_transparency.fresnel_factor = 1.25
                    #bpy.context.object.active_material.subsurface_scattering.use = True
                    # bpy.ops.script.python_file_run(filepath="/Applications/blender.app/Contents/Resources/2.77/scripts/presets/sss/whole_milk.py")

                    #bpy.context.object.active_material.use_shadeless = True

                xsmear = 1.25
                hmag_xelong = 1.0 / np.cos(scanang_rad)

                bpy.context.object.scale = (horizontal_decimation * xsmear * hmag_xelong *
                                        hmag_xelong, horizontal_decimation * hmag_xelong, 1.0)
                bpy.ops.object.transform_apply(scale=True)

print("\nStarting visualization...")
print("Clearing original scene...")
clearScene()
print("Setting up new scene...")
setup()

if testingObject:
    testObject()
else:
    ObjectCreation()

if merge:
    print("Merging all objects...")
    joinObjects()

earthSetup()

print("\nTime(seconds)__________", (time.time()) - startTime)
print("Granule________________", granule)
print("Horizontal Decimation__", horizontal_decimation)
print("Clouds_________________", objectsToClouds)