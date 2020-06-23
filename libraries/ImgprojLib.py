
# This program includes all functions about image projection,
# these functions include projection
#      from cylinder to fisheye image
#      from fisheye image to cylindrical image,
#      from cylindrical image to perspective projection

# Copyright(c) Xiaojiang Li, MIT Senseable City Lab
# Jan 2ed, 2017, Quincy, MA


import math
import numpy as np
import os, os.path


def cylinder2fisheyeImage_noyaw (inputImage,outputPano):

    '''
    convert the cylindrical panorama into hemispherical, without considering
    the yaw angle
    '''
    import cv2
    from PIL import Image

    print('The input pano image is')
    print('The output pano image is')

    # read GSV panorama images
    basename = os.path.basename(inputImage)[:-4]

    # the output filename
    reprojPanoName = '%s.png'%(basename)
    outputImgFile = os.path.join(outputPano,reprojPanoName)

    # read the panorama and get the metadata
    panoImg = np.array(Image.open(inputImage))
    Hs = panoImg.shape[0]
    Ws = panoImg.shape[1]
    panoImg2 = panoImg[0:int(Hs/2),:]
    del panoImg

    # get the radius of the fisheye
    print('Hs and Ws are', Hs,Ws)
    R1 = 0
    R2 = int(2*Ws/(2*3.1415926) - R1 +0.5) # For google Street View pano

    R22 = Hs + R1
    print ('the first R2 is:',R2)
    print ('The second R2 is:',R22)
    
    
    # estimate the size of the sphere or fish-eye image
    Hd = int(Ws/3.1415926)+2
    Wd = int(Ws/3.1415926)+2

    print ('The Hd and Wd are', Hd, Wd)

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
            theta = 1.5*np.pi - math.atan((yD - CSy)/(xD - CSx+0.0001))

            xS = theta/(2*np.pi)*Ws
            yS = (r - R1)/(R2 - R1)*Hs

            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)

        for xD in range(CSx,Wd):
            r = math.sqrt((yD - CSy)**2 + (xD - CSx)**2)
            theta = 0.5*np.pi - math.atan((yD - CSy)/(xD - CSx+0.0001))

            xS = theta/(2*np.pi)*Ws
            yS = (r - R1)/(R2 - R1)*Hs

            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)


    print ('the destination image size is %s,%s'%(Hd,Wd))
    outputImg = cv2.remap(panoImg2,xmap,ymap,cv2.INTER_NEAREST)

    del xmap,ymap,panoImg2
    print ('The size of output image is:', outputImg.shape)

    img = Image.fromarray(outputImg)
    del outputImg
    img.save(outputImgFile)
    del img




##def cylinder2fisheyeImage (inputImage,outputPano, pano_yaw_deg):
def cylinder2fisheyeImage (inputImage,outputPano, flag = 'gsv'):
    '''
        This program is used to convert cylindrical panorama images to original image
        Copyright (C) Xiaojiang Li, UCONN, MIT Senseable City Lab
        First version June 25, 2016
        
        Be careful, for the GSV panoramas, the R2 and R22 are different, the R22
        or the height based method is 3times of the width based method,however,
        for the example fisheye image collected online the R2 and R22 are almost
        the same. This prove that Google SQUIZED THE COLUMN OF GSV PANORAMA, in
        order to rescale the Google paorama, the colums sould time 3
        
        vecX = xD - CSx
        vecY = yD - CSy
        theta1 = math.asin(vecX/(r+0.0001))
        theta2 = math.acos(vecX/(r+0.0001))
        
        return the created fishey image rotatedFisheyeImg
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import cv2
    
    # read GSV panorama images
    basename = os.path.basename(inputImage)[:-4]
    
    # parsing the file name to get the metadata of the GSV images, for Philips
    fields = basename.split(' - ')
    if len(fields) < 3: return
    print (fields)
    
    if flag == 'streetside':
        lat = fields[0]
        lon = fields[1]
        yaw = fields[2]
        year = fields[3][:4]
        month = fields[3][5:7]
        print('This is streetside image')
    else: # default Google Street View, panoID - lon - lat - year - month - yaw
        panoID = fields[0]
        lon = fields[1]
        lat = fields[2]
        year = fields[3]
        month = fields[4]
        yaw = fields[5]
        print('This is Google Street View images')


    rotateAng = 360 - float(yaw) # the rotate angle
    
    # the output filename
    reprojPanoName = '%s_reproj.png'%(basename) # used to be jpg, png is more flexible
    rotatedFisheyeName = '%s_rotated.png'%(basename)
    outputImgFile = os.path.join(outputPano,reprojPanoName)
    outputRotatdImageFile = os.path.join(outputPano,rotatedFisheyeName)
    
    # the output filename
    reprojPanoName = '%s_reproj.png'%(basename)
    outputImgFile = os.path.join(outputPano,reprojPanoName)
    
    # read the panorama and get the metadata
    panoImg = np.array(Image.open(inputImage))
    panoImg = panoImg.astype('uint8') # This is important for rotation
    Hs = panoImg.shape[0]
    Ws = panoImg.shape[1]
    panoImg2 = panoImg[0:int(Hs/2),:]
    del panoImg
    
    # get the radius of the fisheye
    print ('Hs and Ws are', Hs,Ws)
    R1 = 0
    R2 = int(2*Ws/(2*3.1415926) - R1 +0.5) # For google Street View pano
    
    R22 = Hs + R1
    print ('the first R2 is:',R2)
    print ('The second R2 is:',R22)
    
    
    # estimate the size of the sphere or fish-eye image
    Hd = int(Ws/np.pi)+2
    Wd = int(Ws/np.pi)+2
    
    print ('The Hd and Wd are', Hd, Wd)
    
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
            
    
    print ('the destination image size is %s,%s'%(Hd,Wd))
    # outputImg = cv2.remap(panoImg2,xmap,ymap,cv2.INTER_CUBIC)
    outputImg = cv2.remap(panoImg2,xmap,ymap,cv2.INTER_NEAREST)
    
    
    del xmap,ymap,panoImg2
    print ('The size of output image is:', outputImg.shape)
    
    
    # remove the black line in central column of the buttom
    if len(outputImg.shape) > 2:
        outputImg[int(CSy):,CSx,:] = outputImg[int(CSy):,CSx - 1,:]
        outputImg[int(CSy):,int(CSx + 0.5),:] = outputImg[CSy:,int(CSx + 0.5) + 1,:]
    else:
        outputImg[int(CSy):,CSx] = outputImg[int(CSy):,CSx - 1]
        outputImg[int(CSy):,int(CSx + 0.5)] = outputImg[CSy:,int(CSx + 0.5) + 1]
    

    ## ROTATE THE GENRATED FISHEYE IMAGE TO MAKE SURE THE TOP OF THE FISHEYE IMAGE IS THE NORTH
    [rows,cols] = outputImg.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2),rotateAng,1)
    rotatedFisheyeImg = cv2.warpAffine(outputImg,M,(cols,rows))
    
    img = Image.fromarray(rotatedFisheyeImg)
    del outputImg, rotatedFisheyeImg
    img.save(outputImgFile)
    del img
    
    
def cylinder2fisheye(inputPano,outputPano, flag = 'gsv'):
    '''
    This function is used to convert clylinrical projection images to fisheye images
        inRoot: can be folder or image, the input images are the Goolge Street View cylindrical panorama
        Output: can be folder or image, the output images are fisheye images
    '''
    
    from PIL import Image
    import numpy as np
    import urllib
    import os, os.path
    import math
    import cv2
    
    
    # if the input is folder then list GSV images
    if os.path.isdir(inputPano):
        # if there is no output folder, create one
        if not os.path.exists(outputPano):
            os.makedirs(outputPano)
        
        fileLst = os.listdir(inputPano)
        for file in fileLst:
            panoImgFile = os.path.join(inputPano,file)
            cylinder2fisheyeImage(panoImgFile,outputPano, 'streetside')
    else:
        panoImgFile = inputPano
        cylinder2fisheyeImage(panoImgFile,outputPano, 'streetside')
    


def fisheye2cylinderImage (inputFisheyeImage,outputCylinderImg):
    '''
    # This program is used to convert cylindrical panorama images to original image
    # Copyright (C) Xiaojiang Li, UCONN, MIT Senseable City Lab
    # First version June 24, 2016
    
    Parameters:
        inputFisheyeImage: the input fisheye image
        outputCylinderPano: the generated cylindrical panorama
    
    Using example:
        inputFisheyeImage = r'D:\PhD Project\SkyViewFactProj\Panoramas\Sphere.jpg'
        outputCylinderImg = r'D:\PhD Project\SkyViewFactProj\Panoramas\ReprojectedImg2.jpg'
        cylinder2fisheyeImage (inputFisheyeImage,outputCylinderImg)
    
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import cv2
    
    
    panoImg = np.array(Image.open(inputFisheyeImage))
    Hs = panoImg.shape[0]
    Ws = panoImg.shape[1]
    print ('Hs and Ws are', Hs,Ws)
    
    # the center point of panorama
    Cx = int(0.5*Ws)
    Cy = int(0.5*Hs)
    
    R2 = int(0.5*Hs)
    R1 = 4
    
    Wd = int(2*3.14159*(R1+R2))
    Hd = R2 - R1
    
    print ('the Wd and Hd are',Wd,Hd)
    print ('the Cx and Cy are',Cx,Cy)
    xmap = np.zeros((Hd,Wd),np.float32)
    ymap = np.zeros((Hd,Wd),np.float32)
    
    for yD in range(Hd):
        r = float(yD)/float(Hd)*(R2 - R1) + R1
        for xD in range(Wd):
            theta = float(xD)/float(Wd)*2.0*3.1415926
            xS = Cx + r * np.sin(theta)
            yS = Cy + r * np.cos(theta)
            
            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)
    
    print ('the destination image size is %s,%s'%(Hd,Wd))
    outputImg = cv2.remap(panoImg,xmap,ymap,cv2.INTER_LINEAR)
    print ('The size of output image is:', outputImg.shape)
    
    img = Image.fromarray(outputImg)
    img.save(outputCylinderImg)
    
    

