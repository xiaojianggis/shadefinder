
# This code is used to test the algorithm online to get the historical GSV
# data based on "https://github.com/robolyst/streetview"
# First version, June 19th, 2017, MIT Senseable City Lab

import xmltodict
import time
import os,os.path
import fiona
import sys

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
    import sys

    url = _panoids_url(lat, lon)

    # using different url reading method in python2 and python3
    if sys.version_info[0] == 2:
        import urllib
        
        metaData = urllib.urlopen(url).read()
        
    if sys.version_info[0] == 3:
        import urllib.request
        
        request = urllib.request.Request(url)
        metaData = urllib.request.urlopen(request).read()
    
    
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
    
    dataset, batch = GSVpanoMetadataCollectorBatch_Utils(samplesFeatureClass,num,ouputTextFolder)

    for b in range(batch):
        ouputGSVinfoFile = get_output_text_file_path(b, num, ouputTextFolder)
        
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
                # using different url reading method in python2 and python3
                if sys.version_info[0] == 2:
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
                        
                    
        panoInfoText.close()



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
    
    import ogr, osr
    
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
        

def GSVpanoMetadataCollectorBatch_Utils(samplesFeatureClass, num, ouputTextFolder):
    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)

    dataset = fiona.open(samplesFeatureClass)
    featureNum = len(list(dataset))    
    batch = int(featureNum/num) + 1
    
    print ('The batch size is:', batch)

    return dataset, batch
    

def get_output_text_file_path(b, num, ouputTextFolder):
    # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum
    ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
    ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)
    return ouputGSVinfoFile
    

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

    dataset, batch = GSVpanoMetadataCollectorBatch_Utils(samplesFeatureClass,num,ouputTextFolder)
    
    for b in range(batch):
        
        ouputGSVinfoFile = get_output_text_file_path(b, num, ouputTextFolder)
        
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
    


#### ------------------- The Main Function -------------------------
if __name__ == "__main__":
    import re
    from datetime import datetime
    import requests
    import time
    import itertools
    from PIL import Image
    from io import BytesIO
    import os

    ## --------- Create metadata for Dash + AI from street-level images -----------
    
    ## Create metadata for Tokyo shibuya project
    sampleshp = r'/Users/senseablecity/Dropbox (MIT)/Xiaojiang Li/TokyoProj/TokyoShp/shibuya_site10m.shp'
    monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    MetadatTxt = r'/Users/senseablecity/Dropbox (MIT)/Xiaojiang Li/TokyoProj/metadata'
    num = 1000
    # GSVpanoMetadataCollectorBatch_Yaw_TimeMachine(sampleshp, num, MetadatTxt)
    GSVpanoMetadataCollectorBatch_Yaw_TimeMachine2(sampleshp, num, MetadatTxt)
