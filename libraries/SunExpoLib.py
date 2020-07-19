# This code is used to download the  Google Street Panoramas based on Google Street View API
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab


# download the GSV panoramas based on the panoid
def GSVpanoramaDowloader_GoogleMaps(panoId, gsvPanoImgFile='gsvPano.jpg'):
    """
    This function is used to download the GSV panoramas from Google using
    the URL address provided by Google Maps
    
    zoom is 0:
    https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&panoid=c8gcWEqLiOcVwDrtJDiB4g&output=tile&x=0&y=0&zoom=1&nbt&fover=2
    
    zoom is 1:
    https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&panoid=iKXN73P5BhoYdBpxB973zw&output=tile&x=0&y=0&zoom=0&nbt&fover=2
    
    
    parameters:
        panoId: the panorama id
        gsvPanoImgFile: the full name of the output GSV panorama 
    
    first version July 11, 2016, MIT Senseable City Lab. 
    """
    
    import os,os.path
    import urllib
    from PIL import Image
    import numpy as np
    import sys
    

    # check the version of python
    version = sys.version_info[0]
    
    
    # download the GSV panoramas by specifying the parmaters
    # the zoom 0, size is 208*416 (1*1)
    # zoom 1, size is 412*832 (1*2) - > 832*1664 (2*4)
    zoom = 2
    if zoom == 0:
        xNum = 1
        yNum = 1
    else:
        xNum = 2**zoom
        yNum = 2**(zoom - 1)
    
    rowlim = 208*2**zoom
    collim = 208*2**(zoom + 1)
    
    # merge images together to create a panorama
    widths = xNum*512
    heights = yNum*512
    
    mergedImg = np.zeros((heights,widths,3),'uint8')
    print ('The panoid is:------', panoId)
    
    for x in range(xNum):
        for y in range(yNum):
            # The URL is derived from Google Maps, check the source code of Google Maps
            URL = "https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&panoid=%s&output=tile&x=%s&y=%s&zoom=%s&nbt&fover=2"%(panoId,x,y,zoom)
            
            # using different url reading method in python2 and python3
            if sys.version_info[0] == 2:
                import cStringIO
                imgfile = cStringIO.StringIO(urllib.urlopen(URL).read())
            
            if sys.version_info[0] == 3:
                import urllib.request
                import io
                
                request = urllib.request.Request(URL)
                imgfile = io.BytesIO(urllib.request.urlopen(request).read())
                
            
            # the x,y indices of the patch on the merged panorama
            idx_lx = 512*x
            idx_ux = 512*x + 512
            idx_ly = 512*y
            idx_uy = 512*y + 512
            
            # get the image file, if the image is not valid then return
            try: 
                imgPatch = np.array(Image.open(imgfile))
            except IOError:
                return
            
            # merge those tiles together
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,0] = imgPatch[:,:,0]
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,1] = imgPatch[:,:,1]
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,2] = imgPatch[:,:,2]
            
    
    # cut the mergedImg based on the original size of panorama
    cut_mergedImg = np.zeros((rowlim,collim,3),'uint8')
    cut_mergedImg[:,:,0] = mergedImg[:rowlim,:collim,0]
    cut_mergedImg[:,:,1] = mergedImg[:rowlim,:collim,1]
    cut_mergedImg[:,:,2] = mergedImg[:rowlim,:collim,2]
    print('The size of the GSV panorama is:',cut_mergedImg.shape)
    
    img = Image.fromarray(cut_mergedImg)
    img.save(gsvPanoImgFile)
    del img, mergedImg
    
    return cut_mergedImg
    

def cylinder2fisheyeImage (panoImg,yaw,outputImgFile='fisheye.jpg'):
    '''
        This program is used to convert cylindrical panorama images to original image
        Copyright (C) Xiaojiang Li, UCONN, MIT Senseable City Lab
        First version June 25, 2016
        
        Second verion Dec 27, 2017
        
        Be careful, for the GSV panoramas, the R2 and R22 are different, the R22
        or the height based method is 3times of the width based method,however,
        for the example fisheye image collected online the R2 and R22 are almost
        the same. This prove that Google SQUIZED THE COLUMN OF GSV PANORAMA, in
        order to rescale the Google paorama, the colums sould time 3
        
        vecX = xD - CSx
        vecY = yD - CSy
        theta1 = math.asin(vecX/(r+0.0001))
        theta2 = math.acos(vecX/(r+0.0001))
        
        input:
            panoImg the numpy array of the image, watch out datatype, np.array(segPanoImg, dtype=np.uint8)
            yaw: the yaw angle of the input GSV panorama
        
        outputImgFile:
            output fisheye image file name
        
        return the created fishey image rotatedFisheyeImg numpy array
    
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import cv2
    
    
    # read the dimension information of input panorama
    dims = panoImg.shape

    Hs = dims[0]
    Ws = dims[1]
    
    panoImg2 = panoImg[0:int(Hs/2),:]
    del panoImg
    
    
    #the roate anagle
    rotateAng = 360 - float(yaw)# the rotate angle
    
    # get the radius of the fisheye
    R1 = 0
    R2 = int(2*Ws/(2*3.1415926) - R1 +0.5) # For google Street View pano
    
    R22 = Hs + R1
    
    # estimate the size of the sphere or fish-eye image
    Hd = int(Ws/np.pi)+2
    Wd = int(Ws/np.pi)+2
    
    # create empty matrics to store the affine parameters
    xmap = np.zeros((Hd,Wd),np.float32)
    ymap = np.zeros((Hd,Wd),np.float32)
    
    # the center of the destination image, or the sphere image
    CSx = int(0.5*Wd)
    CSy = int(0.5*Hd)
    
    # split the sphere image into four parts, and reproject the panorama for each section
    for yD in range(Hd):
        for xD in range(CSx):
            r = math.sqrt((yD - CSy)**2 + (xD - CSx)**2)
            theta = 0.5*np.pi + math.atan((yD - CSy)/(xD - CSx+0.0000001))
            
            xS = theta/(2*np.pi)*Ws
            yS = (r - R1)/(R2 - R1)*Hs
            
            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)
        
        for xD in range(CSx,Wd):
            r = math.sqrt((yD - CSy)**2 + (xD - CSx)**2)            
            theta = 1.5*np.pi + math.atan((yD - CSy)/(xD - CSx+0.0000001))
            
            xS = theta/(2*np.pi)*Ws
            yS = (r - R1)/(R2 - R1)*Hs 
            
            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)
    
    # using the affine to generate new hemispherical image
    outputImg = cv2.remap(panoImg2,xmap,ymap,cv2.INTER_CUBIC)
    del xmap,ymap,panoImg2    
    
    # remove the black line in central column of the buttom
    if len(dims) > 2:
        outputImg[int(CSy):,CSx,:] = outputImg[int(CSy):,CSx - 1,:]
        outputImg[int(CSy):,int(CSx + 0.5),:] = outputImg[CSy:,int(CSx + 0.5) + 1,:]
    else:
        outputImg[int(CSy):,CSx] = outputImg[int(CSy):,CSx - 1]
        outputImg[int(CSy):,int(CSx + 0.5)] = outputImg[CSy:,int(CSx + 0.5) + 1]
    

    ## ROTATE THE GENRATED FISHEYE IMAGE TO MAKE SURE THE TOP OF THE FISHEYE IMAGE IS THE NORTH
    # [rows,cols,bands] = outputImg.shape
    dims = outputImg.shape
    rows = dims[0]
    cols = dims[1]
    
    M = cv2.getRotationMatrix2D((cols/2,rows/2),rotateAng,1)
    rotatedFisheyeImg = cv2.warpAffine(outputImg,M,(cols,rows))
    
    
    img = Image.fromarray(rotatedFisheyeImg)
    del outputImg
    img.save(outputImgFile)
    del img
    
    return rotatedFisheyeImg
    
 

# overlay the sun position on the hemisphreical image, using pysolar to estimate sun postion
def SunPosOnFisheyeimage(panoImgFile,plotedFisheyeImg,currentTime,lon, lat):
    '''
    # This is used to put the trajectory of the sun on the generated fisheye image
    # the fisheye image could be created based on the GSV images, the trajectory of
    # of the sun is the position of the sun (azimuth, sun elevation)

    0: not shaded
    1: shaded
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version Jan 18, 2017
    
    # Second version Feb 17, 2017
    
    # Third version Dec 23, 2017
    
    Parameters: 
        panoImgFile: the input hemispherical image
        plotedFisheyeImg: the created fisheye image with the trajectory of the sun
        currentTime: the time object
        lon, lat are the coordinate of the site
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import sys
    from pysolar.solar import get_altitude, get_azimuth


    # read the hemispherical image
    outputSunpathImage = np.array(Image.open(panoImgFile))
    #outputSunpathImage = panoImgFile
    dims = outputSunpathImage.shape
    cols = dims[0]
    rows = dims[1]
    if len(dims)>2:
        bands = dims[2]
    
    print (lat,lon,currentTime)

    sunele = get_altitude(lat, lon, currentTime) #the sun elevation angle
    azimuth = abs(get_azimuth(lat, lon, currentTime)) #the get_azimuth will get azimuth start from south as zero
    
    #adjusted sun azimuthal angle, the north is the zero
    azimuth = 180 + azimuth
    if azimuth > 360: azimuth = azimuth - 360 
    
    # adjust the azimuth to to the image azimth, the east is the zero
    azimuth = 360 - azimuth + 90
    if azimuth > 360: azimuth = azimuth - 360

    sunele = sunele*np.pi/180.0
    azimuth = azimuth*np.pi/180.0
    
    print ('The sunele and azimuth are:', sunele, azimuth)
    
    # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
    R = int(0.5*rows)
    
    # get the r in the polar coordinate
    if sunele < 0: sunele = 0
    r = math.cos(sunele)*R
    
    print ('The r is: %s; and the R is: %s'%(r,R))
    
    # get the coordinate of the point on the fisheye images
    px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
    py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
    
    print ('px is: %s and py is: %s'%(px,py))
    
    # set the points as red
    buff = 10
    boundXl = px - buff
    if boundXl < 0: boundXl = 0
    boundXu = px + buff
    if boundXu > cols - 1: boundXu = rows - 1
    boundYl = py - buff
    if boundYl < 0: boundYl = 0
    boundYu = py + buff
    if boundYu > rows - 1: boundYu = cols - 1
    
    if len(dims)==2:
        outputSunpathImage[boundYl:boundYu,boundXl:boundXu] = 123
    else: 
        outputSunpathImage[boundYl:boundYu,boundXl:boundXu,0] = 255
        outputSunpathImage[boundYl:boundYu,boundXl:boundXu,1] = 0
        outputSunpathImage[boundYl:boundYu,boundXl:boundXu,2] = 0
    
    imgSunpath = Image.fromarray(outputSunpathImage)
    imgSunpath.save(plotedFisheyeImg)
    del outputSunpathImage, imgSunpath
    


