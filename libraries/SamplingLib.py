# This program is used in the first step of using GSV for various analysis
# This library includes functions of create sample sites along streets, 
# and cut lines into many street segments based on the minimum distance 
# The samples and street segments will be further used for the GSV metadata
# data collection and the visualization at the street level
# 
# Copyright(C) Xiaojiang Li, Senseable City Lab, MIT 
# First version July 21 2017

# second version May 2ed, 2018
# thrid version May 4, 2018
# Last modified by Xiaojiang Li, MIT Senseable City Lab, March 25, 2018


# now run the python file: createPoints.py, the input shapefile has to be in projection of WGS84, 4326
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

    modified by May 2ed, 2018, consider the linestring and multi-linear string
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
    # s = {'trunk_link','tertiary','motorway','motorway_link','steps', None, ' ','pedestrian','primary', 'primary_link','footway','tertiary_link', 'trunk','secondary','secondary_link','tertiary_link','bridleway','service'}
    # s = {'trunk_link','tertiary','motorway','motorway_link','steps', ' ','pedestrian','primary', 'primary_link','footway','tertiary_link', 'trunk','secondary','secondary_link','tertiary_link','bridleway','service'}
    s = {}
    
    # the temporaray file of the cleaned data
    root = os.path.dirname(inshp)
    basename = 'clean_' + os.path.basename(inshp)
    temp_cleanedStreetmap = os.path.join(root,basename)
    
    # if the tempfile exist then delete it
    if os.path.exists(temp_cleanedStreetmap):
        fiona.remove(temp_cleanedStreetmap, 'ESRI Shapefile')
        print ('removed the existed tempfile')
        
    # clean the original street maps by removing highways, if it the street map not from Open street data, users'd better to clean the data themselve
    with fiona.open(inshp) as source, fiona.open(temp_cleanedStreetmap, 'w', driver=source.driver, crs=source.crs,schema=source.schema) as dest:
        for feat in source:
            try:
                i = feat['properties']['highway'] # for the OSM street data
                # i = feat['properties']['fclass'] # for the OSM tokyo street data
                if i in s:
                    continue
            except:
                # if the street map is not osm, do nothing. You'd better to clean the street map, if you don't want to map the GVI for highways
                key = list(dest.schema['properties'].keys())[0]
                # key = dest.schema['properties'].keys()[0] # get the field of the input shapefile and duplicate the input feature
                i = feat['properties'][key]
                if i in s:
                    continue

            # print feat
            dest.write(feat)

    schema = {
        'geometry': 'Point',
        'properties': {'id': 'int'},
    }
    
    
    # Create point along the streets
    with fiona.drivers():
        #with fiona.open(outshp, 'w', 'ESRI Shapefile', crs=source.crs, schema) as output:
        with fiona.open(outshp, 'w', crs = from_epsg(4326), driver = 'ESRI Shapefile', schema = schema) as output:
            for line in fiona.open(temp_cleanedStreetmap):
                try: 
                    # deal with MultiLineString and LineString
                    featureType = line['geometry']['type']
                    
                    # for the LineString
                    if featureType == "LineString":
                        first = shape(line['geometry'])
                        length = first.length
                        
                        project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                        line2 = transform(project, first)
                        linestr = list(line2.coords)
                        dist = mini_dist 
                        
                        for distance in range(0,int(line2.length), dist):
                            point = line2.interpolate(distance)
                            project2 = partial(pyproj.transform,pyproj.Proj(init='EPSG:3857'),pyproj.Proj(init='EPSG:4326'))
                            point = transform(project2, point)
                            output.write({'geometry':mapping(point),'properties': {'id':1}})
                    
                    # for the MultiLineString, seperate these lines, then partition those lines
                    elif featureType == "MultiLineString":
                        multiline_geom = shape(line['geometry'])
                        print ('This is a multiline')
                        for singleLine in multiline_geom:
                            length = singleLine.length
                            
                            # partion each single line in the multiline
                            project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                            line2 = transform(project, singleLine)
                            linestr = list(line2.coords)
                            dist = mini_dist #set
                            
                            for distance in range(0,int(line2.length), dist):
                                point = line2.interpolate(distance)
                                project2 = partial(pyproj.transform,pyproj.Proj(init='EPSG:3857'),pyproj.Proj(init='EPSG:4326'))
                                point = transform(project2, point)
                                output.write({'geometry':mapping(point),'properties': {'id':1}})
                    
                    else:
                        print('Else--------')
                        continue
                
                except:
                    print ("You should make sure the input shapefile is WGS84")
                    return

    print("Process Complete")
    
    # delete the temprary cleaned shapefile
    fiona.remove(temp_cleanedStreetmap, 'ESRI Shapefile')




def cutLine_1_pnt_backup(line, distance):
    '''
    This function is used to cut the line based on the distance, this function
    will only cut the original line into two parts based on the distance
    
    May 3, 2018
    https://toblerity.org/shapely/manual.html
    
    Copyright(C) Xiaojiang Li, MIT Senseable City Lab
    '''
    
    from shapely.geometry import Point,LineString

    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    
    coords = list(line.coords)

    for i, p in enumerate(coords):
        pd = line.project(Point(p))

        if pd == distance:
            print ('The pd is:---------', pd)
            
            return [LineString(coords[:i+1]),
                    LineString(coords[i:])]

        if pd > distance:
            cp = line.interpolate(distance)
            return [LineString(coords[:i] + [(cp.x, cp.y)]),
                    LineString([(cp.x, cp.y)] + coords[i:])]



