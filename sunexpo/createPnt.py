# This program is used in the first step of the Treepedia project to get points along street 

# network to feed into GSV python scripts for metadata generation.

# Copyright(C) Marwa Abdulhai, Senseable City Lab, MIT 

# First version July 21 2017

# Last modified by Xiaojiang Li, MIT Senseable City Lab, Dec 27, 2017

'''
step 1: INTERSECTION
Before running the python file createPoints.py, run in command line the following command in the folder that contains your files:
ogr2ogr -f "ESRI Shapefile" -clipsrc city_boundry.shp output.shp street_network.shp -skipfailures
where clip_boundry.shp is your shapefile of the target city
      output.shp is your final .shp file containing points along street network
      street_network.shp is your street network obtained from mapzen
'''

# now run the python file: createPoints.py
def createPoints(inshp, outshp, mini_dist):
    
    '''
    This function will parse throigh the street network of provided city and
    clean all highways and create points every mini_dist meters (or as specified) along
    the linestrings
    Required modules: Fiona and Shapely

    parameters:
        inshp: the input linear shapefile, must be in WGS84 projection, ESPG: 4326
        output: the result point feature class
        mini_dist: the minimum distance between two created point

    last modified by Xiaojiang Li, MIT Senseable City Lab
    
    '''
    
    import fiona
    import os,os.path
    from shapely.geometry import shape,mapping
    from shapely.ops import transform
    from functools import partial
    import pyproj
    from fiona.crs import from_epsg
    
    
    count = 0
    s = {'trunk_link','tertiary','motorway','motorway_link','steps', None, ' ','pedestrian','primary', 'primary_link','footway','tertiary_link', 'trunk','secondary','secondary_link','tertiary_link','bridleway','service'}
    
    # the temporaray file of the cleaned data
    root = os.path.dirname(inshp)
    basename = 'clean_' + os.path.basename(inshp)
    temp_cleanedStreetmap = os.path.join(root,basename)
    
    # if the tempfile exist then delete it
    if os.path.exists(temp_cleanedStreetmap):
        fiona.remove(temp_cleanedStreetmap, 'ESRI Shapefile')
        #driver = ogr.GetDriverByName("ESRI Shapefile")
        #driver.DeleteDataSource(temp_cleanedStreetmap)

    
    # clean the original street maps
    with fiona.open(inshp) as source, fiona.open(temp_cleanedStreetmap, 'w', driver=source.driver, crs=source.crs,schema=source.schema) as dest:
        for feat in source:
            try:
                i = feat['properties']['highway'] # for the OSM street data
                if i in s:
                    continue
            except:
                i = feat['properties']['Restrictio'] # for cambridge center line data
                if i in s:
                    continue
            
            dest.write(feat)
                                                                  
    schema = {
        'geometry': 'Point',
        'properties': {'id': 'int'},
    }
    
    with fiona.drivers():
        #with fiona.open(outshp, 'w', 'ESRI Shapefile', crs=source.crs, schema) as output:
        with fiona.open(outshp, 'w', crs = from_epsg(4326), driver = 'ESRI Shapefile', schema = schema) as output:
            for line in fiona.open(temp_cleanedStreetmap):
                first = shape(line['geometry'])                
                length = first.length
                
                # convert degree to meter, in order to split by distance in meter
                project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                
                line2 = transform(project, first)                                
                linestr = list(line2.coords)
                dist = mini_dist #set
                for distance in range(0,int(line2.length), 20):
                    point = line2.interpolate(distance)
                    
                    # convert the local projection back the the WGS84 and write to the output shp
                    project2 = partial(pyproj.transform,pyproj.Proj(init='EPSG:3857'),pyproj.Proj(init='EPSG:4326'))
                    point = transform(project2, point)
                    output.write({'geometry':mapping(point),'properties': {'id':1}})
                    
    print("Process Complete")
    
    # delete the temprary cleaned shapefile
    fiona.remove(temp_cleanedStreetmap, 'ESRI Shapefile')



# ------------main ----------
import os,os.path

root = '/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/spatial-data'
inshp = os.path.join(root,'CambridgeStreet.shp')
outshp = os.path.join(root,'Cambridge10m.shp')
mini_dist = 10

createPoints(inshp, outshp, mini_dist)