# using the NOAA version, https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html
def SunPosOnFisheyeimage_noaa(panoImgFile, azimuth, sunele):
    '''
    # This is used to put the trajectory of the sun on the generated fisheye image
    # the fisheye image could be created based on the GSV images, the trajectory of
    # of the sun is the position of the sun (azimuth, sun elevation)
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # modified August 27, 2018
    
    Parameters: 
        panoImgFile: the input correctly rotated hemispherical image (North is up, East is right, South is down)
        azimuth: azimuth angle
        sunele: the elevation of the sun
    '''
    
    # plotedFisheyeImg
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import sys


    # read the hemispherical image
    # outputSunpathImage = np.array(Image.open(panoImgFile))
    outputSunpathImage = panoImgFile
    dims = outputSunpathImage.shape
    cols = dims[0]
    rows = dims[1]
    if len(dims)>2:
        bands = dims[2]
    
    # convert the azimuth to the new azimuth with east as zero, and anti-clockwise
    azimuth = -(azimuth - 90)
    if azimuth < 0: azimuth = azimuth + 360

    sunele = sunele*np.pi/180.0
    azimuth = azimuth*np.pi/180.0
    
    print ('The sunele and azimuth are:', sunele, azimuth)
    
    # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
    R = int(0.5*rows)
    
    # get the r in the polar coordinate
    if sunele < 0: sunele = 0

    # Using different coordinate, equidistance or equi-anglular hemispherical
    # r = math.cos(sunele)*R
    r = (90 - sunele*180/np.pi)/90.0*R


    print ('The r is: %s; and the R is: %s'%(r,R))
    
    # get the coordinate of the point on the fisheye images
    px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
    py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
    
    return px, py



