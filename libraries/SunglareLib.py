# This is the library to estimate the sun glare based on deep learning algorithm
# on cylindrical Google Street View panoramas. This script include several functions:

# def sunglare_diagram_readskyImg: based on the input metadata and segmented pano, output the sun glare into a csv file
# def sunglare_onesite: one panorama, one record of metadata, sun glare info, (panoid, latitude, longitude, hyaw, tilt, segImg, hdeg, vdeg, zone, year, month, day)
# def sunglare_onesite can replace  "sunglare_sunriseset_cylinder_readskyImg"
# def sunglare_sunriseset_cylinder_readskyImg: read the txt GSV metadata then estimate the sun glare and output it into csv file


# Copyright(C) Xiaojiang Li, SunExpo, MIT Senseable City Lab
# Last modified Aug 8th, 2018


# uinsg HEMISPHERICAL image for the sungalre, may not good
def sunglare_diagram_readskyImg(metadata, skyImgFolder, sunglarefile, latitude, longitude, zone, year, month, day):
	'''
	This function is used to generate the sun glare diagram based on the 
	input metadata and the segmented skyImg 
	
	parameters:
		metadata: the input metadata
		skyImgFolder: the folder of the segmented HEMISPHERICAL images
		sunglarefile: the output sunglare file, csv		
		
		other inputs: longitude, latitude, zone, year, month, day are the next variables
		
	last modified by Xiaojiang Li, on March 1st, 2018
	'''
	
	
	import os,os.path
	import sys
	two_up_root = os.path.abspath(os.path.join(__file__ ,"../.."))
	libraries = os.path.join(two_up_root, 'libraries')
	pysolarlib = os.path.join(libraries,'pysolar')
	sys.path.append(libraries)

	import SunExpoLib as sunexpo
	import SunposLib as sunpos
	import numpy as np
	import csv
	from PIL import Image


	sunglarefile = open(os.path.join(root, sunglare_res),'w')
	with sunglarefile:
		sunglareWriter = csv.writer(sunglarefile)

		# the metadata of the GSV panorama
		# metadata = os.path.join(root,'cleanedMetadata/Cleaned_Pnt_start0_end1000.txt')
		lines = open(metadata,"r")

		# panonum list, used to select only one pano for one site
		panonumlist = []
		panolonlist = []
		panolatlist = []
		panoidlist = []

		# loop all the panorama records
		for line in lines:
			elements = line.split(' ')
			pntnum = elements[1]
			panoId = elements[3]
			panodate = elements[5]
			lon = float(elements[7])
			lat = float(elements[9])
			hyaw = float(elements[11])
			hyaw2 = hyaw + 180
			if hyaw2 > 360: hyaw2 = hyaw2 - 360 # the driving direction and the anti-driving direction
			vyaw = float(elements[13])
			print ('panid, panodate, lon, lat, hyaw, vyaw', panoId, panodate, longitude, latitude, hyaw, vyaw)

			# read the saved segmented image from the folder
			skyImgfile = os.path.join(skyImgFolder, panoId + '.jpg')
			try:
				skyImg = np.array(Image.open(skyImgfile))
			except:
				continue

			# list to save the sun glare time
			sunglare_time_list = []

			for hour in range(5, 20):
				for minute in range(60):
					[azimuth, sunele] = sunpos.calcSun(latitude, longitude, zone, year, month, day, hour, minute, 30)

					# judge if the sun is located in the sun glare zone
					# 0 is the obstructionpixelLabel, 10 is the size of the glare

					# the azimuth angle on the sky image, the azimuth_skyimg start from east direction anti-clockwisely
					azimuth_skyimg = -(azimuth - 90)
					if azimuth_skyimg < 0: azimuth_skyimg = azimuth_skyimg + 360

					# judge if the solar position on the obstruction in sky image, # 0 is not obstructed, 1 is obstructed
					obstructed = sunexpo.Shaded_judgement_noaa(skyImg, 0, 10, azimuth_skyimg, sunele) 
					
					#the horizontal difference between the driving adirection and the sun azimuth angle
					h_angle_diff = abs(azimuth - hyaw)
					h_angle_diff2 = abs(azimuth - hyaw2)
					if h_angle_diff < 25 and sunele < 25 and sunele >0 and obstructed == 0 or h_angle_diff2 < 25 and sunele < 25 and sunele >0 and obstructed == 0:
						# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
						# sunglare_time = '%s-%s'%(hour, minute)
						sunglare_time = hour*60 + minute
						sunglare_time_list.append(sunglare_time)

						# measure the sunglare duration and the start time of the sun glare

				print ('The sunele at this hour is:', lon, lat, hour, sunele)

			# save the sun glare result as a txt file
			sunglaretime = [pntnum, panoId, lon, lat, hyaw, vyaw, len(sunglare_time_list), sunglare_time_list]
			print ('The sunglare data is', sunglaretime)
			sunglareWriter.writerow(sunglaretime)



