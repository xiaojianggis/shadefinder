# This code is used to estiamte the sun position
# Check the NOAA sun calculator https://www.esrl.noaa.gov/gmd/grad/solcalc/azel.html
# Copyright(C) Xiaojiang Li, MIT Senseable City Lab
# last modified Feb 26, 2018

# last modified on March 7th, 2018, by Xiaojiang Li

import os, os.path
import math
import numpy as np


def isLeapYear(yr):
	return ((yr % 4 == 0 and yr % 100 != 0) or yr % 400 == 0)

def radToDeg(angleRad):
	return (180.0 * angleRad / math.pi)

def degToRad(angleDeg):
	return (math.pi*angleDeg / 180.0)

def calcDayOfYear(mn, dy, lpyr):
	'''
	Finds numerical day-of-year from mn, day and lp year info
	month: January = 1
	day  : 1 - 31	
	lpyr : 1 if leap year, 0 if not
	'''

	if lpyr == 1:
		k = 1
	else:
		k=2

	doy = int((275 * mn)/9) - k * int((mn + 9)/12) + dy - 30
	# doy = Math.floor((275 * mn)/9) - k * Math.floor((mn + 9)/12) + dy -30

	return doy

# doy = calcDayOfYear(3, 2, isLeapYear(2000))


def calcDayOfWeek(juld):
	'''
	Derives weekday from Julian Day
	juld : 
		Julian Day
	Return value:
		String containing name of weekday
	'''

	# DOW = (A==0)?"Sunday":(A==1)?"Monday":(A==2)?"Tuesday":(A==3)?"Wednesday":(A==4)?"Thursday":(A==5)?"Friday":"Saturday"

	A = (juld + 1.5) % 7
	if A == 0:
		DOW = "Sunday"
	elif A == 1:
		DOW = "Monday"
	elif A == 2:
		DOW = "Tuesday"
	elif A == 3:
		DOW = "Wednesday"
	elif A == 4:
		DOW = "Thursday"
	elif A == 5:
		DOW = "Friday"
	else:
		DOW = "Saturday"

	return DOW


def calcJD(year, month, day):
	'''
	Julian day from calendar day
	Number is returned for start of day.  Fractional days should be	added later
	
	arguments:
		year : 4 digit year
		month: January = 1
		day  : 1 - 31	
	Return value:
		The Julian day corresponding to the date
	'''

	if month <= 2:
		year = year - 1
		month = month + 12

	A = int(year/100)
	# B = 2 - A + Math.floor(A/4)
	B = 2 - A + int(A/4)
	# JD = Math.floor(365.25*(year + 4716)) + Math.floor(30.6001*(month+1)) + day + B - 1524.5;
	JD = int(365.25*(year + 4716)) + int(30.6001*(month+1)) + day + B - 1524.5

	return JD


def calcDateFromJD(jd):
	'''
	Calendar date from Julian Day
	jd: 
		Julian Day	
	Return value:
		String date in the form DD-MONTHNAME-YYYY
	'''
	z = int(jd + 0.5)
	f = (jd + 0.5) - z
	if z < 2299161:
		A = z
	else:
		alpha = int((z - 1867216.25)/36524.25)
		A = z + 1 + alpha - int(alpha/4)

	B = A + 1524
	C = int((B - 122.1)/365.25)
	D = int(365.25 * C)
	E = int((B - D)/30.6001)
	day = B - D - int(30.6001 * E) + f

	if E < 14:
		month = E - 1
	else:
		month = E - 13

	if month > 2:
		year = C - 4716
	else:
		year = C - 4715

	return day, month, year


