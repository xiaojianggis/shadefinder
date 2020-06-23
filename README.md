
## StreetSensing: Using street-level images to understand urban environment

Using Street-level images and computer vision to understand the urban streetscape environment.

### The structure of the code:

1. **libraries**: all the library functions for metadata, GSV image, etc
    1. image projection
    2. GSV image downloader
    3. metadata collection and cleaning
    4. spatial data operation `SpatialLib.py`
    	1. Aggregate point to Polygon, `AggregatePnt2Polygon`
    	
2. **apps**: the example of calling libraries functions and for different applications
    1. Metadata collection
    2. GSV image downloading

3. **database**: deal with database, connect, insert, query database
    1. Using database to manage metadata of street-level images
    2. Compute GVI, SVF, etc and update the results to database


Applications: 

1. Google Street View data preparation

2. Meatadata collection, cleanning, and organizing

3. GSV images processing
- Collect the street-level images
- Image projections
- Image segmentation
- Object segmentation

4. Urban Microclimate modeling
- Create DSM/DEM from LiDAR cloud point
- Using Solweig model to estimate the mean radiant temperature