# one panorama, one record of metadata, sun glare info
def sunglare_onesite(panoid, latitude, longitude, hyaw, tilt, segImg, hdeg, vdeg, zone, year, month, day):
	'''
	This function is used to generate the sunrise and sunset sun glare diagrams based on the 
	segmented cylindrical image and the yaw, tilt information
	
	parameters:
		latitude, longitude, hyaw, tilt: the metadata the site/panorama
		segImg: segmented cylindrical pano image
		hdeg: the threshold of horizontal degree to judge the sun glare, default 25 here
		vdeg: the threshold of vertical degree to judge the sun glare, default 25 or 20
		zone, year, month, day
	
	return:
		the record of the sun glare
	
	First version May 27, 2018
	
	
	The new version try to save the sunglare time together with the sun elevation. 
	This is because the level of sunglare's impact on drivers may be influence by
	the sun elevation angle also. Therefore, in this case the sun elevation is also
	recorded to categorize the sun glare into different levels based on the sun ele
	
	last modified by Xiaojiang Li, on June 15th, 2018
	
	'''

	import os,os.path
	import numpy as np
	import csv
	from PIL import Image
	import SunposLib as sunpos
	import SunExpoLib as sunexpo

	# the driving direction and the anti-driving direction, for one-way road would be different
	hyaw2 = hyaw + 180
	if hyaw2 > 360: hyaw2 = hyaw2 - 360 

	vyaw = tilt # downsload the vyaw is positive, http://maps.google.com/cbk?output=xml&ll=41.772323,-72.205024
	# print ('panid, lon, lat, hyaw, vyaw', panoid, longitude, latitude, hyaw, vyaw)


	# list to save the sun glare, sunrise, sunset glare times
	sunglare_time_list = []

	sunriseglare_time_list = [] # the sunglare time list, divide 60 for hour, % for minute
	sunriseglare_sunele_list = [] # the vertical degree difference
	sunriseglare_horyaw_list = [] # the horizontal degree difference

	sunsetglare_time_list = [] # the sunset glare time list
	sunsetglare_sunele_list = [] # the vertical degree difference
	sunsetglare_horyaw_list = [] # the horizontal degree difference

	# The time interval for the sun glare mapping, every 2 minutes
	min_interval = 2

	# for the sun rise glare
	for hour in range(5, 11):
		for minute in range(0, 60, min_interval):
			[azimuth, sunele] = sunpos.calcSun(latitude, longitude, zone, year, month, day, hour, minute, 30)
			
			if sunele < 0.05:
				continue
			
			obstructionpixelLabel = 0 #the obstruction pixel number in the segImg
			glareSize = 24 # for the image size of 832*416

			# obstructed is 1 when the sunlight is blocked, 0 the sunlight is not blocked
			obstructed = sunexpo.Shaded_cylindrical_judgement_noaa(segImg, obstructionpixelLabel, glareSize, azimuth, sunele, hyaw)
			
			#the horizontal difference between the driving adirection and the sun azimuth angle
			h_angle_diff = abs(azimuth - hyaw)
			h_angle_diff2 = abs(azimuth - hyaw2)

			# the vertical difference between the driving car and the sun elevataion
			v_angle_diff = abs(sunele - vyaw) # downslope the vyaw is positive
			v_angle_diff2 = abs(sunele + vyaw)
			
			# sunrise sunglare list
			if (h_angle_diff < hdeg and v_angle_diff < vdeg and sunele >0 and obstructed == 0):
				rise_sunglare_time = hour*60 + minute
				sunriseglare_time_list.append(rise_sunglare_time)
				sunriseglare_sunele_list.append(v_angle_diff)
				sunriseglare_horyaw_list.append(h_angle_diff)

			elif (h_angle_diff2 < hdeg and v_angle_diff2 < vdeg and sunele >0 and obstructed == 0):
				# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
				rise_sunglare_time = hour*60 + minute
				sunriseglare_time_list.append(rise_sunglare_time)
				sunriseglare_sunele_list.append(v_angle_diff2)
				sunriseglare_horyaw_list.append(h_angle_diff2)
				
				
	# for the sunset glare
	for hour in range(14, 21):
		for minute in range(0, 60, min_interval):
			[azimuth, sunele] = sunpos.calcSun(latitude, longitude, zone, year, month, day, hour, minute, 30)
			
			if sunele < 0.05:
				continue
			
			obstructionpixelLabel = 0 #the obstruction pixel number in the skyImg
			glareSize = 24 # for the image size of 832*416

			# obstructed is 1 when the sunlight is blocked, 0 the sunlight is not blocked
			obstructed = sunexpo.Shaded_cylindrical_judgement_noaa(segImg, obstructionpixelLabel, glareSize, azimuth, sunele, hyaw)
			
			#the horizontal difference between the driving adirection and the sun azimuth angle
			h_angle_diff = abs(azimuth - hyaw)
			h_angle_diff2 = abs(azimuth - hyaw2)

			# the vertical difference between the driving car and the sun elevataion
			v_angle_diff = abs(sunele - vyaw) # downslope the vyaw is positive
			v_angle_diff2 = abs(sunele + vyaw)
			
			# sunset sunglare list
			if (h_angle_diff < hdeg and v_angle_diff < vdeg and sunele >0 and obstructed == 0): 
				set_sunglare_time = hour*60 + minute
				sunsetglare_time_list.append(set_sunglare_time)
				sunsetglare_sunele_list.append(v_angle_diff)
				sunsetglare_horyaw_list.append(h_angle_diff)
				
			elif (h_angle_diff2 < hdeg and v_angle_diff2 < vdeg and sunele >0 and obstructed == 0):
				# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
				set_sunglare_time = hour*60 + minute
				sunsetglare_time_list.append(set_sunglare_time)
				sunsetglare_sunele_list.append(v_angle_diff2)
				sunsetglare_horyaw_list.append(h_angle_diff2)

	# save the surise sun glare result as a txt file
	sunglaretime = [min_interval*len(sunriseglare_time_list), sunriseglare_time_list, sunriseglare_sunele_list, sunriseglare_horyaw_list, min_interval*len(sunsetglare_time_list), sunsetglare_time_list, sunsetglare_sunele_list, sunsetglare_horyaw_list]
	# print ('The sunglare data is', sunglaretime)
	
	return sunglaretime



