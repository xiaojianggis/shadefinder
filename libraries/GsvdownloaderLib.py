
def GSVpanoramaDowloaderUsingShpfile(panoInfoShpfile, outGSVRoot):
    """
    This function is used to download the GSV panoramas from Google using
    Google API, http://cbk0.google.com/cbk?output=tile&panoid=lKxUOImSaCYAAAQIt71GFQ&zoom=5&x=0&y=0
    
    The second step of this function is to merge all the patches together to create
    a complete panorama
    
    parameters:
        panoInfoShpfile: the shapefile for the metadata of the panoramas
        outGSVRoot: the output folder of the panorama images
    
    first version Aug 27, 2016 Brooklyn, CT. 
    """
    
    import urllib
    from PIL import Image
    import ogr,osr
    import sys
    
    if not os.path.exists(outGSVRoot):
        os.makedirs(outGSVRoot)
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    # change the projection of shapefile to the WGS84
    dataset = driver.Open(panoInfoShpfile)
    layer = dataset.GetLayer()
    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)
    
    panoIDlst = []
    # loop all the features in the featureclass
    feature = layer.GetNextFeature()
    for i in range(0, layer.GetFeatureCount()):
        feature = layer.GetFeature(i)        
        geom = feature.GetGeometryRef()
        
        # trasform the current projection of input shapefile to WGS84
        geom.Transform(transform)
        lon = geom.GetX()
        lat = geom.GetY()
        
        panoId = feature.GetField("panoID")
        panoDate = feature.GetField("panoDate")        
        lon = float(lon)
        lat = float(lat)
        print ('The coordinate is, the panoID is, panoDate',lon,lat,panoId,panoDate)

                
##        # not calculate those sites have GSV images taken in nongreen season            
##        if panoDate[-2:] not in ['06','07','08','09']:
##            print '-------------the GSV is not captured in green season'
##            print 'The data information is :', panoDate[-2:]
##            continue
##        else: 
        if panoId not in panoIDlst:
            panoIDlst.append(panoId)
            
            print ('the panoID,coordinate of thepano is:',panoId,lon,lat)
            
            # the ouput panorama name
            imgName = r'%s - %s - %s - %s.jpg'%(panoId,lon,lat,panoDate)
            mergedImgFile = os.path.join(outGSVRoot,imgName)
            if os.path.exists(mergedImgFile): continue
            
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

                    # using different url reading method in python2 and python3
                    if sys.version_info[0] == 2:
                        import cStringIO
                        imgfile = cStringIO.StringIO(urllib.urlopen(URL).read())
                    
                    if sys.version_info[0] == 3:
                        import urllib.request
                        import io
                        
                        request = urllib.request.Request(URL)
                        imgfile = io.BytesIO(urllib.request.urlopen(request).read())

                    # Image.open(imgfile).show()
                    imgPatch = np.array(Image.open(imgfile))
                    
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
            img.save(mergedImgFile)




def GSVpanoramaDowloader_GoogleMaps(panoId, zoom):
    """
    This function is used to download the GSV panoramas from Google using
    the URL address provided by Google Maps

    zoom is 0:
    https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&panoid=c8gcWEqLiOcVwDrtJDiB4g&output=tile&x=0&y=0&zoom=1&nbt&fover=2
    
    zoom is 1:
    https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&panoid=iKXN73P5BhoYdBpxB973zw&output=tile&x=0&y=0&zoom=0&nbt&fover=2


    parameters:
        panoId: the panorama id
        zoom: size of panoid image

    first version July 11, 2016, MIT Senseable City Lab.
    """

    import numpy as np
    import urllib
    # import cStringIO
    from PIL import Image
    import sys

    # download the GSV panoramas by specifying the parmaters
    # the zoom 0, size is 208*416 (1*1)
    # zoom 1, size is 412*832 (1*2) - > 832*1664 (2*4)

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
    print('The size of the merged image is:'+str(mergedImg.shape))
    print('The panoid is:------'+str(panoId))

    for x in range(xNum):
        for y in range(yNum):
            # The URL is derived from Google Maps, check the source code of Google Maps
            URL = "https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&panoid=%s&output=tile&x=%s&y=%s&zoom=%s&nbt&fover=2"%(panoId,x,y,zoom)
            
            # Open the GSV images are numpy arrayss
            # try:
            #    urllib.request.urlopen(URL)
            # except urllib.request.HTTPError:
            #     print("HTTPError")
            #     #sys.exit()
            #     return(None)
