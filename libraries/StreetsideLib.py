import math
from PIL import Image


def Streetside_Img_collector(samplePntShp, outMetaRoot, outGSVRoot):
    '''
    This function is used to collect StreetSide view images, the input of the function
    is the shapefile of sample site, the coordinates of those sample sites will be 
    used as input to collect Street-side view images

    First version Feb 17, 2019
    Copyright(C) Xiaojiang Li, MIT Senseable City Lab, Temple University
	
    parameters:
        samplePntShp: the shapefile of the sample site
        outMetaRoot: the root of the output metadata
        outGSVRoot: the output root of the streetside image
    '''

    import urllib
    from io import StringIO
    from PIL import Image
    import ogr,osr
    import os, os.path
    import time

    if not os.path.exists(outGSVRoot):
        os.makedirs(outGSVRoot)
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    # change the projection of shapefile to the WGS84
    dataset = driver.Open(samplePntShp)
    layer = dataset.GetLayer()
    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)
    
    featureNum = layer.GetFeatureCount()
    num = 1000 # process 1 k each time
    batch = int(featureNum/num + 0.5)

    for b in range(batch):
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum
        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        ouputGSVinfoFile = os.path.join(outMetaRoot,ouputTextFile)
        
        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue

        time.sleep(5)

        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer.GetFeature(i)
                geom = feature.GetGeometryRef()

                # trasform the current projection of input shapefile to WGS84
                geom.Transform(transform)
                lon = float(geom.GetX())
                lat = float(geom.GetY())
                if i % 100 == 0: print('You have collected %s StreetSide images'%(i))
                try:
                    [heading, year, month] = Streetside_downloader(lon, lat, outGSVRoot)
                    lineTxt = 'lon: %s lat: %s heading: %s year: %s month: %s\n'%(lon, lat, heading, year, month)
                    panoInfoText.write(lineTxt)
                except:
                    print('No Streetside images here')
                    continue

        panoInfoText.close()


def Streetside_downloader(lon, lat, outputdir):
    '''
    This function is used to download the Street-side imagery using Google Street View
    
    modified by Feb 17, 2019
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab, Temple University
    
    Parameters:
        lon: the longitude of the site
        lat: the latitude of the site
        outputdir: the output directory of the mosaiced cube images
    
    '''
    
    import os, os.path
    import numpy as np
    from PIL import Image
    import time
    import sys
    import re
    
    
    monthDict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    
    key = r'Av7_Q7LSu3RPKCTqa---_VKPu3QQ-NJsOc0IFU4xmubJl4Pb8RVg-7uei9uydRSU'
    keys = ['Av7_Q7LSu3RPKCTqa---_VKPu3QQ-NJsOc0IFU4xmubJl4Pb8RVg-7uei9uydRSU', 
            'Ao3MXawqbYdtStO8oFd_BZRX3QLe7NFqo87AC_UmIwYHGObqcHmY5GtbhSUnAdey',
            'AveY71QE0d-d1qYnRuaeiK29VjHQQuFleWBFEyXKQ1Fj1j9GR6OB9_nB7apJuNjS']
    
    meta_url = 'http://dev.virtualearth.net/REST/v1/Imagery/MetaData/Streetside/%s,%s?key=%s'%(lat, lon, key)
    
    time.sleep(0.1)
    
    # Access the metadata, using different url reading method in python2 and python3
    if sys.version_info[0] == 2:
        # from urllib2 import urlopen
        import urllib
        
        metaData = urllib.urlopen(meta_url).read()
        
    if sys.version_info[0] == 3:
        import urllib.request
        
        request = urllib.request.Request(meta_url)
        metaData = urllib.request.urlopen(request).read()
    
    metaData = str(metaData)
    
    # parse the metadata information
    heading = metaData.split('"he":')[1].split(',')[0]
    date = metaData.split('"vintageStart":')[1].split(",")[0]
    url = metaData.split('imageUrl":')[1].split(',"imageUrlSubdomains"')[0]
    size = int(metaData.split('"imageHeight":')[1].split(',')[0])
    tile = re.findall('hs\d*[0-9]', url)[0]
    
    # download tiles of street-side images and mosaic together
    mosaicImg = np.zeros((3*size, 4*size,3),'uint8')
    
    # Assign identifiers to the faces of the cube
    cubes = ['10', '01', '02', '03', '11', '12']# left, forward, right, right, back, up, down
    
    # Access the imagery, using different url reading method in python2 and python3
    for cube in cubes:
        imagery_url = 'http://ecn.t1.tiles.virtualearth.net/tiles/%s%s?g=6617&key=%s'%(tile, cube, key)
        # print('The url address is:', imagery_url)
        
        if sys.version_info[0] == 2:
            import cStringIO
            imgfile = cStringIO.StringIO(urllib.urlopen(imagery_url).read())

        if sys.version_info[0] == 3:
            import urllib.request
            import io

            request = urllib.request.Request(imagery_url)
            imgfile = io.BytesIO(urllib.request.urlopen(request).read())

        tileImg = np.array(Image.open(imgfile))
        dims = tileImg.shape
        width = dims[0]
        height = dims[1]

        if cube == '10':
            mosaicImg[height: 2*height, 0: width, :] = tileImg
        elif cube == '01':
            mosaicImg[height: 2*height, width: 2*width, :] = tileImg
        elif cube == '02':
            mosaicImg[height: 2*height, 2*width: 3*width, :] = tileImg
        elif cube == '03':
            mosaicImg[height: 2*height, 3*width: 4*width, :] = tileImg
        elif cube == '11':
            mosaicImg[0:height, width: 2*width, :] = tileImg
        else:
            mosaicImg[2*height: 3*height, width: 2*width, :] = tileImg
    
    year = date.split(' ')[2]
    month = monthDict[date.split(' ')[1]]
    
    # the output result, lat - lon - heading - year-month.jpg
    outputfile = '%s - %s - %s - %s.jpg'%(lat, lon, heading, year + '-' + month)
    output = os.path.join(outputdir, outputfile)

    # save the mosaic image
    img = Image.fromarray(mosaicImg)
    del mosaicImg, tileImg
    img.save(output)
    del img
    
    return heading, year, month