# one panorama, one record of metadata, sun glare info
# Different from the above function, this function is optimized
def sunglare_onesite_opt(panoid, latitude, longitude, hyaw, tilt, segImg, hdeg, vdeg, zone, year, month, day):
	'''
	This function is used to generate the sunrise and sunset sun glare diagrams based on the 
	segmented cylindrical image and the yaw, tilt information
	
	parameters:
		latitude, longitude, hyaw, tilt: the metadata the site/panorama
		segImg: segmented cylindrical pano image
		hdeg: the threshold of horizontal degree to judge the sun glare, default 25 here
		vdeg: the threshold of vertical degree to judge the sun glare, default 25 or 20
		zone, year, month, day
	
	return:
		the record of the sun glare
	
	This function will select the relatively low sun elevation times and then search
	the sun glare time window in this low sun elevation range.
	
	First version Aug 22, 2018
	
	'''

	import os,os.path
	import numpy as np
	import csv
	from PIL import Image
	import SunposLib as sunpos
	import SunExpoLib as sunexpo
	
	# the driving direction and the anti-driving direction, for one-way road would be different
	hyaw2 = hyaw + 180
	if hyaw2 > 360: hyaw2 = hyaw2 - 360 
	
	vyaw = tilt # downsload the vyaw is positive, http://maps.google.com/cbk?output=xml&ll=41.772323,-72.205024
	# print ('panid, lon, lat, hyaw, vyaw', panoid, longitude, latitude, hyaw, vyaw)
	
	
	# list to save the sun glare, sunrise, sunset glare times
	sunglare_time_list = []
	
	sunriseglare_time_list = [] # the sunglare time list, divide 60 for hour, % for minute
	sunriseglare_sunele_list = [] # the vertical degree difference
	sunriseglare_horyaw_list = [] # the horizontal degree difference
	
	sunsetglare_time_list = [] # the sunset glare time list
	sunsetglare_sunele_list = [] # the vertical degree difference
	sunsetglare_horyaw_list = [] # the horizontal degree difference

	# The time interval for the sun glare mapping, every 2 minutes
	min_interval = 2
	
	
	## --------- sunrise glare time windows ---------------------------
	# locate the potential time windows for sunglare
	time_window_list = []
	for hour in range(5, 11):
		for minute in range(0, 60, min_interval):
			[azimuth, sunele] = sunpos.calcSun(latitude, longitude, zone, year, month, day, hour, minute, 30)
			if sunele < 30 and sunele > 0.05:
				item = (hour, minute, azimuth, sunele)
				time_window_list.append(item)
				
				
	# for the sun rise glare
	for item in time_window_list:
		hour = item[0]
		minute = item[1]
		azimuth = item[2]
		sunele = item[3]


		obstructionpixelLabel = 0 #the obstruction pixel number in the segImg
		glareSize = 24 # for the image size of 832*416
		
		# obstructed is 1 when the sunlight is blocked, 0 the sunlight is not blocked
		obstructed = sunexpo.Shaded_cylindrical_judgement_noaa(segImg, obstructionpixelLabel, glareSize, azimuth, sunele, hyaw)
		
		#the horizontal difference between the driving adirection and the sun azimuth angle
		h_angle_diff = abs(azimuth - hyaw)
		h_angle_diff2 = abs(azimuth - hyaw2)
		
		# the vertical difference between the driving car and the sun elevataion
		v_angle_diff = abs(sunele - vyaw) # downslope the vyaw is positive
		v_angle_diff2 = abs(sunele + vyaw)
		
		# sunrise sunglare list
		if (h_angle_diff < hdeg and v_angle_diff < vdeg and sunele >0 and obstructed == 0):
			rise_sunglare_time = hour*60 + minute
			sunriseglare_time_list.append(rise_sunglare_time)
			sunriseglare_sunele_list.append(v_angle_diff)
			sunriseglare_horyaw_list.append(h_angle_diff)
			
		elif (h_angle_diff2 < hdeg and v_angle_diff2 < vdeg and sunele >0 and obstructed == 0):
			# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
			rise_sunglare_time = hour*60 + minute
			sunriseglare_time_list.append(rise_sunglare_time)
			sunriseglare_sunele_list.append(v_angle_diff2)
			sunriseglare_horyaw_list.append(h_angle_diff2)
			
		

	## --------- sunset glare time windows ---------------------------
	# locate the potential time windows for sunglare
	time_window_list = []
	for hour in range(14, 21):
		for minute in range(0, 60, min_interval):
			[azimuth, sunele] = sunpos.calcSun(latitude, longitude, zone, year, month, day, hour, minute, 30)
			if sunele < 30 and sunele > 0.05:
				item = (hour, minute, azimuth, sunele)
				time_window_list.append(item)
				
				
	# for the sun rise glare
	for item in time_window_list:
		hour = item[0]
		minute = item[1]
		azimuth = item[2]
		sunele = item[3]


		obstructionpixelLabel = 0 #the obstruction pixel number in the segImg
		glareSize = 24 # for the image size of 832*416
		
		# obstructed is 1 when the sunlight is blocked, 0 the sunlight is not blocked
		obstructed = sunexpo.Shaded_cylindrical_judgement_noaa(segImg, obstructionpixelLabel, glareSize, azimuth, sunele, hyaw)
		
		#the horizontal difference between the driving adirection and the sun azimuth angle
		h_angle_diff = abs(azimuth - hyaw)
		h_angle_diff2 = abs(azimuth - hyaw2)
		
		# the vertical difference between the driving car and the sun elevataion
		v_angle_diff = abs(sunele - vyaw) # downslope the vyaw is positive
		v_angle_diff2 = abs(sunele + vyaw)
		
		# sunrise sunglare list
		if (h_angle_diff < hdeg and v_angle_diff < vdeg and sunele >0 and obstructed == 0):
			set_sunglare_time = hour*60 + minute
			sunsetglare_time_list.append(set_sunglare_time)
			sunsetglare_sunele_list.append(v_angle_diff)
			sunsetglare_horyaw_list.append(h_angle_diff)
			
		elif (h_angle_diff2 < hdeg and v_angle_diff2 < vdeg and sunele >0 and obstructed == 0):
			# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
			set_sunglare_time = hour*60 + minute
			sunsetglare_time_list.append(set_sunglare_time)
			sunsetglare_sunele_list.append(v_angle_diff2)
			sunsetglare_horyaw_list.append(h_angle_diff2)
			
			
	# save the surise sun glare result as a txt file
	sunglaretime = [min_interval*len(sunriseglare_time_list), sunriseglare_time_list, sunriseglare_sunele_list, sunriseglare_horyaw_list, min_interval*len(sunsetglare_time_list), sunsetglare_time_list, sunsetglare_sunele_list, sunsetglare_horyaw_list]
	# print ('The sunglare data is', sunglaretime)
	
	return sunglaretime