def cylinder2perspective(inputCylinderImage,outputPerspectiveImg,heading,fov, yaw, tilt_yaw, pitch):
    '''
    # This program is used to convert cylindrical panorama images to perspective image
    # The field of view is set to 70
    # In the perspective projection, there are a couple of pareamters, the first is the
    # field of view angle, the second is the heading angle, the third is the pitch angle
    # (Just like what Google Street View Image API)
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version Jan 3, 2017
    
    Parameters:
        inputFisheyeImage: the input fisheye image
        outputCylinderPano: the generated cylindrical panorama
        heading: the heading angle of the perspecitve projection
        fov: the field of view angle
        pitch: the vertical angle 
    
    Using example:
        inputFisheyeImage = r'D:\PhD Project\SkyViewFactProj\Panoramas\Sphere.jpg'
        outputCylinderImg = r'D:\PhD Project\SkyViewFactProj\Panoramas\ReprojectedImg2.jpg'
        cylinder2fisheyeImage (inputFisheyeImage,outputCylinderImg)
        
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import cv2
    
    
    # read the panorama and get the metadata
    panoImg = np.array(Image.open(inputCylinderImage))
    Hs = panoImg.shape[0]
    Ws = panoImg.shape[1]
    
    print ('The size of the panorama is %s, %s'%(Hs,Ws))
    print ('The fov is %s, the heading angle is %s, and the pitch angle is %s'%(fov,heading,pitch))
    
    # the output size of the output static image, it can also been specified by suers
    width = 600
    height = 600
    
    # create empty matrics to store the affine parameters
    xmap = np.zeros((width,height),np.float32)
    ymap = np.zeros((width,height),np.float32)
    
    # calculate the focuses of the system
    fovRadiance = fov*np.pi/180
    yawRadiance = yaw*np.pi/180
    
    tilt_yawRadiance = tilt_yaw*np.pi/180
    focusW = 0.5*width/math.tan(0.5*fovRadiance)
    focusH = 0.5*height/math.tan(0.5*fovRadiance)
    
    pitchRadiance = pitch*np.pi/180
    headingRadiance = heading*np.pi/180        
    
    # find the corresponding pixels for each pixel in the output static image
    for yD in range(height):
        for xD in range(width):
            
            # convert the cartesian projection coordinate to image coordinate
            coorX = xD - 0.5*width
            coorY = 0.5*height - yD
            
            # get the theta and phi based on the coorX and coorY
            theta = headingRadiance + math.atan(coorX/focusW)
            phi = pitchRadiance + math.atan(coorY/focusH)
            
            # convert the theta and phi to image coordinate on cylinder
            xS = Ws*(theta - yawRadiance)/(2*np.pi) + 0.5*Ws
            yS = 0.5*Hs - Hs*(phi + tilt_yawRadiance)/np.pi
            
            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)
    
    # wrap or rectify the distorted cylinderical image to perspective projection
    outputImg = cv2.remap(panoImg,xmap,ymap,cv2.INTER_CUBIC)
    
    del xmap,ymap,panoImg
    print ('The size of output image is:', outputImg.shape)
    
    img = Image.fromarray(outputImg)
    del outputImg
    img.save(outputPerspectiveImg)
    del img
    


def cylinder2perspective2(panoImg, Hd, Wd, fov, pitch, heading):
    '''
    This is to convert the cylindrical panoramas into perspective projection
    images. For higher pitchs, there still have distortions
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab

    last modified Mar 6th, 2019
    '''
    
    fov = fov*np.pi/180.0
    pitch = pitch*np.pi/180.0
    heading = heading*np.pi/180.0
    
    # create empty matrics to store the affine parameters
    xmap = np.zeros((Hd,Wd),np.float32)
    ymap = np.zeros((Hd,Wd),np.float32)

    # (xD, yD) is the location on the perspective image, (xS, yS) is the pixel on the cylindrical
    for xD in range(Wd):
    # for xD in range(1):
        for yD in range(Hd):
            theta = math.atan((xD - 0.5*Wd)/focus) + heading
            phi = math.atan((yD - 0.5*Hd)/focus) - pitch
            
#             if theta < -2*np.pi: theta = theta + 2*np.pi
#             if theta > 2*np.pi: theta = theta - 2*np.pi
#             if phi < -np.pi: phi = phi + np.pi
#             if phi > np.pi: phi = phi - np.pi
            
    #         print('theta and phi are:', theta, phi)
            
            # based on the polar coordinate, locate the corresponding pixel in the cylindrical pano
            xS = (theta + np.pi)/(2*np.pi)*Ws
            yS = (phi + 0.5*np.pi)/(np.pi)*Hs

            if xS >= Ws-1: xS = xS - Ws + 1
    #         print('(xD, yD) and (xS, yS) are: ', xD, yD, xS, yS)

            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)
            
    #     print ('the destination image size is %s,%s'%(Hd,Wd))
    outputImg = cv2.remap(panoImg,xmap,ymap,cv2.INTER_CUBIC)
    
    img = Image.fromarray(outputImg)
    return img



def GSVpanoMetadata_Single_Collector(longitude,latitude):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the coordinate of
    the site, and return the metadata as xml file.

    Copyright(c) Xiaojiang Li, Jan 19, 2017, MIT Sensable City Lab
    
    Parameters: 
        longitude: the shapefile of the create sample sites
        latitude: the latitude of the site
    return [panoid, panodate, panoLon, panoLat, panoYaw]
    
    example:
        [panoId, panoDate, panoLon, panoLat, yawDegree] = GSVpanoMetadata_Single_Collector(lng,lat)
    
    '''
    
    import urllib
    import xmltodict
    import ogr, osr
    import time
    
    lon = longitude
    lat = latitude
    
    # get the meta data of panoramas
    urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s'%(lat,lon)
    time.sleep(0.01)
    
    # the output result of the meta data is a xml object
    metaDataxml = urllib.request.urlopen(urlAddress)    
    metaData = metaDataxml.read()

    data = xmltodict.parse(metaData)
    
    resList = []
    # in case there is not panorama in the site, therefore, return
    if data['panorama']==None: 
        return 
    else:
        panoInfo = data['panorama']['data_properties']
        
        # get the meta data of the panorama
        panoId = panoInfo['@pano_id']
        resList.append(panoId)
        panoDate = panoInfo['@image_date']
        resList.append(panoDate)
        panoLat = panoInfo['@lat']
        resList.append(panoLat)
        panoLon = panoInfo['@lng']
        resList.append(panoLon)
        
        # the projection information
        projInfo = data['panorama']['projection_properties']
        yawDegree = projInfo['@pano_yaw_deg']
        resList.append(yawDegree)
        return resList
        

