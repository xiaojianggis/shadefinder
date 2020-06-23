
## This script is used to deal with point, line, polygon features for the 
## visualization purpuse. Those function of aggregation, overlapying, 
## Intersection, were included. 
## First version June 19, 2018
## Copyright(c) Xiaojiang Li, MIT Senseable City Lab


# create street segment based on the street
def createStreetSegment(inshp, outshp, mini_dist):
    '''
    This function will segment streets into different street segments
    Required modules: Fiona and Shapely
    
    parameters:
        inshp: the input linear shapefile, must be in WGS84 projection, ESPG: 4326
        output: the result street segment feature class
        mini_dist: the minimum distance between two created point
    
    First version May 3rd, 2018
    last modified by Xiaojiang Li, MIT Senseable City Lab
    
    '''

    import fiona
    import os,os.path
    from shapely.geometry import shape,mapping,Point,LineString
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
    
    # clean the original street maps by removing highways, if it the street map not from Open street data, users'd better to clean the data themselve
    with fiona.open(inshp) as source, fiona.open(temp_cleanedStreetmap, 'w', driver=source.driver, crs=source.crs,schema=source.schema) as dest:
        
        for feat in source:
            try:
                i = feat['properties']['highway'] # for the OSM street data
                if i in s:
                    continue
            except:
                # if the street map is not osm, do nothing. You'd better to clean the street map, if you don't want to map the GVI for highways
                key = dest.schema['properties'].keys()[0] # get the field of the input shapefile and duplicate the input feature
                i = feat['properties'][key]
                if i in s:
                    continue
            
            dest.write(feat)


    schema = {
        'geometry': 'LineString',
        'properties': {'id': 'int'},
    }
    
    # Create street segment along the streets
    with fiona.drivers():
        #with fiona.open(outshp, 'w', 'ESRI Shapefile', crs=source.crs, schema) as output:
        with fiona.open(outshp, 'w', crs = from_epsg(4326), driver = 'ESRI Shapefile', schema = schema) as output:
            for line in fiona.open(temp_cleanedStreetmap):
                
                # define projection and the inverse projection
                project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                project2 = partial(pyproj.transform,pyproj.Proj(init='EPSG:3857'),pyproj.Proj(init='EPSG:4326'))
                
                # deal with MultiLineString and LineString
                featureType = line['geometry']['type']
                dist = mini_dist
                
                # for the LineString
                if featureType == "LineString":
                    first = shape(line['geometry'])
                    length = first.length
                    
                    # convert the projection of wgs84 from degree to meters
                    line2 = transform(project, first)
                    
                    # cut the line feature using the distance of dist
                    st_seg = cutLine_series_pnt(line2, dist)
                    
                    # loop all the street segments and then save them as a new shapefile                    
                    for seg in st_seg:
                        # do inverse projection, and the new feature has WGS84
                        line3 = transform(project2, seg)
                        output.write({'geometry':mapping(line3),'properties': {'id':1}})
                        
                else:
                    continue
    
    print("Process Complete")
    
    # delete the temprary cleaned shapefile
    fiona.remove(temp_cleanedStreetmap, 'ESRI Shapefile')




# Example to use the code, 
# Note: make sure the input linear featureclass (shapefile) is in WGS 84 or ESPG: 4326
# ------------main ----------
if __name__ == "__main__":
    import os,os.path
    import sys
    from shapely.geometry import LineString, mapping, shape
    import MetadataLib as metalib
    import fiona
    
    
    # for whole united states
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/NationalScale-sunglare/StreetMaps/FL'
    streetMap = os.path.join(root,'interstates.shp')
    sunglareMap = os.path.join(root, 'sunglareMap-6-20.shp')
    outputShp = os.path.join(root, 'sunglare_interstates.shp')
    
    
    with fiona.open(sunglareMap, 'r') as sunglare:
        print sunglare.meta
        
        # i = 0
        # for feat in sunglare:
        #     i = i + 1
            
        #     setdur = feat['properties']['setdur']
        #     risedur = feat['properties']['risedur']
        #     setglare = feat['properties']['setglare']
        #     riseglare = feat['properties']['riseglare']

        #     if i % 1000 == 0: print ('You reaching:', i, setglare)


    # # with fiona.open(inshp) as source, fiona.open(temp_cleanedStreetmap, 'w', driver=source.driver, crs=source.crs,schema=source.schema) as dest:
    # with fiona.open(streetMap) as interstates:
    #     crs = interstates.crs # the the coordinate reference system information
    #     schema = interstates.schema.copy() #copy the schema of the input shapefile
        
    #     # add new fields to the street map
    #     schema['properties']['setglare'] = 'str:200'
    #     schema['properties']['riseglare'] = 'str:200'
    #     schema['properties']['risedur'] = 'int'
    #     schema['properties']['setdur'] = 'int'

        # # write a schema and crs to the new output shapefile
        # with fiona.open(outputShp, 'w', driver='ESRI Shapefile', schema=schema, crs=crs) as output:
        #     # loop all features
        #     for feat in interstates:
        #         feat['properties']['setglare'] = ' '
        #         feat['properties']['riseglare'] = ' '
        #         feat['properties']['risedur'] = 0
        #         feat['properties']['setdur'] = 0
        #         output.write({'properties':feat['properties'],'geometry': mapping(shape(feat['geometry']))})


    # outshp = os.path.join(root,'CambridgeStreet_wgs84_20m.shp')
    
    # mini_dist = 100 #the minimum distance between two generated points in meter
    
    # # createPoints(inshp, outshp, mini_dist) # create point features along streets

    # # inshp = os.path.join(root,'test.shp')
    # outshp = os.path.join(root,'CambridgeStreet_wgs84_segments.shp')
    # # createStreetSegment(inshp, outshp, mini_dist) # create street segment from streets 
    
    
    # ## SunGlare Viz, create sample sites along street in Main streets of Cambridge
    # root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/SunGlare/viz-mainstreet-cambridge'
    # streetmap = os.path.join(root, 'street-map.shp')
    # pntshp = os.path.join(root, 'pnt-map.shp')
    
    # # createPoints(streetmap, pntshp, 5)
    # # metalib.GSVpanoMetadataCollectorBatch_Yaw(pntshp, 1000, root)
    
    
    # ## ----------- new sun glare map, denser coverage -----------------------
    # root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/spatial-data'
    # streetmap = os.path.join(root, 'Centerline_4326.shp')
    # pntshp = os.path.join(root, 'Centerline_4326_10m.shp')
    # createPoints(streetmap, pntshp, 10)
    # panofolder = os.path.join(root, 'metadata')
    # # metalib.GSVpanoMetadataCollectorBatch_Yaw(pntshp, 1000, panofolder)
    
