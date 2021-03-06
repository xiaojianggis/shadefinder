
# This library is used to provide tools for the spatial analysis, such as
# Rtree, overlap of the different layers of spatial data, etc

# This function is used to segment the state highways for each state of U.S
# using the batch model to process all the points along interstates highways
# First version April 30, 2018

import rtree
import fiona
import ogr, osr
import os, os.path
from shapely.geometry import shape, mapping, Polygon, MultiPoint


# using recursive statement to split longer roads into shorter segments
# Reference: https://www.azavea.com/blog/2016/10/05/philippines-road-safety-using-shapely-fiona-locate-high-risk-traffic-areas/
def split_line(line, max_line_units):
    '''
    The input:
        line: the LineString object
        max_line_units: the split distance, be careful of the units
    output:
        a list of LineString segment
    '''
    
    if line.length <= max_line_units:
        return [line]
    
    half_length = line.length / 2
    coords = list(line.coords)
    
    for idx, point in enumerate(coords):
        proj_dist = line.project(Point(point))
        if proj_dist == half_length:
            return [LineString(coords[:idx + 1]), LineString(coords[idx:])]
        
        if proj_dist > half_length:
            mid_point = line.interpolate(half_length)
            head_line = LineString(coords[:idx] + [(mid_point.x, mid_point.y)])
            tail_line = LineString([(mid_point.x, mid_point.y)] + coords[idx:])
            return split_line(head_line, max_line_units) + split_line(tail_line, max_line_units)



def SplitStreets2Segments(streetMap, segStreetMap, distance):
    '''
    This function is used to split the streets into shorter street segments for visualization
    and spatial analyses and modeling purposes
    
    parameters:
        streetMap: the original street feature class
        segStreetMap: the filename of the output street segment
        distance: the distance of the spliting the distance
    
    example:
        root = r'/home/xiaojiang/xiaojiang/tokyo-proj/shibuya-proj/spatial-data/'
        streetMap = os.path.join(root, 'Japan_highway_shibuya.shp')
        segStreetMap = os.path.join(root, 'seg_Japan_highway_shibuya.shp')
        
        SplitStreets2Segments(streetMap, segStreetMap, 40)
    
    
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab 
    Last modified Dec 2ed, 2018
    '''
    
    import pyproj
    from shapely.ops import transform
    from functools import partial
    
    split_lines = []
    
    with fiona.open(streetMap, 'r') as streets:
        crs = streets.crs
        schema = streets.schema.copy()
        
        with fiona.open(segStreetMap, 'w', driver="ESRI Shapefile", crs=crs, schema=schema) as output_segment:
            for street in streets:            
                street_attr = street['properties']            
                street_geom = street['geometry']
                featureType = street_geom['type']
                
                # check if the linear feature is LineString or Multi-Line String
                if featureType == 'MultiLineString':
                    print('This is a MultiLineString')
                    multi_street_geom_degree = shape(street_geom)
                    
                    for singleLine_degree in multi_street_geom_degree:
                        length = singleLine_degree.length
                        # partition each single line in the multiline
                        project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                        singleLine_meter = transform(project, singleLine_degree)

                        street_segments = split_line(singleLine_meter, distance)
                        split_lines.extend(street_segments)

                        # save the splitted segment to a shapefile
                        for street_segment in street_segments:                
                            project2 = partial(pyproj.transform,pyproj.Proj(init='EPSG:3857'),pyproj.Proj(init='EPSG:4326'))
                            street_segment_deg = transform(project2, street_segment)

                            output_segment.write({
                                'geometry': mapping(street_segment_deg),
                                'properties': dict(street_attr)
                            })
                
                elif featureType == 'LineString': 
                    # RouteName = street['properties']['FULLNAME']
                    street_geom_degree = shape(street_geom)

                    # convert degree to meter, in order to split by distance in meter
                    project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                    street_geom_meter = transform(project, street_geom_degree)

                    street_segments = split_line(street_geom_meter, distance)
                    split_lines.extend(street_segments)

                    # save the splitted segment to a shapefile
                    for street_segment in street_segments:                
                        project2 = partial(pyproj.transform,pyproj.Proj(init='EPSG:3857'),pyproj.Proj(init='EPSG:4326'))
                        street_segment_deg = transform(project2, street_segment)

                        output_segment.write({
                            'geometry': mapping(street_segment_deg),
                            'properties': dict(street_attr) # this is important statement to save all the previous properties
                        })
                    




