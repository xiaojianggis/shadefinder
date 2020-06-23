
# This code is used to test the algorithm online to get the historical GSV
# data based on "https://github.com/robolyst/streetview"
# First version, June 19th, 2017, MIT Senseable City Lab

def _panoids_url(lat, lon):
    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e2!6m1!1e2&callback=_xdc_._v2mub5"
    return url.format(lat, lon)
    
    
def _panoids_data(lat, lon):
    """
    Gets the response of the script on Google's servers that returns the
    closest panoramas (ids) to a give GPS coordinate.
    """
    # import urllib2
    import sys

    url = _panoids_url(lat, lon)

    # using different url reading method in python2 and python3
    if sys.version_info[0] == 2:
        # from urllib2 import urlopen
        import urllib
        
        metaData = urllib.urlopen(url).read()
        
    if sys.version_info[0] == 3:
        import urllib.request
        
        request = urllib.request.Request(url)
        metaData = urllib.request.urlopen(request).read()
    
    
    # metaDataxml = urllib2.urlopen(url)
    # metaData = metaDataxml.read()
##    return requests.get(url)
    return metaData.decode('utf-8')
    
    
def panoids(lat, lon, closest=False, disp=False):
    """
    Gets the closest panoramas (ids) to the GPS coordinates.
    If the 'closest' boolean parameter is set to true, only the closest panorama
    will be gotten (at all the available dates)
    """
    import re
    from datetime import datetime
    import requests
    import time
    
    resp = _panoids_data(lat, lon)
    
    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    
    # print(resp)

##    pans = re.findall('\[[0-9],"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+).\].+?\[(-?[0-9]+.[0-9]+).\].+?\[(-?[0-9]+\.?[0-9]+)', resp.text)    
    pans = re.findall('\[[0-9],"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+).\].+?\[(-?[0-9]+.[0-9]+).\].+?\[(-?[0-9]+\.?[0-9]+)', resp)
    
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2]),
        "yaw": float(p[4])} for p in pans] # Convert to floats
        
    if disp:
        for pan in pans:
            print(pan)
    
    # Get all the dates
    # The dates seem to be at the end of the file. They have a strange format but
    # are in the same order as the panoids except that the latest date is last
    # instead of first. They also appear to have the index of the panorama before
    # them. However, the last date (which corresponds to the first/main panorama
    # doesn't have an index before it. The following regex just picks out all
    # values that looks like dates and the preceeding index.
##    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', resp.text)
    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', resp)

    dates = [list(d) for d in dates]
    
    
    # Make sure the month value is between 1-12
    dates = [d for d in dates if int(d[2]) <= 12 and int(d[2])>=1]
    
    # Make the first value of the dates the index
    if len(dates) > 0 and dates[-1][0] == '':
        dates[-1][0] = '0'
    dates = [[int(v) for v in d] for d in dates] # Convert all values to integers
    
    # Merge the dates into the panorama dictionaries
    npano = len(pans)
    for i, year, month in dates:
        if i > npano - 1: continue  # go over the limit
        pans[i].update({'year': year, "month": month})
    	
    
    # Sort the pans array
    def func(x):
        if 'year'in x:
            return datetime(year=x['year'], month=x['month'], day=1)
        else:
            return datetime(year=3000, month=1, day=1)
    
    pans.sort(key=func)
    
    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans
    
    

def tiles_info(panoid):
    """
    Generate a list of a panorama's tiles and their position.
    The format is (x, y, filename, fileurl)
    """
    
    image_url = "http://cbk0.google.com/cbk?output=tile&panoid={0:}&zoom=5&x={1:}&y={2:}"
    
    # The tiles positions
    coord = list(itertools.product(range(26),range(13)))
    
    tiles = [(x, y, "%s_%dx%d.jpg" % (panoid, x, y), image_url.format(panoid, x, y)) for x,y in coord]

    return tiles
    

def meta4coord(lon, lat):
    '''
    This function is used to get the panorama info using coordinate as the input
    This funcion is applicable on both Python2 and Python3
    last modified Dec 21, 2018 by Xiaojiang Li, MIT Senseable City Lab
    
    Input:
        lon: 
        lat: 
    Ouput:
        
        [panoDate, panoId, pano_yaw_degree]
    '''
    
    import sys
    import time
    import xmltodict
    
    # get the meta data of panoramas using lon and lat as input
    urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s'%(lat,lon)
    
    time.sleep(1)
    
    # using different url reading method in python2 and python3
    if sys.version_info[0] == 2:
        # from urllib2 import urlopen
        import urllib
        
        metaData = urllib.urlopen(urlAddress).read()
        
    if sys.version_info[0] == 3:
        import urllib.request
        
        request = urllib.request.Request(urlAddress)
        metaData = urllib.request.urlopen(request).read()
    
    
    data = xmltodict.parse(metaData)
    # print (data)
    
    # in case there is not panorama in the site, therefore, continue
    if data['panorama']==None:
        print('The site has not GSV panorama available')
        panoDate = None
        panoId = None
        panoLat = None
        panoLon = None
        pano_yaw_degree = None
        # continue
    else:
        panoInfo = data['panorama']['data_properties']

        # get the meta data of the panorama
        panoDate = panoInfo['@image_date']
        panoId = panoInfo['@pano_id']
        panoLat = panoInfo['@lat']
        panoLon = panoInfo['@lng']
        pano_yaw_degree = panoInfo['@best_view_direction_deg']
        
    return panoId, panoDate, pano_yaw_degree
    


