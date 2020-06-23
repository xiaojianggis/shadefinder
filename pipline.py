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


root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Urban Sensing and Computing/Yuji - Image of cities/Lynch_cities/jersey_city/'
mini_dist = 100

cityname = 'NYC'
cityname = 'LA'
#cityname = 'Dallas'
cityname = 'Houston'
#cityname = 'Philadephia'
cityname = 'Atlanta'
cityname = 'Memphis'
cityname = 'DC'

greenMonthList = ['04','05','06', '07', '08', '09', '10', '11'] 

# For NewJersey City
shpfile = os.path.join(root, r'Jersey_city/clean_Jersey_city_wgs84.shp')
pntshpfile = os.path.join(root, r'Jersey_city/Jersey_city_wgs84_%sm.shp')%mini_dist


# For LA
root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Urban Sensing and Computing/Yuji - Image of cities/Lynch_cities/Los_Angels'
inshp = os.path.join(root, 'Los_Angeles/LosAngeles_data_1_wgs84.shp')
outshp = os.path.join(root, 'Los_Angeles/LosAngeles_data_1_wgs84_100m.shp')

# For Paris
root = '/Users/senseablecity/Dropbox (MIT)/ResearchProj/Street-life/OSMNX/OSMNX'
inshp = os.path.join(root, 'selected_route_double_proj4326.shp')
outshp = os.path.join(root, 'selected_route_pnt_proj4326_20m.shp')
mini_dist = 20

# For Dallas
root = '/home/jiang/Documents/researchProj/thermal-injustice/datasets/Dallas'
outshp = os.path.join(root, 'spatial-data/Dallas100m.shp')

# for Charlotte
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Charlotte'
outshp = os.path.join(root, 'spatial-data/Charlotte100m.shp')


# For NYC
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/%s'%(cityname)
outfilename = 'spatial-data/%s100m.shp'%(cityname)
outshp = os.path.join(root, outfilename)



##### Step 1. -------Sampling part -----------------------
# spl.createPoints(inshp, outshp, mini_dist)



root = r'/mnt/deeplearnurbandiag/dataset/%s'%(cityname)

# ## Step 2. ---------Get the historical GSV metadat ---------------------
MetadatTxt = os.path.join(root, 'metadata')
if not os.path.exists(MetadatTxt):
    os.mkdir(MetadatTxt)


monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
# metalib.GSVpanoMetadataCollectorBatch_Yaw_fiona(outshp, 1000, MetadatTxt)
# print('Collecting metadata')

# for multi-temporal metadata, use
# metalib.GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(outshp, 1000, MetadatTxt)



## STEP 3: -------Clean the metadata to keep summer GSV record, one pano for one site, 2009-2014, can be modified
# Clean the metadata to guarantee that one summer panorama is selected
inroot = MetadatTxt
outroot = os.path.join(root, 'cleaned-metadata-sw-recentyear')
outputShapefile = os.path.join(root, 'spatial-data', cityname+'cleanedSummerGSV.shp')
if not os.path.exists(outroot): os.mkdir(outroot)
metaclean.metadataCleaning(inroot, outroot, greenMonthList)



## STEP 4: --------- Check the spatial distribution of the finally selected GSV panos
metafolder = outroot # the cleaned meta

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



## STEP 5: ---------- Dowload the GSV panoramas-----------
root = r'/mnt/deeplearnurbandiag/dataset/%s'%(cityname)
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
    #downlib.GSVpanoramaDowloader(metatxtfile, monthlist, gsvimgs, 1) # the last para is used to mark historical () or non historical gsv meta


