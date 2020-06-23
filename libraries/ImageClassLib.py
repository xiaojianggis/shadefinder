# This program is used to classify the sky area from the fisheye images
# Frist version Aug 31, 2016
# Copyright(c) Xiaojiang Li, University of Conneticut

# last modified on Dec 28, 2017 by Xiaojiang Li, MIT Senseable City Lab


def graythresh(array,level):
    '''array: is the numpy array waiting for processing
    return thresh: is the result got by OTSU algorithm
    if the threshold is less than level, then set the level as the threshold
    '''
    
    import numpy as np
    
    maxVal = np.max(array)
    minVal = np.min(array)
    
#   if the inputImage is a float of double dataset then we transform the data 
#   in to byte and range from [0 255]
    if maxVal <= 1:
        array = array*255
        # print "New max value is %s" %(np.max(array))
    elif maxVal >= 256:
        array = np.int((array - minVal)/(maxVal - minVal))
        # print "New min value is %s" %(np.min(array))
    
    # turn the negative to natural number
    negIdx = np.where(array < 0)
    array[negIdx] = 0
    
    # calculate the hist of 'array'
    dims = np.shape(array)
    hist = np.histogram(array,range(257))
    P_hist = hist[0]*1.0/np.sum(hist[0])
    
    omega = P_hist.cumsum()
    
    temp = np.arange(256)
    mu = P_hist*(temp+1)
    mu = mu.cumsum()
    
    n = len(mu)
    mu_t = mu[n-1]
    
    sigma_b_squared = (mu_t*omega - mu)**2/(omega*(1-omega))
    
    # try to found if all sigma_b squrered are NaN or Infinity
    indInf = np.where(sigma_b_squared == np.inf)
    
    CIN = 0
    if len(indInf[0])>0:
        CIN = len(indInf[0])
    
    maxval = np.max(sigma_b_squared)
    
    IsAllInf = CIN == 256
    if IsAllInf !=1:
        index = np.where(sigma_b_squared==maxval)
        idx = np.mean(index)
        threshold = (idx - 1)/255.0
    else:
        threshold = level
    
    if np.isnan(threshold):
        threshold = level
        
    return threshold
    

def OBIA_Skyclassification_vote(inputImg,outputFolder):
    '''
    This function is used to extract the sky pixels from the input image
    Different with the OBIA_Skyclassification function, this function
    first classify the sky pixel based on the pixel level spectral signature
    then count the majority of the sky pixels in each segmented object
    
    parameters:
        inputImg: the file path of input image
        outputFolder: the output foldername
    '''
    import os,os.path
    from PIL import Image, ImageEnhance
    import pymeanshift as pms

    
    basename = os.path.basename(inputImg)[:-4]
    
    classImgFile = os.path.join(outputFolder,'%s_skyRes.tif'%(basename))
    resizedImgFile = os.path.join(outputFolder,'%s_Resized.jpg'%(basename))
    segImgFile = os.path.join(outputFolder,'%s_seged.jpg'%(basename))
    
    # resize the original image file to speed the calculation
    basewidth = 600
    img = Image.open(inputImg)
        
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    
    panoImage = np.array(img)
    pixlImg = panoImage/255.0
    redP = pixlImg[:,:,0]
    greenP = pixlImg[:,:,1]
    blueP = pixlImg[:,:,2]
    
    ExG = 2*greenP - redP - blueP
    del pixlImg,greenP,redP,blueP
    
    # call the function from pymeanshift to segment the GSV images
    (segmented_image, labels_image, number_regions) = pms.segment(panoImage,spatial_radius=6, 
                                                          range_radius=4, min_density=40)        
    
    # get the canny edge of original pano image
    cannyEdge = cv2.Canny(panoImage,100,200)   
    
    segmented_imageOut = Image.fromarray(segmented_image)
    segmented_imageOut.save(segImgFile)
    del segmented_imageOut
    
    