def spherical_coordinates(i, j, w, h):
    """ Returns spherical coordinates of the pixel from the output image. 
    """
    theta = 2*float(i)/float(w)-1
    phi = 2*float(j)/float(h)-1
    # phi = lat, theta = long
    return phi*(math.pi/2), theta*math.pi


def vector_coordinates(phi, theta):
    """ Returns 3D vector which points to the pixel location inside a sphere. """
    return (math.cos(phi) * math.cos(theta),  # X
            math.sin(phi),                    # Y
            math.cos(phi) * math.sin(theta))  # Z


# Assign identifiers to the faces of the cube
FACE_Z_POS = 1  # Left
FACE_Z_NEG = 2  # Right
FACE_Y_POS = 3  # Top
FACE_Y_NEG = 4  # Bottom
FACE_X_NEG = 5  # Front
FACE_X_POS = 6  # Back


def get_face(x, y, z):
    """ Uses 3D vector to find which cube face the pixel lies on. """
    largest_magnitude = max(abs(x), abs(y), abs(z))
    if largest_magnitude - abs(x) < 0.00001:
        return FACE_X_POS if x < 0 else FACE_X_NEG
    elif largest_magnitude - abs(y) < 0.00001:
        return FACE_Y_POS if y < 0 else FACE_Y_NEG
    elif largest_magnitude - abs(z) < 0.00001:
        return FACE_Z_POS if z < 0 else FACE_Z_NEG


def raw_face_coordinates(face, x, y, z):
    """
    Return coordinates with necessary sign (- or +) depending on which face they lie on.
    
    From Open-GL specification (chapter 3.8.10) https://www.opengl.org/registry/doc/glspec41.core.20100725.pdf
    """
    if face == FACE_X_NEG:
        xc = z
        yc = y
        ma = x
        return xc, yc, ma
    elif face == FACE_X_POS:
        xc = -z
        yc = y
        ma = x
        return xc, yc, ma
    elif face == FACE_Y_NEG:
        xc = z
        yc = -x
        ma = y
        return xc, yc, ma
    elif face == FACE_Y_POS:
        xc = z
        yc = x
        ma = y
        return xc, yc, ma
    elif face == FACE_Z_POS:
        xc = x
        yc = y
        ma = z
        return xc, yc, ma
    elif face == FACE_Z_NEG:
        xc = -x
        yc = y
        ma = z
        return xc, yc, ma