# plot the sun position on the hemispherical image, using noaa method to estimate the sun position
def plot_SunPosOnFisheyeimage_noaa(hemiImg, plotedHemiImg, azimuth, sunele):
    '''
    This is used to plot the location of sun on hemispherical image
    
    Parameters: 
        hemiImg: the input hemispherical image
        plotedHemiImg: the created fisheye image with the position of the sun
        azimuth: azimuth angle
        sunele: the elevation of the sun
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math


    [px, py] = SunPosOnFisheyeimage_noaa(hemiImg, azimuth, sunele)
    dims = hemiImg.shape
    
    rows = dims[0]
    cols = dims[1]
    
    outputSunpathImage = np.copy(hemiImg)
    
    # if the sun position is no above horizon (outside of the hemispherical image) don't plot
    r0 = math.sqrt((px - 0.5*cols)**2 + (py - 0.5*rows)**2)
    if abs(r0 - 0.5*rows) > 4:
        # set the points as red
        buff = 5
        boundXl = px - buff
        if boundXl < 0: boundXl = 0
        boundXu = px + buff
        if boundXu > cols - 1: boundXu = rows - 1
        boundYl = py - buff
        if boundYl < 0: boundYl = 0
        boundYu = py + buff
        if boundYu > rows - 1: boundYu = cols - 1
        
        if len(dims)==2:
            outputSunpathImage[boundYl:boundYu,boundXl:boundXu] = 123
        else: 
            outputSunpathImage[boundYl:boundYu,boundXl:boundXu,0] = 255
            outputSunpathImage[boundYl:boundYu,boundXl:boundXu,1] = 0
            outputSunpathImage[boundYl:boundYu,boundXl:boundXu,2] = 0
    
    imgSunpath = Image.fromarray(outputSunpathImage)
    imgSunpath.save(plotedHemiImg)
    del imgSunpath, hemiImg
    
    return outputSunpathImage, px, py



# plot the sun path in one day on hemispherical images, using noaa method to estimate the sun position
def plot_SunPathOnFisheyeimage_noaa(hemiImg, plotedHemiImg, lat, lon, zone, year, month, day):
    """
    This function will plot the sun path in one day on the hemispherical image
    parameters:
        hemiImg: The input numpy array of the hemispherical image, correctly rotated hei, north is up, down is south
        plotedHemiImg: the output ploted hemispherical image
        lat, lon: the coordindate of the site
        zone: the zone code of the location of the hemispherical image
        year, month, day: the date information of the sunpath, will be used to calculate the sun positions
    """

    from PIL import Image
    import SunposLib as sunpos

    # plot the sun path on the fisheye image for one day
    for hh in range(5, 20):
        ss = 30

        for mm in range(0, 60, 20):
            [azimuth, sunele] = sunpos.calcSun(lat, lon, zone, year, month, day, hh, mm, ss)
            # print ('The hour, sunele and azimuth are:=======', hh, sunele, azimuth)
            [hemiImg, px, py] = plot_SunPosOnFisheyeimage_noaa(hemiImg, plotedHemiImg, azimuth, sunele)

    # export the outputCylindricalPanoImage as a new Image file
    imgSunpath = Image.fromarray(hemiImg)
    imgSunpath.save(plotedHemiImg)
    del plotedHemiImg, imgSunpath, hemiImg



# shift the cylindrical panorama based on the yaw degree
def ShiftCylindricalPanoImg(cylindrialPanoImg, yaw):
    '''
    This function is used to shift the cylindrical panorama based on the yaw angle
    the shifted cylindrical panorama will have the central column line as the north
    First modified by March 17, 2018, Xiaojiang Li, SCL, MIT
    parameters:
        cylindrialPanoImg: the input cylindrical panorama, numpy array
        yaw: the yaw degree
        
    return:
        shiftedCylindricalPanoImg
    '''

    import numpy as np

    # read the hemispherical image
    # cylindrialPanoImg = np.array(Image.open(panoImgFile))
    dims = cylindrialPanoImg.shape
    cols = dims[1]
    rows = dims[0]

    # shift the cylindrical panorama based on the yaw, move righward by yaw degree
    shiftPx = int(yaw/360.0 * cols)

    # outputCylindricalPanoImage = np.zeros((rows,cols,bands), dtype = np.int)
    outputCylindricalPanoImage = np.copy(cylindrialPanoImg)

    for col in range(cols):
        # the shifted col
        shifted_col = col + shiftPx
        if shifted_col > cols-1:
            shifted_col = shifted_col - cols
            
        # generated the new shifted img
        if len(dims) > 2: #for three bands
            outputCylindricalPanoImage[:,shifted_col,:] = cylindrialPanoImg[:,col,:]
        else:
            outputCylindricalPanoImage[:,shifted_col] = cylindrialPanoImg[:,col]


    return outputCylindricalPanoImage



# This function is used to find the location of the sun pos on the cylindrical panorama
def SunPosOnCylindricalImage_noaa (cylindrialPanoImg, azimuth, sunele):
    '''This function will find the position of sun on cylindrical panorama 
    based on the sun elevation and the azimuth angle
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab
    First version April 25, 2018
    
    parameters:
        cylindrialPanoImg: shifted, central coloumn is north, the numpy array of the clyindrical panorama
        azimuth: the azimuth of the sun position
        sunele: the sun elevation angle
    return:
        px, py the row and the column number of the sun pos on the cylindrical panorama
    '''


    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    
    
    # read the hemispherical image
    # cylindrialPanoImg = np.array(Image.open(panoImgFile))
    dims = cylindrialPanoImg.shape
    cols = dims[1]
    rows = dims[0]

    if len(dims) < 3:
        bands = 1
    else:
        bands = dims[2]

    # get the height of the sun position on the cylindrical panorama
    py = int(0.5*rows - sunele/90.0*0.5*rows)

    # get the column of the sun position on the cylindrical panorama
    if azimuth > 180: azimuth = azimuth - 360
    px = int(azimuth/360.0*cols + 0.5*cols)

    # in case the px, py are out of bounds
    if px > cols - 1: px = cols - 1
    if py > rows - 1: py = rows - 1

    return px, py



# plot the sun position on the cylindrical panorama, using noaa method to estimate the sun position
def plot_SunPosOnCylindricalImage_noaa(cylindrialPanoImg2, plotedCylindImgFile, azimuth, sunele):
    '''
    # This function is used to plot the solar position on cylindrical image
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 17, 2018
    
    Parameters: 
        cylindrialPanoImg: the input shifted cylindrical image, numpy array
        plotedFisheyeImg: the output plotted cylindrical panorama with sun position
        azimuth, sunele: the azimuth and sun elevation angle
        yaw: the yaw angle of the driving car, the north is zero, clockwise
    
    return:
        a new matrix with the solar position as red
    '''
    # import copy
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    

    cylindrialPanoImg = np.copy(cylindrialPanoImg2)
    del cylindrialPanoImg2

    # read the hemispherical image
    # cylindrialPanoImg = np.array(Image.open(panoImgFile))
    dims = cylindrialPanoImg.shape
    cols = dims[1]
    rows = dims[0]

    if len(dims) < 3:
        bands = 1
    else:
        bands = dims[2]
    
    [px, py] = SunPosOnCylindricalImage_noaa(cylindrialPanoImg, azimuth, sunele)

    # locate the glare zone based on the glaresize
    glareSize = 4 #10
    boundYl = py - glareSize
    if boundYl < 0: boundYl = 0
    boundYu = py + glareSize
    if boundYu > rows - 1: boundYu = rows - 1
    
    # the pixel value of the sun position
    sunpxl = 125
    
    boundXl = px - glareSize
    boundXu = px + glareSize
    if boundXl < 0: # too left then part of right
        print ('Too left, move to right')
        boundXl2 = boundXl + cols - 1

        if bands == 1:
            cylindrialPanoImg[boundYl:boundYu,boundXl2:cols-1] = sunpxl
            cylindrialPanoImg[boundYl:boundYu,0:boundXu] = sunpxl
        else:
            cylindrialPanoImg[boundYl:boundYu,boundXl2:cols-1, 0] = sunpxl
            cylindrialPanoImg[boundYl:boundYu,boundXl2:cols-1, 1] = 0
            cylindrialPanoImg[boundYl:boundYu,boundXl2:cols-1, 2] = 0

            cylindrialPanoImg[boundYl:boundYu,0:boundXu, 0] = sunpxl
            cylindrialPanoImg[boundYl:boundYu,0:boundXu, 1] = 0
            cylindrialPanoImg[boundYl:boundYu,0:boundXu, 2] = 0

    elif boundXu > cols - 1: 
        print ("too right, move to left")
        boundXu2 = boundXu - cols + 1

        if bands == 1:
            cylindrialPanoImg[boundYl:boundYu,boundXl:cols-1] = sunpxl
            cylindrialPanoImg[boundYl:boundYu,0:boundXu2] = sunpxl
        else: 
            cylindrialPanoImg[boundYl:boundYu,boundXl:cols-1, 0] = sunpxl
            cylindrialPanoImg[boundYl:boundYu,boundXl:cols-1, 1] = 0
            cylindrialPanoImg[boundYl:boundYu,boundXl:cols-1, 2] = 0

            cylindrialPanoImg[boundYl:boundYu,0:boundXu2, 0] = sunpxl
            cylindrialPanoImg[boundYl:boundYu,0:boundXu2, 1] = 0
            cylindrialPanoImg[boundYl:boundYu,0:boundXu2, 2] = 0
        
    else:
        if bands == 1:
            cylindrialPanoImg[boundYl:boundYu,boundXl:boundXu] = sunpxl
        else:
            cylindrialPanoImg[boundYl:boundYu,boundXl:boundXu, 0] = sunpxl
            cylindrialPanoImg[boundYl:boundYu,boundXl:boundXu, 1] = 0
            cylindrialPanoImg[boundYl:boundYu,boundXl:boundXu, 2] = 0


    # cylindrialPanoImg = ShiftCylindricalPanoImg(cylindrialPanoImg, -1*yaw)

    # export the outputCylindricalPanoImage as a new Image file
    imgSunpath = Image.fromarray(cylindrialPanoImg)
    imgSunpath.save(plotedCylindImgFile)
    del imgSunpath
    return cylindrialPanoImg, px, py



# plot the sun path in one day on the cylindrical panorama, using noaa method to estimate the sun position
def plot_SunPathOnCylindricalImage_noaa(cylindrialPanoImg, plotedCylindImg, lat, lon, zone, year, month, day, yaw):
    '''
    # This function is used to plot the sunpath on cylindrical image
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 17, 2018
    
    Parameters: 
        cylindrialPanoImg: the input cylindrical image, numpy array
        plotedFisheyeImg: the output plotted cylindrical panorama with sun position
        lat, lon: the coordinate of the panorama
        zone: the time zone of the area based on UTC, For example Boston is 5
        year, month, day: used to calculate the solar position
        yaw: the yaw angle of the driving car, the north is zero, clockwise
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import SunposLib as sunpos
    
    # shift the original cylindricalPanorama based on the yaw, to make sure the central column is north
    shiftedCylindrialPanoImg = ShiftCylindricalPanoImg(cylindrialPanoImg, yaw)

    # plot the sun positions at different times in one day on the the cylindrical image
    # for month in range(5,6):
    print ('The month is:-------', month)
    for hour in range(5, 20):
        # minute = 30
        second = 30
        for minute in range(0, 60, 10):
            [azimuth, sunele] = sunpos.calcSun(lat, lon, zone, year, month, day, hour, minute, second)
            print ('The hour, sunele and azimuth are:=======', hour, sunele, azimuth)
            [shiftedCylindrialPanoImg, px, py] = plot_SunPosOnCylindricalImage_noaa(shiftedCylindrialPanoImg, plotedCylindImg, azimuth, sunele)

    # unshift the panorama to original orientation
    # shiftedCylindrialPanoImg = ShiftCylindricalPanoImg(shiftedCylindrialPanoImg, -1*yaw)

    # export the outputCylindricalPanoImage as a new Image file
    imgSunpath = Image.fromarray(shiftedCylindrialPanoImg)
    imgSunpath.save(plotedCylindImg)
    del cylindrialPanoImg, imgSunpath, shiftedCylindrialPanoImg



