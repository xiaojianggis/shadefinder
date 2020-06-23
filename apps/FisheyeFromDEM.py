# -*- coding: cp1252 -*-
# This program is used to compute the Sky View Factor
# based on 3D DEM

# Copyright(c)Xiaojiang Li, UCONN, MIT Senseable City Lab
# First version July 5, 2016, Boston

# Geneate hemispherical images based on the building height model in Boston
# Edit on Oct 20, 2017, MIT Senseable City LAB, Cambridge

# version for Xiaojiang - PC, Be careful of the root and folder


import gdal,osr,ogr
import os,os.path
import numpy as np
import math
from PIL import Image
from osgeo import gdal, ogr


def GetCentroidValue(fc,rast):
    '''
    This function is used to overlap the vector file on the raster file
    and then compute the number of cols and rows in the raster file
    First version July 5, 2016, After PK presentation, MIT Senseable City Lab

    Make sure the two files have the same image projection, in this version,
    no image transform id conducted, think about in future,

    var source = new Proj4js.Proj('PROJ4_ARGS_FOR_YOUR_PROJECTION');
    var dest = new Proj4js.Proj('EPSG:4326') // geographic coordinates + WGS84 (which matches the ellipsoid used in your .prj)
        
    parameters:
        fc: the input feature class
        rast: the corresponding raster file
    '''
    
    #open vector layer
    drv=ogr.GetDriverByName('ESRI Shapefile') #assuming shapefile?
    ds=drv.Open(fc,True) #open for editing
    lyr=ds.GetLayer(0)
        
    # add new field to store the calculated SVF result
    svfDem = ogr.FieldDefn('svfDEM1ft', ogr.OFTReal)
    lyr.CreateField(svfDem)
    
    #open raster layer
    src_ds=gdal.Open(rast) 
    gt=src_ds.GetGeoTransform()
    rb=src_ds.GetRasterBand(1)
    arrayDEM = rb.ReadAsArray()
    gdal.UseExceptions() #so it doesn't print to screen everytime point is outside grid
    
    # get the size of the raster
    rows = arrayDEM.shape[0]
    cols = arrayDEM.shape[1]
    print 'The size rows is %s, the cols is %s :'%(rows,cols)
    
    for feat in lyr:
        geom=feat.GetGeometryRef()
        mx=geom.Centroid().GetX()
        my=geom.Centroid().GetY()
        
        # panoID of the site
        panoID = feat.GetField("panoID")
        
        # here the +1 and -2 are adjusted manully based on checking on ENVI
        px = int((mx - gt[0]) / gt[1])+1 
        py = int((my - gt[3]) / gt[5])-2 
                
        try: #in case raster isnt full extent
            structval=rb.ReadRaster(px,py,1,1,buf_type=gdal.GDT_Float32) #Assumes 32 bit int- 'float'
            intval = struct.unpack('f' , structval) #assume float
            val=intval[0]
        except:
            val=-9999 #or some value to indicate a fail
        
        
        ## CALCULATE SKY VIEW FACTOR FOR ALL GSV SITES
        SVF_res = 0
        
        # search all 360 angles for each pano site
        for thetaN in range(360):
            rangeDist = 500 # 500m
            rangeFeet = int(rangeDist*3.28084)  # convert the meter to feet
            
            # create points along each angle
            radiusRange = range(5,rangeFeet,1)
            theta = np.pi*thetaN/180
            
            # create an empty beta list to store the betas for each spike
            betaLst = []
            
            # create points along the ray line in 200m or 656 feet, one pixel is one foot
            for radius in radiusRange:
                rayX = int(px + radius*math.cos(theta))
                rayY = int(py + radius*math.sin(theta))
                
                # the corresponding building height is, consider the search region could out of the image
                if rayX >= cols or rayX < 0 or rayY >= rows or rayY < 0:
                    continue
                
                buildH = arrayDEM[rayY,rayX]
                
                # if the pixel has its height lower than 2.5m, do not consider anymore
                if buildH < 2.5:
                    continue
                
                # considering the GSV pano is captured at height of 2.5m
                beta = math.atan((buildH - 2.5)*3.28084/radius)
                betaLst.append(beta)
                
            if len(betaLst)>0:
                maxBeta = max(betaLst)