def calcDayFromJD (jd):
	'''
	Calendar day (minus year) from Julian Day
	jd: 
		Julian Day	
	Return value:
		String date in the form DD-MONTH
	'''
	z = int(jd + 0.5)
	f = (jd + 0.5) - z

	if z < 2299161:
		A = z
	else:
		alpha = int((z - 1867216.25)/36524.25)
		A = z + 1 + alpha - int(alpha/4)

	B = A + 1524
	C = int((B - 122.1)/365.25)
	D = int(365.25 * C)
	E = int((B - D)/30.6001)

	day = B - D - int(30.6001 * E) + f

	if E < 14:
		month = E - 1
	else:
		month = E - 13

	if month > 2:
		year = C - 4716
	else:
		year = C - 4715


def calcTimeJulianCent(jd):
	T = (jd - 2451545.0)/36525.0
	return T

def calcJDFromJulianCent(t):
	'''
	convert centuries since J2000.0 to Julian Day
	t: 
		t : number of Julian centuries since J2000.0
	return value:
		the Julian Day corresponding to the t value
	'''

	JD = t * 36525.0 + 2451545.0
	return JD

def calcGeomMeanLongSun(t):
	'''
	calculate the Geometric Mean Longitude of the Sun
	t:
		number of Julian centuries since J2000.0
	return value:
		the Geometric Mean Longitude of the Sun in degrees
	'''
	L0 = 280.46646 + t * (36000.76983 + 0.0003032 * t)
	while L0 > 360.0:
		L0 = L0 - 360

	while L0 < 0:
		L0 = L0 + 360

	return L0


def calcGeomMeanAnomalySun(t):
	'''
	calculate the Geometric Mean Anomaly of the Sun
		t : number of Julian centuries since J2000.0
		return: the Geometric Mean Anomaly of the Sun in degrees
	'''
	M = 357.52911 + t * (35999.05029 - 0.0001537 * t)
	return M

def calcEccentricityEarthOrbit(t):
	'''
	Purpose: calculate the eccentricity of earth's orbit
		t : number of Julian centuries since J2000.0
		return the unitless eccentricity
	'''
	e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
	return e


def calcSunEqOfCenter(t):
	'''
	Purpose: calculate the equation of center for the sun
	t : number of Julian centuries since J2000.0
	return in degrees
	'''

	m = calcGeomMeanAnomalySun(t)
	mrad = degToRad(m)
	sinm = math.sin(mrad)
	sin2m = math.sin(mrad+mrad)
	sin3m = math.sin(mrad+mrad+mrad)
	C = sinm * (1.914602 - t * (0.004817 + 0.000014 * t)) + sin2m * (0.019993 - 0.000101 * t) + sin3m * 0.000289

	return C


def calcSunTrueLong(t):
	'''
	calculate the true longitude of the sun

	return sun's true longitude in degrees
	'''
	l0 = calcGeomMeanLongSun(t)
	c = calcSunEqOfCenter(t)
	O = l0 + c

	return O


def calcSunTrueAnomaly(t):
	'''
	calculate the true anamoly of the sun

	return sun's true anamoly in degrees	
	'''
	m = calcGeomMeanAnomalySun(t)
	c = calcSunEqOfCenter(t)

	v = m + c
	return v


def calcSunRadVector(t):
	'''
	calculate the distance to the sun in AU

	return: sun radius vector in AUs
	'''

	v = calcSunTrueAnomaly(t)
	e = calcEccentricityEarthOrbit(t)

	R = (1.000001018 * (1 - e * e)) / (1 + e * math.cos(degToRad(v)))

	return R


def calcSunApparentLong(t):
	'''
	calculate the apparent longitude of the sun
		return: sun's apparent longitude in degrees
	'''
	o = calcSunTrueLong(t)
	omega = 125.04 - 1934.136 * t
	lambda_v = o - 0.00569 - 0.00478 * math.sin(degToRad(omega))

	return lambda_v

def calcMeanObliquityOfEcliptic(t):
	'''
	calculate the mean obliquity of the ecliptic

		return mean obliquity in degrees
	'''
	seconds = 21.448 - t*(46.8150 + t*(0.00059 - t*(0.001813)))
	e0 = 23.0 + (26.0 + (seconds/60.0))/60.0

	return e0


