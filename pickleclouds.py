#!/opt/python/python-2.7/bin/python

import os
import pickle

import numpy as np

import sys, argparse

parser = argparse.ArgumentParser('Display clouds in 3D -- preprocessor to read HDF and write pickle')

parser.add_argument('--date', action='store', dest='date',
                    default='20020906',
                    help='date yyyymmdd')
parser.add_argument('--gran', action='store', dest='gran',
                    default=50, type=int,
                    help='granule number [1-240]')


def pkl_fld_45x30(tag, hdf, pkl_file):
  var = hdf.select(tag)
  print tag, np.array(var[0,0])
  pickle.dump(np.array(var[:,:]), pkl_file, 2)

def pkl_fld_45x30x3x3(tag, hdf, pkl_file):
  var = hdf.select(tag)
  var45x30x3x3 = np.array(var[:,:,:,:])
  # print np.shape(var45x30x3x3)
  # (45, 30, 3, 3)
  var135x90 = np.zeros((135,90))
  for i in range(3):
    for j in range(3):
      var135x90[i::3,j::3] = var45x30x3x3[:,:,i,j]
  # print var45x30x3x3[0,0,0,0], var135x90[0,0]
  # print var45x30x3x3[-1,-1,-1,-1], var135x90[-1,-1]
  pickle.dump(var135x90, pkl_file, 2)

def pkl_fld_45x30x3x3x2(tag, hdf, pkl_file):
  var = hdf.select(tag)
  var45x30x3x3x2 = np.array(var[:,:,:,:,:])
  # print np.shape(var45x30x3x3x2)
  # (45, 30, 3, 3, 2)
  var135x90x2 = np.zeros((135,90,2))
  for i in range(3):
    for j in range(3):
      var135x90x2[i::3,j::3,:] = var45x30x3x3x2[:,:,i,j,:]
  # print var45x30x3x3x2[0,0,0,0,0], var135x90x2[0,0,0]
  # print var45x30x3x3x2[-1,-1,-1,-1,-1], var135x90x2[-1,-1,-1]
  pickle.dump(var135x90x2, pkl_file, 2)

# test:  pickleclouds('/archive/AIRSOps/airs/gdaac/v6/2002/09/06/airx2sup/AIRS.2002.09.06.050.L2.RetSup.v6.0.7.0.G13202072140.hdf', clouds.pkl')

def pickleclouds(filename_in_hdf, filename_out_pkl):
  from pyhdf.SD import SD, SDC
  # (dirname, filename) = os.path.split(filename_in_hdf)
  # print filename
  hdf = SD(filename_in_hdf, SDC.READ)
  pkl_file = open(filename_out_pkl, 'wb')
  # Read dataset.
  # CldFrcTot = hdf.select('CldFrcTot')
  # CldFrcTot = np.array(CldFrcTot[:,:])
  # pickle.dump(CldFrcTot, pkl_file, 2)
  pkl_fld_45x30('CldFrcTot', hdf, pkl_file)
  pkl_fld_45x30('CldFrcTot_QC', hdf, pkl_file)
  pkl_fld_45x30('Latitude', hdf, pkl_file)
  pkl_fld_45x30('Longitude', hdf, pkl_file)
  pkl_fld_45x30x3x3('latAIRS', hdf, pkl_file)
  pkl_fld_45x30x3x3('lonAIRS', hdf, pkl_file)
  pkl_fld_45x30x3x3('nCld', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('CldFrcStd', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('CldFrcStd_QC', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('CldFrcStdErr', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('PCldTop', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('PCldTop_QC', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('PCldTopErr', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('TCldTop', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('TCldTop_QC', hdf, pkl_file)
  pkl_fld_45x30x3x3x2('TCldTopErr', hdf, pkl_file)
  pkl_fld_45x30x3x3('cloud_phase_3x3', hdf, pkl_file)
  pkl_fld_45x30x3x3('cloud_phase_bits', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_opt_dpth', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_opt_dpth_QC', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_opt_dpth_ave_kern', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_eff_diam', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_eff_diam_QC', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_eff_diam_ave_kern', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_temp_eff', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_temp_eff_QC', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_temp_eff_ave_kern', hdf, pkl_file)
  pkl_fld_45x30x3x3('ice_cld_fit_reduced_chisq', hdf, pkl_file)

  pkl_file.close()
  print ''
        
  # Replace the filled value with NaN, replace with a masked array.
  # data[data == -9999] = np.nan
  # datam = np.ma.masked_array(data, np.isnan(data))
    
if __name__ == "__main__":
  print sys.argv[1:]
  args = parser.parse_args(sys.argv[1:])
  print args

  # year=2002
  # month=9
  # day=6
  # gran=50
  # cyear='{0:04d}'.format(year)
  # cmonth='{0:02d}'.format(month)
  # cday='{0:02d}'.format(day)
  # cgran='{0:03d}'.format(gran)
  cyear=args.date[0:4]
  cmonth=args.date[4:6]
  cday=args.date[6:8]
  cgran='{0:03d}'.format(args.gran)
  dir='/archive/AIRSOps/airs/gdaac/v6/'+cyear+'/'+cmonth+'/'+cday+'/airx2sup/'
  print dir
  for file in os.listdir(dir):
    if file.startswith('AIRS.'+cyear+'.'+cmonth+'.'+cday+'.'+cgran) and file.endswith(".hdf"):
      print file
      pickleclouds(os.path.join(dir,file), 'clouds.'+args.date+'G'+cgran+'.pkl')
