
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
    