def calcObliquityCorrection(t):
	'''
	calculate the corrected obliquity of the ecliptic

	return: corrected obliquity in degrees
	'''

	e0 = calcMeanObliquityOfEcliptic(t)
	omega = 125.04 - 1934.136 * t
	e = e0 + 0.00256 * math.cos(degToRad(omega))

	return e

def calcSunRtAscension(t):
	'''
	calculate the right ascension of the sun

	return :sun's right ascension in degrees
	'''
	e = calcObliquityCorrection(t)
	lambda_v = calcSunApparentLong(t)
	tananum = (math.cos(degToRad(e)) * math.sin(degToRad(lambda_v)))
	tanadenom = (math.cos(degToRad(lambda_v)))

	alpha = radToDeg(math.atan(tananum/tanadenom))
	return alpha


def calcSunDeclination(t):
	'''
	calculate the declination of the sun
	return: 
		sun's declination in degrees
	'''
	e = calcObliquityCorrection(t)
	lambda_v = calcSunApparentLong(t)
	sint = math.sin(degToRad(e)) * math.sin(degToRad(lambda_v))
	theta = radToDeg(math.asin(sint))

	return theta


def calcEquationOfTime(t):
	'''
	calculate the difference between true solar time and mean
	return: equation of time in minutes of time
	'''
	epsilon = calcObliquityCorrection(t)
	l0 = calcGeomMeanLongSun(t)
	e = calcEccentricityEarthOrbit(t)

	m = calcGeomMeanAnomalySun(t)
	y = math.tan(degToRad(epsilon)/2.0)
	y = y**2

	sin2l0 = math.sin(2.0 * degToRad(l0))
	sinm   = math.sin(degToRad(m))
	cos2l0 = math.cos(2.0 * degToRad(l0));
	sin4l0 = math.sin(4.0 * degToRad(l0));
	sin2m  = math.sin(2.0 * degToRad(m));

	Etime = y * sin2l0 - 2.0 * e * sinm + 4.0 * e * y * sinm * cos2l0 - 0.5 * y * y * sin4l0 - 1.25 * e * e * sin2m

	return radToDeg(Etime)*4.0 #/ in minutes of time


#Return the hour angle for the given location, decl, and time of day
def calcHourAngle(time, longitude, eqtime):
	return (15.0*(time - (longitude/15.0) - (eqtime/60.0))) # in degree



# // *****************************************************
# // *****************************************************
# // ***********  Main calculation routine  **************
# // *****************************************************
# // *****************************************************

