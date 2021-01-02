# This is a complete work flow for generating samples, collecting metadata, cleaning metadata, download GSV panoramas
# In order to make life easier, just make everything automatic
# First version April 2ed, 2019
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab

import sys
sys.path.append('./libraries')
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
import ogr,osr
import math

# User-defined parameters 
mini_dist = 100 # in meters
batchNum = 1000
cityname = 'Cambridge'
greenMonthList = ['04', '05', '06', '07', '08', '09', '10', '11']

os.chdir('sample-spatialdata/')
root = os.getcwd()
inshp = os.path.join(root, 'CambridgeStreet_wgs84.shp')
outfilename = f'{cityname}-{mini_dist}m.shp'

outshp = os.path.join(root, outfilename)
MetadatTxt = os.path.join(root, 'metadata')
gsvimgs = os.path.join(root, 'gsv-panos')

# Step 1. ------- Sampling part -----------------------
spl.createPoints(inshp, outshp, mini_dist)


# Step 2. --------- Get the historical GSV metadata ---------------------

print('Collecting metadata')

# for multi-temporal metadata, use
metalib.GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(
    outshp, batchNum, MetadatTxt)
# metalib.GSVpanoMetadataCollectorBatch_Yaw_fiona(outshp, batchNum, MetadatTxt)

# STEP 3. --------- Check the spatial distribution of the finally selected GSV panos
outputShapefile = os.path.join(MetadatTxt, cityname+'_cleanedSummerGSV.shp')

pntNumlist = []
panoIDlist = []
lonlist = []
latlist = []
yawlist = []
datelist = []

for idx, file in enumerate(os.listdir(MetadatTxt)):
    if not file.endswith('.txt'): 
        continue

    metafilename = os.path.join(MetadatTxt, file)
    # read the meta txt file and read the meta into list
    lines = open(metafilename, 'r')
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
    lines.close()


attr_dict = {'pntnum': pntNumlist, 'yaw': yawlist}

spatial.CreatePointFeature_ogr(
    outputShapefile, lonlist, latlist, panoIDlist, datelist, attr_dict, 'metadata')
print('created the file', outputShapefile)


# STEP 4. ---------- Dowload the GSV panoramas-----------

print('Download the gsv panoramas')

for metatxt in os.listdir(MetadatTxt):
    print('The metadata is:', metatxt)
    metatxtfile = os.path.join(MetadatTxt, metatxt)
    # the last param is used to mark historical (1) or non historical (0) gsv meta
    downlib.GSVpanoramaDowloader(metatxtfile, greenMonthList, gsvimgs, historical=1)


# STEP 5. --------- Image segmentation--------

for pano in os.listdir(gsvimgs):
        if not pano.endswith('.jpg'): 
            continue

        file_path = os.path.join(gsvimgs, pano)
        panoImg = np.array(Image.open(file_path))
        skyImgFile = os.path.join(gsvimgs, pano.replace('.jpg', '_sky.tif'))
        skyImg = imgclass.OBIA_Skyclassification_vote2Modifed_2(panoImg, skyImgFile)


# STEP 6. --------- Convert to hemispherical image--------
for pano in os.listdir(gsvimgs):
        if not pano.endswith('_sky.tif'): 
            continue

        basename = pano.split('_sky.tif')[0]
        yaw = basename.split(' - ')[-1]

        file_path = os.path.join(gsvimgs, pano)
        panoImg = np.array(Image.open(file_path))
        hemiImgFile = os.path.join(gsvimgs, pano.replace('_sky.tif', '_hemi.tif'))
        sunexpo.cylinder2fisheyeImage(panoImg, yaw, hemiImgFile)

      
# STEP 7. --------- Calculate if a site is shaded, and save to shapefile--------   
# specify the date and time information
year = 2018
month = 7
day = 15
minute = 0
second = 0
zone = -9 # https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html

# watch out the longitude for the west hemisphere is positive and east is negative
latitude = 35.668263
longitude = -139.697001

# create fields for different time stamps
hours = [9, 12, 14, 17]

# the output sunexpo shapefile
shpfile = os.path.join(root, f'sunexpo-{year}-{month}-{day}-{hours[0]}h-to-{hours[1]}h.shp')

# create a shpafile to save the sun duration
driver = ogr.GetDriverByName('ESRI Shapefile')

if os.path.exists(shpfile):
    driver.DeleteDataSource(shpfile)

data_source = driver.CreateDataSource(shpfile)

targetSpatialRef = osr.SpatialReference()
targetSpatialRef.ImportFromEPSG(4326)

outLayer = data_source.CreateLayer('Sunexpo', targetSpatialRef, ogr.wkbPoint)
panoId = ogr.FieldDefn('panoid', ogr.OFTString)
outLayer.CreateField(panoId)

for hour in hours:
    fieldname = 'expo%s'%(hour)
    exposureField = ogr.FieldDefn(fieldname, ogr.OFTInteger) # 0 means not shaded or exposed to sunlight, 1 mean shaded or not exposed to sunlight
    outLayer.CreateField(exposureField)

i = 0
for skyimgfile in os.listdir(gsvimgs):
        if not skyimgfile.endswith('_hemi.tif'): 
            continue

        i = i + 1
        if i % 1000 == 0: print('You have processed %s'%(i))

        skyImgFileFullname = os.path.join(gsvimgs, skyimgfile)
        skyImg = np.asarray(Image.open(skyImgFileFullname))

        basename = skyimgfile.split('_sky.')[0]
        fields = basename.split(' - ')

        panoID = fields[1]
        lon = float(fields[2]) # watch out in the NOAA sunpos model, the eastern hemisphere has longitude negative, west has longitude positive
        lat = float(fields[3])

        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)
        
        # create feature and set the attribute values
        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        
        # set the geometrical feature
        outFeature.SetGeometry(point)
        outFeature.SetField('panoid', panoID)

        
        for hour in hours:
        # calculate the sun position
            [azimuth, sunele] = sunpos.calcSun(latitude, longitude, zone, year, month, day, hour, minute, second)
            
            # Judge whether the sunlight is blocked or not, 0 is not shaded, 1 is shaded. 
            shade = sunexpo.Shaded_judgement_noaa(skyImg, 0, 4, azimuth, sunele)
            exposure = 1 - shade # exposed to sunlight 1, not exposed to sunlight 0
            fieldname = 'expo%s'%(hour)
            outFeature.SetField(fieldname, exposure)
        
        outLayer.CreateFeature(outFeature)
        outFeature.Destroy()
    

data_source.Destroy()


