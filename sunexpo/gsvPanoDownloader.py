# This is the downloader of GSV panorama
# using the function from SunExpoLib

import os,os.path
import sys
sys.path.append("./libraries/")
import SunExpoLib as sunexpo

panoId = sys.argv[0]
outputroot = sys.argv[1]
outputName = os.path.join(outputroot,panoid + '.jpg')

print sys.argv[0]
print sys.argv[1]

# download the GSV panorama
cylinderPanoImg = sunexpo.GSVpanoramaDowloader_GoogleMaps(panoId, outputName)

