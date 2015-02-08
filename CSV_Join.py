## Code for the CSV joiner

## Run from the command line as:
## python CSV_Join.py filename1.csv filename2.csv

## Joins two SRTM csv files of the same size into one
## The code will attempt to join non-adjacent files so long as they share lat or lon!

import numpy
import sys

if __name__ == '__main__':
    try:
        print 'Joining CSV files'
        
        filename1 = ''
        filename2 = ''
        
        #filename1 = 'S35E018.csv' # Cape Town S
        #filename2 = 'S34E018.csv' # Cape Town N

        #filename1 = 'S35E019.csv' # 
        #filename2 = 'S34E019.csv' # 

        #filename1 = 'S35E018_join.csv' # 
        #filename2 = 'S35E019_join.csv' # 

        #filename1 = 'N54W004.csv' # UK Lake District W
        #filename2 = 'N54W003.csv' # UK Lake District E

        if filename1 == '' or filename2 == '':
            # Check if the csv filenames were passed in argv (e.g. "python CSV_Join.py N54W004.csv N54W003.csv")
            if len(sys.argv) > 2:
                filename1 = sys.argv[1]
                filename2 = sys.argv[2]
        
        if filename1 == '' or filename2 == '':
            # Ask for the two csv filenames
            filename1 = raw_input('Enter the 1st csv filename: ')
            filename2 = raw_input('Enter the 2nd csv filename: ')

        # Find the starting lats & lons from the filenames
        start_lon1 = float(filename1[4:7])
        if filename1[3] == 'W': start_lon1 = -start_lon1
        start_lat1 = float(filename1[1:3])
        if filename1[0] == 'S': start_lat1 = -start_lat1
        start_lon2 = float(filename2[4:7])
        if filename2[3] == 'W': start_lon2 = -start_lon2
        start_lat2 = float(filename2[1:3])
        if filename2[0] == 'S': start_lat2 = -start_lat2

        # Check if files need to be joined L-R or T-B
        if start_lat1 == start_lat2:
            print 'Files have equal latitude. Joining Left-Right.'
            LR = True
            if start_lon1 < start_lon2:
                print 'File order does not need to be changed.'
            else:
                print 'Swapping file order.'
                filename = filename1 # Swap filenames
                filename1 = filename2
                filename2 = filename
        elif start_lon1 == start_lon2:
            print 'Files have equal longitude. Joining Top-Bottom.'
            LR = False
            if start_lat1 < start_lat2:
                print 'File order does not need to be changed.'
            else:
                print 'Swapping file order.'
                filename = filename1 # Swap filenames
                filename1 = filename2
                filename2 = filename
        else:
            raise Exception('Files do not have same lat or lon!')

        outfile = str(filename1[:-4] + '_join' + filename1[-4:])
        
        print 'Processing',filename1,'and',filename2
        print 'Outputting data to',outfile
        
        try:
            # read data from file1 as float
            east1,north1,hgt1 = numpy.loadtxt(filename1,delimiter=',',unpack=True)
        except:
            raise Exception('Invalid file!')

        width1 = int(east1[0]) # Get the width of file1
        height1 = int(north1[0]) # Get the height of file1
        hgt_max1 = int(hgt1[0]) # Get the max_height of file1
        print filename1,': Width',width1,'Height',height1,'Max_Height',hgt_max1

        east1 = east1[1:] # Discard the width
        north1 = north1[1:] # Discard the height
        hgt1 = hgt1[1:] # Discard the max_height

        points1 = len(hgt1) # Check the number of points is correct
        if points1 != width1 * height1:
            raise Exception('Invalid file!')

        # Reshape file1 data into Y,X format
        east1 = numpy.reshape(east1,(height1,-1))
        north1 = numpy.reshape(north1,(height1,-1))
        hgt1 = numpy.reshape(hgt1,(height1,-1))

        try:
            # read data from file2 as float
            east2,north2,hgt2 = numpy.loadtxt(filename2,delimiter=',',unpack=True)
        except:
            raise Exception('Invalid file!')

        width2 = int(east2[0]) # Get the width of file2
        height2 = int(north2[0]) # Get the height of file2
        hgt_max2 = int(hgt2[0]) # Get the max_height of file2
        print filename2,': Width',width2,'Height',height2,'Max_Height',hgt_max2
        
        east2 = east2[1:] # Discard the width
        north2 = north2[1:] # Discard the height
        hgt2 = hgt2[1:] # Discard the max_height

        points2 = len(hgt2) # Check the number of points is correct
        if points2 != width2 * height2:
            raise Exception('Invalid file!')

        # Reshape file2 data into Y,X format
        east2 = numpy.reshape(east2,(height2,-1))
        north2 = numpy.reshape(north2,(height2,-1))
        hgt2 = numpy.reshape(hgt2,(height2,-1))


        # Check both files are the same size
        if points1 != points2: raise Exception('File sizes do not match!')


        if LR:
            # remove duplicated column
            hgt1 = hgt1[:,:-1] 
            east1 = east1[:,:-1]
            north1 = north1[:,:-1]
            width1 -= 1
            points1 -= height1
            
            # join the data
            hgt = numpy.concatenate((hgt1,hgt2),1)
            east = numpy.concatenate((east1,east2),1)
            north = numpy.concatenate((north1,north2),1)
            width = width1 + width2
            height = height1
            points = points1 + points2
            hgt_max = hgt.max()

        else:
            # remove duplicated row
            hgt1 = hgt1[1:,:]
            east1 = east1[1:,:]
            north1 = north1[1:,:]
            height1 -= 1
            points1 -= width1

            # join the data
            hgt = numpy.concatenate((hgt2,hgt1),0)
            east = numpy.concatenate((east2,east1),0)
            north = numpy.concatenate((north2,north1),0)
            width = width1
            height = height1 + height2
            points = points1 + points2
            hgt_max = hgt.max()


        # Convert back to a 1D array
        hgt = numpy.ravel(hgt)
        east = numpy.ravel(east)
        north = numpy.ravel(north)

        print 'Width',width
        print 'Height',height
        print 'Max Height',hgt_max
        print 'Top Left:',int(east[0]),int(north[0])
        print 'Bottom Right:',int(east[points-1]),int(north[points-1])

        # Save the joined data
        print 'Saving to',outfile
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