# estimate the sunrise and sunset sun glares based on the cylindrical panorama
def sunglare_batch(metadata, skyImgFolder, sunglarefile, latitude, longitude, zone, year, month, day):
	'''
	This function is used to generate the sunrise and sunset sun glare diagrams based on the 
	input metadata and the segmented skyImg on cylinderical panoramas
	
	parameters:
		metadata: the input metadata
		skyImgFolder: the folder of the segmented cylindrical images
		sunglarefile: the output sunglare file, csv
		azimuth, sunele: the azimuth and sun elevation angle
		zone, year, month, day
	return: 
		the csvfile of the sunglare results
		
	last modified by Xiaojiang Li, on March 17st, 2018 
	
	last modified by XL, May 27, 2018
	'''

	import os,os.path
	import numpy as np
	import csv
	from PIL import Image
	import SunposLib as sunpos
	import SunExpoLib as sunexpo


	# sunglarefile = open(os.path.join(root, sunglare_res),'w')
	sunglarefile = open(sunglarefile,'w')

	with sunglarefile:
		sunglareWriter = csv.writer(sunglarefile)

		# the metadata of the GSV panorama
		# metadata = os.path.join(root,'cleanedMetadata/Cleaned_Pnt_start0_end1000.txt')
		lines = open(metadata,"r")
		
		# loop all the panorama records
		for line in lines:
			elements = line.split(' ')
			pntnum = elements[1]
			panoId = elements[3]
			print('The panoId is:', panoId)
			
			panodate = elements[5]
			lon = float(elements[7])
			lat = float(elements[9])
			hyaw = float(elements[11])
			# hyaw2 = hyaw + 180
			# if hyaw2 > 360: hyaw2 = hyaw2 - 360 # the driving direction and the anti-driving direction
			
			vyaw = float(elements[13]) # downslope the vyaw is positive, http://maps.google.com/cbk?output=xml&ll=41.772323,-72.205024
			# print ('panid, panodate, lon, lat, hyaw, vyaw', panoId, panodate, longitude, latitude, hyaw, vyaw)
			
			# read the saved segmented image from the folder
			skyImgfile = os.path.join(skyImgFolder, panoId + '.jpg')
			try:
				skyImg = np.array(Image.open(skyImgfile))
			except:
				continue
				
			# generate the result for sunrise and sunset glare
			sunglaretime = sunglare_onesite(panoId, abs(lat), abs(lon), hyaw, vyaw, skyImg, 25, 25, zone, year, month, day)

			# save the sun glare result as a txt file
			meta = [pntnum, panoId, lon, lat, hyaw, vyaw]
			sunglaretime = meta + sunglaretime
			sunglareWriter.writerow(sunglaretime)