# Judge if the site is shaded or not based on the pysolar, may not work well 
def Shaded_judgement(skyImg, skypixelLabel, glareSize, currentTime,lon, lat):
    '''
    # This function is used to judge if one site is exposed to sunlight or not
    # by overlaying the sunposition on the skyImg
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version Dec 23, 2017
    
    # modified by Dec 28, 2017
    
    # last modified by Feb 10, 2018
    
    Parameters: 
        panoImgFile: the input classified hemispherical image, numpy array
        skypixelLabel: the pixel value of the sky in the segmented classification result
        glareSize: The size of the sun glare, default is 4
        currentTime: the time, time object
        lon, lat are the coordinate of the site
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth, radiation
    
    # read the hemispherical image
    # skyImg = np.array(Image.open(panoImgFile))
    [cols, rows] = skyImg.shape
    
    # calculate the position of sun based on the coordinate and the time information
    # sunele = get_altitude(lat, lon, currentTime)
    # sunele = sunele*np.pi/180.0
    
    # azimuth = 180 - abs(get_azimuth(lat, lon, currentTime))
    # azimuth = azimuth*np.pi/180.0 + 0.5*np.pi
    
    sunele = get_altitude(lat, lon, currentTime) #the sun elevation angle
    azimuth = abs(get_azimuth(lat, lon, currentTime)) #the get_azimuth will get azimuth start from south as zero
    
    #adjusted sun azimuthal angle, the north is the zero
    azimuth = 180 + azimuth
    if azimuth > 360: azimuth = azimuth - 360
    
    # adjust the azimuth to to the image azimth, the east is the zero
    azimuth = 360 - azimuth + 90
    if azimuth > 360: azimuth = azimuth - 360

    sunele = sunele*np.pi/180.0
    azimuth = azimuth*np.pi/180.0
    
    
    # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
    R = int(0.5*rows)
    
    # get the r in the polar coordinate
    if sunele < 0: sunele = 0

    # Using different coordinate, equidistance or equi-anglular hemispherical
    # r = math.cos(sunele)*R
    r = (90 - sunele*180/np.pi)/90.0*R

    # get the coordinate of the point on the fisheye images
    px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
    py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
    
    # the sun glare size
    boundXl = px - glareSize
    if boundXl < 0: boundXl = 0
    boundXu = px + glareSize
    if boundXu > cols - 1: boundXu = rows - 1
    boundYl = py - glareSize
    if boundYl < 0: boundYl = 0
    boundYu = py + glareSize
    if boundYu > rows - 1: boundYu = cols - 1
    
    # judge if the sun is located on obstruction or open sky pixel
    # idx = np.where(skyImg[boundYl:boundYu,boundXl:boundXu] > 0)
    # based on the classification algorith of the pspnet, the sky pixels have the value of 2, it may change in different classification result
    idx = np.where(skyImg[boundYl:boundYu,boundXl:boundXu] == skypixelLabel)
    
    if len(idx[0])/(4*glareSize*glareSize) > 0.5:
        #print ('This site is not shaded')
        shade = 0
    else:
        #print ('The site is shaded')
        shade = 1
    del skyImg
    return shade
    


# Judge if the site is shaded or not based on the hemispherical image, using noaa method
# azimuth and sunele are in degrees
def Shaded_judgement_noaa(skyImg, obstructionpixelLabel, glareSize, azimuth, sunele):
    '''
    # This function is used to judge if one site is exposed to sunlight or not
    # by overlaying the sunposition on the skyImg
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version Dec 23, 2017
    
    # modified by Dec 28, 2017
    
    # last modified by Feb 10, 2018
    
    Parameters: 
        panoImgFile: the input classified hemispherical image, numpy array
        obstructionpixelLabel: the pixel value of the obstruction in the segmented classification result
        glareSize: The size of the sun glare, default is 4
        azimuth, sunele: the azimuth and sun elevation angle
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    
    # read the hemispherical image
    # skyImg = np.array(Image.open(panoImgFile))
    [cols, rows] = skyImg.shape
    

    # considering the different coordinate system, the sun azimuth calculated from sun pos 
    # need to convert to the same coordinate system with the hemispherical image
    # the azimuth start from north, with clockwise; the azimuth_skyimg starts from east direction anti-clockwisely
    azimuth_skyimg = -(azimuth - 90)
    if azimuth_skyimg < 0: azimuth_skyimg = azimuth_skyimg + 360
    
    sunele = sunele*np.pi/180.0
    azimuth = azimuth_skyimg*np.pi/180.0
    
    
    # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
    R = int(0.5*rows)
    
    # get the r in the polar coordinate
    if sunele < 0: sunele = 0
    
    # Using different coordinate, equidistance or equi-anglular hemispherical
    # r = math.cos(sunele)*R
    r = (90 - sunele*180/np.pi)/90.0*R
    
    # get the coordinate of the point on the fisheye images
    px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
    py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
    
    # the sun glare size
    boundXl = px - glareSize
    if boundXl < 0: boundXl = 0
    boundXu = px + glareSize
    if boundXu > cols - 1: boundXu = rows - 1
    boundYl = py - glareSize
    if boundYl < 0: boundYl = 0
    boundYu = py + glareSize
    if boundYu > rows - 1: boundYu = cols - 1
    
    # judge if the sun is located on obstruction or open sky pixel
    # idx = np.where(skyImg[boundYl:boundYu,boundXl:boundXu] > 0)
    # based on the classification algorith of the pspnet, the sky pixels have the value of 2, it may change in different classification result
    idx = np.where(skyImg[boundYl:boundYu,boundXl:boundXu] != obstructionpixelLabel)
    
    if len(idx[0])/(4*glareSize*glareSize) > 0.5:
        #print ('This site is not shaded')
        shade = 0
    else:
        #print ('The site is shaded')
        shade = 1
    del skyImg
    return shade



