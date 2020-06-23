# This is a complete work flow for generating samples, collecting metadata, cleaning metadata, download GSV panoramas
# In order to make life easier, just make everything automatic
# First version April 2ed, 2019
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab

import os, os.path
import sys
sys.path.append("./libraries")
import SamplingLib as spl
import MetadataLib as metalib
import GsvdownloaderLib as downlib


root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Urban Sensing and Computing/Yuji - Image of cities/Lynch_cities/jersey_city/'
mini_dist = 100

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


# For NYC
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/NYC'
outshp = os.path.join(root, 'spatial-data/NYC100m.shp')

# for Charlotte
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Charlotte'
outshp = os.path.join(root, 'spatial-data/Charlotte100m.shp')

# for Memphis
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Memphis'
outshp = os.path.join(root, 'spatial-data/Memphis100m.shp')

# for Phily
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Philadephia'
outshp = os.path.join(root, 'spatial-data/PhilyPnt100m.shp')

# for SanDiego
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/SanDiego'
outshp = os.path.join(root, 'spatial-data/SanDiego100m.shp')

# for Houston
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Houston'
outshp = os.path.join(root, 'spatial-data/Houston100m.shp')

# for Miami
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Miami'
outshp = os.path.join(root, 'spatial-data/Miami100m.shp')


## -------Sampling part -----------------------
# spl.createPoints(inshp, outshp, mini_dist)



# ## ---------Metadata part ---------------------
MetadatTxt = os.path.join(root, 'metadata')
if not os.path.exists(MetadatTxt):
	os.mkdir(MetadatTxt)


monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
# metalib.GSVpanoMetadataCollectorBatch_Yaw_fiona(outshp, 1000, MetadatTxt)
# print('Collecting metadata')

# for multi-temporal metadata, use
metalib.GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(outshp, 1000, MetadatTxt)



# # ---------Dowload the GSV panoramas-----------
# # gsvimgs = os.path.join(root, 'gsvpanos')
# gsvimgs = '/Users/senseablecity/Dropbox (MIT)/Programing/nodejs/map-node/pg_mapper/public/images/LA'
# gsvimgs = os.path.join(root, 'gsv-panos')

#if not os.path.exists(gsvimgs):
#	os.mkdir(gsvimgs)

#for metatxt in os.listdir(MetadatTxt):
#	metatxtfile = os.path.join(MetadatTxt, metatxt)
#	monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
	#downlib.GSVpanoramaDowloader(metatxtfile, monthlist, gsvimgs, 0)

# if not os.path.exists(gsvimgs):
# 	os.mkdir(gsvimgs)

# for metatxt in os.listdir(MetadatTxt):
# 	metatxtfile = os.path.join(MetadatTxt, metatxt)
# 	monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
# 	downlib.GSVpanoramaDowloader(metatxtfile, monthlist, gsvimgs, 0)
    