##    subplot(3,3,1)
##    imshow(panoImage)
##    subplot(3,3,2)
##    imshow(labels_image)
    
    I = segmented_image/255.0
    red = I[:,:,0]
    green = I[:,:,1]
    blue = I[:,:,2]
    
    # calculate the difference between green band with other two bands
    green_red_Diff = green - red
    green_blue_Diff = green - blue
    sumImg = (0.5*red + green + 1.5*blue)/3
    
    threshold1 = graythresh(sumImg, 0.75)
    if threshold1 < 0.75:
        threshold1 = 0.75
    
    print ('The threshod for the sum image is',threshold1)
    skyImg1 = sumImg > threshold1
    skyImg = skyImg1*1
    
##    subplot(3,3,3)
##    imshow(ExG)
##    
##    subplot(3,3,4)
##    imshow(sumImg)
##    
##    subplot(3,3,5)
##    imshow(cannyEdge)
##    
##    subplot(3,3,6)
##    imshow(skyImg1)
##    del skyImg1
    
    # threshold for green vegetation pixel
    thresholdGreen = graythresh(ExG,0.08)
    if thresholdGreen > 0.02:
        thresholdGreen = 0.02
    print ('The threshold for the green canpy is:',thresholdGreen)
    del red, blue, green, I,segmented_image
    
    outImg = Image.fromarray(skyImg.astype(np.float32))
    del outImg,sumImg
    
    
    ####REFINE THE CLASSIFICATION RESULT BASED ON GEOMETRICAL INFORMATION
    ### use the morphological method to count the isolated objects
##    labels,nbr_objects = measurements.label(skyImg)
##    labels_image
    
    # split the sphere view images into numbers of strips
    dims = skyImg.shape
    radius = skyImg.shape[0]/2
    
    # loop all the segmented sky object
    for i in range(1,number_regions):
        idx = np.where(labels_image == i)
        
        rows = idx[0]
        cols = idx[1]
        pxlNum = len(rows)
        
        # the object cover the center point must be the sky
        mdPntX = int(0.5*basewidth)
        mdPntY = int(0.5*basewidth)
        
        if mdPntX in rows and mdPntY in cols:
            print ('The center point is sky=================')
            skyImg[rows,cols] = 1
        
        if not skyImg[idx][1]:
            continue
        
        # the center point of the object
        Cy = int(sum(rows)/len(rows))
        Cx = int(sum(cols)/len(cols))
        
        # get all the pixels along the line between (Cx,Cy) and center of the sphere image
        slope = (Cy - 0.5*dims[0])/(Cx - 0.5*dims[1] + 0.0001) # slope of the line
        pxL = int(min(Cx,0.5*dims[1])) # x lower limit
        pxU = int(max(Cx,0.5*dims[1])) # x upper limit
        
        for x in range(pxL,pxU,3):
            y = slope*(x - 0.5*dims[1]) + 0.5*dims[0]
            
            # if we find building pixels in the inner part of the grid, then change the skyobject back to building
            if skyImg[y,x]==0: # and ExG[y,x]<thresholdGreen:
                
                # print 'building find above the "sky pixel", change it back to building'
                skyImg[rows,cols] = 0
                break
        
        if mdPntX in rows and mdPntY in cols:
            print ('The center point is sky=================')
            skyImg[rows,cols] = 1
    
    del labels_image
    
##    subplot(3,3,7)
##    imshow(skyImg)
    
    outImg = Image.fromarray(skyImg.astype(np.float32))
    outImg.save(classImgFile)
    
    del outImg,skyImg
##    show()
    # define new rule base on the percentage of edge density in each object
    # check all sky objects in the preliminary classification result
    
    

