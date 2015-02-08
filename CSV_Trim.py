## Code for the CSV Trimmer

## Run from the command line as:
## python CSV_Trim.py filename.csv x_min x_max y_min y_max
## Where x_min is the left boundary,
## x_max is the right boundary
## y_min is the bottom boundary
## and y_max is the top boundary

import numpy
import sys

if __name__ == '__main__':
    try:
        print 'CSV Trim'
        
        filename = ''
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0

        ## UK Lake District
        #filename = 'N54W004_join.csv' # UK Lake District
        #x_min = 298000 # Roughly 65km square
        #x_max = 363000
        #y_min = 477000
        #y_max = 542000
        

        ## Cape Town
        #filename = 'S35E018_join.csv' # Cape Town
        #x_min = 240000
        #x_max = 315000
        #y_min = 6187500
        #y_max = 6262500

        if filename == '':
            # Check if the csv filename was passed in argv (e.g. "python CSV_Trim.py N54W004.csv")
            if len(sys.argv) > 1: filename = sys.argv[1]
            # Check for x_min etc in argv (e.g. "python CSV_Trim.py N54W004_join.csv 298000 363000 477000 542000")
            if len(sys.argv) > 5:
                x_min = float(sys.argv[2])
                x_max = float(sys.argv[3])
                y_min = float(sys.argv[4])
                y_max = float(sys.argv[5])

        if filename == '': filename = raw_input('Enter the csv filename: ') # Get the hgt filename

        print 'Processing',filename

        outfile = filename[:-4] + '_trim' + filename[-4:]
        
        try:
            # read data as float
            east,north,hgt = numpy.loadtxt(filename,delimiter=',',unpack=True)
        except:
            raise Exception('Invalid file!')

        width = int(east[0]) # Get the width
        height = int(north[0]) # Get the height
        hgt_max = int(hgt[0]) # Get the max_height

        east = east[1:] # Discard the width
        north = north[1:] # Discard the height
        hgt = hgt[1:] # Discard the max_height

        points = len(hgt) # Get the number of data points

        if points != width * height: # Check we've got the right number of data points
            raise Exception('Invalid file!')

        print 'Points:',points
        print 'Maximum height:',hgt_max
        print 'Top Left:',int(east[0]),int(north[0])
        print 'Bottom Right:',int(east[points-1]),int(north[points-1])

        if x_min == 0 or x_max == 0 or y_min == 0 or y_max == 0:
            x_min = float(raw_input('Enter the left boundary (x_min): '))
            x_max = float(raw_input('Enter the right boundary (x_max): '))
            y_min = float(raw_input('Enter the bottom boundary (y_min): '))
            y_max = float(raw_input('Enter the top boundary (y_max): '))
            
        # Reshape into Y,X format
        east = numpy.reshape(east,(height,-1))
        north = numpy.reshape(north,(height,-1))
        hgt = numpy.reshape(hgt,(height,-1))

        print 'Trimming the data...'

        # Go through the file a line at a time looking for where the boundaries are met
        for l in range(height):
            if min(north[l,:]) >= y_max:
                   top = l
        for l in range(height):
            if max(north[l,:]) >= y_min:
                   bottom = l
        for l in range(width):
            if min(east[:,l]) <= x_min:
                   left = l
        for l in range(width):
            if max(east[:,l]) <= x_max:
                   right = l

        # Trim the data
        east = east[top:bottom,left:right]
        north = north[top:bottom,left:right]
        hgt = hgt[top:bottom,left:right]

        # Adjust the width and height
        width = right - left
        height = bottom - top

        # Convert the data back to a 1D array
        east = numpy.ravel(east)
        north = numpy.ravel(north)
        hgt = numpy.ravel(hgt)

        # Correct the number of data points
        points = len(hgt)

        if points != width * height: # Check the new number of data points
            raise Exception('Something bad happened!')

        # Find the minimum height, ignoring invalid data points (-32768)
        hgt_min = 32767.
        for l in range(points):
            if (hgt[l] < hgt_min) and (hgt[l] > -32768.): hgt_min = hgt[l]

        # Find the maximum height
        hgt_max = hgt.max()

        print 'Points:',points
        print 'Maximum height:',hgt_max
        print 'Minimum height:',hgt_min

        print 'Top Left:',int(east[0]),int(north[0])
        print 'Bottom Right:',int(east[points-1]),int(north[points-1])

        print 'Saving to',outfile

        fp = open(outfile,'w')
        # Write the width,height,max_height to the file
        outstr = str(width) + ',' + str(height) + ',' + str(int(hgt_max)) + '\n'
        fp.write(outstr)
        for l in range(points):
            # Write the data
            outstr = str(int(east[l])) + ',' + str(int(north[l])) + ',' + str(int(hgt[l])) + '\n'
            fp.write(outstr)
        fp.close()

        print 'Complete!'

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

