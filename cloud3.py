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



def make_clouds():
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
  # print(cloud_phase_bits)

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
  vertical_mag = 10 # vertical magnification.  puts the clouds 10x higher than they should be

  # for speed.  skip most clouds but make the remaining ones bigger.  This saves time not so much
  # in rendering as in adding objects.
  #   1 Uses all observations: 135x90
  #   2 skips every other in each dimension (1/4 plotted)
  #   3 skips 2/3 in each dimension (1/9 plotted -- one per FOR)
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
    phase_m2_color = makeMaterial('Phase-2', (1.0,0.0,0.0), (0.0,0.0,0.0), 0.25)
    phase_m1_color = makeMaterial('Phase-1', (0.8,0.2,0.0), (0.0,0.0,0.0), 0.25)
    phase_00_color = makeMaterial('Phase+0', (0.5,0.5,0.0), (0.0,0.0,0.0), 0.25)
    phase_p1_color = makeMaterial('Phase+1', (0.3,0.7,0.0), (0.0,0.0,0.0), 0.25)
    phase_p2_color = makeMaterial('Phase+2', (0.2,0.8,0.0), (0.0,0.0,0.0), 0.25)
    phase_p3_color = makeMaterial('Phase+3', (0.1,0.9,0.0), (0.0,0.0,0.0), 0.25)
    phase_p4_color = makeMaterial('Phase+4', (0.0,1.0,0.0), (0.0,0.0,0.0), 0.25)

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
        # print(isc,ifp,icl,numCloud)
	# input field PCldTop gives cloud heights in hPa, but we want km
        # NOAA formula to convert pressure in hPa to altitude in feet
        # (1-(hPa/1013.25)^{.190284})*145366.45
        # This is for a standard atmosphere, but good enough!
        zcl_feet = (1 - np.power(PCldTop[isc,ifp,icl] / 1013.25, .190284)) * 145366.45
        zcl_km = zcl_feet * 0.3048 * 0.001
        zcl = vertical_mag * zcl_km / km_per_blend
        # print(isc,ifp,icl,xfp,ysc,zcl)
        bpy.ops.mesh.primitive_cylinder_add(radius=.02, depth=.02, view_align=False,
                            enter_editmode=False, location=(xfp, ysc, zcl))
        if args.colorby == '':
          setMaterial(bpy.context.object, white)
        elif args.colorby.lower() == 'cloud_phase_3x3':
          setMaterial(bpy.context.object, phasecolor(cloud_phase_3x3[isc,ifp]))
        else:
          print('Unknown colorby: ', args.colorby)
          exit()
        # Scale the cloud voxel along the x (scan) axis
        ob = bpy.context.object
        xsmear = 1.25 # from continuous scan
        hmag = 1. / np.cos(scanang_rad) # horizontal magnification
        xelong = 1. / np.cos(scanang_rad) # x elongation (flat Earth)
        ob.scale = (horizontal_decimation * xsmear * hmag * xelong,
                    horizontal_decimation * hmag,
                    1.0)
        bpy.ops.object.transform_apply(scale=True)



if __name__ == "__main__":

  print(sys.argv[5:])  # need to trim args because the original list includes the whole blender + python command
  args = parser.parse_args(sys.argv[5:])
  print(args)


  make_clouds()
  render_and_save()

""" Need to do:

Basics:
  - speed up creating 10,000+ cloud objects:
    - don't use primitive_cylinder_add!
  	http://blender.stackexchange.com/questions/39721/how-can-i-create-many-objects-quickly
	http://blender.stackexchange.com/questions/7358/python-performance-with-blender-operators
  - move the camera to 500 km above the y axis, maybe 1000 km from the origin
  - better lighting -- extended source and glowing sky
  - more pixels
  - make clouds transparent
    - use CldFrcStd to determine transparency (alternate ice_cld_opt_dpth)

Step it up:
  - put down a map
    - requires using LatAIRS & LonAIRS for horizontal locations instead of current granule coordinates
    - terrain elevation should be enhanced as for clouds
  - curve the world

Use more fields for coloring:
  - need to make 100s or 1000s of colors, preferably without making a separate material for each
  - better sets of colors.  Colorbrewer brewer2mpl.
  - Fields to use include:
    - TCldTop
    - PCldTop
    - each bit of cloud_phase_3x3
    - ice_cld_*

3-D:
  - subtle color by cloud height
    - but only if not also using color for other purposes or red/green stereo
  - 3-D grid
  - stereo: two cameras
    - red/green
       - monochrome images only
    - polarization
      - need special monitor or printer
    - shutters
      - need special monitor
  - animation
    - travel along satellite track, looking ahead/down
    - eventually stitch together several granules or even a whole day
    - looking at the globe from a fixed point as orbits are added
      - especially poles

Photorealistic clouds:
  - random shapes
  - parameterization for cloud thickness?
  - subpixel horizontal variability
    - from AIRS V/NIR or MODIS for daytime
    - from a parameterization

Display with other data sources:
  - translucent clouds above AIRS data fields to illustrate how clouds impact retrieval
    - cloud cleared radiance for a window channel
    - surface temperature
  - CloudSat
  - CALIPSO
  - MODIS clouds
  - clouds from other hyperspectral sounder suites
    - CrIMSS (Joel or NUCAPS or?)
    - IASI (especially polar)

AIRS Level-3:
  - monthly average cloud distribution
    - diffuse

Other cloud-like AIRS products:
  - carbon monoxide
  - volcanic SO2


Boring stuff:
  - clean up code:
    - read HDF directly in python3
    - use objects, moduels, etc.
    - general clean-up
  - make old-style 2-D visualizations that correspond to the new 3-D visualizations for contrast
"""