# estimate the sunrise and sunset sun glares based on the cylindrical panoramas
def sunglare_sunriseset_cylinder_readskyImg(metadata, skyImgFolder, sunglarefile, latitude, longitude, zone, year, month, day):
	'''
	This function is used to generate the sunrise and sunset sun glare diagrams based on the 
	input metadata and the segmented skyImg on cylinderical panoramas
	
	This is because the cylindrical panorama is much larger than the hemispherical image 
	around the horizon, this would be more suitable to estimate the obstruction on sun glare
	
	parameters:
		metadata: the input metadata
		skyImgFolder: the folder of the segmented cylindrical images
		sunglarefile: the output sunglare file, csv
		Other inputs: latitude, longitude, zone, year, month, day
		
	return:
		the csvfile of the sunglare results
	
	last modified by Xiaojiang Li, on March 17st, 2018 

	last modified by XL, May 26, 2018
	'''

	import os,os.path
	import numpy as np
	import csv
	from PIL import Image
	import SunposLib as sunpos
	import SunExpoLib as sunexpo


	# sunglarefile = open(os.path.join(root, sunglare_res),'w')
	sunglarefile = open(sunglarefile,'w')
	with sunglarefile:
		sunglareWriter = csv.writer(sunglarefile)

		# the metadata of the GSV panorama
		# metadata = os.path.join(root,'cleanedMetadata/Cleaned_Pnt_start0_end1000.txt')
		lines = open(metadata,"r")

		# panonum list, used to select only one pano for one site
		panonumlist = []
		panolonlist = []
		panolatlist = []
		panoidlist = []

		# loop all the panorama records
		for line in lines:
			elements = line.split(' ')
			pntnum = elements[1]
			panoId = elements[3]
			panodate = elements[5]
			lon = float(elements[7])
			lat = float(elements[9])
			hyaw = float(elements[11])
			hyaw2 = hyaw + 180
			if hyaw2 > 360: hyaw2 = hyaw2 - 360 # the driving direction and the anti-driving direction
			
			vyaw = float(elements[13]) # downslope the vyaw is positive, http://maps.google.com/cbk?output=xml&ll=41.772323,-72.205024
			print ('panid, panodate, lon, lat, hyaw, vyaw', panoId, panodate, longitude, latitude, hyaw, vyaw)

			# read the saved segmented image from the folder
			skyImgfile = os.path.join(skyImgFolder, panoId + '.jpg')
			try:
				skyImg = np.array(Image.open(skyImgfile))
			except:
				continue

			# list to save the sun glare, sunrise, sunset glare times
			sunglare_time_list = []
			sunriseglare_time_list = []
			sunsetglare_time_list = []

			for hour in range(5, 20):
				for minute in range(60):
					[azimuth, sunele] = sunpos.calcSun(latitude, longitude, zone, year, month, day, hour, minute, 30)

					obstructionpixelLabel = 0 #the obstruction pixel number in the skyImg
					glareSize = 24 # for the image size of 832*416

					# obstructed is 1 when the sunlight is blocked, 0 the sunlight is not blocked
					obstructed = sunexpo.Shaded_cylindrical_judgement_noaa(skyImg, obstructionpixelLabel, glareSize, azimuth, sunele, hyaw)

					#the horizontal difference between the driving adirection and the sun azimuth angle
					h_angle_diff = abs(azimuth - hyaw)
					h_angle_diff2 = abs(azimuth - hyaw2)

					# the vertical difference between the driving car and the sun elevataion
					v_angle_diff = abs(sunele - vyaw) # downslope the vyaw is positive
					v_angle_diff2 = abs(sunele + vyaw)

					# sunrise sunglare list
					if (hour < 12 and h_angle_diff < 25 and v_angle_diff < 25 and sunele >0 and obstructed == 0) or (hour < 12 and h_angle_diff2 < 25 and v_angle_diff2 < 25 and sunele >0 and obstructed == 0):
						# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
						rise_sunglare_time = hour*60 + minute
						sunriseglare_time_list.append(rise_sunglare_time)

					# sunset sunglare list
					if (hour >= 12 and h_angle_diff < 25 and v_angle_diff < 25 and sunele >0 and obstructed == 0) or (hour >= 12 and h_angle_diff2 < 25 and v_angle_diff2 < 25 and sunele >0 and obstructed == 0):
						# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
						set_sunglare_time = hour*60 + minute
						sunsetglare_time_list.append(set_sunglare_time)
						
					# sunglare list
					if (h_angle_diff < 25 and v_angle_diff < 25 and sunele >0 and obstructed == 0) or (h_angle_diff2 < 25 and v_angle_diff2 < 25 and sunele >0 and obstructed == 0):
						# print (hour, minute, sunele, azimuth, '----The driver is exposed to sun glare')
						# sunglare_time = '%s-%s'%(hour, minute)
						sunglare_time = hour*60 + minute
						sunglare_time_list.append(sunglare_time)
						
				# print ('The sunele at this hour is:', lon, lat, hour, sunele)
				
			# save the sun glare result as a txt file
			sunglaretime = [pntnum, panoId, lon, lat, hyaw, vyaw, len(sunriseglare_time_list), sunriseglare_time_list, len(sunsetglare_time_list), sunsetglare_time_list, len(sunglare_time_list), sunglare_time_list]
			print ('The sunglare data is', sunglaretime)
			sunglareWriter.writerow(sunglaretime)



