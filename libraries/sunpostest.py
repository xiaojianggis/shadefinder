from datetime import datetime, timedelta
import os,os.path
import sys
import SunExpoLib as sunexpo

root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab'
panoId = "4G5km0yE7QsmzxE7YBPRYw"

fisheyeImgSunpathFile = os.path.join(root,panoId + 'fisheye_sunpath.jpg')

year = 2014
month = 7
day = 15
hour = 6

currentTime = datetime(year, month, day, hour, 0, 0, 0)
fisheyeImgFile = os.path.join(root, "__Dp6erSCpZzNmUUpSQQVw - -71.0976589001 - 42.3617784647 - 2011 - 10 - 128.76423645_reproj.jpg")
lon = -71.0976589001
lat = 42.3617784647


#plot the sun pos on the fisheye image
sunexpo.SunPosOnFisheyeimage(fisheyeImgFile,fisheyeImgSunpathFile,currentTime,lon,lat)
print ('This is the result')