def OBIA_Skyclassification_vote2Modifed(inputImg,outputFolder):
    '''
    This function is a modified OBIA sky classification used to extract
    the sky pixels from the image. Different with the OBIA_Skyclassification_vote
    This function deals with the the white sky pixels
    
    parameters:
        inputImg: the file path of input image
        outputFolder: the output foldername
    '''
    
    import os,os.path
    from PIL import Image, ImageEnhance
    import numpy as np
    import pymeanshift as pms

    # create outputFolder if there is no such folder
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)
    
    # prepare the outputfile name
    basename = os.path.basename(inputImg)[:-4]
    classImgFile = os.path.join(outputFolder,'%s_skyRes.tif'%(basename))
    
    # check if the file already exist, yes quit
    if os.path.exists(classImgFile):
        return
    
    resizedImgFile = os.path.join(outputFolder,'%s_Resized.jpg'%(basename))
    segImgFile = os.path.join(outputFolder,'%s_seged.jpg'%(basename))
    
    # resize the original image file to speed the calculation
    basewidth = 600
    img = Image.open(inputImg)
    
    
    contrast = ImageEnhance.Contrast(img)
    del img
    img = contrast.enhance(2)
    
    
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    
    panoImage = np.array(img)
    pixlImg = panoImage/255.0
    redP = pixlImg[:,:,0]
    greenP = pixlImg[:,:,1]
    blueP = pixlImg[:,:,2]
    
    ExG = 2*greenP - redP - blueP
    del pixlImg,greenP,redP,blueP
    
    # call the function from pymeanshift to segment the GSV images
##    (segmented_image, labels_image, number_regions) = pms.segment(panoImage,spatial_radius=6, 
##                                                          range_radius=4, min_density=40)        
    
    (segmented_image, labels_image, number_regions) = pms.segment(panoImage,spatial_radius=8, 
                                                          range_radius=6, min_density=40)        
    
    
    # get the canny edge of original pano image    
##    segmented_imageOut = Image.fromarray(segmented_image)
##    segmented_imageOut.save(segImgFile)
##    del segmented_imageOut
    
    
##    subplot(3,3,1)
##    imshow(panoImage)
##    subplot(3,3,2)
##    imshow(labels_image)
    
    I = segmented_image/255.0
    red = I[:,:,0]
    green = I[:,:,1]
    blue = I[:,:,2]
    
    ExB = 2*blue - red - green
    threshBlue = graythresh(ExB, 0.60)
    skyBlue = ExB > threshBlue
##    subplot(3,3,3)
##    imshow(skyBlue)
    
    # calculate the difference between green band with other two bands
    green_red_Diff = green - red
    green_blue_Diff = green - blue
    #sumImg = (0.5*red + green + 1.5*blue)/3
    sumImg = (0.5*red + green + 2*blue)/3
    
    
##    threshold1 = graythresh(sumImg, 0.75)
##    if threshold1 < 0.75:
##        threshold1 = 0.75
    
    threshold1 = graythresh(sumImg, 0.70)
    if threshold1 < 0.70:
        threshold1 = 0.70
    
    print ('The threshod for the sum image is',threshold1)
    skyImg1 = sumImg > threshold1
    skyImg = skyImg1*1
    skyImg = skyBlue + skyImg
    
    
##    subplot(3,3,4)
##    imshow(ExG)
##    
##    subplot(3,3,5)
##    imshow(sumImg)
##    
##    subplot(3,3,6)
##    imshow(ExB)
##    
##    subplot(3,3,7)
##    imshow(skyImg1)
    del skyImg1,skyBlue
     
    # threshold for green vegetation pixel
    thresholdGreen = graythresh(ExG,0.08)
    if thresholdGreen > 0.02:
        thresholdGreen = 0.02
    print ('The threshold for the green canpy is:',thresholdGreen)
    del red, blue, green, I,segmented_image
    
    
    ####REFINE THE CLASSIFICATION RESULT BASED ON GEOMETRICAL INFORMATION
    ### use the morphological method to count the isolated objects
