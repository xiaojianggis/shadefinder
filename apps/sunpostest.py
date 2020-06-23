# This function is used to test plot sun pos and sun path on hemispherical
# images based on the estiamted sun position using NOAA's method
# Modified Aug 27, 2018, 
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab


# from datetime import datetime, timedelta
import datetime
import os,os.path
import sys
sys.path.append("./libraries")
import SunExpoLib as sunexpo
import SunposLib as sunpos
import numpy as np
from PIL import Image


root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab'
panoId = "4G5km0yE7QsmzxE7YBPRYw"

fisheyeImgSunpathFile = os.path.join(root,panoId + 'fisheye_sunpath.jpg')
fisheyeImgFile = os.path.join(root, "__Dp6erSCpZzNmUUpSQQVw - -71.0976589001 - 42.3617784647 - 2011 - 10 - 128.76423645_reproj.jpg")
fisheyeImgFile = os.path.join(root, "ekOhsCAsB-EyR2JHBFL4GAfish.jpg")
fisheyeImgFile = os.path.join(root, "mTwnNn4vUz11SvpwBVGpDAfish.jpg")
fisheyeImgFile = os.path.join(root, "jeR7sPfjowTzt21WRxWWIAfish.jpg")


# Boston, be careful, the west hemisphere is positive longitude
lon = 71.0976589001
lat = 42.3617784647
zone = 5


# For Tokyo
lat = 35.6836474
lon = -139.5963044
zone = 15


daySavings = 0 # = 0 (no) or 1 (yes)

# date
year = 2018
month = 8
day = 15

# time
hh = 13
mm = 0
ss = 0

# calculate the sun position and estimate the location of sun pos on correctly roated hemispherical image
fisheyeImg = np.array(Image.open(fisheyeImgFile))
[azimuth, sunele] = sunpos.calcSun(lat, lon, zone, year, month, day, hh, mm, ss)
[px, py] = sunexpo.SunPosOnFisheyeimage_noaa(fisheyeImg, azimuth, sunele)
print ('The px and py are:', px, py)


# plot the pos of sun on hemispherical image
plotedHemiImg = os.path.join(root, 'test.jpg')
sunexpo.plot_SunPosOnFisheyeimage_noaa(fisheyeImg, plotedHemiImg, azimuth, sunele)


# plot the sun path on hemispherical image
sunpathHemiImg = os.path.join(root, 'sunpath.jpg')
sunexpo.plot_SunPathOnFisheyeimage_noaa(fisheyeImg, sunpathHemiImg, lat, lon, zone, year, month, day)