def raw_coordinates(xc, yc, ma):
    """ Return 2D coordinates on the specified face relative to the bottom-left corner of the face. Also from Open-GL spec."""
    return (float(xc)/abs(float(ma)) + 1) / 2, (float(yc)/abs(float(ma)) + 1) / 2


def face_origin_coordinates(face, n):
    """ Return bottom-left coordinate of specified face in the input image. """
    if face == FACE_X_NEG:
        return n, n
    elif face == FACE_X_POS:
        return 3*n, n
    elif face == FACE_Z_NEG:
        return 2*n, n
    elif face == FACE_Z_POS:
        return 0, n
    elif face == FACE_Y_POS:
        return n, 0
    elif face == FACE_Y_NEG:
        return n, 2*n


def normalized_coordinates(face, x, y, n):
    """ Return pixel coordinates in the input image where the specified pixel lies. """
    face_coords = face_origin_coordinates(face, n)
    normalized_x = math.floor(x*n)
    normalized_y = math.floor(y*n)

    # Stop out of bound behaviour
    if normalized_x < 0:
        normalized_x = 0
    elif normalized_x >= n:
        normalized_x = n-1
    if normalized_y < 0:
        normalized_x = 0
    elif normalized_y >= n:
        normalized_y = n-1

    return face_coords[0] + normalized_x, face_coords[1] + normalized_y


def find_corresponding_pixel(i, j, w, h, n):
    """
    :param i: X coordinate of output image pixel
    :param j: Y coordinate of output image pixel
    :param w: Width of output image
    :param h: Height of output image
    :param n: Height/Width of each square face
    :return: Pixel coordinates for the input image that a specified pixel in the output image maps to.
    """

    spherical = spherical_coordinates(i, j, w, h)
    vector_coords = vector_coordinates(spherical[0], spherical[1])
    face = get_face(vector_coords[0], vector_coords[1], vector_coords[2])
    raw_face_coords = raw_face_coordinates(face, vector_coords[0], vector_coords[1], vector_coords[2])

    cube_coords = raw_coordinates(raw_face_coords[0], raw_face_coords[1], raw_face_coords[2])

    return normalized_coordinates(face, cube_coords[0], cube_coords[1], n)



def convert_img(inimg, outfile):
    '''
    Convert the cube images into cylindrical panoramas, 
    parameters:
        inimg: the numpy array of mosaiced cube imgs
        outfile: the ouput cylindrical panorama images, string, panorama name
    '''
    
    # inimg = Image.open(infile)
    inimg = Image.fromarray(inimg) # convert numpy array into PIL Image format
    wo, ho = inimg.size

    # Calculate height and width of output image, and size of each square face
    h = int(wo/3)
    w = 2*h
    n = int(ho/3)
    # Create new image with width w, and height h
    outimg = Image.new('RGB', (w, h))
    # print("The ouput file size is:", w, h)
    
    # For each pixel in output image find colour value from input image
    for ycoord in range(0, h):
        for xcoord in range(0, w):
            corrx, corry = find_corresponding_pixel(xcoord, ycoord, w, h, n)

            outimg.putpixel((xcoord, ycoord), inimg.getpixel((corrx, corry)))
            
    outimg.save(outfile, 'PNG')



def cubeImageMasaic(leftImg, rightImg, upImg, downImg, frontImg, backImg):
    '''
    This function is used to mosaci the left, right, up, down, front, and back into a masaic
    img, which would be further used to convert into a cylindrical panorama
    '''

    import glob
    import numpy as np
    from PIL import Image
    from matplotlib import pyplot as plt

    dims = leftImg.shape
    width = dims[0]
    height = dims[1]

    mosaicImg = np.zeros((3*height, 4*width,3),'uint8')

    mosaicImg[height: 2*height, 0: width, :] = leftImg
    mosaicImg[height: 2*height, width: 2*width, :] = frontImg
    mosaicImg[height: 2*height, 2*width: 3*width, :] = rightImg
    mosaicImg[height: 2*height, 3*width: 4*width, :] = backImg
    mosaicImg[0:height, width: 2*width, :] = upImg
    mosaicImg[2*height: 3*height, width: 2*width, :] = downImg


    return mosaicImg