##    labels,nbr_objects = measurements.label(skyImg)
##    labels_image
    
    # split the sphere view images into numbers of strips
    dims = skyImg.shape
    radius = skyImg.shape[0]/2
    
    # loop all the segmented sky object
    for i in range(1,number_regions):
        idx = np.where(labels_image == i)
        
        rows = idx[0]
        cols = idx[1]
        pxlNum = len(rows)
        
        # the object cover the center point must be the sky
        mdPntX = int(0.5*basewidth)
        mdPntY = int(0.5*basewidth)
        
        if mdPntX in rows and mdPntY in cols:
            print ('The center point is sky=================')
            skyImg[rows,cols] = 1
        
        if not skyImg[idx][1]:
            continue
        
        # the center point of the object
        Cy = int(sum(rows)/len(rows))
        Cx = int(sum(cols)/len(cols))
        
        # get all the pixels along the line between (Cx,Cy) and center of the sphere image
        slope = (Cy - 0.5*dims[0])/(Cx - 0.5*dims[1] + 0.0001) # slope of the line
        pxL = int(min(Cx,0.5*dims[1])) # x lower limit
        pxU = int(max(Cx,0.5*dims[1])) # x upper limit
        
        for x in range(pxL,pxU,5):
            y = slope*(x - 0.5*dims[1]) + 0.5*dims[0]
            
            # if we find building pixels in the inner part of the grid, then change the skyobject back to building
            #if skyImg[y,x]==0: # and ExG[y,x]<thresholdGreen:
            #if skyImg[y,x]==0 and ExG[y,x]<thresholdGreen:
            if sumImg[y,x] < threshold1 and ExB[y,x] < threshBlue:                
                # print 'building find above the "sky pixel", change it back to building'
                skyImg[rows,cols] = 0
                break
        
        if mdPntX in rows and mdPntY in cols:
            print ('The center point is sky=================')
            skyImg[rows,cols] = 1
    
    del labels_image, sumImg,ExB
    
##    subplot(3,3,8)
##    imshow(skyImg)
    
    outImg = Image.fromarray(skyImg.astype(np.float32))
    outImg.save(classImgFile)
    
    del outImg,skyImg
##    show()
    

def SkyExtractionFromFisheyeImg_vote(inputPano,outputSkyres):
    
    '''
    This program is used to extract the sky pixels from the fisheye images
    This function use pixel level threshold to derive the sky then aggregate to object level
    
    Parameters: 
        inputPano: folder of image of fisheye panorama
        outputSkyres: classification result of fisheye pano image
    '''
    
    import os,os.path
    
    # if the input is folder then list GSV images
    if os.path.isdir(inputPano):
        # the output is also a folder, create the output folder if there is
        
        if not os.path.exists(outputSkyres):
            os.makedirs(outputSkyres)
        
        fileLst = os.listdir(inputPano)
        for file in fileLst:
            panoImgFile = os.path.join(inputPano,file)
            
            # judge if the imput image is a jpg image or not
            extention = os.path.splitext(panoImgFile)[1]
            
            if extention == '.jpg':
                #OBIA_Skyclassification_vote(panoImgFile,outputSkyres)
                OBIA_Skyclassification_vote2Modifed(panoImgFile,outputSkyres)
    else:
        panoImgFile = inputPano
        #OBIA_Skyclassification_vote(panoImgFile,outputSkyres)
        OBIA_Skyclassification_vote2Modifed(panoImgFile,outputSkyres)