def GSV_single_panoramaDowloader(panoId, outputPanoImgFile):
    """
    This function is used to download the GSV panoramas from Google using
    Google API, http://cbk0.google.com/cbk?output=tile&panoid=lKxUOImSaCYAAAQIt71GFQ&zoom=5&x=0&y=0
    
    The second step of this function is to merge all the patches together to create
    a complete panorama
    
    parameters:
        panoId: the id of the panoramas
        outputPanoImgFile: the output panorama file
    
    first version Jan18, 2017, MIT Senseable City Lab. 
    """
    
    import urllib
    import urllib.request
    from io import StringIO
    from PIL import Image
        
    # download the GSV panoramas by specifying the parmaters        
    # the x is from 0-25, y is from 0-12
    xNum = 26
    yNum = 13
    
    # merge images together to create a panorama
    widths = xNum*512
    heights = yNum*512
    
    mergedImg = np.zeros((heights,widths,3),'uint8')
    
    # the panorama image of Google Street View panorama is 12800*6144, therefore, 25*12 patches
    for x in range(xNum):
        for y in range(yNum):
            
            # create a URL based on the specified parameters to download the pano
            URL = "http://cbk0.google.com/cbk?output=tile&panoid=%s&zoom=5&x=%d&y=%d"%(panoId,x,y)
            
            # Open the GSV images from the URL
            imgPatch = np.array(Image.open(urllib.request.urlopen(URL)))
            
            # sometimes the panoID will return to NULL image
            if len(imgPatch.shape) < 3:
                print ('This is a Nulll array')
                break
            
            # the x,y indices of the patch on the merged panorama
            idx_lx = 512*x
            idx_ux = 512*x + 512
            idx_ly = 512*y
            idx_uy = 512*y + 512
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,0] = imgPatch[:,:,0]
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,1] = imgPatch[:,:,1]
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,2] = imgPatch[:,:,2]
    
    img = Image.fromarray(mergedImg)
    
    img.save(outputPanoImgFile)
    del mergedImg,img
    
    
    
def SunPosOnFisheyeimage(panoImgFile,plotedFisheyeImg,currentTime,lon, lat):
    '''
    # This is used to put the trajectory of the sun on the generated fisheye image
    # the fisheye image could be created based on the GSV images, the trajectory of
    # of the sun is the position of the sun (azimuth, sun elevation)
    
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
    from pysolar.solar import get_altitude, get_azimuth
    
    # read the hemispherical image
    outputSunpathImage = np.array(Image.open(panoImgFile))
    dims = outputSunpathImage.shape
    cols = dims[0]
    rows = dims[1]
    if len(dims)>2:
        bands = dims[2]
    
    print (lat,lon,currentTime)
    # calculate the position of sun based on the coordinate and the time information
    sunele = get_altitude(lat, lon, currentTime)
    print ('----',lat,lon,currentTime)
    print ('The sun elevation is:', sunele)
    sunele = sunele*np.pi/180.0
    
##    azimuth = abs(get_azimuth(lat, lon, currentTime)) + 180
##    if azimuth > 360:
##        azimuth = azimuth - 360
##    print ('The azimuth of the sun is:', azimuth)
    
    azimuth = 180 - abs(get_azimuth(lat, lon, currentTime))
    azimuth = azimuth*np.pi/180.0 + 0.5*np.pi
    
    
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



# Judge if the site is shaded or not
def Shaded_judgement(panoImgFile,currentTime,lon, lat):
    '''
    # This function is used to judge if one iste is exposred to sunlight or not
    # by overlaying the sunposition on the skyImg
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version Dec 23, 2017
    
    Parameters: 
        panoImgFile: the input classified hemispherical image
        currentTime: the time
        lon, lat are the coordinate of the site
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth
    
    # read the hemispherical image
    skyImg = np.array(Image.open(panoImgFile))
    [cols, rows] = skyImg.shape
    
    # calculate the position of sun based on the coordinate and the time information
    sunele = get_altitude(lat, lon, currentTime)
    sunele = sunele*np.pi/180.0
    
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
    
    if len(idx[0])/(4*buff*buff) > 0.75:
        print ('This site not shaded')
        shade = 0
    else:
        print ('The site is shaded')
        shade = 1
    del skyImg
    return shade
    


    
def SunTrajectoryOnFisheyeimage(rotatedFishImg,outputSunpathFolder,timeLst):
    '''
    # This is used to put the trajectory of the sun on the generated fisheye image
    # the fisheye image could be created based on the GSV images, the trajectory of
    # of the sun is the position of the sun (azimuth, sun elevation), the 
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version Jan 18, 2017
    
    # ////////Note: This function only suitable on Python3+
    
    Parameters: 
        rotatedFishImg: the input rotated fisheye image or sky classification res
        outputSunpathFolder: the output folder of the created fisheye image with the trajectory of the sun
        timeList: the time series, timeList = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    '''
    
    from PIL import Image
    import numpy as np
    import urllib
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth
    
    # read GSV panorama images
    basename = os.path.basename(rotatedFishImg)[:-4]
    
    print ('The basename of the file is:', basename)
    fields = basename.split(' - ')
    panoID = fields[0]
    lon = float(fields[1])
    lat = float(fields[2])
    month = fields[3][-2:]
    
    print ('The lon, lat, id, month are:', lon, lat, panoID, month)
    
##    lat = 42.365900
##    lon = -71.085796
##    month = '09'
    
    
    # the output filename
    skyImgName = '%s_sky.jpg'%(basename)
    sunpathFisheyeName = '%s_sunpath.jpg'%(basename)
    outputSkyImgFile = os.path.join(outputSunpathFolder,skyImgName)
    outputSunpathImageFile = os.path.join(outputSunpathFolder,sunpathFisheyeName)
    
