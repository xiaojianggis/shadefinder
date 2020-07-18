# This is the downloader of GSV panorama
# using the function from SunExpoLib

import os,os.path
import sys
sys.path.append("../libraries/")
import SunExpoLib as sunexpo
# import ImageClassLib as imgseg
import PanodownloaderLib as pano

# panoId = 'f6rpYgW_TTKuQnKItZZa7g'
# panoId = '69_h0BVwQ4KZgdANK6SsWQ'
# panoId = '_tbxf9SFNDbvAW3ei_bHNA'

# panoId = 'nfgIjioB-DRqwBFLi5p0uw'
# panoId = 'pPvLVqgiW_LhbxD9rA7Hmw'
panoId = 'tbZ9bCkWiYyjE8gLZmUtyA'
panoId = 'DtA04d2XXuskx-YHz2vt3g'
panoId = 'uDbqAtIxNJMYpdIwOmEMFQ'
panoId = 'oCDZtsw-dy8bH9KUJxvskg'
panoId = 'Mg72rzTKgATajxWjoJOhtQ'
panoId = 'YpthazmiBGT4GZUbqxlL1g'
panoId = '9hw_WUB2F_STM7dOSKM1Ew'
panoId = 'lk5TlQEU90mxkES_2bb9pg'
panoId = '09jtcQ4EtoZpdEgw7R4d2A'
panoId = 'YB-wegZ2qvVF8ZtoRVvMXw'
panoId = 'gmq5hqj82E8vjpvYtdu7GA'
panoId = '7Yz2fEFmB7YBeF5TcFx__A'
panoId = 'uL34GGoSUhn4_d68ekbeHg' # NYC Cityscanner
# panoId = '-zczBpu_Kp9r-F4mQnj5Lg'
# panoId = 'ptiv77JqGBYR1XMMUPSI1Q'
panoId = '9HoKZYurub49TdT0Nkg7xw'
panoId = '5v5xiG0U6WBXtrfk2ZQpLQ'
panoId = 'lKSx66LxCdiCypOp0bVadA'
panoId = 'gI4DNHYr0X1K7p3LitSQeg'
panoId = 'kX8NS9ru9-YA4c9tkp3Hmg'
panoId = 'g_97qtay9payiUtmfD8hhA'
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

# # NYC Museum, using different link
# panoId = 'zsbSzbvnOqV31LDcaeU8Tw'
# # panoId = 'Y30_xdNbHMS2W1aftHbaeA'
# panoId = 'h8M9CtAGGRFsYycXLDtFYg'


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

# fisheyeImg = sunexpo.cylinder2fisheyeImage(cylinderPanoImg, 180, fisheOutput)
# skyImg = imgseg.OBIA_Skyclassification_vote2Modifed_2(fisheyeImg)
