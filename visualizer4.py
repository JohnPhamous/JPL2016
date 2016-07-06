# TODO: Volume density, correct geolocations, add stars to scene
import bpy
import random
import argparse
import sys
import time
import pickle
import os
from random import randint
import numpy as np
from math import pi
from tqdm import *

# Used to track how much time elapsed
startTime = time.time()

colorObjectsSwitch = False

date = "20020906"
granule = "50"
horizontal_decimation = 15
satHeight_km = 715
kmPerBlend = 300
verticalMag = 10
colorScheme = 'cloud_phase_3x3'
pickleLocation = "/Users/John/GitHub/JPL2016"
aqua = "/Users/John/Github/JPL2016/Additionals/Models/Aqua.fbx"

layers_tfff = (True, False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False, False)
originX = 0
originY = 0


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
blue = (0, 0, 1)
red = (1, 0, 0)


def setMaterial(obj, mat):
    obj.data.materials.append(mat)
    return


def setup():
    # Light source setup
    bpy.ops.object.lamp_add(type='SUN', radius=1, view_align=False,
                            location=(-1, 20, 18))

    # Front down angle
    bpy.ops.object.camera_add(
        view_align=True, enter_editmode=False, location=(0, -15, 5))
    bpy.ops.transform.rotate(value=1.16299, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL',
                             mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    return


def sceneSetup():
    # Sets up sphere
    bpy.ops.mesh.primitive_uv_sphere_add(ring_count=32, segments=64)
    bpy.context.object.location[0] = 0
    bpy.context.object.location[1] = 6.5
    bpy.context.object.location[2] = -101.979
    bpy.context.object.scale[0] = 100
    bpy.context.object.scale[1] = 100
    bpy.context.object.scale[2] = 100
    matProperties = makeMaterial('Globe', (1, 1, 1), (1, 1, 1), (1))
    matProperties.specular_intensity = 0
    setMaterial(bpy.context.object, matProperties)
    bpy.context.object.active_material.use_cast_shadows = False
    bpy.context.object.active_material.diffuse_shader = 'MINNAERT'
    bpy.context.object.active_material.use_transparent_shadows = True
    bpy.context.object.active_material.darkness = 0.3
    bpy.context.object.active_material.use_cast_buffer_shadows = False
    bpy.context.scene.world.horizon_color = (0, 0, 0)

    # Applies Earth texture to sphere
    earthTexturePath = os.path.expanduser(
        '/Users/John/Github/JPL2016/Additionals/Textures/earth2.jpg')
    img = bpy.data.images.load(earthTexturePath)
    tex = bpy.data.textures.new('EarthTexture', type='IMAGE')
    tex.image = img
    atex = matProperties.texture_slots.add()
    atex.texture = tex
    atex.texture_coords = 'ORCO'
    atex.use_map_color_diffuse = True
    atex.mapping = 'SPHERE'
    bpy.context.object.active_material.use_transparent_shadows = True

    # Sets up heights of terrain
    earthBumpTexturePath = os.path.expanduser(
        '/Users/John/Github/JPL2016/Additionals/Textures/bump.jpg')
    img2 = bpy.data.images.load(earthBumpTexturePath)
    tex2 = bpy.data.textures.new('BumpTexture', type='IMAGE')
    tex2.image = img2
    atex2 = matProperties.texture_slots.add()
    atex2.texture = tex2
    atex2.mapping = 'SPHERE'
    atex2.texture_coords = 'ORCO'
    atex2.use_map_color_diffuse = False
    atex2.use_map_normal = True
    atex2.normal_factor = -0.2
    atex2.bump_method = 'BUMP_BEST_QUALITY'
    bpy.context.object.active_material.use_transparent_shadows = True

    # Sets up atmosphere
    bpy.ops.mesh.primitive_uv_sphere_add(ring_count=32, segments=64)
    bpy.context.object.location[0] = 0
    bpy.context.object.location[1] = 6.5
    bpy.context.object.location[2] = -101.979
    bpy.context.object.scale[0] = 101
    bpy.context.object.scale[1] = 101
    bpy.context.object.scale[2] = 101
    matAtmosphere = makeMaterial('Atmosphere', (0, 0.2, 1), (0, 0, 0), 1)
    setMaterial(bpy.context.object, matAtmosphere)
    bpy.context.object.active_material.use_transparency = True
    bpy.context.object.active_material.transparency_method = 'Z_TRANSPARENCY'
    bpy.context.object.active_material.raytrace_transparency.fresnel = 1.5
    bpy.context.object.active_material.raytrace_transparency.fresnel_factor = 2.4
    bpy.context.object.active_material.specular_intensity = 0
    bpy.context.object.active_material.alpha = 0.2
    bpy.context.object.active_material.use_transparent_shadows = True

    # Sets up stars
    bpy.context.scene.world.use_sky_blend = True
    bpy.context.scene.world.use_sky_real = True
    bpy.context.scene.world.zenith_color = (0, 0, 0)
    bpy.context.scene.world.horizon_color = (0, 0.00850224, 0.0252511)
    # TODO: Add star speckles
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


def testObject():
    bpy.ops.mesh.primitive_cylinder_add(radius=(1), depth=(
        1), view_align=False, enter_editmode=False, location=(0, 0, 0))
    matProperties = makeMaterial(
        'BlueSemi', (0, .25, 1), (0.5, 0.5, 0.5), (1))
    setMaterial(bpy.context.object, matProperties)
    bpy.context.object.active_material.use_transparency = True
    bpy.context.object.active_material.transparency_method = 'RAYTRACE'
    bpy.context.object.active_material.raytrace_transparency.fresnel = 2
    bpy.context.object.active_material.raytrace_transparency.depth = 50
    bpy.context.object.active_material.raytrace_transparency.ior = 1.3
    bpy.context.object.active_material.raytrace_transparency.fresnel_factor = 1.25
    bpy.context.object.active_material.subsurface_scattering.use = True
    return


def boundingBox(originX, originY):
    # max is 100 mBar, tropapoz, if under 0 mBar clouds are ignored
    x = originX - 1
    y = originY - 1
    bpy.ops.mesh.primitive_cube_add(radius=0.5)
    boxProperties = makeMaterial('BoundingBox', (red), (0.5, 0.5, 0.5), (1))
    setMaterial(bpy.context.object, boxProperties)
    bpy.ops.object.modifier_add(type='WIREFRAME')
    bpy.context.object.active_material.use_shadeless = True
    bpy.context.object.active_material.use_shadows = False
    bpy.context.object.active_material.use_ray_shadow_bias = False
    bpy.context.object.active_material.use_cast_shadows = False
    bpy.context.object.active_material.use_cast_buffer_shadows = False

    # Creates bounding boxes in x
    for i in range(6):
        # Creates bounding boxes in y
        for j in range(8):
            bpy.context.scene.objects.active.location = (x, y, 0)
            # Copies mesh data to create new bounding boxes
            obj = bpy.context.scene.objects.active.copy()
            obj.data = bpy.context.scene.objects.active.data.copy()
            bpy.context.scene.objects.link(obj)
            y += 1
        x += 1
        y = originY - 1
    return


def importModel(aqua):
    bpy.ops.import_scene.fbx(filepath=aqua, global_scale=0.5)
    bpy.ops.transform.rotate(value=-0.75, axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL',
                             mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)

    bpy.ops.transform.translate(value=(4, 0, 3), constraint_axis=(True, False, True), constraint_orientation='GLOBAL',
                                mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
    return


def joinObjects():
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
        bpy.ops.object.join()
    bpy.context.scene.cloud_type = '1'
    bpy.ops.cloud.generate_cloud()
    return

def randNum(min, max):
    randNum = random.randint(min, max)
    return randNum

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

    counter = 0

    for isc in tqdm(range(horizontal_decimation // 2, 135, horizontal_decimation), desc='Creating objects', leave=True):
        # for isc in range(10):

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

                # express cloud fraction as IR optical depth
                if frac > 0.9999546:
                    opticalDepth = 10
                else:
                    opticalDepth = np.log(1.0 / (1.0 - frac))

                # Visible optical depth = IR * 4

                # assume cloud thickness relates to optical depth
                thickness = 0.02 * opticalDepth
                smallFactor = 10

                bpy.ops.mesh.primitive_cylinder_add(radius=(0.02 / smallFactor), depth=(thickness / smallFactor),
                                                    view_align=False, enter_editmode=False, location=(xfp, ysc, (zcl - thickness / 2.0)))

                if colorObjectsSwitch:
                    if thickness < .01:
                        thickness * 100
                    matProperties = makeMaterial(
                        'White', (1, 1, 1), (0.5, 0.5, 0.5), (thickness * 10))
                    setMaterial(bpy.context.object, matProperties)
                    bpy.context.object.active_material.use_transparency = True
                    bpy.context.object.active_material.transparency_method = 'RAYTRACE'
                    bpy.context.object.active_material.raytrace_transparency.fresnel = 2
                    bpy.context.object.active_material.raytrace_transparency.depth = 50
                    bpy.context.object.active_material.raytrace_transparency.ior = 1.3
                    bpy.context.object.active_material.raytrace_transparency.fresnel_factor = 1.25

                xsmear = 1.25
                hmag_xelong = 1.0 / np.cos(scanang_rad)

                bpy.context.object.scale = ((horizontal_decimation * xsmear * hmag_xelong * hmag_xelong) /
                                            smallFactor, (horizontal_decimation * hmag_xelong) / smallFactor, 1.0 * smallFactor)
                bpy.ops.object.transform_apply(scale=True)

                # Setup for bonding boxes
                global originX
                global originY
                if counter == 0:
                    originX = xfp
                    originY = ysc
                    counter += 1

print("\nStarting visualization...")
print("Clearing original scene...")
clearScene()
print("Setting up new scene...")
setup()
# testObject()
ObjectCreation()
print("Converting to clouds...")
joinObjects()
print("Creating globe...")
sceneSetup()
print("Importing AQUA...")
importModel(aqua)
print("Creating bounding boxes...")
#boundingBox(originX, originY)


print("\nTime(seconds)__________", (time.time()) - startTime)
print("Granule________________", granule)