def GSVpanoMetadataCollectorBatch_Yaw(samplesFeatureClass,num,ouputTextFolder):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the text file

    /// No historical pano info
    /// This function also include the yaw angle of the GSV panorama included in the returned txt file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    
    import urllib,urllib2
    import xmltodict
    # import cStringIO
    import ogr, osr
    import time
    import os,os.path
    
    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    # change the projection of shapefile to the WGS84
    dataset = driver.Open(samplesFeatureClass)
    layer = dataset.GetLayer()
    
    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)
    
    # loop all the features in the featureclass
    feature = layer.GetNextFeature()
    featureNum = layer.GetFeatureCount()
    batch = featureNum/num + 1
    
    print ('The batch size is:', batch)


    for b in range(batch):
        # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum
        
        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)
        
        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue
        
        time.sleep(1)
        
        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer.GetFeature(i)        
                geom = feature.GetGeometryRef()
                
                # trasform the current projection of input shapefile to WGS84
                #WGS84 is Earth centered, earth fixed terrestrial ref system
                geom.Transform(transform)
                lon = geom.GetX()
                lat = geom.GetY()
                key = r'' #Input Your Key here 
                
                # get the meta data of panoramas 
                urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s'%(lat,lon)
                
                time.sleep(0.05)
                
                # the output result of the meta data is a xml object
                try: 
                    metaDataxml = urllib2.urlopen(urlAddress)
                    metaData = metaDataxml.read()    
                    
                    data = xmltodict.parse(metaData)
                    
                    # in case there is not panorama in the site, therefore, continue
                    if data['panorama']==None:
                        continue
                    else:
                        panoInfo = data['panorama']['data_properties']
                        
                        # get the meta data of the panorama
                        panoDate = panoInfo.items()[4][1]
                        panoId = panoInfo.items()[5][1]
                        panoLat = panoInfo.items()[8][1]
                        panoLon = panoInfo.items()[9][1]
                        
                        # get the pano_yaw_degree
                        pano_yaw_degree = data['panorama']['projection_properties'].items()[1][1]
                        tilt_yaw_deg = data['panorama']['projection_properties'].items()[2][1]
                        tilt_pitch_deg = data['panorama']['projection_properties'].items()[3][1]
                        
                        print (pano_yaw_degree, tilt_yaw_deg, tilt_pitch_deg)
                        
                        print ('The coordinate (%s,%s), panoId is: %s, panoDate is: %s'%(panoLon,panoLat,panoId, panoDate))
                        lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s pano_yaw_degree: %s tilt_yaw_deg: %s tilt_pitch_deg: %s\n'%(panoId, panoDate, panoLon, panoLat, pano_yaw_degree, tilt_yaw_deg, tilt_pitch_deg)
                        panoInfoText.write(lineTxt)
                        
                except:
                    continue
                    
        panoInfoText.close()


        # # ------------Main Function -------------------    
        # import os,os.path

        # root = '/Users/senseablecity/Dropbox (MIT)/ResearchProj/Treepedia/VancoverProj-UBC/SpatialData'
        # inputShp = os.path.join(root,'VancouverMetro100mOutskirt.shp')
        # outputTxt = os.path.join(root, 'metadata')

        # GSVpanoMetadataCollectorBatch_Yaw(inputShp,1000,outputTxt) 


# Fiona based method, not use gdal
def GSVpanoMetadataCollectorBatch_Yaw_fiona(samplesFeatureClass,num,ouputTextFolder):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the text file

    /// No historical pano info
    /// This function also include the yaw angle of the GSV panorama included in the returned txt file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    
    import xmltodict
    import sys
    import time
    import os,os.path
    import fiona
    
    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)
    
    dataset = fiona.open(samplesFeatureClass)
    
    featureNum = len(list(dataset))    
    batch = int(featureNum/num) + 1
    
    print ('The batch size is:', batch)

    for b in range(batch):
        # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum
        
        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)
        
        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue
        
        time.sleep(1)
        
        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                
                feature = dataset[i]       
                coord = feature['geometry']['coordinates']
                lon = coord[0]
                lat = coord[1]

                # get the meta data of panoramas 
                urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s'%(lat,lon)
                
                time.sleep(0.05)
                
                # the output result of the meta data is a xml object
                # try: 
                print('judge python version')
                # using different url reading method in python2 and python3
                if sys.version_info[0] == 2:
                    # from urllib2 import urlopen
                    import urllib
                    
                    metaData = urllib.urlopen(urlAddress).read()
                    
                if sys.version_info[0] == 3:
                    import urllib.request
                    
                    request = urllib.request.Request(urlAddress)
                    metaData = urllib.request.urlopen(request).read()

                
                data = xmltodict.parse(metaData)
                
                # in case there is not panorama in the site, therefore, continue
                if data['panorama']==None:
                    continue
                else:
                    panoInfo = data['panorama']['data_properties']
                    
                    # get the meta data of the panorama
                    panoDate = panoInfo['@image_date']
                    panoId = panoInfo['@pano_id']
                    panoLat = panoInfo['@lat']
                    panoLon = panoInfo['@lng']
                    
                    # get the pano_yaw_degree
                    pano_yaw_degree = data['panorama']['projection_properties']['@pano_yaw_deg']
                    tilt_yaw_deg = data['panorama']['projection_properties']['@tilt_yaw_deg']
                    tilt_pitch_deg = data['panorama']['projection_properties']['@tilt_pitch_deg']
                    
                    print (pano_yaw_degree, tilt_yaw_deg, tilt_pitch_deg)
                    
                    print ('The coordinate (%s,%s), panoId is: %s, panoDate is: %s'%(panoLon,panoLat,panoId, panoDate))
                    lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s pano_yaw_degree: %s tilt_yaw_deg: %s tilt_pitch_deg: %s\n'%(panoId, panoDate, panoLon, panoLat, pano_yaw_degree, tilt_yaw_deg, tilt_pitch_deg)
                    panoInfoText.write(lineTxt)
                        
                # except:
                #     print('You run error')
                #     continue
                    
        panoInfoText.close()