def AggregatePnt2Polygon(pntshp, polygonshp, outPolygonShp):

    '''
    This function is used aggregate the point level feature to polygons
    Last modified Dec 26, 2019 by Xiaojiang Li, Temple University

    Example:
        root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Treepedia/NYC-MillionsTree/spatial-data'
        pntshp = os.path.join(root, 'NYC_2008_2014_GSV.shp')
        polygonshp = os.path.join(root, 'nyc_censustract.shp')
        outPolygonShp = os.path.join(root, 'nyc_gvi_censustract.shp')

        AggregatePnt2Polygon(pntshp, polygonshp, outPolygonShp)
    
    '''

    import rtree
    import fiona
    import os, os.path
    from statistics import median
    from shapely.geometry import shape
    from shapely.ops import transform
    from functools import partial
    import pyproj
    
    
    with fiona.open(pntshp, 'r') as pnt_lyr:     
        # create an empty spatial index object
        index = rtree.index.Index()
        
        # populate the spatial index, the polygon features
        i = 0
        for fid, feature in pnt_lyr.items():
            i = i + 1
            if i % 10000 == 0: print (i)
            geometry = shape(feature['geometry'])
            
            # convert the projection to psudo wgs projection with unit of meter
            project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
            geometry_m = transform(project, geometry)
            
            # add a buffer in order to create a r-tree
            geometry_buffered = geometry_m.buffer(10) 
            geotype = feature['geometry']['type']
            
            index.insert(fid, geometry_buffered.bounds)
        
        # loop all polygons and assign GVI values
        with fiona.open(polygonshp, 'r') as polygon_lyr:
            schema = polygon_lyr.schema.copy()
            schema['properties']['gvi']='float' 
            input_crs = polygon_lyr.crs
            
            # write the intersected point into the new shapefile
            with fiona.open(outPolygonShp, 'w', 'ESRI Shapefile', schema, input_crs) as output:
                
                # loop the polygon feature
                for idx, featPoly in enumerate(polygon_lyr):
                    print('Polygon:', idx)
                    geomPoly = shape(featPoly['geometry'])
                    project = partial(pyproj.transform,pyproj.Proj(init='EPSG:4326'),pyproj.Proj(init='EPSG:3857')) #3857 is psudo WGS84 the unit is meter
                    geomPoly_m = transform(project, geomPoly)
                    
                    attriPoly = featPoly['properties']

                    # using the bounding box to find the close but may not intersected point feature
                    fids = [int(i) for i in index.intersection(geomPoly_m.bounds)]

                    # the mean gvi value of all point in the polygon
                    gvi_list = []

                    # loop all features in bounding box and then judge if they are intersected
                    for fid in fids:
                        featPnt = pnt_lyr[fid]
                        geomPnt = shape(featPnt['geometry'])

                        # if the point is intersected with the polygon, then save the point feature into the output shapefile
                        if geomPoly.intersects(geomPnt):                            
                            gvi = featPnt['properties']['gvi']
                            gvi_list.append(gvi)

                    # the median value to the polygon
                    if len(gvi_list) < 3: 
                        print('No point')
                        attriPoly['gvi'] = -100
                    else:
                        # calculate the median value and assign it to the polygon
                        gvi_mean = median(gvi_list)
                        attriPoly['gvi']=gvi_mean


                    output.write({'geometry': mapping(geomPoly),'properties': attriPoly})