##    if os.path.exists(outputSunpathImageFile):
##        return
    
    ## PLOT THE POSITION OF SUN ON THE FISHEYE IMAGE
    outputSunpathImage = np.array(Image.open(rotatedFishImg))
    [rows,cols,bands] = outputSunpathImage.shape
    
    for i in range(len(timeLst)):
        print ('The time is:',timeLst[i])
        currentTime = timeLst[i]
        
        # calculate the position of sun based on the coordinate and the time information
        sunele = get_altitude(lat, lon, currentTime)
        print ('----',lat,lon,currentTime)
        print ('The sun elevation is:', sunele)
        sunele = sunele*np.pi/180.0
                
        azimuth = 180 - abs(get_azimuth(lat, lon, currentTime))
        azimuth = azimuth*np.pi/180.0 + 0.5*np.pi
        
        
        # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
        R = int(0.5*rows)
        
        # get the r in the polar coordinate
        if sunele < 0: sunele = 0

        # differnet way to put the sunpath in the fisheye image
        #r = math.cos(sunele)*R
        r = 2*R*(0.5*np.pi - sunele)/np.pi   # the distrance between different degree is equal
        
        # get the coordinate of the point on the fisheye images
        px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
        py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
        
        #print ('px is: %s and py is: %s'%(px,py))
        
        # set the points as red
        buff = 50
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
                    outputSunpathImage[y,x,0] = 255
                    outputSunpathImage[y,x,1] = 0
                    outputSunpathImage[y,x,2] = 0
        
        # create the circle based on the boundaries of the circles
        
##        outputSunpathImage[boundYl:boundYu,boundXl:boundXu,0] = 255
##        outputSunpathImage[boundYl:boundYu,boundXl:boundXu,1] = 0
##        outputSunpathImage[boundYl:boundYu,boundXl:boundXu,2] = 0
    
    imgSunpath = Image.fromarray(outputSunpathImage)
    imgSunpath.save(outputSunpathImageFile)
    del outputSunpathImage, imgSunpath
    


def SunTrajectoryOnFisheye(rotatedFishImg,outputSunpathFolder,timeLst):
    '''
    This function is used to call "SunTrajectoryOnFisheyeimag" function to project
    the sunpath on the generated fisheye images, this function can run on GSV images
    in folder or single GSV images
    
    parameters:
        rotatedFishImg: the input rotated fishye images or folders (or the sky images)
        outputSunpathFolder: the output folder for the classified images
        timeLst: the list to store the time object, different hours one day
        
    first version Feb 17, 2017, MIT, Cambridge
    
    '''
    from PIL import Image
    import numpy as np
    import urllib
    import os, os.path
    import math
    import cv2
    
    # if there is no output folder, create one
    if not os.path.exists(outputSunpathFolder):
        os.makedirs(outputSunpathFolder)
    
    # if the input is folder then list GSV images
    if os.path.isdir(rotatedFishImg):
        fileLst = os.listdir(rotatedFishImg)
        for file in fileLst:
            panoImgFile = os.path.join(rotatedFishImg,file)
            SunTrajectoryOnFisheyeimage(panoImgFile,outputSunpathFolder,timeLst)
    else:
        # if the input is a fisheye image
        SunTrajectoryOnFisheyeimage(rotatedFishImg,outputSunpathFolder,timeLst)
    


def SunlightDurationEstimation(skyImgFolder,outputSunpathFolder,timeLst,shpfile):
    '''
    # This is function is used to calculate the sunlight duration based on 
    # the sun trajectories and the classified sky images, save the result as shpfile
    #  --------------The duration of sunlight---------------------
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 21st, 2017
    
    Parameters: 
        skyImg: the input sky image
        timeList: the time series, timeList = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        shpfile: the output shapefile to store the distribution of sunlight duration
    '''
    
    from PIL import Image
    import numpy as np
    import urllib
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth
    import gdal,ogr,osr
    
    
    # create a shpafile to save the sun duration 
    driver = ogr.GetDriverByName("ESRI Shapefile")
    
    if os.path.exists(shpfile):
        driver.DeleteDataSource(shpfile)
    data_source = driver.CreateDataSource(shpfile)
    
    targetSpatialRef = osr.SpatialReference()
    targetSpatialRef.ImportFromEPSG(4326)
    
    outLayer = data_source.CreateLayer("SunDur",targetSpatialRef, ogr.wkbPoint)
    sunDur = ogr.FieldDefn('sundur', ogr.OFTReal)
    panoId = ogr.FieldDefn('panoid', ogr.OFTString)
    outLayer.CreateField(sunDur)
    outLayer.CreateField(panoId)
    
    # loop all the sky image in the folder
    for skyimg in os.listdir(skyImgFolder):
        skyImgFile = os.path.join(skyImgFolder,skyimg)
        
        # read GSV panorama images
        basename = os.path.basename(skyImgFile)[:-4]
        
        print ('The basename of the file is:', basename)
        fields = basename.split(' - ')
        panoID = fields[0]
        lon = float(fields[1])
        lat = float(fields[2])
        month = fields[3][-2:]
        
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)
                
        # the output filename
        skyImgName = '%s_sky.jpg'%(basename)
        sunpathFisheyeName = '%s_sunpath.tif'%(basename)
        outputSkyImgFile = os.path.join(outputSunpathFolder,skyImgName)
        outputSunpathImageFile = os.path.join(outputSunpathFolder,sunpathFisheyeName)
        
        
        ## ESTIMATE THE DURATION OF DIRECT SUNLIGHT
        skyImg = np.array(Image.open(skyImgFile))
        [rows,cols] = skyImg.shape
        
        # the duration hours of sunlight
        hours = 0
        
        for i in range(len(timeLst)):
            #print ('The time is:',timeLst[i])
            currentTime = timeLst[i]       
            
            # flag whether one site is under the shade 0 or not 1
            flag = 1
            
            # calculate the position of sun based on the coordinate and the time information
            sunele = get_altitude(lat, lon, currentTime)
            #print ('----',lat,lon,currentTime)
            #print ('The sun elevation is:', sunele)
            sunele = sunele*np.pi/180.0
            
            azimuth = abs(get_azimuth(lat, lon, currentTime)) + 180
            if azimuth > 360:
                azimuth = azimuth - 360
            #print ('The azimuth of the sun is:', azimuth)
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
            
            if flag == 1:
                hours = hours + 0.1
        
##        imgSunpath = Image.fromarray(skyImg)
##        imgSunpath.save(outputSunpathImageFile)
##        del imgSunpath
        
        print ('The duration of the hours is:'),hours
        del skyImg
        
        
        # create feature and set the attribute values
        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        
        # set the geometrical feature
        outFeature.SetGeometry(point)        
        outFeature.SetField('sundur',hours)
        outFeature.SetField('panoid',panoID)
        
        # push the feature to the layer
        outLayer.CreateFeature(outFeature)
        outFeature.Destroy()
        
    data_source.Destroy()



def SunDiagramOnFisheyeImg(rotatedFishImg,outputSunpathFolder,monthRange):
    '''
    ???????????????????????????
        Not finished
    ???????????????????????????
    
    This function is used to get the sun diagram on Fisheye image
    
    First version Mar 8, 2017
    Author: Xiaojiang Li, MIT Senseable City Lab
    '''
    from PIL import Image
    import numpy as np
    import urllib
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth
    
    
    # read GSV panorama images
    basename = os.path.basename(rotatedFishImg)[:-4]
    
##    print ('The basename of the file is:', basename)
    fields = basename.split(' - ')
    panoID = fields[0]
    lon = float(fields[1])
    lat = float(fields[2])
    month = fields[3][-2:]
    
