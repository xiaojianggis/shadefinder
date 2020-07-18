# This is the downloader of GSV panorama
# using the function from SunExpoLib

import os,os.path
import sys
sys.path.append("../libraries/")
import SunExpoLib as sunexpo

panoId = 'jeR7sPfjowTzt21WRxWWIA' # For TokyoRouting paper
panoId = 'mTwnNn4vUz11SvpwBVGpDA'
panoId = 'ekOhsCAsB-EyR2JHBFL4GA'

panoId = 'XuiMCvuoT__n_aEGpiuKJg' # for Shibuya routing, Fig. 4
panoId = 'GhxNLxO1N7yFO0r4MmZ2Gw'
panoId = 'ozeRlvfwFats6V7Ax4nHDA'
panoId = 'llT0FVhi5JGIY9vzZNVAGw'
panoId = 'hhBvB6JnqLxp4i3c0D_UTg'
panoId = 'L3b_71KuiE_cR3XetUGkIw'
panoId = '5_8yIWi6k1cDj19MiwRzGw'
panoId = 'eHHZaKYC7DQ2spGsDQF5aA'

panoId = 'zFkrZSb5jrQgFySX42iDfg'
panoId = 'hplU5qC5oxcvR01xpzVvVQ'
panoId = 'N4GK03F245mEcnrgyDMGpA'
panoId = 'fxN9hr7KnuKBFrUSw5GB-w'


root = '/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/Sidewalk'
outputName = os.path.join(root, panoId + '.jpg')
fisheOutput = os.path.join(root, panoId + 'fish.jpg')

print ('The output panorama is:', outputName)
# download the GSV panorama
cylinderPanoImg = sunexpo.GSVpanoramaDowloader_GoogleMaps(panoId, outputName)
