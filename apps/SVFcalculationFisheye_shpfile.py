# This script is used to calculate the Sky View Factor from the binary classification
# result of re-projected Sphere view Google Street View panorama


# https://www.researchgate.net/profile/Silvana_Di_Sabatino/publications/2
# https://www.unibo.it/sitoweb/silvana.disabatino/en


# copyright(c) Xiaojiang Li, UCONN, MIT Senseable City Lab
# First version June 27, 2016, in MIT SCL, Messi loses again. 

# second version Sep 6, 2016, UCONN
# The second version add a statement to save the SVF to a shapefile, based on the
# coordinate information in the file name of the panoramas

from PIL import Image
from pylab import*
from scipy.ndimage import measurements, morphology
import numpy as np, cv2
import os, os.path
import math
import csv


def SVFcalculationOnFisheye(skyImgFile):
    '''
    The function is used to calcualte the SVF based on the SKY extract result
        skyImgFile: the input sky extraction result
        SVFres: the value of the SVF
    '''
    
    # read the sky image and get the metadata of the sky image
    skyImg = np.array(Image.open(skyImgFile))
    
    basename = os.path.join(skyImgFile)[:-4]
    panoID = basename[7:-7]
    
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
    
    for i in range(1,ringNum):
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
                if dist2Center > radiusI and dist2Center <= radiusO and skyImg[x,y]==1:
                    totalSkyPxl = totalSkyPxl + 1
                if dist2Center > radiusI and dist2Center <= radiusO:
                    totalPxl = totalPxl + 1
        
        #alphai = totalSkyPxl/(np.pi*(radiusO**2 - radiusI**2))
        alphai = totalSkyPxl*1.0/totalPxl
        
        SVFi = SVFmaxi*alphai
        SVF = SVF + SVFi

    print 'The calculated SVF value for panoID %s is: %s'%(panoID,SVF)    
    return SVF


def SVF_calculation_res2CSVfile(inputFisheyeSKYfile,csvFile):
    '''
    This program is calcualte the SVF based on the sky extract from fisheye image
        inputPano: folder of image of fisheye panorama
        outputSkyres: classification result of fisheye pano image
    '''
    import csv

    o_outFile = open(csvFile, "wb")
    spamWriter = csv.writer(o_outFile)
    title = ['panoID','SVF']
    spamWriter.writerow(title)
    
    # open CSV file to write data in
    with open(csvFile,'w') as csvfile:
        csvObj = csv.writer(csvfile, delimiter=',')
        title = ['panoID','SVF']
        csvObj.writerow(title)
        
        # if the input is folder then list GSV images
        if os.path.isdir(inputFisheyeSKYfile):
            
            # the output is also a folder, create the output folder if there is
            
            fileLst = os.listdir(inputFisheyeSKYfile)
            for file in fileLst:
                panoId = file.split('_reproj')[0]
                
                skyImgFile = os.path.join(inputFisheyeSKYfile,file)
                
                # judge if the imput image is a jpg image or not
                extention = os.path.splitext(skyImgFile)[1]
                
                # the classification is stored as tif file
                if extention == '.tif':
                    SVF = SVFcalculationOnFisheye(skyImgFile)
                attLine = [panoId,SVF]
                spamWriter.writerow(attLine)
    
    o_outFile.close()


def SVF_calculation_res2shapefile(inputFisheyeSKYfile,featureClass):
    
    '''
    This program is used to calculate the SVF from the SVF in the folder, and
    save the SVF result to the shapefile, the coordinate of the SVF sites from
    the filename of the fisheye images
    '''
    
    import GSVpanoProcessingAlgorithmsCombined_Lib as gsvlib
    import csv
    import os,os.path
    
    # create empty lists to store the pano information
    LonLst = []
    LatLst = []
    panoIDlist = []
    panoDateList = []
    svfList = []
    
    for fishImgFile in os.listdir(inputFisheyeSKYfile):
        fileName = os.path.basename(fishImgFile)
        extention = os.path.splitext(fishImgFile)[1]
        
        # get the pano info from the file name
        if extention == '.tif':
            panoInfo = fileName.split(" - ")
            
            panoId = panoInfo[0]
            lon = panoInfo[1]
            lat = panoInfo[2]
            panoDate = panoInfo[3] + '-' + panoInfo[4]
            
            LonLst.append(lon)
            LatLst.append(lat)
            panoIDlist.append(panoId)
            panoDateList.append(panoDate)
            
            SVF = SVFcalculationOnFisheye(os.path.join(inputFisheyeSKYfile,fishImgFile))
            svfList.append(SVF)
            print 'SVF is:=================',SVF
    
    # create shapefile by calling function "CreatePointFeature_ogr"
    gsvlib.CreatePointFeature_ogr(featureClass,LonLst,LatLst,panoIDlist,panoDateList,svfList)
    



