# This is a complete work flow for generating samples, collecting metadata, cleaning metadata, download GSV panoramas
# In order to make life easier, just make everything automatic
# First version April 2ed, 2019
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab

import sys
sys.path.append("./libraries")
import MetadataCleaningLib as metaclean
import GsvdownloaderLib as downlib
import MetadataLib as metalib
import SpatialLib as spatial
import SamplingLib as spl
import SunposLib as sunpos
import SunExpoLib as sunexpo
import ImageClassLib as imgclass
from PIL import Image
import numpy as np
import os
import os.path

# User-defined parameters 
mini_dist = 100
batchNum = 1000
cityname = 'Cambridge'
greenMonthList = ['04', '05', '06', '07', '08', '09', '10', '11']

os.chdir("sample-spatialdata/")
root = os.getcwd()
inshp = os.path.join(root, 'CambridgeStreet_wgs84.shp')
outfilename = '%s100m.shp' % (cityname)

outshp = os.path.join(root, outfilename)
MetadatTxt = os.path.join(root, 'metadata')
cleaned_meta = os.path.join(root, 'cleaned-metadata-sw-recentyear')
gsvimgs = os.path.join(root, 'gsv-panos')

# Step 1. ------- Sampling part -----------------------
spl.createPoints(inshp, outshp, mini_dist)


# Step 2. --------- Get the historical GSV metadata ---------------------

print('Collecting metadata')

# for multi-temporal metadata, use
metalib.GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(
    outshp, batchNum, MetadatTxt)
# metalib.GSVpanoMetadataCollectorBatch_Yaw_fiona(outshp, batchNum, MetadatTxt)

# STEP 3. ------- Clean the metadata to keep summer GSV record, one pano for one site, 2009-2014, can be modified
# Clean the metadata to guarantee that one summer panorama is selected

metaclean.metadataCleaning(MetadatTxt, cleaned_meta, greenMonthList)


# STEP 4. --------- Check the spatial distribution of the finally selected GSV panos
outputShapefile = os.path.join(cleaned_meta, cityname+'_cleanedSummerGSV.shp')

pntNumlist = []
panoIDlist = []
lonlist = []
latlist = []
yawlist = []
datelist = []

for idx, file in enumerate(os.listdir(cleaned_meta)):
    if not file.endswith('.txt'): 
        continue

    metafilename = os.path.join(cleaned_meta, file)
    # read the meta txt file and read the meta into list
    lines = open(metafilename, "r")
    for line in lines:
        try:
            elements = line.split(' ')

            pntNumlist.append(int(elements[1]))
            panoIDlist.append(elements[3])
            lonlist.append(float(elements[9]))
            latlist.append(float(elements[11]))
            yawlist.append(float(elements[13]))
            datelist.append(elements[5] + '-' + elements[7])
        except:
            print('read metadata txt failed')
            continue


attr_dict = {'pntnum': pntNumlist, 'yaw': yawlist}

spatial.CreatePointFeature_ogr(
    outputShapefile, lonlist, latlist, panoIDlist, datelist, attr_dict, 'metadata')
print('created the file', outputShapefile)


# STEP 5. ---------- Dowload the GSV panoramas-----------

print('Download the gsv panoramas')

for metatxt in os.listdir(cleaned_meta):
    print('The metadata is:', metatxt)
    metatxtfile = os.path.join(cleaned_meta, metatxt)
    # the last param is used to mark historical (1) or non historical (0) gsv meta
    downlib.GSVpanoramaDowloader(metatxtfile, greenMonthList, gsvimgs, historical=1)


# STEP 6. --------- Convert to hemispherical image--------
for pano in os.listdir(gsvimgs):
        if not pano.endswith('.jpg'): 
            continue

        file_path = os.path.join(gsvimgs, pano)
        panoImg = np.array(Image.open(file_path))
        hemiImgFile = os.path.join(gsvimgs, pano.replace('.jpg', '_hemi.jpg'))
        sunexpo.cylinder2fisheyeImage(panoImg, 0, hemiImgFile)


# STEP 7. --------- Image segmentation--------
for fisheye in os.listdir(gsvimgs):
        if not fisheye.endswith('_hemi.jpg'): 
            continue

        file_path = os.path.join(gsvimgs, fisheye)
        fisheyeImg = np.array(Image.open(file_path))
        skyImgFile = os.path.join(gsvimgs, fisheye.replace('_hemi.jpg', '_sky.tif'))
        imgclass.OBIA_Skyclassification_vote2Modifed_2(fisheyeImg, skyImgFile)

