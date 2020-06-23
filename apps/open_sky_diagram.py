
# This script is used to estimate the open sky regions and overlay the open sky
# with the sun path diagram in different time in one year for each GSV panorama
# site, the result is a matrix to record whether one site is shaded or not 
# 
# First version Dec 27, 2017
# Copyright(c) Xiaojiang Li, MIT Senseable City Lab
# last modified Jan 21, 2018


def Open_Skydiagram_SVF(dbname, tbname):
    '''
    This function is used to calculate the open sky diagram and Sky 
    view factor, both of which will be used to estimate the sunlight 
    duration and the UV exposure
    
    parameter: 
        dbname: the postgres database name
        tbname: the tbname of the database of dbname
    
    return:
        the SVF value
        the array to represent the opensky diagram
    
    First version Jan 20, 2018 by Xiaojiang Li, MIT Senseable City Lab
    '''

    from datetime import datetime, timedelta
    import os,os.path
    import sys
    import SunExpoLib as sunexpo
    import ImageClassLib as imgseg
    import psycopg2
    
    conn = psycopg2.connect(database = dbname, user = "postgres", host = "localhost", port = "5431")
    cur = conn.cursor()
    
    # loop all records in the table tbname of the database of dbname
    select_statement = "select * from %s"%(tbname)
    cur.execute(select_statement)
    rows = cur.fetchall()
    for row in rows: 
        print ('The row is:', row, row[2])
        
        # the workflow for building the database of sunlight exposure
        # root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab'
        # panoImgFile = os.path.join(root,panoId + '.bmp')
        # fisheyeImgFile = os.path.join(root,panoId + 'fisheye.bmp')
        # skyimgFile = os.path.join(root,panoId + 'skyRes.tif')
        
        panoId = row[0]
        
        # download the GSV panorama
        cylinderPanoImg = sunexpo.GSVpanoramaDowloader_GoogleMaps(panoId)
        
        # Convert GSV panorama into hemispherical image
        fisheyeImg = sunexpo.cylinder2fisheyeImage(cylinderPanoImg, 10)
        
        # using vegetation classication algorithm to classify the sky (using PSPnet)
        skyImg = imgseg.OBIA_Skyclassification_vote2Modifed_2(fisheyeImg)
        
        # # calculate the sky view factor based on the skyimg
        SVF = sunexpo.SVFcalculationOnFisheye(skyImg)
        print ('The SVF of the site is----------------:', SVF)
        
        # update the svf value in the postgre database
        update_statement = """UPDATE %s SET svf=%f where panoid = '%s';"""%(tbname,SVF,panoId)
        print 'The update statement is------:', update_statement
        cur.execute(update_statement)

        print ('You have upadated the value for', panoId, SVF)

        # ## estimate the open sky diagram
        # sys.path.append("./libraries/pysolar")
        
        
        conn.commit()
    
    cursor.close()



# ----------------- Main function ------------------------
import os,os.path
import sys

dbname = "testdb"
tbname = "gsv_info"
Open_Skydiagram_SVF(dbname, tbname)





# ## ESTIMATE THE SHADED DIAGRAM 
# # estimate the sun diagram, build a matrix to judge if the site is shaded or not at one time 
# lon = -71.093652
# lat = 42.359122
# year = 2017

# # a matrix to store the shade information in daytime and differnet days
# shadeMatrix = {}
# monthlist = range(1,13)# Jan - Dec
# daylist = range(1,32)
# hourlist = range(6,18) # 6am - 6pm
# minutelist = range(60)

# for month in monthlist:
#     for day in daylist:
#         for hour in hourlist:
#             # combination year-month-day-hour
#             for minute in minutelist:
#                 ymdhm = '%s-%s-%s-%s-%s'%(year,month,day,hour,minute)
                
#                 try:
#                     site_time = datetime(year,month,day,hour,minute,0,0)
#                     shade = sunexpo.Shaded_judgement(skyImg, site_time, lon, lat)
#                     dir_rad = sunexpo.direct_shaded_radiation(skyImg, site_time, lon, lat)
#                     print (ymdhm, '===========The direct radiation is:',dir_rad)
                    
#                     shadeMatrix[ymdhm] = shade
#                 except: 
#                     shade = -999
                    

# print('The size of the matrix is:',len(shadeMatrix))
# print('The size of the matrix is:',len(shadeMatrix), shadeMatrix['2017-8-2-12-40'])


# for month in monthlist:
#     key = '2017-8-%s-12-40'%(month)
#     print ('for month --',shadeMatrix[key])