def calcSun(latitude, longitude, zone, year, month, day, hh, mm, ss):
	'''
	calculate solar position for the entered date, time and	location. 
	 Results are reported in azimuth and elevation

	argument: 
		latitude
		longitude
		zone: the time zone using UTC, Colorado is 7, Boston is 5
		year, month, day, hh, mm, ss are the time
	return:
		the azimuth and the sun elevation
	'''
	
	
	# for daytime saving, daytime saving judgement, start on March 11, and ends on Nov 4
	if month < 3 or month > 11 or (month ==3 and day < 11) or (month == 11 and day > 4):
		daySavings = 0
	else:
		daySavings = 1
		
	if daySavings == 1:
		hh = hh - 1


	timenow = hh + mm/60 + ss/3600 + zone

	# Calculate the JD
	JD = calcJD(year, month, day)

	# calculate the day of 
	dow = calcDayOfWeek(JD)

	doy = calcDayOfYear(month, day, isLeapYear(year))
	T = calcTimeJulianCent(JD + timenow/24.0)

	R = calcSunRadVector(T)
	alpha = calcSunRtAscension(T)
	theta = calcSunDeclination(T)
	Etime = calcEquationOfTime(T)

	eqTime = Etime
	solarDec = theta #in degrees
	earthRadVec = R
	solarTimeFix = eqTime - 4.0 * longitude + 60.0 * zone
	trueSolarTime = hh * 60.0 + mm + ss/60.0 + solarTimeFix

	while trueSolarTime > 1440:
		trueSolarTime = trueSolarTime - 1440

	hourAngle = trueSolarTime / 4.0 - 180.0
	if hourAngle < -180:
		hourAngle = hourAngle + 360

	haRad = degToRad(hourAngle)
	csz = math.sin(degToRad(latitude)) * \
				math.sin(degToRad(solarDec)) + \
				math.cos(degToRad(latitude)) * \
				math.cos(degToRad(solarDec)) * math.cos(haRad);

	if csz > 1.0: csz = 1
	elif csz < -1.0: csz = -1

	zenith = radToDeg(math.acos(csz))
	azDenom = (math.cos(degToRad(latitude)) * math.sin(degToRad(zenith)))

	if abs(azDenom) > 0.001:
		azRad = (( math.sin(degToRad(latitude)) * math.cos(degToRad(zenith)) ) - math.sin(degToRad(solarDec))) / azDenom;
		if abs(azRad) > 1.0:
			if (azRad < 0):
				azRad = -1.0
			else:
				azRad = 1.0
			
		azimuth = 180.0 - radToDeg(math.acos(azRad))

		if hourAngle > 0.0:
			azimuth = -azimuth
	else:
		if latitude > 0.0:
			azimuth = 180.0
		else:
			azimuth = 0.0
			
	if azimuth < 0.0:
		azimuth = azimuth + 360
		
	exoatmElevation = 90.0 - zenith
	if exoatmElevation > 85.0:
		refractionCorrection = 0.0
	else:
		te = math.tan(degToRad(exoatmElevation))
		if exoatmElevation > 5.0:
			refractionCorrection = 58.1 / te - 0.07 / (te*te*te) + 0.000086 / (te*te*te*te*te)
		elif exoatmElevation > -0.575:
			refractionCorrection = 1735.0 + exoatmElevation * (-518.2 + exoatmElevation * (103.4 +
						exoatmElevation * (-12.79 + exoatmElevation * 0.711) ) );
		else:
			refractionCorrection = -20.774 / te

		refractionCorrection = refractionCorrection / 3600.0

	solarZen = zenith - refractionCorrection


	# print ('The solarZen is:=========', solarZen)


	if solarZen < 108.0:
		# azimuth = (int(100*azimuth))/100
		# elevation = (int(100*(90.0 - solarZen)))/100

		azimuth = (100*azimuth)/100
		elevation = (100*(90.0 - solarZen))/100

		if solarZen < 90.0:
			coszen = (int(10000.0*(math.cos(degToRad(solarZen)))))/10000.0;
		else:
			coszen = 0
	else:
		azimuth = -999 #dark
		elevation = -999
		coszen = 0

	# print ('The year, month, day, hour, min, second are', year, month, day, hh, mm, ss)
	# print ('The azimuth, and sunelevation angles are:', azimuth, elevation)

	# azimuth = -(azimuth - 90)
	# if azimuth < 0: azimuth = azimuth + 360
	
	return azimuth, elevation



