import bpy
import random
import pickle
import numpy as np
import sys
from math import pi
import argparse

parser = argparse.ArgumentParser('Display AIRS clouds in 3D')

parser.add_argument('--date', action='store', dest='date',
                    default='20020906',
                    help='date yyyymmdd')
parser.add_argument('--gran', action='store', dest='gran',
                    default=50, type=int,
                    help='granule number [1-240]')
parser.add_argument('--sub', action='store', dest='subsample',
                    default=1, type=int,
                    help='subsampling factor for horizontal decimation [1-5]')
parser.add_argument('--cirrus', action='store_true', default=False,
                    help='Plot Kahn cirrus cloud results')
parser.add_argument('--colorby', action='store', default='',
                    help='field by which to color clouds')


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


def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)


def render_and_save():
  # for quality in [10, 100]:
  # Does not make any obvious difference with crude clouds
  for quality in [100]:
    # trade off speed vs quality.  quality can be from 1 to 100
    bpy.context.scene.cycles.samples = 70 + quality * 10
    bpy.context.scene.cycles.max_bounces = quality / 8
    bpy.context.scene.cycles.min_bounces = quality / 16
    bpy.context.scene.cycles.transparent_max_bounces = quality / 7.5
    bpy.context.scene.cycles.transparent_min_bounces = quality / 7.5
    if quality < 51:
      bpy.context.scene.cycles.no_caustics = True
      bpy.context.scene.cycles.use_transparent_shadows = False
      bpy.context.scene.render.use_motion_blur = False
    else:
      bpy.context.scene.cycles.no_caustics = False
      bpy.context.scene.cycles.use_transparent_shadows = True
      bpy.context.scene.render.use_motion_blur = True

    print("Starting render quality: ", quality)
    if args.subsample > 1:
      subdot="sub{0}.".format(args.subsample)
    else:
      subdot=''
    if args.colorby != '':
      bydot="{0}.".format(args.colorby.lower())
    else:
      bydot=''
    bpy.context.scene.render.filepath = \
                    "/home/evan/python/blender/cloud.{0}G{1:03d}.".format(args.date, args.gran) \
                    + bydot + subdot + 'png'
    bpy.ops.render.render(write_still=True, use_viewport=True)
    print("Render complete")

# set an appropriate value for each legal value of cloud_phase_3x3
# should use a dictionary instead
# but also shouldn't need a distinct material per color.  Use the same material and just set the color?
def phasecolor(cloud_phase):
  if cloud_phase == -9999:
    return phase_m9999_color
  if cloud_phase == -2:
    return phase_m2_color
  if cloud_phase == -1:
    return phase_m1_color
  if cloud_phase ==  0:
    return phase_00_color
  if cloud_phase ==  1:
    return phase_p1_color
  if cloud_phase ==  2:
    return phase_p2_color
  if cloud_phase ==  3:
    return phase_p3_color
  if cloud_phase ==  4:
    return phase_p4_color

