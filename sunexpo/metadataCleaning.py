import os,os.path
import sys
from shapely.geometry import LineString
sys.path.append('../libraries')
import MetadataCleaningLib as metaclean


## STEP 1: ----- Select most recent year Winter and Summer records-----------
# clean the data for Sun expo project
root = r'/home/jiang/Documents/researchProj/thermal-injustice/datasets/Dallas/gsv'
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Philadephia'
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Atlanta'
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Charlotte'
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Houston'
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Memphis'
root = r'/home/xiaojiang/researchProj/datasets/gsv-data/NYC'
#root = r'/home/xiaojiang/researchProj/datasets/gsv-data/Baltimore'

inroot = os.path.join(root, 'metadata')
outroot = os.path.join(root, 'cleaned-metadata-sw-recentyear')
if not os.path.exists(outroot): os.mkdir(outroot)
metaclean.metadataCleaning(inroot, outroot)


## ----------STEP 2 - complete the metadata in the historical metadata
complete_cleanedMetadata = os.path.join(root, 'tilt_cleanedMetadata-sw-recentyear')
#if not os.path.exists(complete_cleanedMetadata):
#    print('make a folder-----------')
#    os.mkdir(complete_cleanedMetadata)
#metaclean.metadata_add_tilts(outroot, complete_cleanedMetadata)


# for file in os.listdir(outroot):
# 	filename = os.path.join(outroot, file)
# 	print ('The filename is:===============', filename)
# 	metaclean.metadata_txt_add_tilts(filename, complete_cleanedMetadata)


print ('You are calling the function of metadata_add_tilts')


# #------ For Cambridge dense metadata ----------
# root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/spatial-data/metadata'
# cleanedMetadata = os.path.join(root, 'Cleaned_CambridgeMetadata10mHistorical')
# tilt_cleanedMetadata = os.path.join(root, 'Tilt_Cleaned_CambridgeMetadata10m')
# for file in os.listdir(cleanedMetadata):
# 	filename = os.path.join(cleanedMetadata, file)
# 	print ('The filename is:===============', filename)
# 	metadata_txt_add_tilts(filename, tilt_cleanedMetadata)