# Assign point feature the properties of street segment
def Intersect_pnt_street_fiona(pntShp, streetShp, outputfolder):
    '''
    This function is used to intersect the point feature with the linear street feature
    based on the R-tree index. Thi function is used to assign point value based on the
    properties of lines
    
    parameters:
        pntShp: the input point shapefile
        stateShp: the input polygon Shapefile
        outputfolder: the output folder to save the result point features
    
    example:
        root = r'/home/xiaojiang/xiaojiang/tokyo-proj/shibuya-proj/spatial-data/'

        pntShp = os.path.join(root, 'sunexpo-July-15-9am-WGS84.shp')
        streetShp = os.path.join(root, 'seg_Shibuya_streetNetwork_noMotorway.shp')

        Intersect_pnt_street_fiona(pntShp, streetShp, root)

    First version April 30, 2018
    
    last modified Dec 2ed, 2018
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab
    
    '''
    
    import os, os.path
    import fiona
    import rtree
    
    
    with fiona.open(pntShp, 'r') as pnt_lyr:
        # get the spatial reference of the shapefile 
        schema = pnt_lyr.schema.copy()
        input_crs = pnt_lyr.crs
        
        with fiona.open(streetShp, 'r') as street_lyr:
            # create an empty spatial index object
            index = rtree.index.Index()
            
            # populate the spatial index, the polygon features
            i = 0
            for fid, feature in pnt_lyr.items():
                i = i + 1
                if i % 1000 == 0: print (i)
                geometry = shape(feature['geometry'])
                geometry_buffered = geometry.buffer(2) # add a buffer in order to create a r-tree
                geotype = feature['geometry']['type']
                
                index.insert(fid, geometry_buffered.bounds)
                
                
            # loop the polygon feature
            for featLine in street_lyr:
                geomLine = shape(featLine['geometry'])
                stateName = featLine['properties']['STUSPS']

                # write to a shapefile for each polygon
                outputShp = os.path.join(outputfolder, stateName + '_pnt.shp')
                print ('The outputshp file is:', outputShp)
                 
                with fiona.open(outputShp, 'w', 'ESRI Shapefile', schema, input_crs) as output: 
                    
                    # using the bounding box to find the close but may not intersected point feature
                    fids = [int(i) for i in index.intersection(geomPoly.bounds)]
                   
                    for fid in fids:
                        featPnt = pnt_lyr[fid]
                        geomPnt = shape(featPnt['geometry'])
                        
                        # if the point is intersected with the polygon, then save the point feature into the output shapefile
                        if geomPoly.intersects(geomPnt):                            
                            elem = shape(featPnt['geometry'])
                            output.write({'geometry': mapping(shape(featPnt['geometry'])),'properties':{'id':1}})




def Intersect_pnt_polygon_fiona(pntShp, stateShp, outputfolder):
    '''
    This function is used to intersect the point feature with the polygon feature
    based on the R-tree index
    
    parameters:
        pntShp: the input point shapefile
        stateShp: the input polygon Shapefile
        outputfolder: the output folder to save the result point features

    First version April 30, 2018
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab
    
    '''
    import os, os.path
    
    
    with fiona.open(pntShp, 'r') as pnt_lyr:

        # get the spatial reference of the shapefile 
        schema = pnt_lyr.schema.copy()
        input_crs = pnt_lyr.crs
        
        with fiona.open(stateShp, 'r') as state_lyr:
            
            # create an empty spatial index object
            index = rtree.index.Index()
            
            # populate the spatial index, the polygon features
            i = 0
            for fid, feature in pnt_lyr.items():
                i = i + 1
                if i % 1000 == 0: print (i)
                geometry = shape(feature['geometry'])
                geometry_buffered = geometry.buffer(2) # add a buffer in order to create a r-tree
                geotype = feature['geometry']['type']
                
                index.insert(fid, geometry_buffered.bounds)
            
            
            # loop the polygon feature
            for featPoly in state_lyr:
                geomPoly = shape(featPoly['geometry'])
                stateName = featPoly['properties']['STUSPS']

                # write to a shapefile for each state polygon
                outputShp = os.path.join(outputfolder, stateName + '_pnt.shp')
                print ('The outputshp file is:', outputShp)

                # write the intersected point into the new shapefile
                with fiona.open(outputShp, 'w', 'ESRI Shapefile', schema, input_crs) as output:
                    
                    # using the bounding box to find the close but may not intersected point feature
                    fids = [int(i) for i in index.intersection(geomPoly.bounds)]
                    
                    # loop all features in bounding box and then judge if they are intersected
                    for fid in fids:
                        featPnt = pnt_lyr[fid]
                        geomPnt = shape(featPnt['geometry'])
                        
                        # if the point is intersected with the polygon, then save the point feature into the output shapefile
                        if geomPoly.intersects(geomPnt):                            
                            elem = shape(featPnt['geometry'])
                            output.write({'geometry': mapping(shape(featPnt['geometry'])),'properties':{'id':1}})


