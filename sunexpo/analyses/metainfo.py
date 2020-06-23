import csv
import os, os.path


root = '/home/jiang/Documents/researchProj/thermal-injustice/datasets'
city = 'Philadephia'
city = 'Houston'
city = 'SanAntonio'

metacsv = city + 'meta.csv'
imgsfolder = os.path.join(root, city, 'cylinder_img')

with open(metacsv, mode='w') as meta:
    meta_writer = csv.writer(meta, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    meta_writer.writerow(['lat', 'lon', 'yaw', 'year', 'month'])
    for idx, file in enumerate(os.listdir(imgsfolder)):
        elem = file.split(' - ')
        lat = elem[0]
        lon = elem[1]
        yaw = elem[2]
        date = elem[-1][:-4]
        year = date[0:4]
        month = date[-2:]
        if idx%1000 == 0: print('The year and month are:', year, month, lat, lon, yaw)
        
        meta_writer.writerow([lat, lon, yaw, year, month])