def make_clouds():
  # can't currently read AIRS HDF files from python 3, so get them from a pickle file created using python 2.7
  pkl_file=open('clouds.'+args.date+'G{0:03d}'.format(args.gran)+'.pkl', 'rb')
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

  # clear away the Cube blender starts with by default
  for ob in bpy.context.scene.objects:
    ob.select = ob.type == 'MESH' and ob.name.startswith("Cube")
  bpy.ops.object.delete()

  # red = makeMaterial('Red', (1,0,0), (1,1,1), 1)
  blue = makeMaterial('BlueSemi', (0,0,1), (0.5,0.5,0), 0.5)
  white = makeMaterial('White', (1,1,1), (0.0,0.0,0.0), 0.25)
  layers_tfff=(True, False, False, False, False, False, False, False, False, False,
                  False, False, False, False, False, False, False, False, False, False)

  # Start with a plane representing the Earth
  bpy.ops.mesh.primitive_plane_add(radius=5, view_align=False, enter_editmode=False,
                  location=(0, 0, 0), layers=layers_tfff)
  setMaterial(bpy.context.object, blue)


  satheight_km = 715. # average, but close enough.  varies in [702, 731] km
  km_per_blend = 300 # conversion factor between blender units and kilometers
  vertical_mag = 10 # vertical magnification.  puts the clouds 10x higher/thicker than they should be

  # for speed.  skip most clouds but make the remaining ones bigger.  This saves time not so much
  # in rendering as in adding objects.
  #   1 Uses all observations: 135x90
  #   2 skips every other in each dimension (1 in 4 plotted)
  #   3 skips 2/3 in each dimension (1 in 9 plotted -- one per FOR)
  horizontal_decimation = args.subsample

  # cloud_phase_3x3
  # Flag telling whether clouds are ice or liquid water
  # -9999: No cloud phase retrieval was possible
  #    -2: Liquid water (high confidence)
  #    -1: Liquid water (low confidence)
  #     0: Unknown
  #     1: Ice (low confidence)
  #     2: Ice (higher confidence)
  #     3: Ice (very high confidence)
  #     4: Ice (very high confidence)
  if args.colorby.lower() == 'cloud_phase_3x3':
    global phase_m9999_color, phase_m2_color, phase_m1_color, phase_00_color
    global phase_p1_color, phase_p2_color, phase_p3_color, phase_p4_color
    phase_m9999_color = makeMaterial('Phase-9999', (0.5,0.5,0.5), (0.0,0.0,0.0), 0.25)
    # From colorbrewer2.org first diverging color scheme
    # 7-class for negative; 9-class for positive
    phase_m2_color = makeMaterial('Phase-2', (166./254., 97./254., 26./254.), (0.0,0.0,0.0), 0.25)
    phase_m1_color = makeMaterial('Phase-1', (223./254.,194./254.,125./254.), (0.0,0.0,0.0), 0.25)
    phase_00_color = makeMaterial('Phase+0', (245./254.,245./254.,245./254.), (0.0,0.0,0.0), 0.25)
    phase_p1_color = makeMaterial('Phase+1', (199./254.,234./254.,229./254.), (0.0,0.0,0.0), 0.25)
    phase_p2_color = makeMaterial('Phase+2', (128./254.,205./254.,193./254.), (0.0,0.0,0.0), 0.25)
    phase_p3_color = makeMaterial('Phase+3', ( 53./254.,151./254.,143./254.), (0.0,0.0,0.0), 0.25)
    phase_p4_color = makeMaterial('Phase+4', (  1./254.,102./254., 94./254.), (0.0,0.0,0.0), 0.25)
    # simpler manual coloring
    # phase_m2_color = makeMaterial('Phase-2', (1.0,0.0,0.0), (0.0,0.0,0.0), 0.25)
    # phase_m1_color = makeMaterial('Phase-1', (0.8,0.2,0.0), (0.0,0.0,0.0), 0.25)
    # phase_00_color = makeMaterial('Phase+0', (0.5,0.5,0.0), (0.0,0.0,0.0), 0.25)
    # phase_p1_color = makeMaterial('Phase+1', (0.3,0.7,0.0), (0.0,0.0,0.0), 0.25)
    # phase_p2_color = makeMaterial('Phase+2', (0.2,0.8,0.0), (0.0,0.0,0.0), 0.25)
    # phase_p3_color = makeMaterial('Phase+3', (0.1,0.9,0.0), (0.0,0.0,0.0), 0.25)
    # phase_p4_color = makeMaterial('Phase+4', (0.0,1.0,0.0), (0.0,0.0,0.0), 0.25)

  # loop over 135 scans in the granule
  for isc in range(horizontal_decimation // 2, 135, horizontal_decimation):
    # Align y axis with the "along-track" direction -- where the spacecraft is travelling
    # each 6-minute granule has 135 scans, evenly spaced ~15 km apart
    print("processing Scan ", isc+1, " of 135")
    ysc_km = (isc - 135/2.) * 15.     # place the origin in the center
    ysc = ysc_km / km_per_blend
    for ifp in range(horizontal_decimation // 2, 90, horizontal_decimation):
      # align the "footprint" (cross-track or xtrack) dimension with the x axis.
      # The instrument scans at a constant rate taking an observation every 1.1 degrees,
      # centered on nadir (pointing straight down)
      scanang_deg = (ifp - 44.5) * 1.1
      # convert scan angle to radians for trig
      scanang_rad = np.radians(scanang_deg)
      # get the position of each footprint center using simple trig (flat Earth approximation)
      xfp_km = satheight_km * np.tan(scanang_rad) # 15 km at nadir
      # convert x position in km to blender units
      xfp = xfp_km / km_per_blend
      # are there 0, 1 or 2 clouds in this spot?
      numCloud=int(nCld[isc,ifp])
      for icl in range(numCloud):
        # input field PCldTop gives cloud pressure heights in hPa, but we want km
        # NOAA formula to convert pressure in hPa to altitude in feet
        # (1-(hPa/1013.25)^{.190284})*145366.45
        # This is for a standard atmosphere, but good enough!
        zcl_feet = (1 - np.power(PCldTop[isc,ifp,icl] / 1013.25, .190284)) * 145366.45
        zcl_km = zcl_feet * 0.3048 * 0.001
        zcl = vertical_mag * zcl_km / km_per_blend
        # print(isc,ifp,icl,xfp,ysc,zcl)

	# If we're here then there can be 1 or 2 cloud layers.
        if icl == 0:
	  # the cloud fraction of the first (top) cloud layer can be used as-is
          frac = CldFrcStd[isc,ifp,icl]
        else:
	  # the cloud fraction of the second (bottom) cloud layer is only what fraction
	  # of the scene as seen by the instrument is covered by this cloud layer, so that
	  # the two cloud fractions never add up to more than 1.0.  But we can assume
	  # there is a similar amount of the lower cloud under the parts of the scene covered
	  # by the upper cloud.
          frac = CldFrcStd[isc,ifp,icl] / (1.0 - CldFrcStd[isc,ifp,0])

	# express cloud fraction as optical depth
        if frac > 0.9999546:
          optical_depth = 10
        else:
          optical_depth = np.log(1.0 / (1.0 - frac))
        # assume cloud thickness relates to optical depth
        thickness = 0.02 * optical_depth

	# cloud is a disk
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=thickness,
                            view_align=False,
                            enter_editmode=False,
                            location=(xfp, ysc, zcl - thickness / 2.0))
        if args.colorby == '':
          setMaterial(bpy.context.object, white)
        elif args.colorby.lower() == 'cloud_phase_3x3':
          setMaterial(bpy.context.object, phasecolor(cloud_phase_3x3[isc,ifp]))
        else:
          print('Unknown colorby: ', args.colorby)
          exit()

        # Scale the cloud voxel along the x (scan) axis
        ob = bpy.context.object

	# AIRS is continuous scan, so the area of each FOV is elongated in the
	# scan direction
        xsmear = 1.25

	# The farther we are from the spacecraft the larger the FOV gets
        hmag = 1. / np.cos(scanang_rad) # horizontal magnification

        # the FOV also gets stretched into an ellipse along the scan direction
        xelong = 1. / np.cos(scanang_rad) # x elongation (flat Earth)

        ob.scale = (horizontal_decimation * xsmear * hmag * xelong,
                    horizontal_decimation * hmag,
                    1.0)
        bpy.ops.object.transform_apply(scale=True)



if __name__ == "__main__":

  # need to trim args because the original list includes the whole blender + python command
  # print(sys.argv[5:])
  args = parser.parse_args(sys.argv[5:])
  # print(args)


  make_clouds()
render_and_save()