# Judge if the site is shaded or not based on the cylindrical panorama, using noaa method to estimate the sun position
# This one is suitable for the summer, when the street tree canopies are considered as the obstruction
def Shaded_cylindrical_judgement_noaa(cylindrialPanoImg, skypixelLabel, glareSize, azimuth, sunele, yaw):
    '''
    # This function is used to judge if one site is exposed to sunlight or not
    # by overlaying the sunposition on the segmented cylindrical panoramas
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 16, 2018
    
    Parameters: 
        cylindrialPanoImg: the input classified cylindrical image, numpy array
        skypixelLabel: the pixel value of the sky in the segmented classification result
        glareSize: The size of the sun glare, default is 4
        azimuth, sunele: the azimuth and sun elevation angle
        yaw: the yaw angle of the driving car, the north is zero, clockwise
    '''
    

    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    
    # read the hemispherical image
    # cylindrialPanoImg = np.array(Image.open(panoImgFile))
    dims = cylindrialPanoImg.shape
    rows = dims[0]
    cols = dims[1]
    if len(dims) > 2:
        bands = dims[2]
    else:
        bands = 1

    # shift the original segmented based on the yaw angle
    cylindricalSkyImg = ShiftCylindricalPanoImg(cylindrialPanoImg, yaw)
    
    # get the row and col number of sun pos on the cylindrical panorama, it depends on the side of image
    [px, py] = SunPosOnCylindricalImage_noaa(cylindricalSkyImg, azimuth, sunele)
    del cylindrialPanoImg
    
    
    #####################################################
    # # based on the definition of the equidistant cylindrical projection, the distortion vertical rate is 1, the horizontal rate is 1/cos(theta)
    # # the vertical size of the sun glare zone is 25, the horizontal is 25/cos(sunele)
    # xglareSize = int(glareSize/math.cos(sunele*np.pi/180.0))
    # yglareSize = glareSize

    # # locate the glare zone based on the glaresize
    # boundYl = py - yglareSize
    # if boundYl < 0: boundYl = 0
    # boundYu = py + yglareSize
    # if boundYu > rows - 1: boundYu = rows - 1

    # boundXl = px - xglareSize
    # boundXu = px + xglareSize

    # # calculate the percentage of the sky pixel
    # if boundXl < 0: # too left then part of right
    #     # print ('Too left, move to right')
    #     boundXl2 = boundXl + cols - 1
    #     idx1 = np.where(cylindricalSkyImg[boundYl:boundYu,boundXl2:cols-1] == skypixelLabel)
    #     idx2 = np.where(cylindricalSkyImg[boundYl:boundYu,0:boundXu] == skypixelLabel)
        
    #     # the number of sky pixels number in the sun glare zone
    #     skypixelNum = len(idx1[0]) + len(idx2[0])

    # elif boundXu > cols - 1: 
    #     # print ("too right, move to left")
    #     boundXu2 = boundXu - cols + 1
    #     idx1 = np.where(cylindricalSkyImg[boundYl:boundYu,boundXl:cols-1] == skypixelLabel)
    #     idx2 = np.where(cylindricalSkyImg[boundYl:boundYu,0:boundXu2] == skypixelLabel)

    #     # the number of sky pixels number in the sun glare zone
    #     skypixelNum = len(idx1[0]) + len(idx2[0])

    # else:
    #     idx = np.where(cylindricalSkyImg[boundYl:boundYu,boundXl:boundXu] == skypixelLabel)
        
    #     # the number of sky pixels number in the sun glare zone
    #     skypixelNum = len(idx[0]) # idx is a two dimensiontal array

    ######################################################
    
    
    # based on the classification algorith of the pspnet, the sky pixels have the value of 2, it may change in different classification result    
    if cylindricalSkyImg[py,px] == 2 or cylindricalSkyImg[py,px] == 16: #skypixelNum/(4*xglareSize*yglareSize) > 0.5:
        shade = 0 # not shaded/obstructed
    else: 
        shade = 1 # shaded/obstructed
    
    del cylindricalSkyImg
    return shade



# Judge if the site is shaded or not based on the cylindrical panorama, using noaa method to estimate the sun position
# This is used to judge the obstructions in winter, considering the fact the tree canopies cannot fully obtruct the sun
# glare during winter seasons. 
def Shaded_cylindrical_winter_judgement_noaa(cylindrialPanoImg, obstructionpixelLabel, glareSize, azimuth, sunele, yaw):
    '''
    # This function is used to judge if one site is exposed to sunlight or not
    # by overlaying the sunposition on the segmented cylindrical panoramas
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 16, 2018
    
    Parameters: 
        panoImgFile: the input classified hemispherical image, numpy array
        obstructionpixelLabel: the pixel value of the obstruction in the segmented classification result
        glareSize: The size of the sun glare, default is 4
        azimuth, sunele: the azimuth and sun elevation angle
        yaw: the yaw angle of the driving car, the north is zero, clockwise
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    
    # read the hemispherical image
    # cylindrialPanoImg = np.array(Image.open(panoImgFile))
    dims = cylindrialPanoImg.shape
    rows = dims[0]
    cols = dims[1]
    if len(dims) > 2:
        bands = dims[2]
    else:
        bands = 1

    # shift the original segmented based on the yaw angle
    cylindricalSkyImg = ShiftCylindricalPanoImg(cylindrialPanoImg, yaw)

    del cylindrialPanoImg

    # get the height of the sun position on the cylindrical panorama
    py = int(0.5*rows - sunele/90.0*0.5*rows)

    # get the column of the sun position on the cylindrical panorama
    if azimuth > 180: azimuth = azimuth - 360
    px = int(azimuth/360.0*cols + 0.5*cols)

    # based on the definition of the equidistant cylindrical projection, the distortion vertical rate is 1, the horizontal rate is 1/cos(theta)
    # the vertical size of the sun glare zone is 25, the horizontal is 25/cos(sunele)
    xglareSize = int(glareSize/math.cos(sunele*np.pi/180.0))
    yglareSize = glareSize

    # locate the glare zone based on the glaresize
    boundYl = py - yglareSize
    if boundYl < 0: boundYl = 0
    boundYu = py + yglareSize
    if boundYu > rows - 1: boundYu = rows - 1

    boundXl = px - xglareSize
    boundXu = px + xglareSize

    # calculate the percentage of the sky pixel
    if boundXl < 0: # too left then part of right
        # print ('Too left, move to right')
        boundXl2 = boundXl + cols - 1
        # cylindricalSkyImg[boundYl:boundYu,boundXl2:cols-1, 0] = 255
        # cylindricalSkyImg[boundYl:boundYu,0:boundXu, 0] = 255
        idx1 = np.where(cylindricalSkyImg[boundYl:boundYu,boundXl2:cols-1] != obstructionpixelLabel)
        idx2 = np.where(cylindricalSkyImg[boundYl:boundYu,0:boundXu] != obstructionpixelLabel)
        
        # the number of sky pixels number in the sun glare zone
        skypixelNum = len(idx1[0]) + len(idx2[0])

    elif boundXu > cols - 1: 
        # print ("too right, move to left")
        boundXu2 = boundXu - cols + 1
        # cylindricalSkyImg[boundYl:boundYu,boundXl:cols-1, 0] = 255
        # cylindricalSkyImg[boundYl:boundYu,0:boundXu2, 0] = 255
        idx1 = np.where(cylindricalSkyImg[boundYl:boundYu,boundXl:cols-1] != obstructionpixelLabel)
        idx2 = np.where(cylindricalSkyImg[boundYl:boundYu,0:boundXu2] != obstructionpixelLabel)

        # the number of sky pixels number in the sun glare zone
        skypixelNum = len(idx1[0]) + len(idx2[0])

    else:
        idx = np.where(cylindricalSkyImg[boundYl:boundYu,boundXl:boundXu] != obstructionpixelLabel)
        # cylindricalSkyImg[boundYl:boundYu,boundXl:boundXu, 0] = 255
        
        # the number of sky pixels number in the sun glare zone
        skypixelNum = len(idx[0]) # idx is a two dimensiontal array

    # print ('The sky pixel number is:', skypixelNum)
    # based on the classification algorith of the pspnet, the sky pixels have the value of 2, it may change in different classification result    
    if skypixelNum/(4*xglareSize*yglareSize) > 0.5:
        #print ('This site is not shaded')
        shade = 0
    else: 
        #print ('The site is shaded')
        shade = 1

    del cylindricalSkyImg
    return shade




# estimate direct radiation based on the hemispherical image and sun path
def direct_shaded_radiation(skyImg,currentTime,lon, lat):
    '''
    # This function is used to estimate the direct solar radiation for one time
    at the site of (lon, lat), the direct radiation will be multiplied by the
    shade condition based on overlaying the sun position and open sky hemispherical image
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab, SunExpo team
    # First version Dec 23, 2017
    
    # last modified by Dec 31, 2017
    
    Parameters: 
        panoImgFile: the input classified hemispherical image, numpy array
        currentTime: the time, time object
        lon, lat are the coordinate of the site
    
    return:
        the amount of direct solar radiation multiply the 
        
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth, radiation
    
    # read the hemispherical image
    # skyImg = np.array(Image.open(panoImgFile))
    [cols, rows] = skyImg.shape
    
    # calculate the position of sun based on the coordinate and the time information
    sunele = get_altitude(lat, lon, currentTime)    
    
    # calculate the direct solar radiation
    directRad = radiation.get_radiation_direct(currentTime, sunele)
    
    # convert the sunele into radius
    sunele = sunele*np.pi/180.0
    
    # calculate the azimuth angle and match with the generated hemispherical image
    azimuth = 180 - abs(get_azimuth(lat, lon, currentTime))
    azimuth = azimuth*np.pi/180.0 + 0.5*np.pi
    
    # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
    R = int(0.5*rows)
    
    # get the r in the polar coordinate
    if sunele < 0: sunele = 0
    r = math.cos(sunele)*R
    
    # get the coordinate of the point on the fisheye images
    px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
    py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
    
    # set the points as red
    buff = 2
    boundXl = px - buff
    if boundXl < 0: boundXl = 0
    boundXu = px + buff
    if boundXu > cols - 1: boundXu = rows - 1
    boundYl = py - buff
    if boundYl < 0: boundYl = 0
    boundYu = py + buff
    if boundYu > rows - 1: boundYu = cols - 1
    
    # judge if the sun is located on obstruction or open sky pixel
    idx = np.where(skyImg[boundYl:boundYu,boundXl:boundXu] > 0)
    
    if len(idx[0])/(4*buff*buff) > 0.25:
        #print ('This site is not shaded')
        shade = 1
    else:
        #print ('The site is shaded')
        shade = 0
    del skyImg
    
    return shade*directRad
    