#             print(urllib.request.urlopen(URL).read())

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
                print("IOError")
                return(None)

            # merge those tiles together
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,0] = imgPatch[:,:,0]
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,1] = imgPatch[:,:,1]
            mergedImg[idx_ly:idx_uy,idx_lx:idx_ux,2] = imgPatch[:,:,2]


    # cut the mergedImg based on the original size of panorama
    cut_mergedImg = np.zeros((rowlim,collim,3),'uint8')
    cut_mergedImg[:,:,0] = mergedImg[:rowlim,:collim,0]
    cut_mergedImg[:,:,1] = mergedImg[:rowlim,:collim,1]
    cut_mergedImg[:,:,2] = mergedImg[:rowlim,:collim,2]
#     print('The size of the GSV panorama is:'+(''.join(cut_mergedImg.shape)))
    
    # img = Image.fromarray(cut_mergedImg)
    return(cut_mergedImg)




def GSVpanoramaDowloaderFromText(gsvInfoText, greenMonthList, outGSVRoot, flag):
    """
    This function is used to download the GSV panoramas from Google using
    Google API, http://cbk0.google.com/cbk?output=tile&panoid=lKxUOImSaCYAAAQIt71GFQ&zoom=5&x=0&y=0
    
    This code can parse the metadata collected from historical version

    The second step of this function is to merge all the patches together to create
    a complete panorama
    
    parameters:
        panoInfo: the metadata of the panoramas
        outGSVRoot: the output folder of the panorama images
        flag: mark if you are dowloading based on historical or not historical metadata
        historical is 1, not historical 0
    
    first version July 11, 2016, MIT Senseable City Lab. 
    """
    
    import urllib
    from PIL import Image
    import os, os.path
    import numpy as np
    
    
    if not os.path.exists(outGSVRoot):
        os.makedirs(outGSVRoot)
    
    panoIDlst = []
    pntnumList = []

    # read the GSV infor from the metadata of the GSV panorama
    lines = open(gsvInfoText, 'r')
    pntnum = 0
    for line in lines:
        # create a dictionary to record the metadata information
        pano_metaDict = {}
        
        # split the line elements twice, because the last character in the line is '\r\n'
        elements = line.split('\r')[0].split(" ")
        num_fields = int(len(elements)/2)

        for i in range(num_fields):
            field = elements[2*i][:-1]
            pano_metaDict[field] = elements[2*i+1]

        print('The dictionary is-------:', pano_metaDict)
        
        if flag >0: # historical meta
            pntnum = pano_metaDict['pntNum']
            panoId = pano_metaDict['panoID']
            year = pano_metaDict['year']
            month = pano_metaDict['month']
            lonStr = pano_metaDict['longitude']
            latStr = pano_metaDict['latitude']
            yaw = pano_metaDict['pano_yaw_degree']
        else: #non historical meta
            pntnum = pntnum + 1
            panoId = pano_metaDict['panoID']
            panoDate = pano_metaDict['panoDate']
            year = panoDate[0:4]
            month = panoDate[-2:]
            lonStr = pano_metaDict['longitude']
            latStr = pano_metaDict['latitude']
            yaw = pano_metaDict['pano_yaw_degree']

        print('month and year are', month, year)
        

        # in case of the invalid pano infor
        if len(lonStr) < 3:
            continue
        
        lon = float(lonStr)
        lat = float(latStr)
        
        # not calculate those sites have GSV images taken in nongreen season            
        if month not in greenMonthList:
            print ('-------------the GSV is not captured in green season')
            print ('The data information is :', month)
            continue
        else:
            if panoId not in panoIDlst and pntnum not in pntnumList:
                panoIDlst.append(panoId)
                pntnumList.append(pntnum)

                print ('the panoID,coordinate of thepano is:',panoId,lon,lat, yaw)
                
                # the ouput panorama name
                panoDate = year + '-' + month
                imgName = r'%s - %s - %s - %s - %s - %s.jpg'%(pntnum, panoId,lon,lat,panoDate,yaw[:-2])
                mergedImgFile = os.path.join(outGSVRoot,imgName)
                if os.path.exists(mergedImgFile): 
                    print('The GSV pano has been downloaded')
                    continue
                
                print(panoId, imgName)
                try:
                    mergedImg = GSVpanoramaDowloader_GoogleMaps(panoId, 2)
                    img = Image.fromarray(mergedImg)
                    del mergedImg
                    img.save(mergedImgFile)
                    del img
                except:
                    print('panorama collection failed')
                


