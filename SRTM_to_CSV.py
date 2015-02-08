## Code for the SRTM to CSV converter

## Converts a NASA SRTM3 hgt file into csv format
## The first line of the csv file contains the width, height and maximum_height
## Each line after that is in the format east,north,height
## The csv files can then be:
## joined together with CSV_Join.py
## trimmed with CSV_Trim.py
## healed with CSV_Heal.py
## converted to stl format for 3D printing with CSV_to_STL.py
## and then displayed in 3D with 3D_CSV.py or 3D_STL.py

## To create a trimmed stl file of the UK Lake District:
## Download N54W004.hgt and N54W003.hgt
## Put SRTM_to_CSV.py, CSV_Join.py, CSV_Trim.py, CSV_to_STL.py in the same directory
## From the command line:
## python SRTM_to_CSV.py N54W004.hgt y
## python SRTM_to_CSV.py N54W003.hgt y
## python CSV_Join.py N54W004.csv N54W003.csv
## python CSV_Trim.py N54W004_join.csv 298000 363000 477000 542000
## python CSV_Heal.py N54W004_join_trim.csv
## python CSV_to_STL.py N54W004_join_trim_heal.csv 5.0 130.0 0.5 1.0
## python 3D_CSV.py N54W004_join_trim_heal.csv 5.0 y
## python 3D_STL.py N54W004_join_trim_heal.stl

## Run from the command line as:
## python STRM_to_CSV.py filename.hgt UK_data
## UK_data = 'y' or 'n'

## Download the SRTM3 (3 arc-second) hgt files from:
## http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/
## The continent map is available at:
## http://dds.cr.usgs.gov/srtm/version2_1/Documentation/Continent_def.gif

## The hgt filename refers to the lower left pixel or sample in the data
## Sample spacing is 3 arc-seconds for SRTM3 data
## Data is two byte signed integers (big endian)
## First row in the file is the ***northernmost*** one

## Download the utm package from:
## https://pypi.python.org/pypi/utm
## Unzip, cd into the utm-0.3.1 directory, then run
## python setup.py install

## WGS84toOSGB36 gratefully plagiarised from:
## http://hannahfry.co.uk/2012/02/01/converting-latitude-and-longitude-to-british-national-grid/

import utm
import numpy
import sys
from scipy import *

def WGS84toOSGB36(lat, lon):

    #First convert to radians
    #These are on the wrong ellipsoid currently: GRS80. (Denoted by _1)
    lat_1 = lat*pi/180
    lon_1 = lon*pi/180

    #Want to convert to the Airy 1830 ellipsoid, which has the following:
    a_1, b_1 =6378137.000, 6356752.3141 #The GSR80 semi-major and semi-minor axes used for WGS84(m)
    e2_1 = 1- (b_1*b_1)/(a_1*a_1)   #The eccentricity of the GRS80 ellipsoid
    nu_1 = a_1/sqrt(1-e2_1*sin(lat_1)**2)

    #First convert to cartesian from spherical polar coordinates
    H = 0 #Third spherical coord.
    x_1 = (nu_1 + H)*cos(lat_1)*cos(lon_1)
    y_1 = (nu_1+ H)*cos(lat_1)*sin(lon_1)
    z_1 = ((1-e2_1)*nu_1 +H)*sin(lat_1)

    #Perform Helmut transform (to go between GRS80 (_1) and Airy 1830 (_2))
    s = 20.4894*10**-6 #The scale factor -1
    tx, ty, tz = -446.448, 125.157, -542.060 #The translations along x,y,z axes respectively
    rxs,rys,rzs = -0.1502, -0.2470, -0.8421  #The rotations along x,y,z respectively, in seconds
    rx, ry, rz = rxs*pi/(180*3600.), rys*pi/(180*3600.), rzs*pi/(180*3600.) #In radians
    x_2 = tx + (1+s)*x_1 + (-rz)*y_1 + (ry)*z_1
    y_2 = ty + (rz)*x_1  + (1+s)*y_1 + (-rx)*z_1
    z_2 = tz + (-ry)*x_1 + (rx)*y_1 +  (1+s)*z_1

    #Back to spherical polar coordinates from cartesian
    #Need some of the characteristics of the new ellipsoid
    a, b = 6377563.396, 6356256.909 #The GSR80 semi-major and semi-minor axes used for WGS84(m)
    e2 = 1- (b*b)/(a*a)   #The eccentricity of the Airy 1830 ellipsoid
    p = sqrt(x_2**2 + y_2**2)

    #Lat is obtained by an iterative proceedure:
    lat = arctan2(z_2,(p*(1-e2))) #Initial value
    latold = 2*pi
    while abs(lat - latold)>10**-16:
        lat, latold = latold, lat
        nu = a/sqrt(1-e2*sin(latold)**2)
        lat = arctan2(z_2+e2*nu*sin(latold), p)

    #Lon and height are then pretty easy
    lon = arctan2(y_2,x_2)
    H = p/cos(lat) - nu

    #E, N are the British national grid coordinates - eastings and northings
    F0 = 0.9996012717                   #scale factor on the central meridian
    lat0 = 49*pi/180                    #Latitude of true origin (radians)
    lon0 = -2*pi/180                    #Longtitude of true origin and central meridian (radians)
    N0, E0 = -100000, 400000            #Northing & easting of true origin (m)
    n = (a-b)/(a+b)

    #meridional radius of curvature
    rho = a*F0*(1-e2)*(1-e2*sin(lat)**2)**(-1.5)
    eta2 = nu*F0/rho-1

    M1 = (1 + n + (5/4)*n**2 + (5/4)*n**3) * (lat-lat0)
    M2 = (3*n + 3*n**2 + (21/8)*n**3) * sin(lat-lat0) * cos(lat+lat0)
    M3 = ((15/8)*n**2 + (15/8)*n**3) * sin(2*(lat-lat0)) * cos(2*(lat+lat0))
    M4 = (35/24)*n**3 * sin(3*(lat-lat0)) * cos(3*(lat+lat0))

    #meridional arc
    M = b * F0 * (M1 - M2 + M3 - M4)          

    I = M + N0
    II = nu*F0*sin(lat)*cos(lat)/2
    III = nu*F0*sin(lat)*cos(lat)**3*(5- tan(lat)**2 + 9*eta2)/24
    IIIA = nu*F0*sin(lat)*cos(lat)**5*(61- 58*tan(lat)**2 + tan(lat)**4)/720
    IV = nu*F0*cos(lat)
    V = nu*F0*cos(lat)**3*(nu/rho - tan(lat)**2)/6
    VI = nu*F0*cos(lat)**5*(5 - 18* tan(lat)**2 + tan(lat)**4 + 14*eta2 - 58*eta2*tan(lat)**2)/120

    N = I + II*(lon-lon0)**2 + III*(lon- lon0)**4 + IIIA*(lon-lon0)**6
    E = E0 + IV*(lon-lon0) + V*(lon- lon0)**3 + VI*(lon- lon0)**5 

    #Job's a good'n.
    return E,N

