# This is the downloader of GSV panorama
# using the function from SunExpoLib

import os,os.path
import sys
sys.path.append("../libraries/")
import SunExpoLib as sunexpo

panoId = 'XuiMCvuoT__n_aEGpiuKJg' # for Shibuya routing, Fig. 4

root = '/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/Sidewalk'
outputName = os.path.join(root, panoId + '.jpg')
print ('The output panorama is:', outputName)

# download cylinder GSV panorama
cylinderPanoImg = sunexpo.GSVpanoramaDowloader_GoogleMaps(panoId, outputName)