# For the calculation of the SVF
def SVFcalculationOnFisheye(skyImg, skyPixlValue=1):
    '''
    This script is used to calculate the Sky View Factor from the binary classification
    result of re-projected Sphere view Google Street View panorama
    
    https://www.researchgate.net/profile/Silvana_Di_Sabatino/publications/2
    https://www.unibo.it/sitoweb/silvana.disabatino/en
    Recommended by Rex
    
    copyright(c) Xiaojiang Li, UCONN, MIT Senseable City Lab
    First version June 27, 2016, in MIT SCL, Messi loses again. 
    
    The function is used to calcualte the SVF based on the SKY extract result
    
    Input: 
        skyImg: the input sky extraction result in numpy array format
        skyPixlValue: the pixel value of the sky pixels
    Output:
        SVFres: the value of the SVF
    '''
    
    import numpy as np
    import math
    
    # read the sky image and get the metadata of the sky image
    # skyImg = np.array(Image.open(skyImgFile))
    
    rows = skyImg.shape[0]
    cols = skyImg.shape[1]
    
    # split the sphere view images into numbers of strips based on spikes
    ringNum = 36
    ringRad = rows/(2.0*ringNum)
    
    # the center of the fisheye image
    Cx = int(0.5*cols)
    Cy = int(0.5*rows)
    
    # the SVF value
    SVF = 0.0
    
    for i in range(ringNum):
        # calculate the SVFi for each ring
        ang = np.pi*(i - 0.5)/(2*ringNum)
        SVFmaxi = 2*np.pi/(4*ringNum)*math.sin(np.pi*(2*i-1)/(2*ringNum))
        
        # the radii of inner limit and the outer limit
        radiusI = i*ringRad
        radiusO = (i+1)*ringRad
        
        # Total areas (pixels) of sky in the ring region, search in a squre box
        totalSkyPxl = 0
        totalPxl = 0
        
        for x in range(int(Cx - (i+1)*ringRad),int(Cx + (i+1)*ringRad)):
            for y in range(int(Cy - (i+1)*ringRad),int(Cy + (i+1)*ringRad)):
                # the distance to the center of the fisheye image
                dist2Center = math.sqrt((x - Cx)**2 + (y - Cy)**2)
                
                # if the pixel in the search box in the ring region
                if dist2Center > radiusI and dist2Center <= radiusO and skyImg[x,y] == skyPixlValue:
                    totalSkyPxl = totalSkyPxl + 1
                if dist2Center > radiusI and dist2Center <= radiusO:
                    totalPxl = totalPxl + 1
        
        #alphai = totalSkyPxl/(np.pi*(radiusO**2 - radiusI**2))
        alphai = totalSkyPxl*1.0/totalPxl
        
        SVFi = SVFmaxi*alphai
        SVF = SVF + SVFi

    print ('The calculated SVF value is:',SVF)    
    return SVF
    



def DirectRadiationEst(skyImgFile,timeLst):
    '''
    # This is function is used to calculate the direct solar
    radiation based on the classified hemisperhical photos
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 22ed, 2017
    
    
    # Modified by April 20, 2018, Xiaojiang Li, MIT Senseable City Lab
    # in the revised version, the cosine effect is corrected, using the zenith
    # angle rather than the sun elevation angle
    
    
    Parameters: 
        skyImgFolder: the input sky image folder
        timeList: the time series, timeList = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    
    return:
        the estimated direct solar radiation
    
    '''
    
    from PIL import Image
    import numpy as np
    import urllib
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth
    
    
    # read GSV panorama images
    basename = os.path.basename(skyImgFile)[:-4]
    
    fields = basename.split(' - ')
    panoID = fields[0]
    lon = float(fields[1])
    lat = float(fields[2])
    #month = fields[3][-2:]
    
    # read te skyimage file into sky image
    skyImg = np.array(Image.open(skyImgFile))
    [rows,cols] = skyImg.shape
    
    # the direct and the diffuse radiation
    dir_radiation = 0 # radiation after the shading
    dir_T_radiation = 0  # the total radiation
    
    # the solar radiation at specific time
    directRadLst = []
    hours = 0
    
    # calculate for each day
    for i in range(len(timeLst)):
        currentTime = timeLst[i]
        
        # flag whether one site is under the shade 0 or not 1
        flag = 1
        
        # calculate the position of sun based on the coordinate and the time information
        sunele = get_altitude(lat, lon, currentTime)
        sunele = sunele*np.pi/180.0
        
        azimuth = abs(get_azimuth(lat, lon, currentTime)) + 180
        if azimuth > 360:
            azimuth = azimuth - 360
        azimuth = azimuth*np.pi/180.0 + 0.5*np.pi
        
        # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
        R = int(0.5*rows)
        
        # get the r in the polar coordinate
        if sunele < 0:
            flag = 0
            sunele = 0
        
        # differnet way to put the sunpath in the fisheye image
        r = 2*R*(0.5*np.pi - sunele)/np.pi   # the distrance between different degree is equal
        
        # get the coordinate of the point on the fisheye images
        px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
        py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
        
        
        # if the x,y is out of the hemispherical images
        radi = math.sqrt((px - 0.5*cols)**2 + (py - 0.5*rows)**2)
        #print ('The radius is:=================', radi)
        if radi >= 0.5*cols:
            flag = 0
        
        # check whether the site is located on the clear sky or the obstructions
        buff = 10
        boundXl = px - buff
        if boundXl < 0: boundXl = 0
        boundXu = px + buff
        if boundXu > cols - 1: boundXu = rows - 1
        boundYl = py - buff
        if boundYl < 0: boundYl = 0
        boundYu = py + buff
        if boundYu > rows - 1: boundYu = cols - 1
        
        # create a circle like sun postion
        for x in range(boundXl,boundXu):
            for y in range(boundYl, boundYu):
                
                # calculate the distance between the pixel with the center
                dist = math.sqrt((x - px)**2 + (y - py)**2)
                
                if dist < buff:
                    if skyImg[y,x] < 1 and flag == 1:
                        flag = 0
                        skyImg[y,x] = 125
                        continue
            continue
        
        # estimate the direct radiation for this time is, using the cos(zenith) or sin(sunele)
        directRad = flag*math.sin(sunele)
        direct_T_Rad = math.sin(sunele)
        dir_radiation = dir_radiation + directRad
        dir_T_radiation = dir_T_radiation + direct_T_Rad
        
        if flag == 1:
            hours = hours + 1
    #print ('The number of hour is',hours)
    
    # estimate 14 hours direct radiation
    dir_radiation = dir_radiation/dir_T_radiation
    #print ('The proportion of the dirction radiation is:', dir_radiation)
    
    return dir_radiation