def CreatePointFeature_ogr(outputShapefile, LonLst, LatLst, panoIDlist, panoDateList, attr_dict, lyrname):
    
    """
    Create a shapefile based on the template of inputShapefile
    This function will delete existing outpuShapefile and create a new shapefile containing points with
    panoID, panoDate, and green view as respective fields.
    
    Parameters:
    outputShapefile: the file path of the output shapefile name, example 'd:\greenview.shp'
      LonLst: the longitude list
      LatLst: the latitude list
      panoIDlist: the panorama id list
      panoDateList: the panodate list
      attr_dict: the attribute dictionary, the key is the string name of the attribute, {'svf': svflist, 'gvi': gvilist}
    
    Copyright(c) Xiaojiang Li, Senseable city lab
    
    last modified by Xiaojiang li, MIT Senseable City Lab on March 27, 2018
    
    
    last modified by Xiaojiang Li, MIT Senseable CIty Lab on June 11, 2019
    
    """
    
    import ogr
    import osr
    
    # create shapefile and add the above chosen random points to the shapfile
    driver = ogr.GetDriverByName("ESRI Shapefile")
    
    # create new shapefile
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)

    data_source = driver.CreateDataSource(outputShapefile)
    targetSpatialRef = osr.SpatialReference()
    targetSpatialRef.ImportFromEPSG(4326)

    outLayer = data_source.CreateLayer(lyrname, targetSpatialRef, ogr.wkbPoint)
    numPnt = len(LonLst)

    print ('the number of points is:',numPnt)

    if numPnt > 0:
        # create a field
        idField = ogr.FieldDefn('PntNum', ogr.OFTInteger)
        panoID_Field = ogr.FieldDefn('panoID', ogr.OFTString)
        panoDate_Field = ogr.FieldDefn('panoDate', ogr.OFTString)
        outLayer.CreateField(idField)
        outLayer.CreateField(panoID_Field)
        outLayer.CreateField(panoDate_Field)
        
        # for all Real attributes
        for key in attr_dict.keys():
            attr_Field = ogr.FieldDefn(key, ogr.OFTReal)
            outLayer.CreateField(attr_Field)
        
        for idx in range(numPnt):
            #create point geometry
            point = ogr.Geometry(ogr.wkbPoint)
            
            # in case of the returned panoLon and PanoLat are invalid
            # if len(LonLst[idx]) < 3:
            #     continue      
            
            try:
                point.AddPoint(float(LonLst[idx]),float(LatLst[idx]))
            except:
                continue
            
            # Create the feature and set values
            featureDefn = outLayer.GetLayerDefn()
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(point)
            outFeature.SetField('PntNum', idx)
            if len(panoIDlist) < 1:
                outFeature.SetField('panoID', 'Null')
            else:
                outFeature.SetField('panoID', panoIDlist[idx])
            outFeature.SetField('panoDate',panoDateList[idx])
            
            # assign the attribute values
            for attrName in attr_dict.keys():
                attrList = attr_dict[attrName]
                if len(attrList) == 0:
                    outFeature.SetField(attrName,-999)
                else:
                    outFeature.SetField(attrName,float(attrList[idx]))
            
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()
            
        data_source.Destroy()
        
    else:
        print ('You created a empty shapefile')