##    print ('The lon, lat, id, month are:', lon, lat, panoID, month)
    
    # the output filename
    skyImgName = '%s_sky.jpg'%(basename)
    sunpathFisheyeName = '%s_sunpath.jpg'%(basename)
    outputSkyImgFile = os.path.join(outputSunpathFolder,skyImgName)
    outputSunpathImageFile = os.path.join(outputSunpathFolder,sunpathFisheyeName)
    
##    if os.path.exists(outputSunpathImageFile):
##        return
    
    outputSunpathImage = Image.open(rotatedFishImg)
    
    # resize the original image file to speed the calculation
    basewidth = 600       
    wpercent = (basewidth / float(outputSunpathImage.size[0]))
    hsize = int((float(outputSunpathImage.size[1]) * float(wpercent)))
    img = outputSunpathImage.resize((basewidth, hsize), Image.ANTIALIAS)
    outputSunpathImage = np.array(img)
    
    [rows,cols,bands] = outputSunpathImage.shape
    
    
    for m in range(3,4):
        # calculate the boundary of each sun sector
        # the days in different months
        days = 30
        if m == 2: days = 28
        if m in [1,3,5,7,8,10,12]: days = 31
        
        
        # for different hours in one day
        for h in range(5,20):
            
            # the time of boundary sectors
            timeRU = datetime(2014, m, days, h, 0, 0, 0) # Right and up
            timeRB = datetime(2014, m, 1, h, 0, 0, 0) # Right and down
            timeLU = timeRU + timedelta(hours=0.5) # Left and Up
            timeLB = timeRB + timedelta(hours=0.5) # left and buttom
            print (timeRB,timeLB)
            
            
            # calculate the position of sun based on the coordinate and the time information
            suneleRU = get_altitude(lat, lon, timeRU)
            suneleRU = suneleRU*np.pi/180.0
            if suneleRU < 0: suneleRU = 0
            
            suneleLU = get_altitude(lat, lon, timeLU)
            suneleLU = suneleLU*np.pi/180.0
            if suneleLU < 0: suneleLU = 0
            
            suneleRB = get_altitude(lat, lon, timeRB)
            suneleRB = suneleRB*np.pi/180.0
            if suneleRB < 0: suneleRB = 0
            
            suneleLB = get_altitude(lat, lon, timeLB)
            suneleLB = suneleLB*np.pi/180.0
            if suneleLB < 0: suneleLB = 0
            print ('The buttom sun elevation are:-------------', suneleRB,suneleLB)
            print ('The top sun elevation are:-------------', suneleRU,suneleLU)
            
            # Calculate the azimuth angles of the four corner point of the sector
            azimuthRU = abs(get_azimuth(lat, lon, timeRU)) + 180
            if azimuthRU > 360:
                azimuthRU = azimuthRU - 360
            azimuthRU = azimuthRU*np.pi/180.0 + 0.5*np.pi
            
            azimuthRB = abs(get_azimuth(lat, lon, timeRB)) + 180
            if azimuthRB > 360:
                azimuthRB = azimuthRB - 360
            azimuthRB = azimuthRB*np.pi/180.0 + 0.5*np.pi
            
            azimuthLU = abs(get_azimuth(lat, lon, timeLU)) + 180
            if azimuthLU > 360:
                azimuthLU = azimuthLU - 360
            azimuthLU = azimuthLU*np.pi/180.0 + 0.5*np.pi
            
            azimuthLB = abs(get_azimuth(lat, lon, timeLB)) + 180
            if azimuthLB > 360:
                azimuthLB = azimuthLB - 360
            azimuthLB = azimuthLB*np.pi/180.0 + 0.5*np.pi
            
            
            # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
            R = int(0.5*rows)
            
##            # differnet way to put the sunpath in the fisheye image
##            #r = math.cos(sunele)*R
##            rRU = 2*R*(0.5*np.pi - suneleRU)/np.pi   # the distrance between different degree is equal
##            rRB = 2*R*(0.5*np.pi - suneleRB)/np.pi   # the distrance between different degree is equal
##            rLU = 2*R*(0.5*np.pi - suneleLU)/np.pi   # the distrance between different degree is equal
##            rLB = 2*R*(0.5*np.pi - suneleLB)/np.pi   # the distrance between different degree is equal
##            
##            
##            # get the coordinate of the point on the fisheye images
##            pxLU = int(rLU*math.cos(azimuthLU) + int(0.5*cols)) - 1
##            pyLU = int(int(0.5*rows) - rLU*math.sin(azimuthLU)) - 1
##            
##            outputSunpathImage[pyLU:pyLU+5,pxLU-5:pxLU,0] = 255
##            outputSunpathImage[pyLU:pyLU+5,pxLU-5:pxLU,1] = 0
##            outputSunpathImage[pyLU:pyLU+5,pxLU-5:pxLU,2] = 0
##            
##            pxLB = int(rLB*math.cos(azimuthLB) + int(0.5*cols)) - 1
##            pyLB = int(int(0.5*rows) - rLB*math.sin(azimuthLB)) - 1
##            
##            outputSunpathImage[pyLB:pyLB+5,pxLB-5:pxLB,0] = 0
##            outputSunpathImage[pyLB:pyLB+5,pxLB-5:pxLB,1] = 0
##            outputSunpathImage[pyLB:pyLB+5,pxLB-5:pxLB,2] = 0
##            
##            
##            pxRU = int(rRU*math.cos(azimuthRU) + int(0.5*cols)) - 1
##            pyRU = int(int(0.5*rows) - rRU*math.sin(azimuthRU)) - 1
##            
##            outputSunpathImage[pyRU:pyRU+5,pxRU-5:pxRU,0] = 255
##            outputSunpathImage[pyRU:pyRU+5,pxRU-5:pxRU,1] = 0
##            outputSunpathImage[pyRU:pyRU+5,pxRU-5:pxRU,2] = 255
##            
##            
##            pxRB = int(rRB*math.cos(azimuthRB) + int(0.5*cols)) - 1
##            pyRB = int(int(0.5*rows) - rRB*math.sin(azimuthRB)) - 1
##            
##            outputSunpathImage[pyRB:pyRB+5,pxRB-5:pxRB,0] = 255
##            outputSunpathImage[pyRB:pyRB+5,pxRB-5:pxRB,1] = 255
##            outputSunpathImage[pyRB:pyRB+5,pxRB-5:pxRB,2] = 0
##            
##            
##            # get the bound row and col num
##            px = [pxLU,pxRB,pxRU,pxLB]
##            py = [pyLU,pyRB,pyRU,pyLB]
##            
##            
##            pyU = max(py)
##            pyB = min(py)
##            pxU = max(px)
##            pxB = min(px)
##
##            print ('-----------------',pyRB,pyRU,pxLU,pxLB)
##            
##            outputSunpathImage[pyRB:pyRU,pxLU:pxRB,0] = 0
##            outputSunpathImage[pyRB:pyRU,pxLU:pxRB,1] = 0
##            outputSunpathImage[pyRB:pyRU,pxLU:pxRB,2] = 255
            
##            outputSunpathImage[pyB:pyU,pxB:pxU,0] = 0
##            outputSunpathImage[pyB:pyU,pxB:pxU,1] = 0
##            outputSunpathImage[pyB:pyU,pxB:pxU,2] = 255

##            for y in range(pyB,pyU):
##                for x in range(pxB,pxU):
##                    # calculate the azimuth and the sun elevation
##                    azimuth = 