def cylinder2perspective(inputCylinderImage,outputPerspectiveImg,heading,fov, yaw, tilt_yaw, pitch):
    '''
    # This program is used to convert cylindrical panorama images to perspective image
    # The field of view is set to 70
    # In the perspective projection, there are a couple of pareamters, the first is the
    # field of view angle, the second is the heading angle, the third is the pitch angle
    # (Just like what Google Street View Image API)
    
    # Copyright (C) Xiaojiang Li, MIT Senseable City Lab
    # First version Jan 3, 2017
    
    Parameters:
        inputFisheyeImage: the input fisheye image
        outputCylinderPano: the generated cylindrical panorama
        heading: the heading angle of the perspecitve projection
        fov: the field of view angle
        pitch: the vertical angle 
    
    Using example:
        inputFisheyeImage = r'D:\PhD Project\SkyViewFactProj\Panoramas\Sphere.jpg'
        outputCylinderImg = r'D:\PhD Project\SkyViewFactProj\Panoramas\ReprojectedImg2.jpg'
        cylinder2fisheyeImage (inputFisheyeImage,outputCylinderImg)
        
    '''
    
    from PIL import Image
    import numpy as np
    import os, os.path
    import math
    import cv2
    
    
    # read the panorama and get the metadata
    panoImg = np.array(Image.open(inputCylinderImage))
    Hs = panoImg.shape[0]
    Ws = panoImg.shape[1]
    
    print ('The size of the panorama is %s, %s'%(Hs,Ws))
    print ('The fov is %s, the heading angle is %s, and the pitch angle is %s'%(fov,heading,pitch))
    
    # the output size of the output static image, it can also been specified by suers
    width = 600
    height = 600
    
    # create empty matrics to store the affine parameters
    xmap = np.zeros((width,height),np.float32)
    ymap = np.zeros((width,height),np.float32)
    
    # calculate the focuses of the system
    fovRadiance = fov*np.pi/180
    yawRadiance = yaw*np.pi/180
    
    tilt_yawRadiance = tilt_yaw*np.pi/180
    focusW = 0.5*width/math.tan(0.5*fovRadiance)
    focusH = 0.5*height/math.tan(0.5*fovRadiance)
    
    pitchRadiance = pitch*np.pi/180
    headingRadiance = heading*np.pi/180        
    
    # find the corresponding pixels for each pixel in the output static image
    for yD in range(height):
        for xD in range(width):
            
            # convert the cartesian projection coordinate to image coordinate
            coorX = xD - 0.5*width
            coorY = 0.5*height - yD
            
            # get the theta and phi based on the coorX and coorY
            theta = headingRadiance + math.atan(coorX/focusW)
            phi = pitchRadiance + math.atan(coorY/focusH)
            
            # convert the theta and phi to image coordinate on cylinder
            xS = Ws*(theta - yawRadiance)/(2*np.pi) + 0.5*Ws
            yS = 0.5*Hs - Hs*(phi + tilt_yawRadiance)/np.pi
            
            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)
    

    # wrap or rectify the distorted cylinderical image to perspective projection
    # outputImg = cv2.remap(panoImg,xmap,ymap,cv2.INTER_CUBIC) #may not work for one band image
    outputImg = cv2.remap(panoImg,xmap,ymap,cv2.INTER_NEAREST)
    
    
    del xmap,ymap,panoImg
    print ('The size of output image is:', outputImg.shape)
    
    img = Image.fromarray(outputImg)
    del outputImg
    img.save(outputPerspectiveImg)
    del img
    