def OBIA_Skyclassification_vote2Modifed_2(panoImage,classImgFile='skyRes.tif'):
    '''
    Modfied based on "OBIA_Skyclassification_vote2Modifed"
    the input of this function is numpy array and return numpy array class res
    
    This function is a modified OBIA sky classification used to extract
    the sky pixels from the image. Different with the OBIA_Skyclassification_vote
    This function deals with the the white sky pixels
    
    parameters:
        inputImg: the input hemispherical image, numpy array
        outputFileName: the output sky image file name
    return:
        classification result in numpy array format
    
    last modified on Dec 28, 2017 by Xiaojiang Li, MIT Senseable City Lab
    
    '''
    
    import os,os.path
    from PIL import Image, ImageEnhance
    import numpy as np
    import pymeanshift as pms
    
    
    basewidth = panoImage.shape[0]
    pixlImg = panoImage/255.0
    redP = pixlImg[:,:,0]
    greenP = pixlImg[:,:,1]
    blueP = pixlImg[:,:,2]
    
    ExG = 2*greenP - redP - blueP
    del pixlImg,greenP,redP,blueP
    
    # call the function from pymeanshift to segment the GSV images    
    (segmented_image, labels_image, number_regions) = pms.segment(panoImage,spatial_radius=8, 
                                                          range_radius=6, min_density=40)        
    
    
    I = segmented_image/255.0
    red = I[:,:,0]
    green = I[:,:,1]
    blue = I[:,:,2]
    
    ExB = 2*blue - red - green
    threshBlue = graythresh(ExB, 0.60)
    skyBlue = ExB > threshBlue
    
    # calculate the difference between green band with other two bands
    green_red_Diff = green - red
    green_blue_Diff = green - blue
    sumImg = (0.5*red + green + 2*blue)/3
    
    threshold1 = graythresh(sumImg, 0.70)
    if threshold1 < 0.70:
        threshold1 = 0.70
    
    #print ('The threshod for the sum image is',threshold1)
    skyImg1 = sumImg > threshold1
    skyImg = skyImg1*1
    skyImg = skyBlue + skyImg
    
    del skyImg1,skyBlue
     
    # threshold for green vegetation pixel
    thresholdGreen = graythresh(ExG,0.08)
    if thresholdGreen > 0.02:
        thresholdGreen = 0.02
    #print ('The threshold for the green canpy is:',thresholdGreen)
    del red, blue, green, I,segmented_image
    
    
    ####REFINE THE CLASSIFICATION RESULT BASED ON GEOMETRICAL INFORMATION
    ### use the morphological method to count the isolated objects
    
    # split the sphere view images into numbers of strips
    dims = skyImg.shape
    radius = int(skyImg.shape[0]/2)
        
    
    # loop all the segmented sky object
    for i in range(1,number_regions):
        idx = np.where(labels_image == i)
        
        rows = idx[0]
        cols = idx[1]
        pxlNum = len(rows)
        
        # the object cover the center point must be the sky
        mdPntX = int(0.5*basewidth)
        mdPntY = int(0.5*basewidth)
        
        if mdPntX in rows and mdPntY in cols:
            skyImg[rows,cols] = 1
        
        if not skyImg[idx][1]:
            continue
        
        # the center point of the object
        Cy = int(sum(rows)/len(rows))
        Cx = int(sum(cols)/len(cols))
         
        # get all the pixels along the line between (Cx,Cy) and center of the sphere image
        slope = (Cy - 0.5*dims[0])/(Cx - 0.5*dims[1] + 0.0001) # slope of the line
        pxL = int(min(Cx,0.5*dims[1])) # x lower limit
        pxU = int(max(Cx,0.5*dims[1])) # x upper limit
                
        for x in range(pxL,pxU,5):
            y = int(slope*(x - 0.5*dims[1]) + 0.5*dims[0])
            
            # if we find building pixels in the inner part of the grid, then change the skyobject back to building
            if sumImg[y,x] < threshold1 and ExB[y,x] < threshBlue:                
                # print 'building find above the "sky pixel", change it back to building'
                skyImg[rows,cols] = 0
                break
                
        if mdPntX in rows and mdPntY in cols:
            skyImg[rows,cols] = 1
    
    del labels_image, sumImg,ExB
    
    outImg = Image.fromarray(skyImg.astype(np.float32))
    # outImg.save(classImgFile)
    del outImg
    
    return skyImg

