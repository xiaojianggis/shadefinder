
# Copyright(C) Xiaojiang Li, MIT Senseable City Lab
def metadataCleaning_winter_summer_txt (MetadataTxt, cleanedMetadataFolder, greenMonthList):
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

        print (MetadataTxt)

        s_pntnum_list = [] # mark as the summer pntnum list

        for i in range (startPnt, endPnt):
            iLine_list = []

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
            # print ('the number of point at %s is %s' %(i, pnt_pano_number))

            # if there is no panorama availalbe, then skip
            if pnt_pano_number < 1:
                continue
    #         elif pnt_pano_number == 1: # if there is only one panorama then save this pano info
    #             panoInfoText.write(iLine_list[0])
    #             s_pntnum_list.append(i)
            else:
                # temprary variables, used to find the most recent pano
                newpanoyear_s = 2007
                summerFlag = 0 # flag if we can find a summer panorama
                
                # there is more than one pano available, loop all the panoramas for point number i
                for iline in iLine_list:
                    elements = iline.split(' ')
                    panoid = elements[3]
                    try: 
                        panoyear = int(elements[5])
                        panomonth = elements[7]
                    except: 
                        continue                

    #                 # for the leaf off seasons, keep one panorama, using the most recent image
    #                 # if i not in w_pntnum_list and panomonth in ['11', '12', '01', '02', '03', '04'] and panoyear > 2008:
    #                 if i not in w_pntnum_list and panomonth in ['12', '01', '02', '03'] and panoyear > 2008:
    #                     w_pntnum_list.append(i)
    #                     if panoyear > newpanoyear_w:
    #                         newpanoyear_w = panoyear
    #                         insertWLine = iline
    #                         winterFlag = 1

                    # for leaf on seasons, keep one panorama, using the most recent image
                    if i not in s_pntnum_list and panomonth in greenMonthList and panoyear > 2009 and panoyear < 2016: 
                        s_pntnum_list.append(i)

                        if panoyear > newpanoyear_s: 
                            newpanoyear_s = panoyear
                            insertSLine = iline
                            summerFlag = 1

                if summerFlag: panoInfoText.write(insertSLine)            

    panoInfoText.close()


def metadataCleaning(Metadata, cleanedMetadataFolder, greenMonthList):
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
            metadataCleaning_winter_summer_txt(filename, cleanedMetadataFolder, greenMonthList)
    
    elif os.path.isfile(Metadata) and Metadata.endswith('.txt'): # the input is a file
        print ('---------------------', Metadata)
        metadataCleaning_winter_summer_txt(Metadata, cleanedMetadataFolder, greenMonthList)

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
    import xmltodict
    import time
    import sys


    if not os.path.exists(complete_cleanedMetadata):
        print('make a folder', complete_cleanedMetadata)
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
                    # get the meta data of the panorama
                    panoInfo = data['panorama']['data_properties']
                    print(panoInfo)

                    panoDate = panoInfo['@image_date']
                    panoId = panoInfo['@pano_id']
                    panoLat = panoInfo['@lat']
                    panoLon = panoInfo['@lng']

                    print('pano projection_properties', data['panorama']['projection_properties'])

                    # get the pano_yaw_degree
                    panoProj = data['panorama']['projection_properties']
                    pano_yaw_degree = float(panoProj['@pano_yaw_deg'])
                    tilt_yaw_deg = float(panoProj['@tilt_yaw_deg'])
                    tilt_pitch_deg = float(panoProj['@tilt_pitch_deg'])


                    # if the tilt yaw is negative then the tilt_pitch_deg is negative
                    if tilt_yaw_deg < 0:
                        tilt_pitch_deg = -tilt_pitch_deg
                    
                    # compared with the hyaw and the pano_yaw_degree, if they are for different directions, then use minus tilt angle
                    if abs(hyaw - pano_yaw_degree) > 40:
                        tilt_pitch_deg = -tilt_pitch_deg
                        tilt_yaw_deg = -tilt_yaw_deg

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

    cleanedMetadatTxt = os.path.join(root, 'cleanedMetadata2')
    # metadataCleaning_txt(MetadatTxt, cleanedMetadatTxt)
    # metadataCleaning_winter_summer_txt(MetadatTxt, cleanedMetadatTxt)
    # metadataCleaning(root, cleanedMetadatTxt)
    
    
    ## STEP 1: ----- Select most recent year Winter and Summer records-----------
    # for all states
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Sun Expo/database'
    infolder = os.path.join(root, 'Metadata_US_InterState')
    for file in os.listdir(infolder):
        inroot = os.path.join(infolder, file)
        basename = os.path.basename(file)
        outroot = os.path.join(root, 'Cleaned_Metadata_US_InterState','Cleaned_'+basename)
        # metadataCleaning(inroot, outroot)
        
    
    
    
    ## ----------STEP 2 - complete the metadata in the historical metadata
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Data-pre'
    cleanedMetadata = os.path.join(root, 'cleanedMetadata')  #, 'Cleaned_Pnt_start0_end1000.txt'
    complete_cleanedMetadata = os.path.join(root, 'tilt_cleanedMetadata')

    
    #------ For Cambridge dense metadata ----------
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/spatial-data/metadata'
    cleanedMetadata = os.path.join(root, 'Cleaned_CambridgeMetadata10mHistorical')
    tilt_cleanedMetadata = os.path.join(root, 'Tilt_Cleaned_CambridgeMetadata10m')
    for file in os.listdir(cleanedMetadata):
        filename = os.path.join(cleanedMetadata, file)
        print ('The filename is:===============', filename)
        metadata_txt_add_tilts(filename, tilt_cleanedMetadata)

