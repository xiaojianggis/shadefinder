# This program is used to download all images in study area and the gsv info
# It is implementing OTSU algorithm to chose the threshold automatically
# the current program dependent on numpy, cv2 moduels
# For more details about the OTSU algorithm and python implmentation
# cite: http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html

# Copyright(C) Xiaojiang Li, Department of Geography, UCONN

# Version July 21 2017 

def graythresh(array,level):

    '''array: is the numpy array waiting for processing
    return thresh: is the result got by OTSU algorithm
    if the threshold is less than level, then set the level as the threshold
    '''
    maxVal = np.max(array)
    minVal = np.min(array)
    
#   if the inputImage is a float of double dataset then we transform the data 
#   in to byte and range from [0 255]
    
    if maxVal <= 1:
        array = array*255
    elif maxVal >= 256:
        array = np.int((array - minVal)/(maxVal - minVal))
    
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
    


def OBIAotsuVegClass(ImgFilename):

    '''
    This function is used to classify the green vegetation from GSV image,
    This is based on object based and otsu automatically thresholding method
        ImgFilename: the file name of the GSV image
        return the percentage of the green vegetation pixels in the GSV image
        and the classification result
    '''
    
    import pymeanshift as pms
    import urllib
    
    try:
        img = np.array(Image.open(ImgFilename))
    except IOError:
        return "Cannot open Image"

    # use the meanshift segmentation algorithm to segment the original GSV image
    (segmented_image, labels_image, number_regions) = pms.segment(img,spatial_radius=6, 
                                                     range_radius=7, min_density=40)
    
    
    I = segmented_image/255.0
    red = I[:,:,0]
    green = I[:,:,1]
    blue = I[:,:,2]

    # calculate the difference between green band with other two bands
    green_red_Diff = green - red
    green_blue_Diff = green - blue
    
    ExG = green_red_Diff + green_blue_Diff
    diffImg = green_red_Diff*green_blue_Diff
    
    redThreImgU = red < 0.7
    greenThreImgU = green < 0.7
    blueThreImgU = blue < 0.7

    del red, blue, green, I
    greenImg1 = redThreImgU * greenThreImgU * blueThreImgU
    del redThreImgU, greenThreImgU, blueThreImgU

    threshold = graythresh(ExG, 0.08)
    if threshold > 0.08:
        threshold = 0.08

    elif threshold < 0.05:
        threshold = 0.05

    greenImg2 = ExG > threshold    
    greenImg3 = diffImg > 0.0025
    greenImg4 = green_red_Diff > 0
    greenImg = greenImg1*greenImg2

    del ExG,green_blue_Diff,green_red_Diff

    # calculate the percentage of the green vegetation
    greenPxlNum = len(np.where(greenImg != 0)[0])
    greenPercent = greenPxlNum/(400.0*400)*100
    del greenImg1,greenImg2,greenImg3, greenImg4
    
    outImg = Image.fromarray(greenImg.astype(np.float32))
    
    return greenPercent,outImg


def VegetationClassification(ImgFilename):

    '''
    This function is used to classify the green vegetation from GSV image,
    This is object based and uses the otsu automatic thresholding method
    The season of GSV images were also considered in this function
        ImgFilename: the file name of the GSV image
        return the percentage of the green vegetation pixels in the GSV image
        and the classification result
    '''

    import pymeanshift as pms
    import urllib
    import cv2
    import numpy as np
    from matplotlib import pyplot as plt
    
    img = np.array(Image.open(ImgFilename))

    # use the meanshift segmentation algorithm to segment the original GSV image
    (segmented_image, labels_image, number_regions) = pms.segment(img,spatial_radius=6, 
                                                     range_radius=7, min_density=40)
    
    
    # lablImg = Image.fromarray(labels_image/255.0)
    # print type(lablImg)
    # lablImg.save("labelImg.tif")
    # segImg = Image.fromarray(segmented_image)
    # segImg.save("segmentedImg.jpg")

    
    I = segmented_image/255.0
    red = I[:,:,0]
    green = I[:,:,1]
    blue = I[:,:,2]

    # calculate the difference between green band with other two bands
    green_red_Diff = green - red
    green_blue_Diff = green - blue
    
    ExG = green_red_Diff + green_blue_Diff
    diffImg = green_red_Diff*green_blue_Diff

    redThreImgU = red < 0.6
    greenThreImgU = green < 0.9
    blueThreImgU = blue < 0.6

    shadowRedU = red < 0.3
    shadowGreenU = green < 0.3
    shadowBlueU = blue < 0.3

    del red, blue, green, I

    greenImg1 = redThreImgU * blueThreImgU*greenThreImgU
    greenImgShadow1 = shadowRedU*shadowGreenU*shadowBlueU

    del redThreImgU, greenThreImgU, blueThreImgU
    del shadowRedU, shadowGreenU, shadowBlueU
    
    
    greenImg3 = diffImg > 0.0
    greenImg4 = green_red_Diff > 0
    threshold = graythresh(ExG, 0.1)
    
    if threshold > 0.1:
        threshold = 0.1
    
    elif threshold < 0.05:
        threshold = 0.05
    
    greenImg2 = ExG > threshold
    greenImgShadow2 = ExG > 0.05
    greenImg = greenImg1*greenImg2 + greenImgShadow2*greenImgShadow1
    
    del ExG,green_blue_Diff,green_red_Diff
    del greenImgShadow1,greenImgShadow2
    
    # calculate the percentage of the green vegetation
    greenPxlNum = len(np.where(greenImg != 0)[0])
    greenPercent = greenPxlNum/(400.0*400)*100
    
    del greenImg1,greenImg2
    del greenImg3,greenImg4
    
    outImg = Image.fromarray(greenImg.astype(np.float32))
    # outImg.save('Classification.tif')

    return greenPercent,outImg


