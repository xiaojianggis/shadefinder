
# Copyright(C) Xiaojiang Li, MIT Senseable City Lab

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


def metadataCleaning_txt (MetadataTxt, cleanedMetadataFolder):
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



def metadata_temporal_year(MetadataTxt, cleanedMetadataFolder):
    '''
    This function is used to filter out non-green season GSV, some points may have
    more than one GSV of different years.
    
    Parameters:
        MetadataTxt: the input metadata txt file or folder
        cleanedMetadataFolder: the output folder of the cleaned metadata
    
    Copyright(c) Xiaojiag Li, Department of Geography and Urban Studies, Temple University
    First version Nov 9th, 2019
    
    '''
    
    import os,os.path
    import sys
    
    # get the basename and formulate the output name
    basename = os.path.basename(MetadataTxt)
    if not os.path.exists(cleanedMetadataFolder):
        os.mkdir(cleanedMetadataFolder)
    cleanedMetadataTxt = os.path.join(cleanedMetadataFolder, 'Cleaned_'+basename)

    # if the file already existed, return
    if os.path.exists(cleanedMetadataTxt): return

    # write to the output cleaned folder
    with open(cleanedMetadataTxt, 'w') as panoInfoText:
        # the metadata of the GSV panorama
        lines = open(MetadataTxt,"r")
        
        # panonum list, used to select only one pano for one site
        panonumlist = []
        panolonlist = []
        panolatlist = []
        panoidlist = []
        year_pnt_list = []

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
            # vyaw = float(elements[15])

            # one year-pntnum combination
            year_pnt = pntnum + panoyear
            
            # print ('panid, panodata, lon, lat, hyaw, vyaw', panoid, panoyear, panomonth, panolon, panolat, hyaw, vyaw)

            # for the leaf on seasons, could change to other seasons
            if panomonth not in ['06', '07', '08', '09', '10'] or panoyear == '2007':
                continue
                
            # for each site, only select One GSV image for each year
            if panoid not in panoidlist and year_pnt not in year_pnt_list:
                panoidlist.append(panoid)
                year_pnt_list.append(year_pnt)

                lineTxt = 'pntnum: %s panoID: %s panoDate: %s longitude: %s latitude: %s pano_yaw_degree: %s tilt_pitch_deg: %s\n'%(pntnum, panoid, panodate, panolon, panolat, hyaw, 0)
                panoInfoText.write(lineTxt)

    panoInfoText.close()



def metadataCleaning (Metadata, cleanedMetadataFolder):
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
            # metadataCleaning_winter_summer_txt(filename, cleanedMetadataFolder)
            metadata_temporal_year(filename, cleanedMetadataFolder)
    elif os.path.isfile(Metadata) and Metadata.endswith('.txt'): # the input is a file
        # metadataCleaning_txt (Metadata, cleanedMetadataFolder)
        print ('---------------------', Metadata)
        # metadataCleaning_winter_summer_txt(Metadata, cleanedMetadataFolder)
        metadata_temporal_year(Metadata, cleanedMetadataFolder)
    else:
        return




