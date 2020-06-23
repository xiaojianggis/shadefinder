# call the function in SunExpoLib
# read the zip code shapefile and calculate the UV index
# Last modified at Jan 7th, 2018
# Copyright(C) Xiaojiang Li, MIT Senseable City Lab

from datetime import datetime, timedelta
import os,os.path
import sys
import SunExpoLib as sunexpo
import ImageClassLib as imgseg
import ogr,osr
import json

zipcode = '02171'
zenith = 60
obstruction = 1 # 1 is obstructed and 0 is open sky
SVF = 0.536

# estimate the percentage of UV radiation reaching the street canyons
UV_ratio = sunexpo.UV_transmision(zenith, obstruction, SVF)
print ('The percentage of UV radiation reaching the street canyon is:', UV_ratio)


# # loop for Cambridge zip code map
# root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/spatial-data/zipcode-boundary.shp'
# shpfile = os.path.join(root,'BOUNDARY_Zipcodes.shp')
# driver = ogr.GetDriverByName("ESRI Shapefile")
# datasource = driver.Open(shpfile, 1)
# layer = datasource.GetLayer()

# # add a new field
# # loop all fields in the shapefile
# fieldlist = []
# layer_defn = layer.GetLayerDefn()
# for i in range(layer_defn.GetFieldCount()):
# 	fieldname = layer_defn.GetFieldDefn(i).GetName()
# 	fieldlist.append(fieldname)

# if not 'uv_idx' in fieldlist: 
# 	print ('there is no exiting field, and add the new field')
# 	uv_field = ogr.FieldDefn("uv_idx", ogr.OFTReal)
# 	layer.CreateField(uv_field)


# # loop features and update the value of the new field
# for feature in layer:
# 	zipcode = feature.GetField('ZIP_CODE')
# 	print ('The zipcode for the feature is:',zipcode)
# 	# the URL address of the UV index, UV index API: https://www.epa.gov/enviro/web-services
# 	uv_req_json = "https://iaspub.epa.gov/enviro/efservice/getEnvirofactsUVHOURLY/ZIP/%s/json"%(zipcode)
# 	print ('The url address i:', uv_req_json)
    
    
# 	# judge the version of the python you are using
# 	version = sys.version_info[0]
# 	if version == 2:
# 	    import urllib2
# 	    import urllib, urllib2
# 	    import xmltodict

# 	    print ('You are using python 2')
# 	    opener = urllib2.build_opener()
# 	    f = opener.open(uv_req_json)
# 	    uv_idx_lst = json.loads(f.read())

# 	    # loop all UV idx hourly
# 	    for i in range(len(uv_idx_lst)):
# 	        uv_obj = uv_idx_lst[i]
# 	        uv_idx = uv_obj['UV_VALUE']
# 	        hour = uv_obj['DATE_TIME']

# 	        print ('The UV index at %s is %s '%(hour, uv_idx))

#     # elif version == 3:
#     #     import requests
#     #     import json

#     #     print ('You are using Python3')
#     #     r = requests.get(uv_req_json)
#     #     uv_idx_lst = r.json()

#     #     # loop all uv idx in the list of the json object
#     #     for i in range(len(uv_idx_lst)):
#     #         uv_obj = uv_idx_lst[i]
#     #         uv_idx = uv_obj['UV_VALUE']
#     #         hour = uv_obj['DATE_TIME']

#     #         print ('The UV index at %s is %s '%(hour, uv_idx))



# 	# calculate the UV exposure for each zip
# 	UV_index = sunexpo.UV_radiation(zipcode, zenith, obstruction, SVF)
# 	print ('The UV_idex is:',UV_index)


# print ("Done!")