# using 18 directions is too time consuming, therefore, here I only use 6 horizontal directions

# Each time the function will read a text, with 1000 records, and save the result as a single TXT
def GreenViewComputing_ogr_6Horizon(GSVinfoFolder, outGSVRoot, outTXTRoot):

    """
    This function is used to download the GSV from the information provide
    by the gsv info txt, and save the result to a shapefile
    
    Required modules: urllib and PIL
    
    GSVinfoTxt: the input folder name of GSV info txt
    outGSVRoot: the output directory of the GSV images
    outShpRoot: the output folder to store result feature classes
    """

    import urllib
    import time

    # set a series of heading angle

    headingArr = 360/6*np.array([0,1,2,3,4,5])    
    pitchArr = np.array([0])
    numGSVImg = len(headingArr)*len(pitchArr)*1.0

    # create a folder for GSV images and grenView Info
    if not os.path.exists(outGSVRoot):
        os.makedirs(outGSVRoot)

    if not os.path.exists(outTXTRoot):
        os.makedirs(outTXTRoot)

    # the input GSV info should be in a folder
    if not os.path.isdir(GSVinfoFolder):
        print 'You should input a folder'
        return

    else:
        allTxtFiles = os.listdir(GSVinfoFolder)

        for txtfile in allTxtFiles:
            if not txtfile.endswith('.txt'):
                continue

            txtfilename = os.path.join(GSVinfoFolder,txtfile)
            lines = open(txtfilename,"r")

            # create empty lists, to store the information of panos,and remove duplicates
            panoIDLst = []
            panoDateLst = []
            panoLonLst = []
            panoLatLst = []

            greenSeason = ['03','04','05','06','07','08','09','10']  #Change array to indicate region's Green Months 

            for line in lines:
                panoID = line.split(" panoDate")[0][-22:]
                panoDate = line.split(" longitude")[0][-7:]
                coordinate = line.split("longitude: ")[1]

                # to make sure the line is complete
                if 'latitude' not in coordinate:
                    continue
                
                lon = coordinate.split(" latitude: ")[0]
                lat = coordinate.split(" latitude: ")[1]
                lat = lat.split(" pano_yaw_degree")[0]
                
                # in case, the longitude and latitude are invalide
                if len(lon)<3:
                    continue
                
                if panoDate[-2:] not in greenSeason:
                    continue
                else:
                    # remove the duplicate panoramas
                    if panoID not in panoIDLst:
                        panoIDLst.append(panoID)
                        panoDateLst.append(panoDate)
                        panoLonLst.append(lon)
                        panoLatLst.append(lat)
            
            # the output text file to store the green view and pano info
            gvTxt = 'GV_'+os.path.basename(txtfile)
            GreenViewTxtFile = os.path.join(outTXTRoot,gvTxt)
            
            # check whether the file already generated
            print GreenViewTxtFile
            if os.path.exists(GreenViewTxtFile):
                continue
            
            # write the green view and pano info to txt            
            with open(GreenViewTxtFile,"w") as gvResTxt:
                for i in range(len(panoIDLst)):
                    panoDate = panoDateLst[i]
                    panoID = panoIDLst[i]
                    lat = panoLatLst[i]
                    lon = panoLonLst[i]
                    
                    print lon,lat,panoID,panoDate
                    
                    # calculate the green view
                    greenPercent = 0.0
                    print 'panoID is:',panoID
                    
                    for heading in headingArr:
                        print "Heading is: ",heading
                        
                        for pitch in pitchArr:
                            # using different keys for different process, each key can only request 25,000 imgs every 24 hours
                            URL = "http://maps.googleapis.com/maps/api/streetview?size=400x400&pano=%s&fov=60&heading=%d&pitch=%d&sensor=false&key=AIzaSyAwLr6Oz0omObrCJ4n6lI4VbCCvmaL1Z3Y"%(panoID,heading,pitch)
                            
                            # save the image at the current URL as a jpg image in the current workspace
                            GSVImageName = '%s_%s_%s_%s_panoID_%s_date_%s.jpg'%(lat,lon,heading,pitch,panoID,panoDate)
                            ResImageName = '%s_%s_%s_%s_panoID_%s_date_%s_Res.tif'%(lat,lon,heading,pitch,panoID,panoDate)
                            GSVimgFileName = os.path.join(outGSVRoot,GSVImageName)
                            GSVimgResFileName = os.path.join(outGSVRoot,ResImageName)
                            
                            time.sleep(1.5)
                            
                            urllib.urlretrieve(URL, GSVimgFileName)
                            
                            if GSVimgFileName=='' or os.path.getsize(GSVimgFileName)<2000:
                                # null image
                                greenPercent = -100
                                break
                            else:
                                # open the image at corresponding URL, and use PIL library to open it
                                [percent,outImg] = VegetationClassification(GSVimgFileName)
                                #print percent

                                # outImg.save(GSVimgResFileName)
                                greenPercent = greenPercent + percent
                                
                            # os.remove(GSVimgFileName)

                    greenViewVal = greenPercent/numGSVImg
                    print 'the green view for pano: %s is %s'%(greenViewVal,panoID)
                    
                    lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s, greenview: %s\n'%(panoID, panoDate, lon, lat, greenViewVal)
                    gvResTxt.write(lineTxt)