def metadata_txt_add_tilts(in_metadata_filename, complete_cleanedMetadata):
    '''
    The function is used to complete the metadata generated by historicalMeta version
    since the historical metadata missed the "tilt_yaw_deg" and "tilt_pitch_deg"
    
    parameters:
        in_metadata_filename: the cleaned txt metadata generated from the historical metadata function 
        complete_cleanedMetadata: folder, the generated result with the complete metadata information
    
    last modified May 14, 2018
    
    Copyright(c), Xiaojiang Li, SunExpo
    
    '''

    import os, os.path
    import urllib
    import xmltodict
    import time


    if not os.path.exists(complete_cleanedMetadata):
        os.mkdir(complete_cleanedMetadata)

    if not in_metadata_filename.endswith('.txt'): return
    basename = os.path.basename(in_metadata_filename)
    outbasename = 'tilt_' + basename
    
    ot_metadata_filename = os.path.join(complete_cleanedMetadata, outbasename)
    
    # skip over those existing txt files
    if os.path.exists(ot_metadata_filename):
        print ('The output file already exists', ot_metadata_filename)
        return
    
    with open (ot_metadata_filename, 'w') as panoInfoText:
        lines = open(in_metadata_filename, 'r')
        i = 0
        for line in lines:
            i = i + 1
            elements = line.split(' ')
            pntnum = elements[1]
            panoid = elements[3]
            panoyear = elements[5]
            panomonth = elements[7]
            panodate = panoyear + '-' + panomonth

            # get the coordinate info and collect the yaw, tilt angles
            try:
                panolon = float(elements[9])
                panolat = float(elements[11])
                hyaw = float(elements[13])
                
                if i % 500 == 0: print ('The panolon, panolat, hyaw are ----', panolon, panolat, hyaw)
                
                urlAddress = "http://maps.google.com/cbk?output=xml&ll=%f,%f"%(panolat,panolon)             
                time.sleep(0.005)
                
                
                # the output result of the meta data is a xml object
                metaDataxml = urllib.urlopen(urlAddress)
                metaData = metaDataxml.read()
                data = xmltodict.parse(metaData)

                # in case there is not panorama in the site, therefore, continue
                if data['panorama']==None:
                    continue
                else:
                    # get the meta data of the panorama
                    panoInfo = data['panorama']['data_properties']
                    panoDate = panoInfo.items()[4][1]
                    panoId = panoInfo.items()[5][1]
                    panoLat = panoInfo.items()[8][1]
                    panoLon = panoInfo.items()[9][1]

                    # get the pano_yaw_degree
                    pano_yaw_degree = float(data['panorama']['projection_properties'].items()[1][1])
                    tilt_yaw_deg = float(data['panorama']['projection_properties'].items()[2][1])
                    tilt_pitch_deg = float(data['panorama']['projection_properties'].items()[3][1])

                    # if the tilt yaw is negative then the tilt_pitch_deg is negative
                    if tilt_yaw_deg < 0:
                        tilt_pitch_deg = -tilt_pitch_deg
                    
                    # compared with the hyaw and the pano_yaw_degree, if they are for different directions, then use minus tilt angle
                    if abs(hyaw - pano_yaw_degree) > 40:
                        tilt_pitch_deg = -tilt_pitch_deg
                        tilt_yaw_deg = -tilt_yaw_deg

                    # print ('The coordinate (%s,%s), panoId is: %s, panoDate is: %s'%(panoLon,panoLat,panoId, panoDate))
                    lineTxt = 'pntnum: %s panoID: %s panoDate: %s longitude: %s latitude: %s pano_yaw_degree: %s tilt_yaw_deg: %s tilt_pitch_deg: %s\n'%(pntnum, panoid, panodate, panolon, panolat, hyaw, tilt_yaw_deg, tilt_pitch_deg)
                    panoInfoText.write(lineTxt)
            
            except:
                lineTxt = 'pntnum: %s panoID: %s panoDate: %s longitude: %s latitude: %s pano_yaw_degree: %s tilt_yaw_deg: %s tilt_pitch_deg: %s\n'%(pntnum, panoid, panodate, panolon, panolat, hyaw, 0, 0)
                panoInfoText.write(lineTxt)
                
    panoInfoText.close()




if __name__ == "__main__":
    
    import os,os.path
    import sys
    from shapely.geometry import LineString
    
    
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/sunglare-pano'
    # MetadatTxt = os.path.join(root,'Pnt_start0_end1000.txt')
    # MetadatTxt = os.path.join(root,'Pnt_start1000_end2000.txt')
    
    cleanedMetadatTxt = os.path.join(root, 'cleanedMetadata2')
    # metadataCleaning_txt(MetadatTxt, cleanedMetadatTxt)
    # metadataCleaning_winter_summer_txt(MetadatTxt, cleanedMetadatTxt)
    # metadataCleaning(root, cleanedMetadatTxt)
    
    
    # clean the data for Florida
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Sun Expo/database'
    inroot = os.path.join(root, 'Metadata_Florida_Allroads')
    outroot = os.path.join(root, 'Cleaned_Metadata_Florida_Allroads')
    # metadataCleaning(inroot, outroot)
    
    
    # for all states
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Sun Expo/database'
    infolder = os.path.join(root, 'Metadata_US_InterState')
    # for file in os.listdir(infolder):
    #     inroot = os.path.join(infolder, file)
    #     basename = os.path.basename(file)
    #     outroot = os.path.join(root, 'Cleaned_Metadata_US_InterState','Cleaned_'+basename)
        # metadataCleaning(inroot, outroot)
        

    # complete the metadata in the historical metadata
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Data-pre'
    cleanedMetadata = os.path.join(root, 'cleanedMetadata')  #, 'Cleaned_Pnt_start0_end1000.txt'
    complete_cleanedMetadata = os.path.join(root, 'tilt_cleanedMetadata')

    
    
    
    #------ For Cambridge dense metadata ----------
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/spatial-data/metadata'
    cleanedMetadata = os.path.join(root, 'Cleaned_CambridgeMetadata10mHistorical')
    tilt_cleanedMetadata = os.path.join(root, 'Tilt_Cleaned_CambridgeMetadata10m')
    # for file in os.listdir(cleanedMetadata):
    #     filename = os.path.join(cleanedMetadata, file)
    #     print ('The filename is:===============', filename)
        # metadata_txt_add_tilts(filename, tilt_cleanedMetadata)

    
    # for temporal studies of NYC Million Trees
    print('------------For NYC-----------------------')
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Treepedia/NYC-MillionsTree'
    root = r'/mnt/deeplearnurbandiag/dataset/NYC/millionTree'
    infolder = os.path.join(root, 'metadata')
    for file in os.listdir(infolder):
        inroot = os.path.join(infolder, file)
        basename = os.path.basename(file)
        outroot = os.path.join(root, 'metadata-clean-years')
        metadataCleaning(inroot, outroot)
        
