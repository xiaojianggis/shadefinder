
# This script is used to estimate the duration of sunlight on any specified day
# First version March 21st, 2017
#
# Second version Oct 24, 2017, MIT
# The second version adds the sunlight duration estimtion in winter using hemispherical image calculated from building height model

# Copyright(c) Xiaojiang Li, MIT Senseable City Lab


from datetime import datetime, timedelta
import os,os.path
import sys
sys.path.append(os.getcwd() + '/library')
import ImageProjectionCombined_python3_Lib as gsvPro


### -----------------FOR SUMMER ---------
####skyImgFiles = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\Skyimages'
##skyImgFiles = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\FisheyeClassResBoston100m'
##outputSunpathFolder = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\sunpath'
##shpfile = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\Shapefiles\SunDurationAug1st_Complete.shp'
##
##
### set the start time for the calculation
##iniTime = datetime(2014, 8, 1, 4, 0, 0, 0)
##timeList = []
##timeList.append(iniTime)
##
### for different hours in one day
##for h in range(140):
##    iniTime = iniTime + timedelta(hours=0.1)
##    timeList.append(iniTime)
##
##gsvPro.SunlightDurationEstimation(skyImgFiles,outputSunpathFolder,timeList,shpfile)



## -------------- For Winter Jan 1st ---------------------------
skyImgFiles = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\SkyImg_DSM2'
##skyImgFiles = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\FisheyeClassResBoston100m'

outputSunpathFolder = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\sunpath'
shpfile = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\Shapefiles\SunDurationJan1st_Complete.shp'



## --------------For Aug 1st, Cambridge, Book Chapter ------------------------------
skyImgFiles = r'D:\PhD Project\Darksky-Philips\PanoLab\FisheyeClassRes_Cambridge'
outputSunpathFolder = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\sunpath'
shpfile = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\Shapefiles\SunDurationJan1st_Complete.shp'



# set the start time for the calculation
iniTime = datetime(2014, 1, 1, 4, 0, 0, 0)
timeList = []
timeList.append(iniTime)

# for different hours in one day
for h in range(140):
    iniTime = iniTime + timedelta(hours=0.1)
    timeList.append(iniTime)

gsvPro.SunlightDurationEstimation(skyImgFiles,outputSunpathFolder,timeList,shpfile)
