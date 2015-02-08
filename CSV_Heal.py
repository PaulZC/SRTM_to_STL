## Code for the CSV Heal

## Run from the command line as:
## python CSV_Heal.py filename.csv

import numpy
import sys

if __name__ == '__main__':
    try:
        print 'CSV Heal'
        
        filename = ''

        #filename = 'N54W004_join_trim.csv' # UK Lake District
        #filename = 'S35E018_join_trim.csv' # Cape Town

        if filename == '':
            # Check if the csv filename was passed in argv (e.g. "python CSV_Heal.py N54W004.csv")
            if len(sys.argv) > 1: filename = sys.argv[1]

        if filename == '': filename = raw_input('Enter the csv filename: ') # Get the hgt filename

        print 'Processing',filename

        outfile = filename[:-4] + '_heal' + filename[-4:]
        
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

        # Reshape into Y,X format
        east = numpy.reshape(east,(height,-1))
        north = numpy.reshape(north,(height,-1))
        hgt = numpy.reshape(hgt,(height,-1))

        cannot_heal = 0

        # Go through the file a pixel at a time looking for values of -32768.
        for y in range(height):
            for x in range(width):
                if hgt[y,x] == -32768.:
                    neighbours = []
                    if (x>0) and (y>0) and (x<width-1) and (y<height-1):
                        if hgt[y-1,x-1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y-1,x] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y-1,x+1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y,x-1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y,x+1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y+1,x-1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y+1,x] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y+1,x+1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                    elif (x>0) and (y>0):
                        if hgt[y-1,x-1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y-1,x] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y,x-1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                    elif (x<width-1) and (y<height-1):
                        if hgt[y,x+1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y+1,x] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                        if hgt[y+1,x+1] > -32768.:
                            neighbours.append(hgt[y-1,x-1])
                    if len(neighbours) > 0:
                        average = sum(neighbours)/float(len(neighbours))
                        hgt[y,x] = average
                        print 'Changed point',int(east[y,x]),',',int(north[y,x]),'to',average,'using',len(neighbours),'neighbouring points'
                    else:
                        print 'Cannot heal point',int(east[y,x]),',',int(north[y,x]),'as it has no valid neighbours!'
                        cannot_heal += 1

        # Convert the data back to a 1D array
        east = numpy.ravel(east)
        north = numpy.ravel(north)
        hgt = numpy.ravel(hgt)

        # Find the minimum height
        hgt_min = hgt.min()

        print 'Minimum height:',hgt_min

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

        if cannot_heal > 0: print 'Could not heal',cannot_heal,'points!'

        print 'Complete!'

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

