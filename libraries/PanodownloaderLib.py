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
    print ('The size of the GSV panorama is:',cut_mergedImg.shape)
    
    img = Image.fromarray(cut_mergedImg)
    # mergedImgFile = os.path.join(outGSVRoot,panoId+'.jpg')
    img.save(gsvPanoImgFile)
    del img,mergedImg
    
    return cut_mergedImg
    


# download the GSV panoramas based on the panoid
def GSVpanoramaDowloader_GoogleMaps_indoor(panoId, gsvPanoImgFile='gsvPano.jpg'):
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
    