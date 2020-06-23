# This code is used to analyze the temporal change of the GSV metadata
# First version Dec 7, 2019
# Copyright(c) Xiaojiang Li, Temple University

import os
import sqlite3
import sys


# insert GSV metadata record to postsqre db
def insert_metadata_record(user, host, port, dbname, tbname, panoid, num, panodate, lon, lat, pano_yaw, tilt_yaw, tilt_pitch, GVI, SVF):
    '''
        Insert the GSV metadata records to the table
        
        dbname: the database name
        tbname: the table name in the database of dbname
        panoid, .., the metadata of the GSV info
    
    '''
    
    import psycopg2
    
    conn = psycopg2.connect(database = dbname, user = user, host = host, port = "5432", password="@LIxiao5424796")
    cursor = conn.cursor()
    query_statement = "INSERT INTO %s (panoid, num, panodate, lon, lat, pano_yaw, tilt_yaw, tilt_pitch, GVI, SVF) VALUES ('%s', '%s', '%s', %f, %f, %f, %f, %f, %f, %f)"%(tbname, panoid, num, panodate, lon, lat, pano_yaw, tilt_yaw, tilt_pitch, GVI, SVF)
    

    print(query_statement)


    cursor.execute(query_statement)
    conn.commit()
    cursor.close()


# retreive the information from the db
def retreiveDB (db_filename, tb_name):     
    import psycopg2
    
    user = 'xiaojiang@urbanenv'
    host = 'urbanenv.postgres.database.azure.com'
    port = "5432"
    # db_filename = "panodb"
    # tb_name = "millionTreeNYC"

    conn = psycopg2.connect(database = db_filename, user = user, host = host, port = port, password="@LIxiao5424796")
    cursor = conn.cursor()
    
    # loop all the records
    for num in range(710000):
        if num >20: break
        
        # retrieve_query = "select panoid, num, panodate, lon, lat, pano_yaw from %s where num = '%s'"%(tb_name, 1)
        retrieve_query = "select count(*) from %s where num = '%s'"%(tb_name, num)
        print('The select query is:', retrieve_query)

        cursor.execute(retrieve_query)
        for row in cursor.fetchall():
            print(row)
            # panoid, num, panodate, longitude, latitude, pano_yaw = row
            # print ('panoid:%s num:%s panodate:%s lon:%s lat:%s panoyaw:%s' % (panoid, num, panodate, longitude, latitude, pano_yaw))
        
    conn.commit()
    cursor.close()
    
    
    # with sqlite3.connect(database = db_filename, user = user, host = host, port = "5432", password="@LIxiao5424796") as conn:
        
    #     print ('Retreiving the database')
        
    #     retrieve_query = "select panoid, num, panodate, lon, lat, pano_yaw from %s where num = '%s'"%(tb_name, 10)
    #     print('The query is:', retrieve_query)

    #     cursor.execute(retrieve_query)

    #     for row in cursor.fetchall():
    #         panoid, num, panodate, longitude, latitude, pano_yaw = row
    #         print ('panoid:%s num:%s panodate:%s lon:%s lat:%s panoyaw:%s' % (panoid, num, panodate, longitude, latitude, pano_yaw))
            
    #     cursor.close()



def GVI_calculation_DB(metadb_filename):
    """
        This function is used to calculate the GVI and save the GVI result together
        with the metadata to the Database
        
        input:
        metadb_filename: the database of the GSV metadata
        
        First version Dec 25, 2017
        
        Copyright(c) Xiaojiang Li, MIT Senseable City Lab
        """
    
    import GVIcal
    
    with sqlite3.connect(metadb_filename) as conn:
        cursor = conn.cursor()
        
        # read metadata from the metadata table
        read_query = "select panoid, panodate, longitude, latitude, pano_yaw, tilt_yaw, tilt_pitch from metadata where project = 'metadata'"
        cursor.execute(read_query)
        
        for row in cursor.fetchall():
            panoid, panodate, longitude, latitude, pano_yaw, tilt_yaw, tilt_pitch = row
            print ('panoid:%s panodate:%s lon:%s lat:%s panoyaw:%s tilt_yaw:%s' % (panoid, panodate, longitude, latitude, pano_yaw, tilt_yaw))
            
            # calculate the gvi
            GVI = GVIcal.GreenViewComputing_6Horizon(panoid)
            print ('The GVI is:', GVI)
            
            insert_gvi_meta(db_filename, panoid, panodate, GVI, longitude, latitude, pano_yaw, tilt_yaw, tilt_pitch, 'GVIcal')
        
        
        print ('You have %s records'%(i))
        
        cursor.close()



# ---------------------Main function--------------------------
if __name__ == '__main__':
    
    import os,os.path
    import sys

    # dbname = "testdb"
    # tbname = "gsv_info"

    # dbname = sys.argv[1] # panodb
    # tbname = sys.argv[2] # millionTreeNYC
    # user = sys.argv[3] #xiaojiang@urbanenv
    # host = sys.argv[4] #urbanenv.postgres.database.azure.com
    # port = sys.argv[5]


    folder = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Treepedia/NYC-MillionsTree/metadata-clean'
    # createTable(dbname, tbname, user, host, port)
    # createTable('panodb', 'millionTreeNYC2', 'xiaojiang@urbanenv', 'urbanenv.postgres.database.azure.com', 5432)

    # for txt in os.listdir(folder):
    #     txtfile = os.path.join(folder, txt)
    #     meta2db(txtfile, 'xiaojiang@urbanenv', 'urbanenv.postgres.database.azure.com', "5432", "panodb", "millionTreeNYC")

    
    # retreive the information from the db
    db_filename = 'panodb'
    tb_name = 'milliontreenyc2'
    retreiveDB (db_filename, tb_name)     