def GSVpanoMetadataCollector_Yaw_TimeMachine_shpfilebased(FeatureClass,outputFeatureClass):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the same shapefile
    
    /// This function also include the yaw angle of the GSV panorama included in the returned txt file
    
    Parameters: 
        FeatureClass: the shapefile of the create sample sites
        outputFeatureClass: the output shapefile with the GSV metadata
    '''
    
    import urllib,urllib2
    import xmltodict
    import cStringIO
    import ogr, osr
    import time
    import os,os.path
    
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    # change the projection of shapefile to the WGS84
    dataset = driver.Open(FeatureClass)
    layer = dataset.GetLayer()
    
    # get the projection of the shapefile
    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)
    
    # create a new shapefile based on the current feature, and save the gsv metadata in it
    if os.path.exists(outputFeatureClass):
        os.remove(outputFeatureClass)
    data_source = driver.CreateDataSource(outputFeatureClass)
    
    # define the spatial reference system of the created shapefile
    targetSpatialRef = osr.SpatialReference()
    targetSpatialRef.ImportFromEPSG(4326)
    outLayer = data_source.CreateLayer("randomPnt", targetSpatialRef, ogr.wkbPoint)
    
    # record all the field list
    fieldNameList = []
    
    # get the fields of the input shapefile and add to the outputshapefile
    layerDefinition = layer.GetLayerDefn()
    for i in range(layerDefinition.GetFieldCount()):
        fieldName = layerDefinition.GetFieldDefn(i).GetName()
        fieldNameList.append(fieldName)
        fieldDefinition = layerDefinition.GetFieldDefn(i)
        print ('The filedName and the fieldDefinition are:', fieldName)
        outLayer.CreateField(fieldDefinition)
    
    if 'pntNum' not in fieldNameList:
        outLayer.CreateField(ogr.FieldDefn('pntNum', ogr.OFTInteger))
    
    # create fields to save the gsv metadata
    outLayer.CreateField(ogr.FieldDefn('panoid', ogr.OFTString))
    outLayer.CreateField(ogr.FieldDefn('lon', ogr.OFTReal))
    outLayer.CreateField(ogr.FieldDefn('lat', ogr.OFTReal))
    outLayer.CreateField(ogr.FieldDefn('year', ogr.OFTString))
    outLayer.CreateField(ogr.FieldDefn('month', ogr.OFTString))
    outLayer.CreateField(ogr.FieldDefn('yaw', ogr.OFTReal))
    
    # loop all the features in the featureclass
    feature = layer.GetNextFeature()
    featureNum = layer.GetFeatureCount()
    
    # loop all features in the layer
    for i in range(featureNum):
        feature = layer.GetFeature(i)
        geom = feature.GetGeometryRef()
        geom.Transform(transform)
        lon = geom.GetX()
        lat = geom.GetY()
        
        # define a new feature        
        featureDefn = outLayer.GetLayerDefn()
        feature_new = ogr.Feature(featureDefn)
        
        # copy the geometry of input feature to outputfeature
        geom_new = feature.GetGeometryRef()
        feature_new.SetGeometry(geom_new)
        
        # loop all fields and copy attribute from the input feature to outputfeature
        for field in fieldNameList:
            # get the field attribute from the input shapefile
            attribute = feature.GetField(field)
            
            # assign the attribute to the new field, copy
            feature_new.SetField(field,attribute)

        # call the function to get historical gsv panoramas metadata
        time.sleep(0.05)
        try:
            res = panoids(lat,lon)
            
            count = 0 # count how many panorama ids
            for j in range(len(res)):
                if res[j].has_key("year"):
                    count = count + 1
                    panoid = res[j]["panoid"]
                    panoLon = res[j]["lon"]
                    panoLat = res[j]["lat"]
                    pano_yaw_degree = res[j]["yaw"]
                    year = str(res[j]["year"])
                    month = res[j]["month"]
                    if month<10: month = '0' + str(month)
                    
                    # set the GSV metadata to the generated shapefile
                    feature_new.SetField('pntNum', i)
                    feature_new.SetField('panoid', panoid)
                    feature_new.SetField('lon', panoLon)
                    feature_new.SetField('lat', panoLat)
                    feature_new.SetField('yaw', pano_yaw_degree)
                    feature_new.SetField('year', year)
                    feature_new.SetField('month', month)
                    
                    outLayer.CreateFeature(feature_new)
                    # print 'The collected metadata is:',i, panoid,panoLon,panoLat,pano_yaw_degree,year,month
                    
                    time.sleep(0.05)
            print ('This point (%s,%s) has %d panorama ids'%(panoLon,panoLat,count))
            
            
            feature_new.Destroy()
        
        except:
            continue
            print('no pano available')

    data_source.Destroy()
    


def GSVpanoMetadataCollectorBatch_Yaw_TimeMachine(samplesFeatureClass,num,ouputTextFolder):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The historical panorama ID will also be collected
    by this code, based on Adrian Letchford's code 
    
    /// This function also include the yaw angle of the GSV panorama included in the returned txt file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    
    import urllib,urllib2
    import xmltodict
    import ogr, osr
    import time
    import os,os.path
    
    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    # change the projection of shapefile to the WGS84
    dataset = driver.Open(samplesFeatureClass)
    layer = dataset.GetLayer()
    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)
    
    # loop all the features in the featureclass
    feature = layer.GetNextFeature()
    featureNum = layer.GetFeatureCount()
    batch = int(featureNum/num + 0.5)
    

    for b in range(batch):
        # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum
        
        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        # print '------------', ouputTextFile
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)
        
        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue
        
        time.sleep(1)
        
        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer.GetFeature(i)        
                geom = feature.GetGeometryRef()
                
                # trasform the current projection of input shapefile to WGS84
                geom.Transform(transform)
                lon = geom.GetX()
                lat = geom.GetY()
                
                try:
                    res = panoids(lat,lon)
                    count = 0 # count how many panorama ids
                    for j in range(len(res)):
                        if res[j].has_key("year"):
                            count = count + 1
                            panoid = res[j]["panoid"]
                            panoLon = res[j]["lon"]
                            panoLat = res[j]["lat"]
                            pano_yaw_degree = res[j]["yaw"]
                            year = str(res[j]["year"])
                            month = res[j]["month"]
                            if month<10: month = '0' + str(month)
                            
                            lineTxt = 'pntNum: %d panoID: %s year: %s month: %s longitude: %s latitude: %s pano_yaw_degree: %s\n'%(i, panoid, year, month, panoLon, panoLat, pano_yaw_degree)
                            #print lineTxt                                                                             
                            
                            time.sleep(0.05)
                            panoInfoText.write(lineTxt)
                    print ('This point (%s,%s) has %d panorama ids'%(panoLon,panoLat,count))
                except:
                    print('no pano availalbe')
                    continue
                    
        panoInfoText.close()
        



# Using Fiona not gdal
def GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(samplesFeatureClass,num,ouputTextFolder):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The historical panorama ID will also be collected
    by this code, based on Adrian Letchford's code 
    
    /// This function also include the yaw angle of the GSV panorama included in the returned txt file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    
    import xmltodict
    import time
    import os,os.path
    import fiona
    import sys

    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)
    
    # change the projection of shapefile to the WGS84
    dataset = fiona.open(samplesFeatureClass)
    print('len(list(data))', len(list(dataset)))
    
    
    # loop all the features in the featureclass
    featureNum = len(list(dataset))
    batch = int(featureNum/num) + 1
    
    
    for b in range(batch):
        print('process batch: ', b)
        # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum
        
        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        # print '------------', ouputTextFile
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)
        
        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            print('The file exists: ', ouputGSVinfoFile)
            continue
        
        time.sleep(1)
        
        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                if i % 100== 0: print('reaching: ', i)
                feature = dataset[i]       
                coord = feature['geometry']['coordinates']
                lon = coord[0]
                lat = coord[1]

                # get the metadata of GSV panorama
                try:
                    res = panoids(lat,lon)

                    # parse the metadata and save the results to txt files
                    if len(res) < 1: continue

                    count = 0 # count how many panorama ids
                    for j in range(len(res)):

                        # using different url reading method in python2 and python3
                        if sys.version_info[0] == 2:
                            # from urllib2 import urlopen
                            has_year_key = res[j].has_key("year")
                            
                        if sys.version_info[0] == 3:
                            has_year_key = 'year' in res[j]

                        if has_year_key:
                            count = count + 1
                            panoid = res[j]["panoid"]
                            panoLon = res[j]["lon"]
                            panoLat = res[j]["lat"]
                            pano_yaw_degree = res[j]["yaw"]
                            year = str(res[j]["year"])
                            month = res[j]["month"]
                            if month<10: month = '0' + str(month)
                            
                            lineTxt = 'pntNum: %d panoID: %s year: %s month: %s longitude: %s latitude: %s pano_yaw_degree: %s\n'%(i, panoid, year, month, panoLon, panoLat, pano_yaw_degree)
                            #print lineTxt                                                                             
                            
                            time.sleep(0.05)
                            panoInfoText.write(lineTxt)
                    print ('This point (%s,%s) has %d panorama ids'%(panoLon,panoLat,count))
                
                except:
                    continue
                    print('no pano available')

        panoInfoText.close()
  


## Read the txt file and save it as shpfile
def Read_GSVinfo_Text(GSVinfoText):
    '''
    This function is used to read the information in text files or folders
    The function will judge by the content of the txt file and create different
    lists to save the different data
    
    Return:
        lists of the data in the txt files
    
    Pamameters: 
        GSVinfoText: the file name of the GSV information text
    
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab June 21st, 2017
    
    '''
    
    import os,os.path
    
    # create a list to save the gsv metadata
    gsvInfoLst = []
    
    if os.path.isfile(GSVinfoText) and GSVinfoText.endswith('.txt'):
        lines = open(GSVinfoText,"r")
        
        for line in lines:
            elements = line.split(" ")
            fieldNum = len(elements)/2            
            newEle = {elements[2*i][:-1]:elements[2*i+1] for i in range(fieldNum)} 
            if newEle not in gsvInfoLst:
                gsvInfoLst.append(newEle)
    
#     print 'The length of the list is:', len(gsvInfoLst)
    return gsvInfoLst
    


def Read_GSVinfo_Text_File2Folder(GSVinfoText):
    '''
    This function is used to read the information in text files or folders
    The function will judge by the content of the txt file and create different
    lists to save the different data
    
    Return:
        lists of the data in the txt files
    
    Pamameters: 
        GSVinfoText: the file name of the GSV information text
    
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab June 21st, 2017
    
    '''
    import os, os.path
    
    if os.path.isfile(GSVinfoText):
        gsvInfoLst = Read_GSVinfo_Text(GSVinfoText)
    elif os.path.isdir(GSVinfoText):
        gsvInfoLst = []
        for infofile in os.listdir(GSVinfoText):
            infofileName = os.path.join(GSVinfoText,infofile)
            gsvInfoLstTemp = Read_GSVinfo_Text(infofileName)
            gsvInfoLst.extend(gsvInfoLstTemp)
            print ('The length is:',len(gsvInfoLst))
    
    print ('The lengh of the list is:', len(gsvInfoLst))
    return gsvInfoLst
    


def metadataCleaning (MetadataTxt, cleanedMetadataFolder):
    '''
    This script is used to clean the metadata collected from historyMetadata code
    the historical metadata include several sites for one point, we need select one
    site for a specific point, we may only need some specific seasons data
    First Version Feb 28, 2018
    last modified by Xiaojiang Li, MIT Senseable City Lab
    
    parameters:
        MetadataTxt: the input metadata txt file or folder
        cleanedMetadataFolder: the output folder of the cleaned metadata
    '''
    
    import os,os.path
    import sys
    
    # get the basename and formulate the output name
    basename = os.path.basename(MetadataTxt)
    if not os.path.exists(cleanedMetadataFolder):
        os.mkdir(cleanedMetadataFolder)
    cleanedMetadataTxt = os.path.join(cleanedMetadataFolder, 'Cleaned_'+basename)
    
    # write to the output cleaned folder
    with open(cleanedMetadataTxt, 'w') as panoInfoText:
        # the metadata of the GSV panorama
        lines = open(MetadataTxt,"r")
        
        # panonum list, used to select only one pano for one site
        panonumlist = []
        panolonlist = []
        panolatlist = []
        panoidlist = []
        
        # loop all the panorama records
        for line in lines:
            elements = line.split(' ')
            pntnum = elements[1]
            panoid = elements[3]
            panoyear = elements[5]
            panomonth = elements[7]
            panodate = panoyear + '-' + panomonth

            panolon = float(elements[9])
            panolat = float(elements[11])
            hyaw = float(elements[13])
            vyaw = float(elements[15])

            print ('panid, panodata, lon, lat, hyaw, vyaw', panoid, panoyear, panomonth, panolon, panolat, hyaw, vyaw)
            
            # for the leaf on seasons, could change to other seasons
            if panomonth not in ['06', '07', '08', '09', '10'] or panoyear == '2007':
                continue
                
            # calculate the sun glare for leaf-on season
            if pntnum not in panonumlist and panoid not in panoidlist:
                panonumlist.append(pntnum)
                panoidlist.append(panoid)

                lineTxt = 'pntnum: %s panoID: %s panoDate: %s longitude: %s latitude: %s pano_yaw_degree: %s tilt_pitch_deg: %s\n'%(pntnum, panoid, panodate, panolon, panolat, hyaw, vyaw)
                panoInfoText.write(lineTxt)
    
    panoInfoText.close()



# # Main function, example
# import os,os.path

# root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/sunglare-pano'
# MetadatTxt = os.path.join(root,'Pnt_start0_end1000.txt')
# MetadatTxt = os.path.join(root,'Pnt_start1000_end2000.txt')
# cleanedMetadatTxt = os.path.join(root, 'cleanedMetadata')
# metadataCleaning (MetadatTxt, cleanedMetadatTxt)



def metadataCleaning_winter_summer_txt (MetadataTxt, cleanedMetadataFolder):
    '''
    This script is used to clean the metadata collected from historyMetadata code
    the historical metadata include several sites for one point, we need select one
    site for a specific point, we may only need some specific seasons data
    First Version Feb 28, 2018
    last modified by Xiaojiang Li, MIT Senseable City Lab
    
    modified by Xiaojiang Li, May 9, 2018

    parameters:
        MetadataTxt: the input metadata txt file or folder
        cleanedMetadataFolder: the output folder of the cleaned metadata
    '''

    import os,os.path
    import sys
    
    # get the basename and formulate the output name
    basename = os.path.basename(MetadataTxt)
    if not os.path.exists(cleanedMetadataFolder):
        os.mkdir(cleanedMetadataFolder)
    cleanedMetadataTxt = os.path.join(cleanedMetadataFolder, 'Cleaned_'+basename)
    print ('The output is:', cleanedMetadataTxt)

    if os.path.exists(cleanedMetadataTxt): return

    # write to the output cleaned folder
    with open(cleanedMetadataTxt, 'w') as panoInfoText:
        txtlist = MetadataTxt.split("_end")

        # create an empty list of the panorama id, to guratee there is no duplicate panorama
        panoidlist = []

        # the point number of the txt file
        startPnt = int(txtlist[0].split("Pnt_start")[1])
        endPnt = int(txtlist[1][:-4])

        # print (startPnt, endPnt)
        print (MetadataTxt)

        for i in range (startPnt, endPnt):
            iLine_list = []
            w_pntnum_list = [] # mark the winter pntnum list
            s_pntnum_list = [] # mark as the summer pntnum list

            # the metadata of the GSV panorama
            lines = open(MetadataTxt,"r")

            # loop all panorama records
            for line in lines:
                try:
                    elements = line.split(' ')
                    pntnum = int(elements[1])

                    # add the line for pnt i to the list
                    if pntnum==i:
                        iLine_list.append(line)
                except:
                    continue

            # count the number of panorama in point number i
            pnt_pano_number = len(iLine_list)
            # print 'the number of point at %s is %s' %(i, pnt_pano_number)

            # if there is no panorama availalbe, then skip
            if pnt_pano_number < 1:
                continue
            elif pnt_pano_number == 1: # if there is only one panorama then save this pano info
                panoInfoText.write(iLine_list[0])
                w_pntnum_list.append(i)
                s_pntnum_list.append(i)
            else:

                # temprary variables, used to find the most recent pano
                newpanoyear_w = 2007
                newpanoyear_s = 2007

                # there is more than one pano available, loop all the panoramas for point number i
                for iline in iLine_list:
                    elements = iline.split(' ')
                    panoid = elements[3]
                    try: 
                        panoyear = int(elements[5])
                        panomonth = elements[7]
                    except: 
                        continue

                    insertLine = iline

                    # for the leaf off seasons, keep one panorama, using the most recent image
                    if i not in w_pntnum_list and panomonth in ['11', '12', '01', '02', '03', '04'] and panoyear > 2008:
                        w_pntnum_list.append(i)
                        if panoyear > newpanoyear_w:
                            newpanoyear_w = panoyear
                            insertLine = iline

                        panoInfoText.write(insertLine)
                        
                        # print ('You have added one winter panorama')
                        continue
                    
                    # for leaf on seasons, keep one panorama, using the most recent image
                    if i not in s_pntnum_list and panomonth in ['05','06', '07', '08', '09', '10'] and panoyear > 2008: 
                        
                        s_pntnum_list.append(i)

                        if panoyear > newpanoyear_s: 
                            newpanoyear_s = panoyear
                            insertLine = iline

                        panoInfoText.write(insertLine)
                        # print ('You have added one summer panorama===========')
                        continue            

    panoInfoText.close()



def metadataCleaning_winter_summer (Metadata, cleanedMetadataFolder):
    '''
    This script is used to clean the metadata collected from historyMetadata code
    input txtfile/folder output as folder
    
    modified by Xiaojiang Li, May 9, 2018
    
    parameters:
        MetadataFolder: the input metadata file or folder
        cleanedMetadataFolder: the output folder of the cleaned metadata
    '''

    import os,os.path
    import sys
    
    # the input is a folder
    if os.path.isdir(Metadata):
        print ('This is a directory')
        for file in os.listdir(Metadata):
            if not file.endswith('.txt'): continue
            filename = os.path.join(Metadata, file)
            # metadataCleaning_txt (filename, cleanedMetadataFolder)
            metadataCleaning_winter_summer_txt(filename, cleanedMetadataFolder)
    
    elif os.path.isfile(Metadata) and Metadata.endswith('.txt'): # the input is a file
        # metadataCleaning_txt (Metadata, cleanedMetadataFolder)
        print ('---------------------', Metadata)
        metadataCleaning_winter_summer_txt(Metadata, cleanedMetadataFolder)

    else:
        return



# This code is used to get the GSV data collected in different seasons, 
# Winter in Boston is defined as Nov, Dec, Jan, Feb, March, April
# Summer is the rest month
def Seasonal_GSVmetadata_extraction (MetadataTxt, monthlist, cleanedMetadataFolder):
    '''
    This script is used to extract the GSV panoramas collected from historyMetadata code
    the historical metadata include several sites for one point, we need select one
    site has GSV panoramas captured in winter for a specific point, we may only need 
    some specific seasons data
    First Version March 20, 2018
    last modified by Xiaojiang Li, MIT Senseable City Lab
    
    parameters:
        MetadataTxt: the input metadata txt file or folder
        monthlist: the month list of the image you want to get 
        cleanedMetadataFolder: the output folder of the cleaned metadata
    '''

    import os,os.path
    import sys


    # get the basename and formulate the output name
    basename = os.path.basename(MetadataTxt)
    if not os.path.exists(cleanedMetadataFolder):
        os.mkdir(cleanedMetadataFolder)
    cleanedMetadataTxt = os.path.join(cleanedMetadataFolder, 'Extracted_' + basename)

    # write to the output cleaned folder
    with open(cleanedMetadataTxt, 'w') as panoInfoText:
        # the metadata of the GSV panorama
        lines = open(MetadataTxt,"r")
        
        # panonum list, used to select only one pano for one site
        panonumlist = []
        panolonlist = []
        panolatlist = []
        panoidlist = []
        
        # loop all the panorama records
        for line in lines:
            elements = line.split(' ')
            pntnum = elements[1]
            panoid = elements[3]
            panoyear = elements[5]
            panomonth = elements[7]
            panodate = panoyear + '-' + panomonth

            panolon = float(elements[9])
            panolat = float(elements[11])
            hyaw = float(elements[13])
            vyaw = float(elements[15])

            print ('panid, panodata, lon, lat, hyaw, vyaw', panoid, panoyear, panomonth, panolon, panolat, hyaw, vyaw)
            
            # for the leaf on seasons, could change to other seasons
            if panomonth not in monthlist or panoyear == '2007':
                continue
            
            # calculate the sun glare for leaf-on season
            if pntnum not in panonumlist and panoid not in panoidlist:
                panonumlist.append(pntnum)
                panoidlist.append(panoid)

                lineTxt = 'pntnum: %s panoID: %s panoDate: %s longitude: %s latitude: %s pano_yaw_degree: %s tilt_pitch_deg: %s\n'%(pntnum, panoid, panodate, panolon, panolat, hyaw, vyaw)
                panoInfoText.write(lineTxt)

    panoInfoText.close()


# # Main function, example
# import os,os.path

# root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/sunglare-pano'
# MetadatTxt = os.path.join(root,'Pnt_start0_end1000.txt')
# MetadatTxt = os.path.join(root,'Pnt_start1000_end2000.txt')
# cleanedMetadatTxt = os.path.join(root, 'cleanedMetadata')
# monthlist = ['11', '12', '01', '02', '03', '04']
# Seasonal_GSVmetadata_extraction (MetadatTxt, monthlist, cleanedMetadatTxt)



def CreatePointFeature_ogr(outputShapefile,gsvInfoLst):
    """
    Create a shapefile based on the template of inputShapefile
    This function will delete existing outpuShapefile and create a new
    
    Parameters:
      outputShapefile: the ouput shapefile name
      gsvInfoLst: the list of the metadata, lon and lat are included
    
    Examples:
    
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab, June 22ed, 2017
    
    """
    
    import ogr
    import osr
    import re
    import os,os.path
    
    # create shapefile and add the above chosen random points to the shapfile
    driver = ogr.GetDriverByName("ESRI Shapefile")
    
    # create new shapefile
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    data_source = driver.CreateDataSource(outputShapefile)
    
    targetSpatialRef = osr.SpatialReference()
    targetSpatialRef.ImportFromEPSG(4326)
    
    outLayer = data_source.CreateLayer("randomPnt", targetSpatialRef, ogr.wkbPoint)
    
    numPnt = len(gsvInfoLst)
    print ('the number of points is:',numPnt)
    
    
    if numPnt > 0:
        # create fields
        fieldLst = gsvInfoLst[0].keys()
        
        for field in fieldLst:
            if field == 'pntNum' or field == 'year' or field == 'duration' or field == 'risedur' or field == 'setdur':
                outLayer.CreateField(ogr.FieldDefn(field, ogr.OFTInteger))
            elif field == 'pano_yaw_degree': #the name is too long
                outLayer.CreateField(ogr.FieldDefn("yaw", ogr.OFTReal))
            elif field == 'tilt_pitch_deg': #the name is too long
                outLayer.CreateField(ogr.FieldDefn("tilt", ogr.OFTReal))
            # elif field == 'longitude' or field == 'latitude':
            #     outLayer.CreateField(ogr.FieldDefn(field, ogr.OFTReal))
            # elif field == 'duration' or field == 'risedur' or field == 'setdur':
            #     outLayer.CreateField(ogr.FieldDefn(field, ogr.OFTReal))
            else:
                fieldname = ogr.FieldDefn(field, ogr.OFTString)
                outLayer.CreateField(fieldname)
                
                
        for info in gsvInfoLst:
            #create point geometry
            point = ogr.Geometry(ogr.wkbPoint)
            
            # in case of the returned panoLon and PanoLat are invalid            
            if type(info["longitude"]) is str:
                print ('This is a string------------------')
                if len(info["longitude"]) < 3:
                    continue
            
            point.AddPoint(float(info["longitude"]),float(info["latitude"]))
            
            # Create the feature and set values
            featureDefn = outLayer.GetLayerDefn()
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(point)
            
            for field in fieldLst:
                # print ('The field name is ------------------:', field)

                if field == 'pntNum' or field == 'year':
                    outFeature.SetField(field, int(info[field]))
                elif field == 'pano_yaw_degree':
                    outFeature.SetField("yaw", float(info[field]))
                elif field == 'tilt_pitch_deg':
                    outFeature.SetField("tilt", float(info[field]))
                else:
                    # print ('The field is:', field, info[field])
                    outFeature.SetField(field, str(info[field]))
            
            outLayer.CreateFeature(outFeature)
            
            outFeature.Destroy()
        data_source.Destroy()
    else:
        print ('You create a empty shapefile')




def tst(*args,**kargs):
    print (len(args))
    print (args[0])
    print (args[1])

tst(12,3,4,5)



#### ------------------- The Main Function -------------------------
if __name__ == "__main__":
    import re
    from datetime import datetime
    import requests
    import time
    import shutil
    import itertools
    from PIL import Image
    from io import BytesIO
    import os


    ##root = r'/Users/xiaojiang/Documents/GSVproj/TreepediaMac/CambridgeProj'
    ##samplesFeatureClass = os.path.join(root,'SpatialData/CambridgePnt20m.shp')
    ##ouputTextFolder = os.path.join(root,'CambridgeMetadata20mHistorical')
    ##num = 1000
    ##GSVpanoMetadataCollectorBatch_Yaw_TimeMachine(samplesFeatureClass,num,ouputTextFolder)
    
    
    root = r'/Users/xiaojiang/Documents/GSVproj/TreepediaMac/CambridgeProj'
    metadata = os.path.join(root,'history-metadata')
    outputShapefile = os.path.join(root,'spatial-data/CambridgeGSV_Pnt20m.shp')

    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/sunglare-pano'
    metadata = os.path.join(root, 'cleanedMetadata_winter')
    # gsvInfoLst = Read_GSVinfo_Text_File2Folder(metadata)

    # The winter Google Street View panoramas
    outputShapefile = os.path.join(root,'map-sunglare/CambridgeGSV_Winter.shp')
    # CreatePointFeature_ogr(outputShapefile,gsvInfoLst)
    
    
    # the copy of streetlight shapefile
    # root = r'E:\ResearchProj\SunGlare\Spatial-data'
    # pntShp = os.path.join(root,'Cambridge40m.shp')
    # ouputTextFolder = os.path.join(root,'CambridgeMetadata40mHistorical')
    # num = 1000
    # GSVpanoMetadataCollectorBatch_Yaw_TimeMachine(samplesFeatureClass,num,ouputTextFolder)
    
    
    # # Main function, example
    # import os,os.path
    
    # root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/sunglare-pano'
    # MetadatTxt = os.path.join(root,'Pnt_start0_end1000.txt')
    # # MetadatTxt = os.path.join(root,'Pnt_start1000_end2000.txt')
    # cleanedMetadatTxt = os.path.join(root, 'cleanedMetadata_winter')
    # monthlist = ['11', '12', '01', '02', '03', '04']
    # # monthlist = ['05', '06', '07', '08', '09', '10']
    # Seasonal_GSVmetadata_extraction (MetadatTxt, monthlist, cleanedMetadatTxt)
    
    
    ## --------- Create metadata for Dash + AI from street-level images -----------
    pntShp = r'/Users/senseablecity/Dropbox (MIT)/Start-up/street-right/spatial-data/mass-ave-pnt5m.shp'
    monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    MetadatTxt = r'/Users/senseablecity/Dropbox (MIT)/Start-up/street-right/metadata'
    # GSVpanoMetadataCollectorBatch_Yaw_TimeMachine(pntShp, 1000, MetadatTxt)
    
    
    ## Create metadata for Tokyo shibuya project
    sampleshp = r'/Users/senseablecity/Dropbox (MIT)/Xiaojiang Li/TokyoProj/TokyoShp/shibuya_site10m.shp'
    monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    # MetadatTxt = r'/home/xiaojiang/shibuya-proj/gsv-images/metadata'
    MetadatTxt = r'/Users/senseablecity/Dropbox (MIT)/Xiaojiang Li/TokyoProj/metadata'
    # GSVpanoMetadataCollectorBatch_Yaw_TimeMachine(sampleshp, 1000, MetadatTxt)
    # GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(sampleshp, 1000, MetadatTxt)
    
    
    ## Create metadata for Tokyo shibuya project
    sampleshp = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Environmental Injustice/Thermal comfort injustice/datasets/Boston/spatial-data/Boston100m.shp'
    monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    # MetadatTxt = r'/home/xiaojiang/shibuya-proj/gsv-images/metadata'
    MetadatTxt = r'/Users/senseablecity/Dropbox (MIT)/Programing/nodejs/map-node/pg_mapper/metadata'
    # GSVpanoMetadataCollectorBatch_Yaw_TimeMachine(sampleshp, 1000, MetadatTxt)
    GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(sampleshp, 1000, MetadatTxt)