def Sunele2csv_1(lat, lon, zone, year, day, outputcsvfile):
	'''
	This function is used to save the sun elevation angles in different days 
	of one year to csv file
	
	parameters:
		lat: the latitude of the location
		lon: the longitude of the location
		zone: the time zone of the study area, compared with the UTC, Boston is 5
		year: the year of the sun elevation diagram
		day: the day of one month, in order to plot the sun elevation diagram in different month of the day
		outputcsvfile: the filename of the ouput csv file
	
	(C) Copyright(c) Xiaojiang Li, MIT Senseable City Lab
	Last modified by Xiaojiang Li on March 11, 2018
	
	'''

	import csv
	import os, os.path

	
	ouputcsv = open(outputcsvfile,'w')
	with ouputcsv:
		csvWriter = csv.writer(ouputcsv)
		day = 15 # the middle of one month
		mm = 0
		ss = 0

		# the title of the record
		title = ['month', 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
		csvWriter.writerow(title)

		for month in range(1, 13):
			# daytime saving judgement, start on March 11, and ends on Nov 4
			if month < 3 or month > 11 or (month ==3 and day < 11) or (month == 11 and day > 4):
				daySavings = 0
			else:
				daySavings = 1

			# the list of the sun elevation angle
			sunelelist = [month]
			for hh in range(5, 20):
				[azimuth, sunele] = calcSun(lat, lon, zone, year, month, day, hh, mm, ss)
				print ('The sun azimuth and sunele are:', hh, azimuth, sunele)
				if sunele < 0: sunele = 0
				sunelelist.append(sunele)

			# writeline = [month, sunelelist]
			csvWriter.writerow(sunelelist)
	ouputcsv.close()




def Sunele2csv(lat, lon, zone, year, day, outputcsvfile):
	'''
	This function is used to save the sun elevation angles in different days 
	of one year to csv file
	
	parameters:
		lat: the latitude of the location
		lon: the longitude of the location
		zone: the time zone of the study area, compared with the UTC, Boston is 5
		year: the year of the sun elevation diagram
		day: the day of one month, in order to plot the sun elevation diagram in different month of the day
		outputcsvfile: the filename of the ouput csv file
	
	(C) Copyright(c) Xiaojiang Li, MIT Senseable City Lab
	Last modified by Xiaojiang Li on March 11, 2018
	
	'''

	import csv
	import os, os.path

	
	ouputcsv = open(outputcsvfile,'w')
	with ouputcsv:
		csvWriter = csv.writer(ouputcsv)
		day = 15 # the middle of one month
		mm = 0
		ss = 0

		# the title of the record
		title = ['Jan', 'Feb', 'Mar', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		csvWriter.writerow(title)

		
		for hh in range(5, 21):
			# the list of the sun elevation angle
			sunelelist = []

			for month in range(1, 13):
				# daytime saving judgement, start on March 11, and ends on Nov 4
				if month < 3 or month > 11 or (month ==3 and day < 11) or (month == 11 and day > 4):
					daySavings = 0
				else:
					daySavings = 1

				[azimuth, sunele] = calcSun(lat, lon, zone, year, month, day, hh, mm, ss)
				# print ('The sun azimuth and sunele are:', hh, azimuth, sunele)
				if sunele < 0: sunele = 'NA'
				sunelelist.append(sunele)

			# writeline = [month, sunelelist]
			csvWriter.writerow(sunelelist)
	ouputcsv.close()



def Sunazimuth2csv_1(lat, lon, zone, year, day, outputcsvfile):
	'''
	This function is used to save the sun azimuth angles in different days 
	of one year to csv file
	
	parameters:
		lat: the latitude of the location
		lon: the longitude of the location
		zone: the time zone of the study area, compared with the UTC, Boston is 5
		year: the year of the sun elevation diagram
		day: the day of one month, in order to plot the sun elevation diagram in different month of the day
		outputcsvfile: the filename of the ouput csv file
	
	(C) Copyright(c) Xiaojiang Li, MIT Senseable City Lab
	Last modified by Xiaojiang Li on March 11, 2018
	'''

	import csv
	import os, os.path

	mm = 0
	ss = 0

	ouputcsv = open(outputcsvfile,'w')
	with ouputcsv:
		csvWriter = csv.writer(ouputcsv)

		# the title of the record
		title = ['month', 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
		csvWriter.writerow(title)

		for month in range(1, 13):
			# daytime saving judgement, start on March 11, and ends on Nov 4
			if month < 3 or month > 11 or (month ==3 and day < 11) or (month == 11 and day > 4):
				daySavings = 0
			else:
				daySavings = 1

			# the list of the sun elevation angle
			azimuthlist = [month]
			for hh in range(5, 21):
				# the east is zero
				[azimuth, sunele] = calcSun(lat, lon, zone, year, month, day, hh, mm, ss)

				# the north is zero now
				azimuth = -(azimuth - 90)
				if azimuth < 0: azimuth = azimuth + 360

				# sunglare azimuth zone
				if sunele > 2 and sunele < 25:
					downlimit = azimuth - 25
					uplimit = azimuth + 25
					print ('The month, hour, downlimit, uplimit are:==============', month, hh, downlimit, uplimit)

				# print ('The sun azimuth and sunele are:', hh, azimuth, sunele)
				azimuthlist.append(azimuth)

			# writeline = [month, sunelelist]
			csvWriter.writerow(azimuthlist)
	ouputcsv.close()





def Sunazimuth2csv(lat, lon, zone, year, day, outputcsvfile):
	'''
	This function is used to save the sun azimuth angles in different days 
	of one year to csv file
	
	parameters:
		lat: the latitude of the location
		lon: the longitude of the location
		zone: the time zone of the study area, compared with the UTC, Boston is 5
		year: the year of the sun elevation diagram
		day: the day of one month, in order to plot the sun elevation diagram in different month of the day
		outputcsvfile: the filename of the ouput csv file
	
	(C) Copyright(c) Xiaojiang Li, MIT Senseable City Lab
	Last modified by Xiaojiang Li on March 11, 2018
	
	'''

	import csv
	import os, os.path

	mm = 0
	ss = 0

	ouputcsv = open(outputcsvfile,'w')
	with ouputcsv:
		csvWriter = csv.writer(ouputcsv)

		# the title of the record
		title = ['Jan', 'Feb', 'Mar', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		csvWriter.writerow(title)
		
		for hh in range(5, 21):
			# the list of the sun elevation angle
			azimuthlist = []
			for month in range(1, 13):
				# daytime saving judgement, start on March 11, and ends on Nov 4
				if month < 3 or month > 11 or (month ==3 and day < 11) or (month == 11 and day > 4):
					daySavings = 0
				else:
					daySavings = 1

				[azimuth, sunele] = calcSun(lat, lon, zone, year, month, day, hh, mm, ss)

				# the north is zero now
				azimuth = -(azimuth - 90)
				if azimuth < 0: azimuth = azimuth + 360

				if azimuth < 0: azimuth = 'NA'

				# print ('The sun azimuth and sunele are:', hh, azimuth, sunele)
				azimuthlist.append(azimuth)

			# writeline = [month, sunelelist]
			csvWriter.writerow(azimuthlist)
	ouputcsv.close()



# This section contains subroutines used in calculating solar position */
if __name__ == "__main__": 

	# For Boston
	latitude = 42.35
	longitude = 71.05
	zone = 5
	
	# # # Colorado, Bouder
	# # latitude = 40.125
	# # longitude = 105.237
	# # zone = 7
	
	# For Miami, Florida
	latitude = 25.762445
	longitude = 80.195792

	# # date
	year = 2018
	month = 5
	day = 1
	 
	# time
	hh = 12
	mm = 0
	ss = 0
	
	for hh in range(5, 20):
		[azimuth, sunele] = calcSun(latitude, longitude, zone, year, month, day, hh, mm, ss)
		print ('The sun azimuth and sunele are:', hh, azimuth, sunele)
		
	# output_sunele_csvfile = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/Sunele-%s-%s-%s.csv'%(month, day, year)
	# output_azimuth_csvfile = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/SunGlare/Sunazimuth-%s-%s-%s.csv'%(month,day,year)
	# Sunele2csv(latitude, longitude, zone, year, day, output_sunele_csvfile)
	# Sunazimuth2csv(latitude, longitude, zone, year, day, output_azimuth_csvfile)
	# Sunazimuth2csv_1(latitude, longitude, zone, year, day, output_azimuth_csvfile)