def cylindrical2Perspective(panoImg, heading, fov, pitch):
    '''
    The scirpt can generate perspective images from cylindrical panoramas, 
    this would be used for the street-side images. However, the distortion
    of the curved surface has not been solved yet.
    
    It is good to go, but just not perfect. 
    last modified Jan 6th, 2019
    Copyright(c) Xiaojiang Li, MIT Senseable City Lab

    example: 

        heading = 120
        fov=90
        pitch = 10
        cylindrical2Perspective(panoImg, heading, fov, pitch)
    '''
    # the field of view parameters
    import numpy as np
    import cv2

    heading = heading*np.pi/180
    fov = fov*np.pi/180
    pitch = pitch*np.pi/180
    
    Hs = panoImg.shape[0]
    Ws = panoImg.shape[1]

    # the output size of the output static image, it can also been specified by uers
    width = 800
    height = 800

    # create empty matrics to store the affine parameters
    xmap = np.zeros((width,height),np.float32)
    ymap = np.zeros((width,height),np.float32)

    for yD in range(height):
        for xD in range(width):
            
            theta = heading + (xD - width/2)*(1.0*fov/width)
            phi = pitch + (height/2 - yD)*(1.0*fov/height)
            
            if phi > 0.5*np.pi: phi = phi - 0.5*np.pi
            if theta > np.pi: theta = theta - 2*np.pi
            
    # #         theta = math.atan(2*xD/width - 1)
    #         theta = math.atan(heading + xD/(width*1.0/fov))
    # #         phi = math.atan(2*yD/height - 1)*math.sin(theta)
    #         phi = math.atan(yD/(height*1.0/fov))*math.sin(theta)
            
            # find the corresponding location on the cylindrical panoramas
            xS = (theta + np.pi)/(2*np.pi) * Ws
            yS = (np.pi/2 - phi)/np.pi*Hs
            
            xmap.itemset((yD,xD),xS)
            ymap.itemset((yD,xD),yS)


    # outputImg = cv2.remap(panoImg,xmap,ymap,cv2.INTER_CUBIC) # may not working for grayscale image
    outputImg = cv2.remap(panoImg,xmap,ymap,cv2.INTER_NEAREST)

    return outputImg
    
    # plt.imshow(panoImg)
    # plt.show()
    # plt.imshow(outputImg)
    # plt.show()



if __name__ == '__main__':
    import glob
    import numpy as np
    import os, os.path
    from PIL import Image


    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/code/cube2sphere'
    root = r'/Users/senseablecity/Dropbox (MIT)/Start-up/Exposure Model/source-code/skyview/code/cube2sphere'

    # # prepare the six cube images
    # # print(glob.glob(root, 'left*'))
    # leftImgfile = glob.glob('left*')[0]
    # rightImgfile = glob.glob('right*')[0]
    # upImgfile = glob.glob('up*')[0]
    # downImgfile = glob.glob('down*')[0]
    # frontImgfile = glob.glob('front*')[0]
    # backImgfile = glob.glob('back*')[0]

    # leftImg = np.array(Image.open(leftImgfile))
    # rightImg = np.array(Image.open(rightImgfile))
    # upImg = np.array(Image.open(upImgfile))
    # downImg = np.array(Image.open(downImgfile))
    # frontImg = np.array(Image.open(frontImgfile))
    # backImg = np.array(Image.open(backImgfile))
    
    # mosaicImg = cubeImageMasaic(leftImg, rightImg, upImg, downImg, frontImg, backImg)
    # convert_img(mosaicImg, 'output.png')
    

    # For NYC create static image from panos
    root = r'/Users/senseablecity/Dropbox (MIT)/ResearchProj/Treepedia/NYC-MillionsTree/'
    panos = os.path.join(root,'sample-GSV-panos')
    for file in os.listdir(panos):
        panoid = os.path.splitext(file)[0]
        filepath = os.path.join(panos, file)

        print(filepath)

        panoImg = np.asarray(Image.open(filepath))
        heading = 60

        for i in range(6):
            heading = i*60
            fov=90
            pitch = 10

            staticimg = cylindrical2Perspective(panoImg, heading, fov, pitch)
            im = Image.fromarray(staticimg)
            outname = '%s-%s.jpg'%(panoid, heading)
            outnamepath = os.path.join(root, outname)
            im.save(outnamepath)