# using 18 directions is too time consuming, therefore, here I only use 6 horizontal directions
# Each time the function will read a text, with 1000 records, and save the result as a single TXT
def GreenViewComputing_6Horizon(panoID):
    
    """
    This function is used to download the GSV from the information provide
    by the gsv info, return the calculated Green View Index value
    
    Required modules: urllib and PIL
    
    input: 
        panoID: the panorama id of the GSV site
    
    output:
        return the green view index value for the site
    
    """
    
    import urllib
    import time
    import pymeanshift as pms
    from PIL import Image
    import numpy as np
    import os,os.path
    
    
    # set a series of heading angle
    headingArr = 360/6*np.array([0,1,2,3,4,5])    
    pitchArr = np.array([0])
    numGSVImg = len(headingArr)*len(pitchArr)*1.0
    
    # calculate the green view
    greenPercent = 0.0
    
    for heading in headingArr:
        print "Heading is: ",heading
        
        for pitch in pitchArr:
            # using different keys for different process, each key can only request 25,000 imgs every 24 hours
            URL = "http://maps.googleapis.com/maps/api/streetview?size=400x400&pano=%s&fov=60&heading=%d&pitch=%d&sensor=false&key=AIzaSyAwLr6Oz0omObrCJ4n6lI4VbCCvmaL1Z3Y"%(panoID,heading,pitch)
            
            # save the image at the current URL as a jpg image in the current workspace
            GSVImageName = '%s.jpg'%(panoID)
            ResImageName = '%s_Res.tif'%(panoID)
            
            time.sleep(1.5)            
            urllib.urlretrieve(URL, GSVImageName)
            
            if GSVImageName=='' or os.path.getsize(GSVImageName)<2000:
                # null image
                greenPercent = -100
                break
            else:
                # open the image at corresponding URL, and use PIL library to open it
                [percent,outImg] = VegetationClassification(GSVImageName)                
                greenPercent = greenPercent + percent
                
            # os.remove(GSVImageName)

    greenViewVal = greenPercent/numGSVImg
    
    print 'the green view for pano: %s is %s'%(greenViewVal,panoID)
    
    return greenViewVal


### ---------------------------------------Main function---------------------------------------------
import numpy as np
import os,os.path
from PIL import Image
import pymeanshift as pms
import urllib


GSVinfoRoot = r"/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/treepedia-db"
GSVimgpath = r"/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/treepedia-db/spatial-data"
outputTextPath = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/treepedia-db/spatial-data'
# panoid = r'_STgPdsvCuKxJoLIKlv7IA'
panoid = r'izIx2WCKLMV4KyXtq7Bydw'
gvi = GreenViewComputing_6Horizon(panoid)
print ('The gvi is:', gvi)