def DiffuseRadiationEst(skyImgFile,skymapfile):
    '''
    The fuction is used to estimate the the diffuse radiation based on sky image
    Reference:
        http://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/how-solar-radiation-is-calculated.htm
    parameters:
        skyImgFile: the input sky image file
        skymapfile: the input skymap file
    
    return:
        the diffused radiation
    
    First version March 23, 2017
    Author: Xiaojiang Li, MIT Senseable City Lab
    '''
    
    import os,os.path
    from PIL import Image
    import math
    import numpy as np
    
    skyImg = np.array(Image.open(skyImgFile))
    skyMap = np.array(Image.open(skymapfile))
    [rows,cols] = skyImg.shape
    n_skySector = int(skyMap.max())
    R = 0.5*cols # the radius of the sky image
    #print ('The rows and cols are, the number of sky sectors is:',rows,cols,n_skySector)
    
    # initialize the diffuse radiation
    difRadiation = 0
    
    # loop all sectors in the sky map
    for i in range(1,n_skySector + 1):
        idx = np.where(skyMap == i)
        
        # the number of total pixels in each sector
        n_pxl = len(idx[0])
        
        # get the number of visible sky pixels
        skyImg = skyImg>0
        n_sky_pxl = sum(skyImg[idx])
        
        # the gap fraction in each sector
        gapFraction = n_sky_pxl/n_pxl
        
        # there are 16 azimuthal sections, and 8 zenith sections
        azDiv = 16
        zenDiv = 8
        
        # calculate the weight for each sector
        theta1 = int((i - 0.0001)/azDiv)
        theta1 = theta1/zenDiv * (0.5*np.pi)
        theta2 = theta1 + (0.5*np.pi)/zenDiv
        weight = (math.cos(theta1) - math.cos(theta2))/azDiv
        
        # the zenith angle, I use the mean value of the theta1 and theta2
        theta = (theta1 + theta2)/2
        
        # the diffuse radiation equals the cos(theta)*weight*gapFraction
        diffueR_tem = 2*math.cos(theta)*weight*gapFraction
        
        # The total diffuse radiation
        difRadiation = difRadiation + diffueR_tem
    
    basename = os.path.basename(skyImgFile)
    #print('The file and total diffuseRadiation are:',basename,difRadiation)
    
    return difRadiation
    




def UV_transmision(zenith, obstruction, SVF):
    """
    This function is used to estimate the percentage of UV radiation reaching the 
    street canyons based on hemispherical images and the sun path, there are two 
    major parts of UV radiation reaching the ground, direct beam and diffusion
    the direct beam can be estimated based on the obstruction, and the diffuseion 
    can be estimated based on the SVF. The returned ratio will need to multiply the 
    UV index to get the actual UV index in the street canyons
    
    Reference: 
        https://www.epa.gov/enviro/web-services#hourlyzip
        https://www.epa.gov/sunsafety
        
        PhD dissertation of Roberto Hernandez, 2015
    
    Parameters:
        zenith: the sun zenith angle, in degree
        obstruction: 1 for obstructed, 0 open sky
        SVF: the sky view factor value
    
    return:
        UV_transRatio: the ratio of the UV reaching the street canyon
    
    Last modified by Xiaojiang Li, MIT Senseable City Lab, Jan 8th, 2018
    """
    
    import sys
    import math
    import numpy as np

    # if the point at the time, sun is blocked, then shade is 0 or is 1
    opensky_bool = 1 - obstruction

    # calcualte the percentages of the direct radiation and the diffuse radiation
    dif_rad_ratio_list = []

    # convert the zenith angle to radians
    zenith = np.pi*zenith/180.0

    # band width of UV radiation, based on EPA, UV band width ranges from 280-400nm
    numda_range = range(280,400,3)
    for numda in numda_range:
        exponent = math.pow(280.0/numda, 4*0.79)
        exponent = exponent * math.pow(1 - (255.0/numda)**10, 1 - math.tan(zenith))
        exponent = -exponent/math.cos(zenith)
        dif_rad_ratio = 1 - math.exp(exponent)        
        dif_rad_ratio_list.append(dif_rad_ratio)

    # convert the list to array and calculate the mean value of the diff/total ratio 
    dif_rad_ratioArr = np.asarray(dif_rad_ratio_list)
    diffRatio = np.mean(dif_rad_ratioArr)
    print ('The mean diffuse ratio is:', diffRatio)
    
    # estimate the accumulated exposure to UV radiation
    # The total UV exposure should be calculated as: (opensky_bool*(1 - diffRatio) + SVF*diffRatio)*UV_value
    UV_transRatio = opensky_bool*(1 - diffRatio) + SVF*diffRatio
    
    return UV_transRatio




def UV_radiation(zipcode, UV_transRatio, time):
    """
    This function is used to estimate the amount of UV radiation based on the estimated 
    UV transmitant ratio (from the function of "UV_transmision") and the amount of the 
    UV index images and the UV index
    
    
    Reference: 
        https://www.epa.gov/enviro/web-services#hourlyzip
        https://www.epa.gov/sunsafety
        
        PhD dissertation of Roberto Hernandez, 2015
    
    Parameters:
        zipcode: the zipcode of the current location
        zenith: the sun zenith angle, in degree
            
    return:
        the UV index of the zip code area in form of json
    
    Last modified by Xiaojiang Li, MIT Senseable City Lab, Jan 5th, 2018
    """

    # get the UV map for any location
    
    import json
    import sys
    import math
    import numpy as np

    uv_idx = 4
    # estimate the accumulated exposure to UV radiation
    UV_value = UV_transRatio*uv_idx


#   # the URL address of the UV index, UV index API: https://www.epa.gov/enviro/web-services
#   uv_req_json = "https://iaspub.epa.gov/enviro/efservice/getEnvirofactsUVHOURLY/ZIP/%s/json"%(zipcode)
#   print ('The url address i:', uv_req_json)
    
    
#   # judge the version of the python you are using
#   version = sys.version_info[0]
#   if version == 2:
#       import urllib2
#       import urllib, urllib2
#       import xmltodict

#       print ('You are using python 2')
#       opener = urllib2.build_opener()
#       f = opener.open(uv_req_json)
#       uv_idx_lst = json.loads(f.read())

#       # loop all UV idx hourly
#       for i in range(len(uv_idx_lst)):
#           uv_obj = uv_idx_lst[i]
#           uv_idx = uv_obj['UV_VALUE']
#           hour = uv_obj['DATE_TIME']

#           print ('The UV index at %s is %s '%(hour, uv_idx))

#     # elif version == 3:
#     #     import requests
#     #     import json

#     #     print ('You are using Python3')
#     #     r = requests.get(uv_req_json)
#     #     uv_idx_lst = r.json()