def cutLine_1_pnt(line, distance):
    '''
    This function is used to cut the line based on the distance, this function
    will only cut the original line into two parts based on the distance
    
    May 3, 2018
    https://toblerity.org/shapely/manual.html
    
    Copyright(C) Xiaojiang Li, MIT Senseable City Lab
    '''

    from shapely.geometry import Point, LineString

    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    
    coords = list(line.coords)

    for i, p in enumerate(coords):
        pd = line.project(Point(p))

        if pd == distance:
            print ('The pd is:---------', pd)

            return [LineString(coords[:i+1]),
                    LineString(coords[i:])]

        if pd > distance:
            cp = line.interpolate(distance)
            return [LineString(coords[:i] + [(cp.x, cp.y)]),
                    LineString([(cp.x, cp.y)] + coords[i:])]



def cutLine_series_pnt2(line, distance):
    '''
    This function is used to cut the line based on the distance
    Different from the previous function, this function will cut
    the line into many street segments based on the minimum distance
    
    May 4, 2018
    https://toblerity.org/shapely/manual.html
    
    Copyright(C) Xiaojiang Li, MIT Senseable City Lab
    '''

    from shapely.geometry import Point,LineString

    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    
    # create a series points along the streets
    coords = list(line.coords)
    print ('The coords are:', coords)

    # loop all vertices of the line and create line segments
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        print ('The pd is:', pd)
        print ('The i is:', i)

        if pd == distance:
            print ('=================')
            return [LineString(coords[:i+1]),
                    LineString(coords[i:])]
        
        if pd > distance:
            print ('--------------------')
            segLineList = [] # the list the line segments
            interPntLst = [] # create a point list to save the vertices of the line segment
            
            # loop the line and create point along line using interpolate
            for dist in range(0,int(line.length), distance):
                cp = line.interpolate(dist) # create the point with dist
                interPntLst.append((cp.x, cp.y))

            # add end point to the interPntLst
            interPntLst.append(coords[-1])

            # rebuild the LineStrings based on these vertices
            for i in range(len(interPntLst) - 1):
                pnt1 = interPntLst[i]
                pnt2 = interPntLst[i + 1]

                # add the linked segment to the line list
                segLineList.append(LineString([pnt1, pnt2]))
            
            return segLineList



def cutLine_series_pnt(line, distance):
    '''
    This function is used to cut the line based on the distance
    Different from the previous function, this function will cut
    the line into many street segments based on the minimum distance
    
    May 4, 2018
    https://toblerity.org/shapely/manual.html
    
    Copyright(C) Xiaojiang Li, MIT Senseable City Lab
    '''

    from shapely.geometry import Point,LineString
    from shapely.ops import split

    resultLinelist = []
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        resultLinelist = [LineString(line)]
        
    else:
        # add a vertices from the start point, therefore, the first part is good, the second part need to be further segmented
        dividLine = cutLine_1_pnt(line, distance)
        line_1 = dividLine[0] # the first part need to be added in the result segment
        line_2 = dividLine[1] # the second part will be segmented using the recursive method

        # using the recursive method to segment all the long lines into line segment
        resultLinelist = [line_1] + cutLine_series_pnt(line_2, distance)
    
    return resultLinelist



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
    from shapely.geometry import shape, mapping,Point,LineString
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
    from shapely.geometry import LineString
    import MetadataLib as metalib

    # for whole united states
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Treepedia/Treepedia-master - old/sample-spatialdata'
    inshp = os.path.join(root,'CambridgeStreet_wgs84.shp')
    outshp = os.path.join(root,'CambridgeStreet_wgs84_20m.shp')
    
    mini_dist = 100 #the minimum distance between two generated points in meter
    
    # createPoints(inshp, outshp, mini_dist) # create point features along streets

    # inshp = os.path.join(root,'test.shp')
    outshp = os.path.join(root,'CambridgeStreet_wgs84_segments.shp')
    # createStreetSegment(inshp, outshp, mini_dist) # create street segment from streets 
    
    
    ## SunGlare Viz, create sample sites along street in Main streets of Cambridge
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/SunGlare/viz-mainstreet-cambridge'
    streetmap = os.path.join(root, 'street-map.shp')
    pntshp = os.path.join(root, 'pnt-map.shp')
    
    # createPoints(streetmap, pntshp, 5)
    # metalib.GSVpanoMetadataCollectorBatch_Yaw(pntshp, 1000, root)
    
    
    ## ----------- new sun glare map, denser coverage -----------------------
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/spatial-data'
    streetmap = os.path.join(root, 'Centerline_4326.shp')
    pntshp = os.path.join(root, 'Centerline_4326_20m.shp')
    # createPoints(streetmap, pntshp, 20)
    panofolder = os.path.join(root, 'metadata')
    # metalib.GSVpanoMetadataCollectorBatch_Yaw(pntshp, 1000, panofolder)
    
    
    ## Create pnts along Massachusetts Avenue for Dash+AI proj
    inshp = r'/Users/senseablecity/Dropbox (MIT)/Start-up/street-right/spatial-data/mass-ave.shp'
    outshp = r'/Users/senseablecity/Dropbox (MIT)/Start-up/street-right/spatial-data/mass-ave-pnt5m.shp'
    # createPoints(inshp, outshp, 5)
    
    ## Create sample sites along streets in Shibuya
    inshp = r'/Users/senseablecity/Dropbox (MIT)/Xiaojiang Li/TokyoProj/TokyoShp/shibuya_street.shp'
    outshp = r'/Users/senseablecity/Dropbox (MIT)/Xiaojiang Li/TokyoProj/TokyoShp/shibuya_site10m.shp'
    # createPoints(inshp, outshp, 10)

    ## Create sample site along streets in Paris
    inshp = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Street-life/OSMNX/OSMNX/selected_route_double_proj4326.shp'
    outshp = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Street-life/OSMNX/OSMNX/selected_route_pnt_proj4326.shp'
    
    createPoints(inshp, outshp, 20)