##           pxLB = int(rLB*math.cos(azimuthLB) + int(0.5*cols)) - 1
##           pyLB = int(int(0.5*rows) - rLB*math.sin(azimuthLB)) - 1
            
            
            
            # set the start time for the calculation
            iniTime = datetime(2014, m, 1, 5, 0, 0, 0)
            
            # for different hours in one day
            for h in range(30):
                iniTime = iniTime + timedelta(hours=0.5)
                
                currentTime = iniTime      
                
                # calculate the position of sun based on the coordinate and the time information
                sunele = get_altitude(lat, lon, currentTime)
                sunele = sunele*np.pi/180.0
                print ('lat,lon, currentTime, and sun elevation',lat,lon,currentTime,sunele)
                
                azimuth = abs(get_azimuth(lat, lon, currentTime)) + 180
                if azimuth > 360:
                    azimuth = azimuth - 360
                print ('The azimuth of the sun is:', azimuth)
                azimuth = azimuth*np.pi/180.0 + 0.5*np.pi
                
                
                # BASED ON THE AZIMUTH AND SUN ELEVATION TO LOCATE THE CORRESPODING PIXELS ON THE FISHEYE IMAGE
                R = int(0.5*rows)
                
                # get the r in the polar coordinate
                if sunele < 0: sunele = 0
                
                # differnet way to put the sunpath in the fisheye image
                #r = math.cos(sunele)*R
                r = 2*R*(0.5*np.pi - sunele)/np.pi   # the distrance between different degree is equal
                
                # get the coordinate of the point on the fisheye images
                px = int(r*math.cos(azimuth) + int(0.5*cols)) - 1
                py = int(int(0.5*rows) - r*math.sin(azimuth)) - 1
                
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
                
                # create a circle like sun postion
                for x in range(boundXl,boundXu):            
                    for y in range(boundYl, boundYu):
                        # calculate the distance between the pixel with the center
                        dist = math.sqrt((x - px)**2 + (y - py)**2)
                        if dist < buff:
                            outputSunpathImage[y,x,0] = 255
                            outputSunpathImage[y,x,1] = 0
                            outputSunpathImage[y,x,2] = 0
                            
    imgSunpath = Image.fromarray(outputSunpathImage)
    imgSunpath.save(outputSunpathImageFile)
    del outputSunpathImage, imgSunpath
    
    

def DirectDiffuseRadiationEst(skyImgFolder,skymapfile,timeLst,shpfile):
    '''
    # This is function is used to calculate the direct and diffuse solar
    radiation based on the classified hemisperhical photos and save the
    result direct and diffused solar radiation as a shpfile
    #  ---------The direct and the diffuse solar radiation-------------
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 22ed, 2017
    
    Parameters: 
        skyImgFolder: the input sky image folder
        timeList: the time series, timeList = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        shpfile: the output shapefile to store the distribution of sunlight duration
    '''
    
    from PIL import Image
    import numpy as np
    import urllib
    import os, os.path
    import math
    from pysolar.solar import get_altitude, get_azimuth
    import gdal,ogr,osr
    
    
    # create a shpafile to save the sun duration 
    driver = ogr.GetDriverByName("ESRI Shapefile")
    
    if os.path.exists(shpfile):
        driver.DeleteDataSource(shpfile)
    data_source = driver.CreateDataSource(shpfile)
    
    targetSpatialRef = osr.SpatialReference()
    targetSpatialRef.ImportFromEPSG(4326)
    
    outLayer = data_source.CreateLayer("Radiation",targetSpatialRef, ogr.wkbPoint)
    direct = ogr.FieldDefn('direct', ogr.OFTReal)
    diffuse = ogr.FieldDefn('diffuse', ogr.OFTReal)
    panoId = ogr.FieldDefn('panoid', ogr.OFTString)
    outLayer.CreateField(direct)
    outLayer.CreateField(diffuse)
    outLayer.CreateField(panoId)
    
    # loop all the sky image in the folder
    for skyimg in os.listdir(skyImgFolder):
        skyImgFile = os.path.join(skyImgFolder,skyimg)

        basename = os.path.basename(skyImgFile)[:-4]
        fields = basename.split(' - ')
        panoID = fields[0]
        lon = float(fields[1])
        lat = float(fields[2])
        
        # calculate the direct radiation
        directRadiation = DirectRadiationEst(skyImgFile,timeLst)
        
        # calculate the diffuse radiation
        diffuseRadiation = DiffuseRadiationEst(skyImgFile,skymapfile)
        
        print ('The direct and diffuser radiation are:',panoID,directRadiation,diffuseRadiation)
        
        # add point feature
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)
        
        # create feature and set the attribute values
        featureDefn = outLayer.GetLayerDefn()
        outFeature = ogr.Feature(featureDefn)
        
        # set the geometrical feature
        outFeature.SetGeometry(point)        
        outFeature.SetField('direct',directRadiation)
        outFeature.SetField('diffuse',diffuseRadiation)
        outFeature.SetField('panoid',panoID)
        
        # push the feature to the layer
        outLayer.CreateFeature(outFeature)
        outFeature.Destroy()
        
    data_source.Destroy()
    
    


