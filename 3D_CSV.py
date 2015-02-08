## Code for the 3D CSV Plotter

## Run from the command line as:
## python 3D_CSV.py filename.csv zscale base_and_walls
## A zscale value of around 5 seems to work well
## base_and_walls = 'y' or 'n'

from mayavi import mlab
import numpy
import sys

PSEUDO_COLOUR = True

if __name__ == '__main__':
    try:
        print 'Displaying csv file in 3D'

        filename = ''
        z_scale = 0.
        base_and_walls = ''
        
        #filename = 'N54W004.csv' # UK Lake District
        #filename = 'N54W004_join.csv' # UK Lake District
        #filename = 'N54W004_join_trim.csv' # UK Lake District
        #filename = 'N54W004_join_trim_heal.csv' # UK Lake District
        #filename = 'S35E018.csv' # Cape Town
        #filename = 'S35E018_join.csv' # Cape Town
        #filename = 'S35E018_join_trim.csv' # Cape Town
        #filename = 'S35E018_join_join.csv' # Cape Town area
        
        if filename == '':
            # Check if the csv filename was passed in argv (e.g. "python 3D_CSV.py N54W004.csv")
            if len(sys.argv) > 1: filename = sys.argv[1]
            # Check if the z_scale was passed in argv (e.g. "python 3D_CSV.py N54W004.csv 5.0")
            if len(sys.argv) > 2: z_scale = float(sys.argv[2])
            # Check if base_and_walls was passed in argv (e.g. "python 3D_CSV.py N54W004.csv 5.0 y")
            if len(sys.argv) > 3: base_and_walls = sys.argv[3]

        if filename == '': filename = raw_input('Enter the csv filename: ') # Get the hgt filename

        print 'Processing',filename
        
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

        points = len(hgt) # Check the number of points is correct

        if points != width * height:
            raise Exception('Invalid file!')

        # Find the minimum height, ignoring invalid data points (-32768)
        hgt_min = 32767.
        for l in range(points):
            if (hgt[l] < hgt_min) and (hgt[l] > -32768.): hgt_min = hgt[l]

        # Fix invalid data points (-32768)
        for l in range(points):
            if hgt[l] == -32768.: hgt[l] = hgt_min

        hgt_max = hgt.max()

        print 'Width:',width
        print 'Height:',height
        print 'Points:',points
        print 'Maximum height (before scaling):',hgt_max
        print 'Minimum height (before scaling):',hgt_min

        if z_scale == 0.:
            try:
                z_scale = float(raw_input('Enter the z scale (a value around 5.0 seems to work well): '))
            except:
                raise Exception('Invalid z_scale!')
        hgt *= z_scale

        if base_and_walls == '': base_and_walls = raw_input('Do you want this displayed with base and walls (y/n)? ') # Is it UK data?
        if base_and_walls == '' or base_and_walls == 'Y' or base_and_walls == 'y': base_and_walls = True
        else: base_and_walls = False

        hgt_max = hgt.max()
        hgt_min = hgt.min()

        base = hgt * 0. # Create a flat base same size as data
        if hgt_min < 0.: base += hgt_min # Move base to hgt_min if hgt_min is negative

        # Duplicate the eastings and northings arrays
        east = numpy.concatenate((east,east))
        north = numpy.concatenate((north,north))
        # Add the base array to the height array
        hgt = numpy.concatenate((hgt,base))

        print 'Generating triangles...'

        triangles = []
        shades = []

        # Surface

        for row in range(height - 1):
            for col in range(width - 1):
                origin = (row * width) + col
                triangle = [origin,origin+1,origin+width]
                triangles.append(triangle)
                shades.append((hgt[origin]))

        for row in range(height - 1):
            for col in range(width - 1):
                origin = (row * width) + col
                triangle = [origin+1,origin+width,origin+width+1]
                triangles.append(triangle)
                shades.append((hgt[origin]))

        if base_and_walls:
            #Base

            for row in range(height - 1):
                for col in range(width - 1):
                    origin = (row * width) + col + points
                    triangle = [origin,origin+1,origin+width]
                    triangles.append(triangle)
                    shades.append((hgt[origin]))

            for row in range(height - 1):
                for col in range(width - 1):
                    origin = (row * width) + col + points
                    triangle = [origin+1,origin+width,origin+width+1]
                    triangles.append(triangle)
                    shades.append((hgt[origin]))

            #Walls

            for col in range(width - 1):
                origin = col
                triangle = [origin,origin+1,origin+points]
                triangles.append(triangle)
                shades.append((hgt[origin]))
            for col in range(width - 1):
                origin = col
                triangle = [origin+1,origin+points,origin+points+1]
                triangles.append(triangle)
                shades.append((hgt[origin]))

            for col in range(width - 1):
                origin = ((height - 1) * width) + col
                triangle = [origin,origin+1,origin+points]
                triangles.append(triangle)
                shades.append((hgt[origin]))
            for col in range(width - 1):
                origin = ((height - 1) * width) + col
                triangle = [origin+1,origin+points,origin+points+1]
                triangles.append(triangle)
                shades.append((hgt[origin]))

            for row in range(height - 1):
                origin = row * width
                triangle = [origin,origin+width,origin+points]
                triangles.append(triangle)
                shades.append((hgt[origin]))
            for row in range(height - 1):
                origin = row * width
                triangle = [origin+width,origin+points,origin+width+points]
                triangles.append(triangle)
                shades.append((hgt[origin]))

            for row in range(height - 1):
                origin = (row * width) + (width - 1)
                triangle = [origin,origin+width,origin+points]
                triangles.append(triangle)
                shades.append((hgt[origin]))
            for row in range(height - 1):
                origin = (row * width) + (width - 1)
                triangle = [origin+width,origin+points,origin+width+points]
                triangles.append(triangle)
                shades.append((hgt[origin]))

        print 'Plotting...'

        try:
            mesh = mlab.pipeline.triangular_mesh_source(east,north,hgt,triangles)
            mesh.data.cell_data.scalars = shades
            if PSEUDO_COLOUR:
                surf = mlab.pipeline.surface(mesh)
                surf.module_manager.scalar_lut_manager.reverse_lut = False
            else:
                surf = mlab.pipeline.surface(mesh,colormap='Greys')
                surf.module_manager.scalar_lut_manager.reverse_lut = True
            surf.contour.filled_contours = True
            surf.module_manager.scalar_lut_manager.show_scalar_bar = False #True
            surf.module_manager.scalar_lut_manager.use_default_range = False
            surf.module_manager.scalar_lut_manager.data_range = [hgt_min,hgt_max]
            surf.module_manager.scalar_lut_manager.use_default_name = False
            surf.module_manager.scalar_lut_manager.data_name = 'Height'
            surf.module_manager.lut_data_mode = 'cell data'
            #mlab.title(filename,height=0.0,size=0.5)
            mlab.show()
        except:
            raise Exception('Could not plot data!')

        print 'Complete!'

    except KeyboardInterrupt:
        print 'CTRL+C received...'
     
    finally:
        print 'Bye!'