# create shapefiles based on the csv file and the coordindates in the csv spreadsheet
def sunglare2shp(sunglareFile, outputShp):
	'''
	This function is used to save the csv file of the sun glare result to a shapefile
	last modified by Xiaojiang Li at March 1st, 2018
	
	parameters:
		sunglareFile: the result sunglare csv file
		outputShp: the result shapefile of the saved sun glare map
	'''

	import ogr, osr
	import csv
	import os,os.path
	import sys
	two_up_root = os.path.abspath(os.path.join(__file__ ,"../.."))
	libraries = os.path.join(two_up_root, 'libraries')
	sys.path.append(libraries)
	import MetadataLib as metalib


	gsvInfoLst = [] # create a list to save the gsv metadata and the sun glare information
	# headnamelist = ['pntNum', 'panoid','longitude', 'latitude', 'pano_yaw_degree', 'tilt_pitch_deg', 'duration', 'sunglare']
	headnamelist = ['pntNum', 'panoid','longitude', 'latitude', 'pano_yaw_degree', 'tilt_pitch_deg', 'risedur', 'riseglare', 'setdur', 'setglare', 'duration', 'sunglare']

	with open(sunglareFile, 'rb') as sunglare_csv:
		reader = csv.reader(sunglare_csv, delimiter=',')
		for row in reader:
			sunglare_time = row[6]
			if len(sunglare_time) < 1: print ('There is no sunglare')
			
			# create a dictionary to save the metadata and the sun glare
			fieldNum = len(headnamelist)
			newEle = {headnamelist[i]:row[i] for i in range(fieldNum)}
			if newEle not in gsvInfoLst:
				gsvInfoLst.append(newEle)

	metalib.CreatePointFeature_ogr(outputShp, gsvInfoLst)



