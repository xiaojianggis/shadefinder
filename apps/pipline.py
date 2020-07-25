# This is a complete work flow for generating samples, collecting metadata, cleaning metadata, download GSV panoramas
# In order to make life easier, just make everything automatic
# First version April 2ed, 2019
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab

import os, os.path
import sys
sys.path.append("./libraries")
import SamplingLib as spl
import SpatialLib as spatial
import MetadataLib as metalib
import GsvdownloaderLib as downlib
import MetadataCleaningLib as metaclean


mini_dist = 100
cityname = 'Cambridge'
greenMonthList = ['04','05','06', '07', '08', '09', '10', '11'] 

os.chdir("sample-spatialdata/")
root = os.getcwd()
inshp = os.path.join(root, 'CambridgeStreet_wgs84.shp')
outfilename = '%s100m.shp'%(cityname)
outshp = os.path.join(root, outfilename)


## Step 1. ------- Sampling part -----------------------
spl.createPoints(inshp, outshp, mini_dist)


## Step 2. --------- Get the historical GSV metadata ---------------------
batchNum = 1000

MetadatTxt = os.path.join(root, 'metadata')
if not os.path.exists(MetadatTxt):
    os.mkdir(MetadatTxt)

# metalib.GSVpanoMetadataCollectorBatch_Yaw_fiona(outshp, batchNum, MetadatTxt)
print('Collecting metadata')

# for multi-temporal metadata, use
metalib.GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(outshp, batchNum, MetadatTxt)



## STEP 3. ------- Clean the metadata to keep summer GSV record, one pano for one site, 2009-2014, can be modified
# Clean the metadata to guarantee that one summer panorama is selected
inroot = MetadatTxt
outroot = os.path.join(root, 'cleaned-metadata-sw-recentyear')

metaclean.metadataCleaning(inroot, outroot, greenMonthList)



## STEP 4. --------- Check the spatial distribution of the finally selected GSV panos
metafolder = outroot # the cleaned meta
outputShapefile = os.path.join(outroot, cityname+'_cleanedSummerGSV.shp')

pntNumlist = []
panoIDlist = []
lonlist = []
latlist = []
yawlist = []
datelist = []

for idx, file in enumerate(os.listdir(metafolder)):
    metafilename = os.path.join(metafolder, file)

    # read the meta txt file and read the meta into list
    lines = open(metafilename,"r")
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

    if idx%100 == 0: print(idx)


attr_dict = {'pntnum': pntNumlist, 'yaw': yawlist}

spatial.CreatePointFeature_ogr(outputShapefile, lonlist, latlist, panoIDlist, datelist, attr_dict, 'metadata')
print('created the file', outputShapefile)



## STEP 5. ---------- Dowload the GSV panoramas-----------
gsvimgs = os.path.join(root, 'gsv-panos')

if not os.path.exists(gsvimgs):
    os.mkdir(gsvimgs)

print('Download the gsv panoramas')
cleanedMeta = outroot
print('The meta is:', cleanedMeta)
for metatxt in os.listdir(cleanedMeta):
    print('The metadata is:', metatxt)
    metatxtfile = os.path.join(cleanedMeta, metatxt)
    monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    downlib.GSVpanoramaDowloader(metatxtfile, monthlist, gsvimgs, 1) # the last para is used to mark historical () or non historical gsv meta


