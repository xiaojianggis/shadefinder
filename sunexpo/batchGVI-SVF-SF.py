# this is used to compute SVF, GVI for SF using street-side imagery
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab, Temple University

import os, os.path
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import cv2
import numpy as np
import sys
sys.path.append('../libraries/')
import StreetsideLib as sslib
import SpatialLib as spl
import SunExpoLib as sunexpo
import ImgprojLib as improj


# for SF
root = '/home/xiaojiang/xiaojiang/thermal-injustice/datasets/SF'
outputroot = '/home/xiaojiang/xiaojiang/thermal-injustice/datasets/SF/spatial-data'

# For Phily
root = '/home/jiang/Documents/researchProj/thermal-injustice/datasets/Philadephia'
outputroot = '/home/jiang/Documents/researchProj/thermal-injustice/datasets/Philadephia/spatial-data'


## Step 1-------- convert clyindrical seged image to seged hemispherical images
segCylinderImgs = os.path.join(root, 'seg_cylindri_panos')
segHemiImgs = os.path.join(root, 'seg_hemi_panos')
if not os.path.exists(segHemiImgs): os.mkdir(segHemiImgs)

improj.cylinder2fisheye(segCylinderImgs, segHemiImgs, 'streetside')



## Step 2 --------Compute GVI and SVF based on the seged hemispherical images
heading = 60
fov=90
pitch = 10

# cylinder_img = os.path.join(root, 'cylinder_img')
cylinder_img = os.path.join(root, 'seg_cylindri_panos')

panoIDlist = []
lonlist = []
latlist = []
yawlist = []
datelist = []
svflist = []
gvilist = []

seg_cylinder = os.path.join(root, 'seg_cylindri_panos')
seg_hemi = os.path.join(root, 'seg_hemi_panos')

num_files = len(os.listdir(seg_cylinder)) # number of files
batch_size = 1000 # process every 1000 pnts


for idx, file in enumerate(os.listdir(seg_cylinder)):
    if idx%100 == 0: print(idx)
    
    if idx%batch_size == 0 and idx >1:
        attr_dict = {'svf': svflist, 'yaw': yawlist, 'gvi': gvilist}
        outputfilename = 'gvi_svf%s000.shp'%(int(idx/batch_size))
        outputShapefile = os.path.join(outputroot, outputfilename)

        spl.CreatePointFeature_ogr(outputShapefile, lonlist, latlist, panoIDlist, datelist, attr_dict, 'metadata')
        print('created the file', outputShapefile)

        lonlist = []
        latlist = []
        yawlist = []
        datelist = []
        svflist = []
        gvilist = []
    
    elif idx == num_files - 1:
        attr_dict = {'svf': svflist, 'yaw': yawlist, 'gvi': gvilist}
        outputfilename = 'gvi_svf%s.shp'%(num_files)
        spl.CreatePointFeature_ogr(outputShapefile, lonlist, latlist, panoIDlist, datelist, attr_dict, 'metadata')
        print('created the file', outputShapefile)
    
    
    metadata = file.split(" - ")
    lat = metadata[0]
    
    lon = metadata[1]
    yaw = metadata[2]
    date = metadata[3][0:7]
                
    lonlist.append(lon)
    latlist.append(lat)
    yawlist.append(yaw)
    datelist.append(date)
    
    # read the seg hemi image and seg cylindrical image from different folder
    hemifile = os.path.splitext(file)[0]+'_reproj'+os.path.splitext(file)[1]
    skyImg = np.asarray(Image.open(os.path.join(seg_hemi, hemifile)))
    cylinderImg = np.asarray(Image.open(os.path.join(seg_cylinder, file)))
    

    # compute the SVF
    svf = sunexpo.SVFcalculationOnFisheye(skyImg, skyPixlValue=1)
    svflist.append(svf)
    
    # compute the GVI by convert cylindrical images to perspective projection
    gvi_ave = 0
    for i in range(6):
        img = sslib.cylindrical2Perspective(cylinderImg, heading*i, fov, pitch)
        gvi = 100*(len(np.where(img==4)[0]) + len(np.where(img==9)[0]))/(800*800)
        gvi_ave = gvi_ave + gvi
    
    gvi_ave = gvi_ave/6.0
    gvilist.append(gvi_ave)

print('Generating shapefile...')