# ---------Main function, example---------
if __name__ == "__main__":
	import datetime
	import os,os.path
	
	# specify the date information
	year = 2018
	month = 9
	day = 20
	
	# for Boston
	lat = 42.36589214
	lon = 71.1060453
	zone = 5
	daySavings = 0 # began on Mar11 ends on Nov 4, the function can recognize it itself
	
	root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/pano-lab/sunglare-pano'
	skyImgFolder = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Sun Expo/SunGlare/CambridgePanoHemi' # using the segmented hemispherical image
	skyImgFolder = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Sun Expo/SunGlare/CambridgePanoSegSlow' # using the segmented cylindrical image
	# metadata = os.path.join(root,'cleanedMetadata/Cleaned_Pnt_start0_end1000.txt')
	metadata = os.path.join(root,'cleanedMetadata')
	
	
	# based on the metadata, generate the sunglare map
	if os.path.isdir(metadata):
		print('This is a folder')
		for file in os.listdir(metadata):
			if os.path.splitext(file)[1] != '.txt':
				continue

			res_name = 'Sunglare_' + os.path.splitext(file)[0] + str(year) + '-' + str(month) + '-' + str(day) + '.csv'
			sunglare_res = os.path.join(root, res_name)
			metadatatxt = os.path.join(metadata, file)
			# sunglare_diagram_readskyImg(metadatatxt, skyImgFolder, sunglare_res, lat, lon, zone, year, month, day)
			# sunglare_sunriseset_cylinder_readskyImg(metadatatxt, skyImgFolder, sunglare_res, lat, lon, zone, year, month, day)
			sunglare_batch(metadatatxt, skyImgFolder, sunglare_res, lat, lon, zone, year, month, day)
	else: 
		res_name = 'Sunglare_' + os.path.splitext(file)[0] + str(year) + '-' + str(month) + '-' + str(day) + '.csv'
		sunglare_res = os.path.join(root, res_name)
		# sunglare_diagram_readskyImg(metadata, skyImgFolder, sunglare_res, lat, lon, zone, year, month, day)
		# sunglare_sunriseset_cylinder_readskyImg(metadatatxt, skyImgFolder, sunglare_res, lat, lon, zone, year, month, day)
		sunglare_batch(metadatatxt, skyImgFolder, sunglare_res, lat, lon, zone, year, month, day)
		
	
	# convert the csv file to shapefile
	# sunglare_res = os.path.join(root, 'Sunglare_obstruction_Pnt2018-9-20.csv')
	shpfile = os.path.splitext(os.path.basename(sunglare_res))[0] + '.shp'
	# sunglare_res = os.path.join(root, 'Sunglare_Cleaned_Pnt_start1000_end2000.csv')
	outputshp = os.path.join(root, shpfile)
	print ('The output shapefile is:', outputshp)
	sunglare2shp(sunglare_res, outputshp)