#     #     # loop all uv idx in the list of the json object
#     #     for i in range(len(uv_idx_lst)):
#     #         uv_obj = uv_idx_lst[i]
#     #         uv_idx = uv_obj['UV_VALUE']
#     #         hour = uv_obj['DATE_TIME']

#     #         print ('The UV index at %s is %s '%(hour, uv_idx))
    
    return UV_value






# ---------Main function, example---------
if __name__ == "__main__":
    import datetime
    import os,os.path
    from PIL import Image
    import numpy as np
    import SunposLib as sunpos

    #panoFolder = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/ShadeProvisionBoston/code'
    panoFolder = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab'

    panoId = "U8B4cKDxnauFW-Yt7siKtw"
    panoId = "c8gcWEqLiOcVwDrtJDiB4g"
    panoId = "8TrMswYKbaU8FCSYFlQuqQ"
    panoId = "n9rwq7DxgtoWkD8I96caEg"
    panoId = "4G5km0yE7QsmzxE7YBPRYw"
    panoId = "XSBf9u3gM6LVrrhKTXZO6w" # https://www.google.com/maps/@42.391247,-71.110218,3a,90y,187.3h,110.37t/data=!3m6!1e1!3m4!1sXSBf9u3gM6LVrrhKTXZO6w!2e0!7i13312!8i6656
    panoId = "WFeq-xC3gkzkPDxU2Os3Zw" # https://www.google.com/maps/@42.3908457,-71.1093114,3a,75y,205.58h,110.3t/data=!3m6!1e1!3m4!1sWFeq-xC3gkzkPDxU2Os3Zw!2e0!7i13312!8i6656
    panoId = "98t1y9unJQ6JSHk9w8WBkA" # https://www.google.com/maps/@42.3630527,-71.0995882,3a,75y,222.56h,120.17t/data=!3m7!1e1!3m5!1s98t1y9unJQ6JSHk9w8WBkA!2e0!6s%2F%2Fgeo1.ggpht.com%2Fcbk%3Fpanoid%3D98t1y9unJQ6JSHk9w8WBkA%26output%3Dthumbnail%26cb_client%3Dmaps_sv.tactile.gps%26thumb%3D2%26w%3D203%26h%3D100%26yaw%3D164.61484%26pitch%3D0%26thumbfov%3D100!7i13312!8i6656
    panoId = "-kYdtGyFfKaIeQjji2Cd0g" # yaw: 309.38, https://www.google.com/maps/@42.3606862,-71.0957474,3a,75y,301.9h,82.93t/data=!3m7!1e1!3m5!1s-kYdtGyFfKaIeQjji2Cd0g!2e0!5s20130901T000000!7i13312!8i6656
    panoId = "qg2tq2RkyYBIWMNLADjwpg" # yaw: 55.649998, https://www.google.com/maps/@42.3573843,-71.1004699,3a,75y,207.7h,118.23t/data=!3m7!1e1!3m5!1sqg2tq2RkyYBIWMNLADjwpg!2e0!5s20130901T000000!7i13312!8i6656
    panoId = "Ef9pF_YcUTz2MRUsT-DvwA" # yaw: 273.156433105 
    panoId = "uUxR_NdBVXujWIjZmTqJiw"
    
    panoImgFile = os.path.join(panoFolder,panoId + '.jpg')
    panoImg = GSVpanoramaDowloader_GoogleMaps(panoId,panoImgFile)
    
    hemiImgFile = os.path.join(panoFolder, panoId + '_hemi.jpg')
    cylinder2fisheyeImage (panoImg,0,hemiImgFile)
    
    # specify the date information
    year = 2018
    month = 4
    day = 23
    hour = 7
    minute = 0

    # for Boston
    lat = 42.3624523811
    lon = 71.0862483971
    zone = 5
    daySavings = 0 # began on Mar11 ends on Nov 4

    yaw = 273.156433105
    glareSize = 25
    obstructionpixelLabel = 0

    plotedFisheyeImg = os.path.join(panoFolder, panoId+'-hemi-ploted.jpg')
    plotedCylindImg = os.path.join(panoFolder, panoId+'-cylin-ploted.jpg')

    [azimuth, sunele] = sunpos.calcSun(lat, lon, zone, year, month, day, hour, minute, 30)
    print ('The year-month-hour-minute, the azimuth, sunele, are', year, month, hour, minute, azimuth, sunele)
    # SunPosOnFisheyeimage_noaa(hemiImgFile,plotedFisheyeImg, azimuth, sunele)
    # Shaded_cylindrical_judgement_noaa(panoImg, obstructionpixelLabel, glareSize, azimuth, sunele, yaw)
    # SunPosOnCylindricalImage_noaa(panoImg, plotedCylindImg, azimuth, sunele, yaw)
    # SunPathOnCylindricalImage_noaa(panoImg, plotedCylindImg, lat, lon, zone, year, month, day, yaw)
    

    ###---------------- Plot the sun path on the cylindrical images --------------------------------
    # panoImgFile = os.path.join(panoFolder, '-kYdtGyFfKaIeQjji2Cd0g-seg.jpg') #segmented image, yaw = 117.718757629
    # # panoImgFile = os.path.join(panoFolder, '-kYdtGyFfKaIeQjji2Cd0g-pano-plotted') #original pano
    # plotedCylindImg = os.path.join(panoFolder, '-kYdtGyFfKaIeQjji2Cd0g-seg-plotted.jpg')
    # yaw = 309.38 #based on the metadata

    # panoImgFile = os.path.join(panoFolder, 'qg2tq2RkyYBIWMNLADjwpg.jpg') #segmented image, yaw = 55.649998
    # plotedCylindImg = os.path.join(panoFolder, 'qg2tq2RkyYBIWMNLADjwpg-pano-plotted.jpg')
    # yaw = 55.649998

    panoImgFile = os.path.join(panoFolder, '-kYdtGyFfKaIeQjji2Cd0g-seg.jpg') #segmented image, yaw = 55.649998
    plotedCylindImg = os.path.join(panoFolder, '-kYdtGyFfKaIeQjji2Cd0g-seg-plotted.jpg')
    yaw = 309.38
    
    # panoImg = np.array(Image.open(panoImgFile))
    # # SunPathOnCylindricalImage_noaa(panoImg, plotedCylindImg, lat, lon, zone, year, month, day, yaw)
    # panoImg = ShiftCylindricalPanoImg(panoImg, yaw)
    # SunPosOnCylindricalImage_noaa(panoImg, plotedCylindImg, azimuth, sunele)
    # shade = Shaded_cylindrical_judgement_noaa(panoImg, obstructionpixelLabel, glareSize, azimuth, sunele, yaw)
    # print('This site is shade or not', shade) # 0 not shaded, 1 is shaded


    # ## ---------------Judgement of the sun glare in winter using Google Street View ------------------------
    # skyImgFolder = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Sun Expo/aws_ec2_ebs1/pspoutput'
    # panoImgFile = os.path.join(skyImgFolder, '_Ah5GODoaFCGuAeW5sFhNw.tiff') #segmented image, yaw = 55.649998
    # print ('The panoImg File is:', panoImgFile)

    # plotedCylindImg = os.path.join(panoFolder, '_Ah5GODoaFCGuAeW5sFhNw-plotted.jpg')
    # yaw = 119.998733521
    # panoImg = np.array(Image.open(panoImgFile))
    # panoImg = ShiftCylindricalPanoImg(panoImg, yaw)
    # SunPosOnCylindricalImage_noaa(panoImg, plotedCylindImg, azimuth, sunele)
    # shade = Shaded_cylindrical_winter_judgement_noaa(panoImg, obstructionpixelLabel, glareSize, azimuth, sunele, yaw)
    # print('This site is shade or not', shade) # 0 not shaded, 1 is shaded
    
    