##                print 'The largest angle,thetaN:====',maxBeta,len(betaLst),thetaN
            else:
                maxBeta = 0
                        
            SVF_res = SVF_res + math.cos(maxBeta)**2
        
        SVF = SVF_res*1.0/360
        print 'The SVF for panoID %s, is %f, row is %s, col is %s'%(panoID,SVF,px,py)
        
        feat.SetField('svfDEM1ft',SVF)
        lyr.SetFeature(feat)
    
    print 'The geoinformation of the gt:',gt
    
    src_ds=None
    ds=None



def SVFcalculationOnDEM_efficient(fc,rast):
    '''
    This function is used to overlap the vector file on the raster file
    and then compute the number of cols and rows in the raster file

    IT IS INEFFICIENT TO READ THE WHOLE RASTER FILE DIRECTLY, THEREFORE, THIS
    CODE WILL READ RASTER FILE BY BLOCKS
    
    First version, Sep 7, 2016
    
    
    Make sure the two files have the same image projection, in this version,
    no image transform id conducted, think about in future,

    var source = new Proj4js.Proj('PROJ4_ARGS_FOR_YOUR_PROJECTION');
    var dest = new Proj4js.Proj('EPSG:4326') // geographic coordinates + WGS84 (which matches the ellipsoid used in your .prj)
    
    parameters:
        fc: the input feature class
        rast: the corresponding raster file
    '''
    
    #open vector layer
    drv=ogr.GetDriverByName('ESRI Shapefile') #assuming shapefile?
    ds=drv.Open(fc,True) #open for editing
    lyr=ds.GetLayer(0)
    sourceProj = lyr.GetSpatialRef()
    print sourceProj
    
##    # add new field to store the calculated SVF result
##    svfDem = ogr.FieldDefn('svfDEM1ft', ogr.OFTReal)
##    lyr.CreateField(svfDem)
    
    
    #open raster layer
    src_ds=gdal.Open(rast) 
    gt=src_ds.GetGeoTransform()
    rb=src_ds.GetRasterBand(1)
    print 'the gt is:',gt
    print 'the rb is:',rb
    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize
    print 'The rows is:%s, the cols is:%s'%(rows,cols)
    
    x_offset = 510
    y_offset = 510
    
    for feat in lyr:
        geom=feat.GetGeometryRef()
        mx=geom.Centroid().GetX()
        my=geom.Centroid().GetY()
        
        # panoID of the site
        panoID = feat.GetField("panoID")

        
##        if panoID != '1n4gzzr_wshjXmvifCDtmQ':
##            continue


        # here the +1 and -2 are adjusted manully based on checking on ENVI
        px = int((mx - gt[0]) / gt[1])+1 
        py = int((my - gt[3]) / gt[5])-2 
        
        print px,py
        
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
        
        print 'The boundary of the block group is:',x_block_low,x_block_high,y_block_low,y_block_high
        print 'The panoID is:',panoID
        
        # read theDSM of the block
        x_size = x_block_high - x_block_low
        y_size = y_block_high - y_block_low
        arrayDEM = rb.ReadAsArray(x_block_low, y_block_low, x_size, y_size)
        if arrayDEM is None:
            print 'This is a noneTyep array==================='
            continue
                        
        ## CALCULATE SKY VIEW FACTOR FOR ALL GSV SITES
        SVF_res = 0
        
        # search all 360 angles for each pano site
        for thetaN in range(360):
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
                rayY = int(py + radius*math.sin(theta))
                
                # the corresponding building height is, consider the search region could out of the image
                if rayX >= cols or rayX < 0 or rayY >= rows or rayY < 0:
                    continue
                
                XinBlc = rayX - x_block_low
                YinBlc = rayY - y_block_low
                
                buildH = arrayDEM[YinBlc,XinBlc]
                
                # if the pixel has its height lower than 2.5m, do not consider anymore
                if buildH < 2.5:
                    continue
                
                # considering the GSV pano is captured at height of 2.5m
                beta = math.atan((buildH - 2.5)/radius)
                betaLst.append(beta)
                
            if len(betaLst)>0:
                maxBeta = max(betaLst)
