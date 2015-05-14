## Code for the CSV to STL Converter

## Converts a csv file into binary stl for 3D printing

## Run from the command line as:
## python CSV_to_STL.py filename.csv printheight printwidth baseoffset basethickness
## printheight is the maximum print height in mm
## printwidth is the (maximum) print width (or height - whichever is larger) in mm
## baseoffset is the extra material in mm that is added to non-minimum data to help define coastlines etc. (set to zero as required)
## basethickness is the base layer thickness in mm

import numpy
import sys

if __name__ == '__main__':
    try:
        filename = ''
        print_height = 0.
        print_width = 0.
        base_offset = 0.
        base_thickness = 0.
        # Binary STL header must be 80 characters wide
        header = 'Generated from NASA SRTM data                                                   '
        
        ## UK Lake District
        ## N54W004_join_trim is roughly 65km square so scale to 130mm (1:500,000)
        #filename = 'N54W004_join_trim_heal.csv'
        #print_height = 5.0
        #print_width = 130.
        #base_offset = 0.5
        #base_thickness = 1.0
        #header = 'Lake District National Park from NASA SRTM. XY Scale 1:500,000. Z not to scale! '

        ## Cape Town
        #filename = 'S35E018_join_trim_heal.csv'
        #print_height = 7.5
        #print_width = 150.
        #base_offset = 0.5
        #base_thickness = 1.0
        #header = 'Cape Town and False Bay from NASA SRTM. XY scale is arbitary. Z not to scale!   '
        
        if filename == '':
            # Check if the csv filename was passed in argv (e.g. "python CSV_to_STL.py N54W004_join_trim.csv")
            if len(sys.argv) > 1: filename = sys.argv[1]
            # Check if the print height was passed in argv (e.g. "python CSV_to_STL.py N54W004_join_trim.csv 5.0")
            if len(sys.argv) > 2: print_height = float(sys.argv[2])
            # Check if the print width was passed in argv (e.g. "python CSV_to_STL.py N54W004_join_trim.csv 5.0 130.0")
            if len(sys.argv) > 3: print_width = float(sys.argv[3])
            # Check if the base offset was passed in argv (e.g. "python CSV_to_STL.py N54W004_join_trim.csv 5.0 130.0 0.5")
            if len(sys.argv) > 4: base_offset = float(sys.argv[4])
            # Check if the base thickness was passed in argv (e.g. "python CSV_to_STL.py N54W004_join_trim.csv 5.0 130.0 0.5 1.0")
            if len(sys.argv) > 5: base_thickness= float(sys.argv[5])

        if filename == '': filename = raw_input('Enter the csv filename: ') # Get the csv filename

        print 'Processing',filename

        outfile = filename[:-4] + '.stl' # Create the output file name
        
        try:
            # read data (as float)
            east,north,hgt = numpy.loadtxt(filename,delimiter=',',unpack=True)
        except:
            raise Exception('Invalid file!')

        width = int(east[0]) # Get the width from the file data
        height = int(north[0]) # Get the height from the file data
        hgt_max = int(hgt[0]) # Get the max_height from the file data

        east = east[1:] # Discard the width
        north = north[1:] # Discard the height
        hgt = hgt[1:] # Discard the max_height

        points = len(hgt) # Check the number of data points
        if points != width * height:
            raise Exception('Invalid file!')

        # Find the minimum height, ignoring invalid data points (-32768)
        hgt_min = 32767.
        for l in range(points):
            if (hgt[l] < hgt_min) and (hgt[l] > -32768.): hgt_min = hgt[l]

        hgt_max = hgt.max() # Find the max_height

        print 'Points:',points
        print 'Maximum height (before scaling):',hgt_max
        print 'Minimum height (before scaling):',hgt_min

        if print_height == 0.:
            try:
                print_height = float(raw_input('Enter the print height in mm: '))
            except:
                raise Exception('Invalid print height!')
            
        if print_width == 0.:
            try:
                print_width = float(raw_input('Enter the print width in mm: '))
            except:
                raise Exception('Invalid print width!')
            
        if base_offset == 0.:
            try:
                base_offset = float(raw_input('Enter the base offset (for coastline definition) in mm: '))
            except:
                raise Exception('Invalid base offset!')
            
        if base_thickness == 0.:
            try:
                base_thickness = float(raw_input('Enter the base layer thickness in mm: '))
            except:
                raise Exception('Invalid base thickness!')
            
        #Make all valid points zero height or greater
        if hgt_min < 0.:
            for l in range(points):
                if hgt[l] > -32768.: hgt[l] -= hgt_min

        #Scale height and add base_offset to all valid points to help define coastlines etc..
        #Zero invalid points
        for l in range(points):
            if hgt[l] > 0.:
                hgt[l] = base_offset + (print_height * hgt[l] / hgt_max)
            else:
                hgt[l] = 0.

        # Add base thickness
        hgt += base_thickness

        # Shift E,N origin to zero
        min_east = east.min()
        min_north = north.min()
        east -= min_east
        north -= min_north

        # Find the maximum E or N dimension
        max_east = east.max()
        max_north = north.max()
        maxd = max_north
        if max_east > max_north: maxd = max_east

        # Scale to print width
        east *= print_width / maxd
        north *= print_width / maxd

        base = hgt * 0. # Create a zero base layer array for triangle generation

        # Duplicate coordinates arrays for triangle generation
        east = numpy.concatenate((east,east))
        north = numpy.concatenate((north,north))
        hgt = numpy.concatenate((hgt,base))

        print 'Generating triangles...'

        triangles = []
        #shades = [] # For VisCAM / SolidView color STL files : not currently implemented

        # Surface

        for row in range(height - 1):
            for col in range(width - 1):
                origin = (row * width) + col
                triangle = [origin,origin+1,origin+width]
                triangles.append(triangle)
                #shades.append((hgt[origin]))

        for row in range(height - 1):
            for col in range(width - 1):
                origin = (row * width) + col
                triangle = [origin+1,origin+width,origin+width+1]
                triangles.append(triangle)
                #shades.append((hgt[origin]))

        #Base

        for row in range(height - 1):
            for col in range(width - 1):
                origin = (row * width) + col + points
                triangle = [origin,origin+1,origin+width]
                triangles.append(triangle)
                #shades.append((hgt[origin]))

        for row in range(height - 1):
            for col in range(width - 1):
                origin = (row * width) + col + points
                triangle = [origin+1,origin+width,origin+width+1]
                triangles.append(triangle)
                #shades.append((hgt[origin]))

        #Walls

        for col in range(width - 1):
            origin = col
            triangle = [origin,origin+1,origin+points]
            triangles.append(triangle)
            #shades.append((hgt[origin]))
        for col in range(width - 1):
            origin = col
            triangle = [origin+1,origin+points,origin+points+1]
            triangles.append(triangle)
            #shades.append((hgt[origin]))

        for col in range(width - 1):
            origin = ((height - 1) * width) + col
            triangle = [origin,origin+1,origin+points]
            triangles.append(triangle)
            #shades.append((hgt[origin]))
        for col in range(width - 1):
            origin = ((height - 1) * width) + col
            triangle = [origin+1,origin+points,origin+points+1]
            triangles.append(triangle)
            #shades.append((hgt[origin]))

        for row in range(height - 1):
            origin = row * width
            triangle = [origin,origin+width,origin+points]
            triangles.append(triangle)
            #shades.append((hgt[origin]))
        for row in range(height - 1):
            origin = row * width
            triangle = [origin+width,origin+points,origin+width+points]
            triangles.append(triangle)
            #shades.append((hgt[origin]))

        for row in range(height - 1):
            origin = (row * width) + (width - 1)
            triangle = [origin,origin+width,origin+points]
            triangles.append(triangle)
            #shades.append((hgt[origin]))
        for row in range(height - 1):
            origin = (row * width) + (width - 1)
            triangle = [origin+width,origin+points,origin+width+points]
            triangles.append(triangle)
            #shades.append((hgt[origin]))

        print 'Created',len(triangles),'triangles'
        print 'File size should be',80+4+(50*len(triangles)),'bytes'

        print 'Writing STL file...'

        try: # Write data to file
            fp = open(outfile,'wb')
            fp.write(header)
            fp.write(numpy.uint32(len(triangles)))
            for l in range(len(triangles)):
                fp.write(numpy.float32(0.0))
                fp.write(numpy.float32(0.0))
                fp.write(numpy.float32(0.0))
                fp.write(numpy.float32(east[triangles[l][0]]))
                fp.write(numpy.float32(north[triangles[l][0]]))
                fp.write(numpy.float32(hgt[triangles[l][0]]))
                fp.write(numpy.float32(east[triangles[l][1]]))
                fp.write(numpy.float32(north[triangles[l][1]]))
                fp.write(numpy.float32(hgt[triangles[l][1]]))
                fp.write(numpy.float32(east[triangles[l][2]]))
                fp.write(numpy.float32(north[triangles[l][2]]))
                fp.write(numpy.float32(hgt[triangles[l][2]]))
                fp.write(numpy.uint16(0)) # <- data from shades[l] would go here
            fp.close()
        except:
            raise Exception('Could not write data!')

        print 'Complete!'

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