def GSVpanoramaDowloader(GSVinfo, greenMonthList, outGSVRoot, flag):
    """
    This function is used to download the GSV panoramas from Google using
    Google API, http://cbk0.google.com/cbk?output=tile&panoid=lKxUOImSaCYAAAQIt71GFQ&zoom=5&x=0&y=0
    
    The second step of this function is to merge all the patches together to create
    a complete panorama
    
    parameters:
        panoInfo: the metadata of the panoramas, could be text file or folder
        greenMonthList: the list of the green month, ['06','07','08','09', '10']
        outGSVRoot: the output folder of the panorama images
        flag: mark whether you are using historical meta or regular meta, historical 1, regular 0
    First version Feb 16, 2017, MIT Senseable City Lab. 
    """
    
    import urllib
    from PIL import Image
    import os, os.path
    
    
    if not os.path.exists(outGSVRoot):
        os.makedirs(outGSVRoot)

    print ('the green mont list is:', greenMonthList)
    if os.path.isfile(GSVinfo) and GSVinfo.endswith('.txt'):
        # call the function to save the metadata as lists
        GSVpanoramaDowloaderFromText(GSVinfo, greenMonthList, outGSVRoot, flag)
    
    elif os.path.isdir(GSVinfo):
        allTxtFiles = os.listdir(GSVinfo)
        for gsvTextFile in allTxtFiles:
            gsvTextFilename = os.path.join(GSVinfo, gsvTextFile)
            GSVpanoramaDowloaderFromText(gsvTextFilename, greenMonthList, outGSVRoot, flag)



# download the GSV panoramas based on the panoid
def GSVpanoramaDowloader_GoogleMaps_indoor(panoId, gsvPanoImgFile='gsvPano.jpg'):
    """
    This function is used to download the GSV panoramas from Google using
    the URL address provided by Google Maps
    
    zoom is 0:
    https://geo2.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&gl=us&panoid=%s&output=tile&x=0&y=0&zoom=0&nbt&fover=2
    
    zoom is 1:
    https://geo0.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&panoid=iKXN73P5BhoYdBpxB973zw&output=tile&x=0&y=0&zoom=1&nbt&fover=2
    
    
    parameters:
        panoId: the panorama id
        gsvPanoImgFile: the full name of the output GSV panorama 
    
    first version March 8, 2019, Xiaojiang Li, MIT Senseable City Lab. 
    """
    
    import os,os.path
    import urllib
    from PIL import Image
    import numpy as np
    import sys
    

    # check the version of python
    version = sys.version_info[0]
    
    
    # download the GSV panoramas by specifying the parmaters    
    zoom = 2
    xNum = 3
    yNum = 2
    rowlim = 704
    collim = rowlim*2
    shift = 20

    # zoom = 3
    # xNum = 6
    # yNum = 3

    
    # merge images together to create a panorama
    widths = xNum*512
    heights = yNum*512
    
    mergedImg = np.zeros((heights,widths,3),'uint8')
    print ('The panoid is:------', panoId)
    

    for x in range(xNum):
        for y in range(yNum):
            # The URL is derived from Google Maps, check the source code of Google Maps
            URL = 'https://geo2.ggpht.com/cbk?cb_client=maps_sv.tactile&authuser=0&hl=en&gl=us&panoid=%s&output=tile&x=%s&y=%s&zoom=%s&nbt&fover=2'%(panoId, x, y, zoom)

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
    cut_mergedImg[:,:,0] = mergedImg[:rowlim,shift:collim + shift,0]
    cut_mergedImg[:,:,1] = mergedImg[:rowlim,shift:collim + shift,1]
    cut_mergedImg[:,:,2] = mergedImg[:rowlim,shift:collim + shift,2]
    print ('The size of the GSV panorama is:',cut_mergedImg.shape)
    
    img = Image.fromarray(cut_mergedImg)
    # mergedImgFile = os.path.join(outGSVRoot,panoId+'.jpg')
    img.save(gsvPanoImgFile)
    del img,mergedImg
    
    return cut_mergedImg
    


# Main function
if __name__=="__main__":
    GSVinfo = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Cleaned_Pnt_start0_end1000.txt'
    outGSVRoot = r'/Users/senseablecity/Dropbox (MIT)/Start-up/testpano'
    greenMonthList = ['05', '06', '07', '08', '09']
    # GSVpanoramaDowloader(GSVinfo, greenMonthList, outGSVRoot)
    
    
    ## ------ Dash + AI for Massachusetts Avenue-----------
    GSVinfo = r'/Users/senseablecity/Dropbox (MIT)/Start-up/street-right/metadata/Cleaned_Pnt_start0_end321.txt'
    outGSVRoot = r'/Users/senseablecity/Dropbox (MIT)/Start-up/street-right/visualization/GSV-Mass-avenue-zoom2'
    greenMonthList = ['05', '06', '07', '08', '09', '10']
    GSVpanoramaDowloader(GSVinfo, greenMonthList, outGSVRoot)
    