def DirectRadiationEst(skyImgFile,timeLst):
    '''
    # This is function is used to calculate the direct and diffuse solar
    radiation based on the classified hemisperhical photos and save the
    result direct and diffused solar radiation as a shpfile
    #  ---------The direct and the diffuse solar radiation-------------
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version March 22ed, 2017
    
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
    month = fields[3][-2:]
    
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
        
        # estimate the direct radiation for this time is
        directRad = flag*math.cos(sunele)
        direct_T_Rad = math.cos(sunele)
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
    


def CreateSkyMap(skyImgFile,skymapfile):
    '''
    The fuction is used to create sky map based on the input sky images
    First version March 24, 2017
    Author: Xiaojiang Li, MIT Senseable City Lab
    '''
    
    import os,os.path
    from PIL import Image
    import math
    import numpy as np
    
    skyImg = np.array(Image.open(skyImgFile))
    [rows,cols] = skyImg.shape
    R = 0.5*cols # the radius of the sky image
    print ('The rows and cols are:',rows,cols)
    
    # initialize the diffuse radiation
    difRadiation = 0
    
    # azimuth division and zenith division
    azDiv = 16
    zenDiv = 8
    
    # initialize the sector image
    skymap = np.zeros([rows,cols])
    
    sector = 0
    for zen in range(zenDiv):
        for az in range(azDiv):
            sector = sector + 1
            
            # the zenith and azimuth angle boundaries for each sector
            zenAngle1 = 1.0*zen/zenDiv * (0.5*np.pi)
            zenAngle2 = (1.0*zen + 1)/zenDiv * (0.5*np.pi)
            zenR1 = 1.0*zen/zenDiv * 0.5*cols
            zenR2 = (1.0*zen + 1)/zenDiv * 0.5*cols
            
            azAngle1 = 1.0*az/azDiv * (2*np.pi)
            azAngle2 = (1.0*az + 1)/azDiv * (2*np.pi)
            
            print ('The az and zen are:',azAngle1,zenAngle1)
            
            # check the two models in http://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/how-solar-radiation-is-calculated.htm
            weight = (math.cos(azAngle1)- math.cos(azAngle1)) / azDiv
            
            # get the boundary of each sector
            rlow = 2*zenAngle1/np.pi * R
            rhigh = 2*zenAngle2/np.pi * R
            x1 = rlow * math.cos(azAngle1) + 0.5*cols
            x3 = rhigh * math.cos(azAngle1) + 0.5*cols
            
            x2 = rlow * math.cos(azAngle2) + 0.5*cols
            x4 = rhigh * math.cos(azAngle2) + 0.5*cols
            
            y1 = 0.5*rows - rlow * math.sin(azAngle1) 
            y3 = 0.5*rows - rhigh * math.sin(azAngle1)
            
            y2 = 0.5*rows - rlow * math.sin(azAngle2)
            y4 = 0.5*rows - rhigh * math.sin(azAngle2)
            
            
            xlow = int(min(x1,x2,x3,x4))
            xhigh = int(max(x1,x2,x3,x4))
            ylow = int(min(y1,y2,y3,y4))
            yhigh = int(max(y1,y2,y3,y4))
            
##            print ('The xlow,xhigh,ylow,yhight are:',xlow,xhigh,ylow,yhigh)
            # seach the small box confined by the xlow,yhigh for caculating the gap fraction
##            for x in range(xlow,xhigh):
##                for y in range(ylow,yhigh):
            for x in range(cols):
                for y in range(rows):
                    # calculate the angle and check if the angle is in the range of the sector
                    ycoor = 0.5*rows - y
                    xcoor = x - 0.5*cols
                    rcoor = math.sqrt(xcoor**2 + ycoor**2)
                    
                    # for different quandrants
                    if y <= 0.5*rows:
                        theta = math.acos(xcoor/(rcoor + 0.000001))
                    else:
                        theta = np.pi + math.acos(xcoor/(rcoor + 0.000001))
                    
                    if rcoor <= zenR2 and rcoor >= zenR1 and theta <= azAngle2 and theta >= azAngle1:
                        skymap[y,x] = sector
                    
                    
    # save the result sky map
    skymapImg = Image.fromarray(skymap)
    skymapImg.save(skymapfile)
    del skymapImg,skymap
    
    


def FisheyeSidewalk_efficient(fisheyeImg, orientation, outfisheyeImg):
    '''
    This function is used to generate hemispherical images on the sidewalk based
    on the association between the central street and the sidework.
    
    Based on the model, the hemispherical images can be generated on sidework based
    on Google Street View hemispherical images
    
    
    First version Feb 4, 2018, based on Jan 29, 2018, function of FisheyeSidewalk_efficient
    
    parameters:
        fc: the input feature class
        rast: the corresponding raster file
        fisheyeSize: the size of the generated hemishperical image
        outputFolder: the output folder of the generated fisheye images
    '''
    
    import osr,ogr
    import os,os.path
    import numpy as np
    import cv2
    from PIL import Image, ImageDraw
    
    #open vector layer
    drv=ogr.GetDriverByName('ESRI Shapefile') #assuming shapefile
    ds=drv.Open(fc,0) # read only
    lyr=ds.GetLayer(0)
    sourceProj = lyr.GetSpatialRef()
    print (sourceProj)
    
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    
    #open raster layer
    src_ds=gdal.Open(rast) 
    gt=src_ds.GetGeoTransform()
    rb=src_ds.GetRasterBand(1)
    print ('the gt is:',gt)
    print ('the rb is:',rb)
    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize
    print ('The rows is:%s, the cols is:%s'%(rows,cols))
    
    x_offset = 510
    y_offset = 510
    
    
    # iterate all features in the shapefile
    for feat in lyr:
        geom=feat.GetGeometryRef()
        mx=geom.Centroid().GetX()
        my=geom.Centroid().GetY()
        
        # panoID of the site
        panoID = feat.GetField("panoID")
        
        # convert the projection into WGS, used to recored the coordinate of the fisheye image
        coordTrans = osr.CoordinateTransformation(sourceProj, targetProj)
        geom.Transform(coordTrans)
        lon = geom.GetX()
        lat = geom.GetY()
        
        # the output generated fisheye image name
        FileName = '%s - %s - %s.tif'%(panoID,lon,lat)
        outputFileName = os.path.join(outputFolder,FileName)
        if os.path.exists(outputFileName):
            continue
        
        # create an empty array to save the generated hemispherical image
        fisheyeImg = np.zeros(shape=(fisheyeSize,fisheyeSize),dtype = np.int8)
        
        if panoID != 'dZ5wxUSM0WZvyZUcYiLwgQ': 
            continue
        
        print ('The coordinate of the site is---------:', mx, my)
        

        # panoid = 'dZ5wxUSM0WZvyZUcYiLwgQ'
        mx = 236101
        my = 900019
        
####        # right, panoid = 'R1sW0zaU-SM5Nxv90qakQg'
##        mx = 236412
##        my = 900127

##        # panoid = 'AlWYC64Tu9hNYB3bS_ZwNg'
##        mx = 235619
##        my = 899956

##        # right
##        mx = 235620
##        my = 899953

        #panoid = 'eZMtpC_VaYZbabiLQIsagg'
        mx = 233504
        my = 890948

        # panoid = 'H5VSlPKIklCN7-WZA69A6A'
        mx = 236552
        my = 900596
        
        # here the +1 and -2 are adjusted manully based on checking on ENVI
        px = int((mx - gt[0]) / gt[1])+1 
        py = int((my - gt[3]) / gt[5])-2
        
        print (px,py)
        
        # based on the px, py location to locate the corresponding blocks 1000*1000
        x_block_low = px - x_offset
        x_block_high = px + x_offset
        
        # the col boundary
        if x_block_low < 0:
            x_block_low = 0
            x_block_high = 2*x_offset
        if x_block_high > cols - 1:
            x_block_low = cols - 1 - 2*x_offset
            x_block_high = cols - 1
        
        y_block_low = py - y_offset
        y_block_high = py + y_offset
        
        # the row boundary
        if y_block_low < 0:
            y_block_low = 0
            y_block_high = 2*y_offset
        if y_block_high > rows - 1:
            y_block_high = rows - 1
            y_block_low = rows - 1 - 2*y_offset
        
        print ('The boundary of the block group is:',x_block_low,x_block_high,y_block_low,y_block_high)
        print ('The panoID is:',panoID)
        
        # read the DSM of the block
        x_size = x_block_high - x_block_low
        y_size = y_block_high - y_block_low
        arrayDEM = rb.ReadAsArray(x_block_low, y_block_low, x_size, y_size)
        if arrayDEM is None:
            print ('This is a noneTyep array===================')
            continue
        
        ## CALCULATE SKY VIEW FACTOR FOR ALL GSV SITES
        SVF_res = 0
        
        #list to save the vertix of mask sky area
        polysLst = []
        polysLst2 = []
        
        # search all 360 angles for each pano site
        for thetaN in range(0,360,1):
            rangeDist = 500 # 500m
            #rangeFeet = int(rangeDist*3.28084)  # convert the meter to feet
            rangeFeet = int(rangeDist*1)  # convert the meter to meter
            
            # create points along each angle
            radiusRange = range(5,rangeFeet,1)
            theta = np.pi*thetaN/180
            
            # create an empty beta list to store the betas for each spike
            betaLst = []
            
            # create points along the ray line in 200m or 656 feet, one pixel is one foot
            for radius in radiusRange:
                rayX = int(px + radius*math.cos(theta))
                rayY = int(py - radius*math.sin(theta))
                
                # the corresponding building height is, consider the search region could out of the image
                if rayX >= cols or rayX < 0 or rayY >= rows or rayY < 0:
                    continue
                
                XinBlc = rayX - x_block_low
                YinBlc = rayY - y_block_low
                
                if XinBlc < 0: XinBlc = 0
                if XinBlc >= 2*x_offset: XinBlc = 2*x_offset - 1
                if YinBlc < 0: YinBlc = 0
                if YinBlc >= 2* y_offset: YinBlc = 2*y_offset - 1
                
                buildH = arrayDEM[YinBlc,XinBlc]
                
                # if the pixel has its height lower than 2.5m, do not consider anymore
                if buildH < 2.5:
                    continue
                
                # considering the GSV pano is captured at height of 2.5m
                beta = math.atan((buildH - 2.5)/(radius))
                # beta = math.atan((buildH - 1.05)/(radius))
                betaLst.append(beta)
                
            if len(betaLst)>0:
                maxBeta = max(betaLst)
            else: 
                maxBeta = 0
            



            
            
            # on the right, of 5 meter, the parameter is suitable to represent the case of GSV 
            
            # convert the theta to a new theta' based on the shift of the distance to the center street line
            orientation = 0.1*np.pi  #dZ5wxUSM0WZvyZUcYiLwgQ
##            orientation = - math.atan(-0.3333)
##            orientation = - math.atan(-3)
            orientation = -np.pi # panoid = dZ5wxUSM0WZvyZUcYiLwgQ
            orientation = -math.atan(1/9.0)
            
            theta2 = theta + orientation
            if theta2 > 2*np.pi:
                theta2 = theta2 - 2*np.pi
            elif theta2 < 0:
                theta2 = theta2 + 2*np.pi
            
            
            # convert the beta after the distance shift
            if theta2 < 0.5*np.pi or 1.5*np.pi < theta2:
                # the coefficient is ((D-d)/d)**2
                coef = 1/math.sqrt((math.sin(theta2)**2 + 0.15*math.cos(theta2)**2))
                tan_maxBeta2 = math.tan(maxBeta)*coef
                print ('The theta2 and theta3 are:', theta2, coef)
                maxBeta = math.atan(tan_maxBeta2)
                
            if theta2 > 0.5*np.pi and theta2 < 1.5*np.pi:
                coef = 1/math.sqrt((math.sin(theta2)**2 + 2.5*math.cos(theta2)**2))
                tan_maxBeta2 = math.tan(maxBeta)*coef
                maxBeta = math.atan(tan_maxBeta2)
                print ('The theta2 and theta3 ------- are:', theta2, coef)           
                
            
            # the theta will change after the shift
            if theta2 <= 0.5*np.pi:
                theta3 = math.atan(3*math.tan(theta2)) - orientation
                if theta3 > 2*np.pi: theta3 = theta3 - 2*np.pi
                if theta3 < 0: theta3 = theta3 + 2*np.pi
                
            elif theta2 <= 1.5*np.pi and theta2 > 0.5*np.pi:
                theta3 = math.atan(0.7*math.tan(theta2)) + np.pi - orientation
                if theta3 > 2*np.pi: theta3 = theta3 - 2*np.pi
                if theta3 < 0: theta3 = theta3 + 2*np.pi
            
            elif 1.5*np.pi <= theta2 and theta2 <= 2*np.pi:
                theta3 = math.atan(3*math.tan(theta2)) - orientation
                if theta3 > 2*np.pi: theta3 = theta3 - 2*np.pi
            
            
            # the distance to the center of the fisheye image
            fr = (0.5*fisheyeSize)/(0.5*np.pi)*(0.5*np.pi - maxBeta)
            
            # the coordinate the the sky line in the fisheye image                
            fx = int(0.5*fisheyeSize + fr*math.cos(theta3))
            fy = int(0.5*fisheyeSize - fr*math.sin(theta3))
            
            # append the vertice to the list
            polysLst.append((fx,fy))
            polysLst2 = [polysLst]
            
        
        polys2 = np.asarray(polysLst2)
        cv2.fillPoly(fisheyeImg, polys2, 1)
        outImg = Image.fromarray(fisheyeImg.astype('uint8')*255)
        outImg.save(outputFileName)
        
        del fisheyeImg,outImg,polys2
        
    print ('The geoinformation of the gt:',gt)
    
    src_ds=None
    ds=None



# main function
if __name__ == "__main__":

    ## -------------------------MAIN FUNCTION-----------------------------------
    import os,os.path
    import numpy as np
    from PIL import Image
    from datetime import datetime, timedelta

    ##fishImg = np.array(Image.open(fisheyeImgFile))
    timeLst = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    azimuthLst = [115.84, 126.21, 137.82, 151, 165.72, 181.38, 196.95, 211.43, 224.34, 235.72, 245.94, 255.48]
    suneleLst = [-2.19, 7.29, 15.47, 21.92, 26.01, 27.27, 25.51, 20.97, 14.19, 5.78, -3.95, -14.45]

    ##panoId = 'k9rRYLdJh0xBLA86MOjFbw'
    ##pano_yaw_deg = 317.78
    lat = 42.268570
    lng = -71.028542


    # --------------Download single GSV panorama--------------------------
    ##imgName = 'panoid - %s - lon -%s - lat - %s - panoyaw - %s.jpg'%(panoId,lng,lat,pano_yaw_deg)
    ##outputPanoImgFile = os.path.join(r'D:\PhD Project\RouteFindingProj\PanoImges',imgName)
    ##GSV_single_panoramaDowloader(panoId, outputPanoImgFile)


    # ---------------Convert cylindrical pano to fisheye-------------
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/ChinaStreetView'
    inPanoImg = os.path.join(root, 'Baidupano.jpeg')
    outHemiImg = os.path.join(root, 'hemi.jpg')
    print ('The inPanoImg is:', inPanoImg)
    print ('The output file is:', outHemiImg)
    # cylinder2fisheyeImage_noyaw (inPanoImg, root)


    #---------------- For Shibuya, Tokyo proj
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Routing2Shade/Figures and Table/seg-panos/output_segs'
    inPanoImg = os.path.join(root, '5672 - ekOhsCAsB-EyR2JHBFL4GA - 139.696491162 - 35.6571870555 - 2013-06 - 136.97720336.jpg')
    outroot = os.path.join(root, 'hemi-seg')
    cylinder2fisheyeImage_noyaw (inPanoImg, outroot)


    # ----------------generate the perspective projection image ------------
    inPanoImg = os.path.join(root, '46 - -71.092837 - 42.362911 - yCtk8WniqptsUHKKncjgYQ.png')
    outputPerspectiveImg = os.path.join(root, 'perspecitve.jpg')
    heading = 240
    fov=60
    yaw = 0
    tilt_yaw = 0
    pitch = 0
    # cylinder2perspective (inPanoImg,outputPerspectiveImg,heading,fov, yaw, tilt_yaw, pitch)


    # --------------CONVERT CLYINDERICAL IMAGES TO FISHEYE IMAGES --------
    ##inPanoImg = r'D:\PhD Project\RouteFindingProj\PanoImges\panoImg.jpg'
    ##outputFolder = r'D:\PhD Project\RouteFindingProj\FisheyeImgs'
    ##cylinder2fisheyeImage (outputPanoImgFile,panoRoot, pano_yaw_deg)

    # ---------------CONVERT CYLINDERICAL IMAGES INTO PERSPECTIVE IMAGE WITH DIFFERENT PARAMETERS
    ##fov = 60
    ##pitch = 0
    ##heading = 0
    
    ### the yaw is the direction of driving, it is included in the metadata
    ##yaw = 113.68
    ##tilt_yaw = 0
    
    ##inputCylinderImg = r'/Users/xiaojiang/Documents/xiaojiang/gsvproj/panoramas/uBuAad7LXOmsjma-oORM3w - -71.066685 - 42.340159 - 2014-06.jpg'
    ##outputPerspectiveFolder = r'/Users/xiaojiang/Documents/xiaojiang/gsvproj/panoramas'
    ##filename = 'perspective-fov%s-pitch%s-heading-%s.jpg'%(fov,pitch,heading)
    ##outputPerspectiveImg = os.path.join(outputPerspectiveFolder,filename)
    cylinder2perspective(inputCylinderImg,outputPerspectiveImg,heading,fov,pitch)
    