def SVF_calculation_Fisheye2shapefile(inputFisheyeSKYfile,featureClass):
    
    '''
    This program is used to calculate the SVF from the SVF in the folder, and
    save the SVF result to the shapefile

    Sep 17, 2017, Quincy, MA
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab
    '''
    
    import GSVpanoProcessingAlgorithmsCombined_Lib as gsvlib
    import csv
    import os,os.path
    import ogr,osr
    import re
    
    # read the feature class and find the panoid
    driver = ogr.GetDriverByName('ESRI Shapefile')
    datasource = driver.Open(featureClass,1)
    layer = datasource.GetLayer()
    
    # get the current field names
    fieldLst = []
    lyrDef = layer.GetLayerDefn()
    for i in range(lyrDef.GetFieldCount()):
        field = lyrDef.GetFieldDefn(i).name
        fieldLst.append(field)
    
    # add a new filed
    newfield = 'svfGSV'
    if newfield not in fieldLst:
        pntNum_Field = ogr.FieldDefn(newfield, ogr.OFTReal)
        layer.CreateField(pntNum_Field)
    
    # loop all features and update the SVF value
    for feature in layer:
        panoid = feature.GetField('panoID')
        
        for fishImgFile in os.listdir(inputFisheyeSKYfile):
            feature.SetField(newfield,-999.0)
            
            # find the fisheye image based on the panoid using file matching
            if re.match(panoid,fishImgFile):
                # calculate the SVF using photographic method and update the SVF in the shpfile
                SVF = SVFcalculationOnFisheye(os.path.join(inputFisheyeSKYfile,fishImgFile))
                feature.SetField(newfield,SVF)
                layer.SetFeature(feature)
    
    datasource.Destroy()
    
    
## ------------------------MAIN FUNCTION -------------------
##inputPano = r"D:\PhD Project\SkyViewFactProj\Panoramas\GSV_fisheye pano2 SKY"
##print 'The file name is:',inputPano
##
### the output csv file
##SVFcsvFile = r"D:\PhD Project\SkyViewFactProj\Validation\GSV_SVFres.csv"
##
### calculate the SVF and output the result to csv file
##SVF_calculation_res2CSVfile(inputPano,SVFcsvFile)


##inputPano = r'D:\PhD Project\SkyViewFactProj\Boston  Data\PanoLab\panoImgs2016FisheyeSep1-2016'
####inputPano = r'D:\PhD Project\SkyViewFactProj\Boston  Data\PanoLab\Testing\SkyPanoImgAug23-2016Fisheye'
##featureClass = r'D:\PhD Project\SkyViewFactProj\Boston  Data\Shapefiles\SVF_Res_fromFisheyeimageSep1_2016.shp'
##SVF_calculation_res2shapefile(inputPano,featureClass)


# For Philip Project, light pollution
inputPano = r'D:\PhD Project\Darksky-Philips\PanoLab\FisheyeClassRes_Cambridge'
##inputPano = r'D:\PhD Project\SkyViewFactProj\Boston  Data\PanoLab\Testing\SkyPanoImgAug23-2016Fisheye'
#featureClass = r'D:\PhD Project\Darksky-Philips\SpatialDataCambridge\SVF_Res_fromFisheyeCambridge.shp'
featureClass = r'D:\PhD Project\Darksky-Philips\SpatialDataCambridge\SVF_Cambridge_Lightpollution_leaf.shp'
##SVF_calculation_res2shapefile(inputPano,featureClass)
SVF_calculation_Fisheye2shapefile(inputPano,featureClass)

