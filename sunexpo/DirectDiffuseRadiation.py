
# This script is used to estimate the duration of sunlight on any specified day
# First version March 21st, 2017
#
# Second version Oct 26th, 2017, for the solar radaition calculation in winter
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab

# third version on April 19, 2018, with the correction of the solar radiation calculation
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab


from datetime import datetime, timedelta
import os,os.path
import sys
sys.path.append(os.getcwd() + '/library')
import ImageProjectionCombined_python3_Lib as gsvPro


outputSunpathFolder = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest'

## ----------for the summer, from June 1st to September 1st-----------
shpfile = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\Shapefiles\DirectDiffuseRadiationJune_Sep2.shp'
timeList = []
monthLst = [6,7,8]

# ----------for winter, from Dec 1st to Feb 28st-----------------
##shpfile = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\DurationTest\Shapefiles\DirectDiffuseRadiationDec_Feb2.shp'
##timeList = []
##monthLst = [12,1,2]


for month in monthLst:
    if month == 6:
        days = 30
    if month == 7 or month == 8 or month == 1 or month == 12:
        days = 31
    if month == 2:
        days = 28
    
    for day in range(1,days+1):        
        # the initTime for all the day in these months
        iniTime = datetime(2014, month, day, 4, 0, 0, 0)
        
        # for different months of the year
##        for cent_hour in range(140):
##            iniTime = iniTime + timedelta(hours=0.1)
##            timeList.append(iniTime)
        for cent_hour in range(28):
            iniTime = iniTime + timedelta(hours=0.5)
            timeList.append(iniTime)
        
        
# calculate the direct and diffuse radiation for all the time in the timlist
##for skyimage in os.listdir(skyImgFiles):
##    skyImgFile = os.path.join(skyImgFiles,skyimage)
##    skymap = os.path.join(outputSunpathFolder,'skymap.tif')
##    gsvPro.CreateSkyMap(skyImgFile,skymap)
##    gsvPro.DiffuseRadiationEst(skyImgFile,skymap)
##    gsvPro.DirectRadiationEst(skyImgFile,timeList)


# calculate the direct and diffuse radiation for al the time in the timlist
skymap = os.path.join(outputSunpathFolder,'skymap.tif')

# for summer using Google Street View
skyImgFiles = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\FisheyeClassResBoston100m'

# for winter using the building height model
##skyImgFiles = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\SkyImg_DSM2'
gsvPro.DirectDiffuseRadiationEst(skyImgFiles,skymap,timeList,shpfile)

