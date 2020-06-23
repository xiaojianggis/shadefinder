
# This function is used to estimate human exposure to solar radiation from one
# time to another time point based on the sun position and the street-level images

# Copyright(c) Xiaojiang Li, MIT Senseable City Lab
# Frist version Dec 23, 2017

from datetime import datetime, timedelta
import os,os.path
import sys
import ImageProjectionCombined_python3_Lib as gsvPro
from pysolar.solar import get_altitude, get_azimuth
import numpy as np


# The folder of hemispehrical images
skyImgFiles = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\FisheyeClassResBoston100m'
outputSunpathFolder = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\sunpath'
shpfile = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\Shapefiles\SunDurationAug1st_Complete.shp'


# estimate the human exposure to solar radiation based on a trajectory, for one trajectory we have to information
# the location of the site

# the time of the runner
# radaition = b*Rad*cos(theta), theta = ele(lon,lat,t)

# location of the site
lon = -71.0976589001
lat = 42.3617784647

##skyImg = r'__Dp6erSCpZzNmUUpSQQVw - -71.0976589001 - 42.3617784647 - 2011 - 10 - 128.76423645_reproj.jpg'
##folder = r'D:\PhD Project\Darksky-Philips\PanoLab\streetlight-fisheye'
skyImg = r'__Dp6erSCpZzNmUUpSQQVw - -71.0976589001 - 42.3617784647 - 2011 - 10 - 128.76423645_reproj_skyRes.tif'
folder = r'D:\PhD Project\Darksky-Philips\PanoLab\FisheyeClassRes_Cambridge'

# hemispherical image
skyImgFile = os.path.join(folder,skyImg)

plotedFisheyeImg = r'D:\PhD Project\RouteFindingProj\FreeRunner\plotteImg.tif'
# time of the stop on pedestrian trajectory
year = 2014
month = 8
day = 1
hour = 12
currentTime = datetime(year, month, day, hour, 0, 0, 0)
print ('The current time is:', currentTime)
gsvPro.SunPosOnFisheyeimage(skyImgFile,plotedFisheyeImg,currentTime, lon, lat)