if __name__ == '__main__':
    try:
        print 'Converting SRTM to CSV'
        
        filename = ''
        UK = ''
        
        #filename = 'S35E018.hgt' # Cape Town SW
        #filename = 'S34E018.hgt' # Cape Town NW
        #filename = 'S35E019.hgt' # Cape Town SE
        #filename = 'S34E019.hgt' # Cape Town NE
        #filename = 'N54W004.hgt' # UK Lake District W
        #filename = 'N54W003.hgt' # UK Lake District E

        if filename == '':
            # Check if the hgt filename was passed in argv (e.g. "python SRTM_to_CSV.py N54W004.hgt")
            if len(sys.argv) > 1: filename = sys.argv[1]
            # Check if the UK flag was passed in argv (e.g. "python SRTM_to_CSV.py N54W004.hgt y")
            if len(sys.argv) > 2: UK = sys.argv[2]

        if filename == '': filename = raw_input('Enter the hgt filename: ') # Get the hgt filename

        outfile = str(filename[:-4] + '.csv') # Create the output filename
        
        if UK == '': UK = raw_input('Is this UK data (y/n)? ') # Is it UK data?
        if UK == '' or UK == 'Y' or UK == 'y': UK = True
        else: UK = False

        print 'Processing',filename
        print 'Outputting data to',outfile
        
        start_lon = float(filename[4:7]) # Get the start latitude from the filename
        if filename[3] == 'W': start_lon = -start_lon
        start_lat = float(filename[1:3]) # Get the start longitude from the filename
        if filename[0] == 'S': start_lat = -start_lat

        print 'Bottom Left: Latitude',start_lat,'Longitude',start_lon
        
        start_lat += 1 # Add 1 to the start latitude as the first row in the file is the northernmost one

        try:
            # read data
            hgt = numpy.fromfile(filename,dtype='>i2')
        except:
            raise Exception('Invalid file!')

        points = len(hgt) # Get the numper of points

        width = 1201 # SRTM3 files are 1201 * 1201
        height = 1201

        if points != width * height: # Check we've got the correct amount of data
            raise Exception('Invalid file!')

        hgt = hgt.astype(float) # Convert to float

        # Find the minimum height, ignoring invalid data points (-32768)
        hgt_min = 32767.
        for l in range(points):
            if (hgt[l] < hgt_min) and (hgt[l] > -32768.): hgt_min = hgt[l]

        hgt_max = hgt.max() # Find the maximum height
        
        print 'Points:',points
        print 'Maximum height:',hgt_max
        print 'Minimum height:',hgt_min

        # Create an array of longitudes
        lon = []
        for l in range(height):
            for m in range(width):
                lon.append(start_lon + (m * (3. / (60. * 60.)))) # 3 arc-second spacing

        # Create an array of latitudes
        lat = []
        for l in range(height):
            for m in range(width):
                lat.append(start_lat - (l * (3. / (60. * 60.)))) # 3 arc-second spacing

        print 'Converting lat&lon to east&north...'
        if UK: print '(This could take a while...)'

        east = []
        north = []

        for l in range(points): # Do the conversion
            if UK:
                e,n = WGS84toOSGB36(lat[l],lon[l]) # UK
            else:
                e,n,zn,zl = utm.from_latlon(lat[l],lon[l]) # Rest of the World
            east.append(e)
            north.append(n)

        print 'Top Left:',int(east[0]),int(north[0])
        print 'Bottom Right:',int(east[points-1]),int(north[points-1])

        print 'Saving to',outfile

        # Write the data to outfile in integer format
        # Include "width,height,hgt_max" as the first line
        fp = open(outfile,'w')
        outstr = str(width) + ',' + str(height) + ',' + str(int(hgt_max)) + '\n'
        fp.write(outstr)
        for l in range(points):
            outstr = str(int(east[l])) + ',' + str(int(north[l])) + ',' + str(int(hgt[l])) + '\n'
            fp.write(outstr)
        fp.close()

        print 'Complete!'

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