##                print 'The largest angle,thetaN:====',maxBeta,len(betaLst),thetaN
            else:
                maxBeta = 0
            
            SVF_res = SVF_res + math.cos(maxBeta)**2
        
        SVF = SVF_res*1.0/360
        print 'The SVF for panoID %s, is %f, row is %s, col is %s'%(panoID,SVF,px,py)
        
##        feat.SetField('svfDEM1ft',SVF)
##        lyr.SetFeature(feat)
    
    print 'The geoinformation of the gt:',gt
    
    src_ds=None
    ds=None



def FisheyeFromDEM_efficient(fc,rast,fisheyeSize,outputFolder):
    '''
    This function is used to generate hemispherical images based on
    building height model. The shapefile will overlay on the raster file
    and then use the ray-tracing algorithm to generate hemispherical images
    
    IT IS INEFFICIENT TO READ THE WHOLE RASTER FILE DIRECTLY, THEREFORE, THIS
    CODE WILL READ RASTER FILE BY BLOCKS
    
    First version, Oct 20,2017
    
    
    Make sure the two files have the same image projection, in this version,
    no image transform id conducted, think about in future,
    
    var source = new Proj4js.Proj('PROJ4_ARGS_FOR_YOUR_PROJECTION');
    var dest = new Proj4js.Proj('EPSG:4326') // geographic coordinates + WGS84 (which matches the ellipsoid used in your .prj)
    
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
    drv=ogr.GetDriverByName('ESRI Shapefile') #assuming shapefile?
    ds=drv.Open(fc,0) # read only
    lyr=ds.GetLayer(0)
    sourceProj = lyr.GetSpatialRef()
    print sourceProj

    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)

    #open raster layer
    src_ds=gdal.Open(rast) 
    gt=src_ds.GetGeoTransform()
    rb=src_ds.GetRasterBand(1)
    print 'the gt is:',gt
    print 'the rb is:',rb
    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize
    print 'The rows is:%s, the cols is:%s'%(rows,cols)
    
    x_offset = 510
    y_offset = 510
    
        
    # iterate all features in the shapefile
    for feat in lyr:
        geom=feat.GetGeometryRef()
        mx=geom.Centroid().GetX()
        my=geom.Centroid().GetY()
        
        # panoID of the site
        panoID = feat.GetField("panoID")

        # convert the projection into WGS
        coordTrans = osr.CoordinateTransformation(sourceProj, targetProj)
        geom.Transform(coordTrans)
        lon = geom.GetX()
        lat = geom.GetY()
        
        # the output generated fisheye image name
        FileName = '%s - %s - %s.tif'%(panoID,lon,lat)
        outputFileName = os.path.join(outputFolder,FileName)
        if os.path.exists(outputFileName):
            continue
        
        print 'The output fisheye name is:',FileName
        
        
        # create an empty array to save the generated hemispherical image
        fisheyeImg = np.zeros(shape=(fisheyeSize,fisheyeSize),dtype = np.int8)

        
##        if panoID != '2tkDFKC7RMV9Q0jALFmW8w':
##            continue
        
        
        # here the +1 and -2 are adjusted manully based on checking on ENVI
        px = int((mx - gt[0]) / gt[1])+1 
        py = int((my - gt[3]) / gt[5])-2 
        
        print px,py
        
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
        
        print 'The boundary of the block group is:',x_block_low,x_block_high,y_block_low,y_block_high
        print 'The panoID is:',panoID
        
        # read theDSM of the block
        x_size = x_block_high - x_block_low
        y_size = y_block_high - y_block_low
        arrayDEM = rb.ReadAsArray(x_block_low, y_block_low, x_size, y_size)
        if arrayDEM is None:
            print 'This is a noneTyep array==================='
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
                betaLst.append(beta)
            
            if len(betaLst)>0:
                maxBeta = max(betaLst)
            else:
                maxBeta = 0
            
            # the distance to the center of the fisheye image
            fr = (0.5*fisheyeSize)/(0.5*np.pi)*(0.5*np.pi - maxBeta)
            
            # the coordinate the the sky line in the fisheye image                
            fx = int(0.5*fisheyeSize + fr*math.cos(theta))
            fy = int(0.5*fisheyeSize - fr*math.sin(theta))
            
            # append the vertice to the list
            polysLst.append((fx,fy))
            polysLst2 = [polysLst]
                    
        # connect all vertices generated on the 
##        img = Image.new('L', (fisheyeSize, fisheyeSize), 0)   # The Zero is to Specify Background Color
##        draw = ImageDraw.Draw(img)
##
##        vertexlist = polysLst
##        for vertex in range(len(vertexlist)):
##            startpoint = vertexlist[vertex]
##            
##            try: endpoint = vertexlist[vertex+1]
##            except IndexError: endpoint = vertexlist[0]
##            
##            # The exception means We have reached the end and need to complete the polygon
##            draw.line((startpoint[0], startpoint[1], endpoint[0], endpoint[1]), fill=255)
##        
##        # save the outline of the sky pixels
##        img.save(r'd:\polgon.tif')

        
##        # convert list to numpy array
##        polys = np.asarray(polysLst2,np.int16)
##        
##        for i in polys.tolist():
##            cv2.fillConvexPoly(fisheyeImg, np.array(i), 1)
        
        polys2 = np.asarray(polysLst2)
        cv2.fillPoly(fisheyeImg, polys2, 1)
        outImg = Image.fromarray(fisheyeImg.astype('uint8')*255)
        outImg.save(outputFileName)

        del fisheyeImg,outImg,polys2
        
    print 'The geoinformation of the gt:',gt
    
    src_ds=None
    ds=None



## ------------------------- Main Function -------------------------------

import os,os.path

##inRoot = r'D:\PhD Project\SkyViewFactProj\BostonDowntonDataSVF'
##buildHfile = r'buildft1ra.tif'
##panoSite = r'Reproj_gsvSite_lyr.shp'
##
##buildHeightFile = os.path.join(inRoot,buildHfile)
##panoSiteFile = os.path.join(inRoot,panoSite)
##
##print 'the building and pano files are:',buildHeightFile,panoSiteFile
##GetCentroidValue(panoSiteFile,buildHeightFile)


## FOR BOSTON STREET GREENERY PROJECT
##inRoot = r'D:\PhD Project\SkyViewFactProj\Boston  Data\boston_buildings'
##buildHeightFile = os.path.join(inRoot,'BuildingHeightby_arcgisNotPythoncode.tif')
##panoSiteFile = r'D:\PhD Project\SkyViewFactProj\Boston  Data\Shapefiles\Reproj_SVF_Res_fromFisheyeimageSep1_2016_v2.shp'


## FOR BOSTON SOLAR RADIATION MODELSING PROJECT
inRoot = r'D:\PhD Project\SkyViewFactProj\Boston  Data\boston_buildings'
buildHeightFile = os.path.join(inRoot,'BuildingHeightby_arcgisNotPythoncode.tif')
panoSiteFile = 'D:\PhD Project\RouteFindingProj\Spatial Data\SunDurationAug1stCompleteMapping_reproj.shp'
outputFolder = r'D:\PhD Project\RouteFindingProj\FisheyeImgs\SkyImg_DSM2'
print 'the building and pano files are:',buildHeightFile,panoSiteFile

fisheyeSize = 600 # the size of the generated hemispherical image
FisheyeFromDEM_efficient(panoSiteFile,buildHeightFile,fisheyeSize,outputFolder)

