## Code for the SRTM resampler

## Converts a NASA SRTM 1arcsec hgt file into a 3arcsec hgt file

## Run from the command line as:
## python SRTM_resample.py filename.hgt

## The hgt filename refers to the lower left pixel or sample in the data
## Data is two byte signed integers (big endian)
## First row in the file is the ***northernmost*** one

import sys
import numpy

if __name__ == '__main__':
    try:
        print 'Resampling SRTM (Converting 1 arc-second data to 3 arc-second)'
        
        filename = ''
        
        #filename = 'S26E131.hgt' # Ayers Rock

        if filename == '':
            # Check if the hgt filename was passed in argv
            if len(sys.argv) > 1: filename = sys.argv[1]

        if filename == '': filename = raw_input('Enter the hgt filename: ') # Get the hgt filename

        outfile = filename[:-4] + '_resample' + filename[-4:]
        
        print 'Processing',filename
        print 'Outputting data to',outfile
        
        try:
            # read data
            hgt = numpy.fromfile(filename,dtype='>i2')
        except:
            raise Exception('Invalid file!')

        points = len(hgt) # Get the numper of points

        width = 3601 # SRTM1 files are 3601 * 3601
        height = 3601

        if points != width * height: # Check we've got the correct amount of data
            raise Exception('Invalid file!')

        print 'Points:',points

        # Reshape into Y,X format
        hgt = numpy.reshape(hgt,(height,-1))

        newhgt = [] # Create an empty array to hold the new height data

        for h in range(0,(height+1),3): # process every third row
            for w in range(0,(width+1),3): # process every third column
                # calculate the average height of the next nine data points (3x3)
                av_hgt = hgt[h:h+2,w:w+2].sum() / 9. 
                newhgt.append(int(av_hgt))

        newhgt = numpy.ravel(newhgt)

        print 'Saving to',outfile # Save the resampled data
        fp = open(outfile,'wb')
        for i in newhgt:
            fp.write(i.astype('>i2').byteswap())
        fp.close()

        print 'Complete!'

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

