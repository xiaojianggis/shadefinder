# This function is used to download the GSV panoramas for NYC Million tree project
# First version Nov 9, 2019
# Copyright(c) Xiaojiang Li, Temple University

import os, os.path
import sys
sys.path.append("../libraries")
import GsvdownloaderLib as downlib


root = r'/mnt/deeplearnurbandiag/dataset/NYC/millionTree'
MetadatTxt = os.path.join(root, 'metadata-clean-years')
gsvimgs = os.path.join(root, 'gsv-panos')

for metatxt in os.listdir(MetadatTxt):
	metatxtfile = os.path.join(MetadatTxt, metatxt)
	monthlist = ['11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
	downlib.GSVpanoramaDowloader(metatxtfile, monthlist, gsvimgs, 0)
