## Code for the 3D STL Plotter

## Doesn't do any fancy like remove duplicated verticies!

## Run from the command line as:
## python 3D_STL.py filename.stl

from mayavi import mlab
import numpy
import sys
import struct
import os

PSEUDO_COLOUR = True

if __name__ == '__main__':
    try:
        print 'Displaying binary stl file in 3D'

        filename = ''
        
        #filename = 'N54W004_join_trim_heal.stl' # UK Lake District
        #filename = 'S35E018_join_trim_heal.stl' # Cape Town

        if filename == '':
            # Check if the stl filename was passed in argv (e.g. "python 3D_STL.py N54W004_join_trim.stl")
            if len(sys.argv) > 1: filename = sys.argv[1]

        if filename == '': filename = raw_input('Enter the stl filename: ') # Get the stl filename

        print 'Processing',filename

        filesize = os.path.getsize(filename) # Get the file size

        fp = open(filename,'rb') # Open file for reading

        header = str(fp.read(80)) # Read and print header
        print 'Header:',header

        num_triangles = struct.unpack('I', fp.read(4))[0] # Read number of triangles (uint32)

        if filesize != 80 + 4 + (num_triangles * 50):
            raise Exception('Incorrect file size! Not a binary stl file?')

        print 'Reading',num_triangles,'triangles'

        east = []
        north = []
        hgt = []
        triangles = []
        shades = []
        triangle = 0
        max_hgt = 0.

        for l in range(num_triangles):
            zero = struct.unpack('f', fp.read(4))[0] # Read null float32
            zero = struct.unpack('f', fp.read(4))[0] # Read null float32
            zero = struct.unpack('f', fp.read(4))[0] # Read null float32
            east.append(struct.unpack('f', fp.read(4))[0]) # Read vertex float32
            north.append(struct.unpack('f', fp.read(4))[0]) # Read vertex float32
            hgt1 = struct.unpack('f', fp.read(4))[0] # Read vertex float32
            hgt.append(hgt1)
            east.append(struct.unpack('f', fp.read(4))[0]) # Read vertex float32
            north.append(struct.unpack('f', fp.read(4))[0]) # Read vertex float32
            hgt2 = struct.unpack('f', fp.read(4))[0] # Read vertex float32
            hgt.append(hgt2)
            east.append(struct.unpack('f', fp.read(4))[0]) # Read vertex float32
            north.append(struct.unpack('f', fp.read(4))[0]) # Read vertex float32
            hgt3 = struct.unpack('f', fp.read(4))[0] # Read vertex float32
            hgt.append(hgt3)
            zero = struct.unpack('H', fp.read(2))[0] # Read 'shade' uint16
            triangles.append([triangle,triangle+1,triangle+2])
            if hgt[triangle] > max_hgt: max_hgt = hgt[triangle]
            if hgt[triangle+1] > max_hgt: max_hgt = hgt[triangle+1]
            if hgt[triangle+2] > max_hgt: max_hgt = hgt[triangle+2]
            triangle += 3
            if hgt1 >= hgt2 and hgt1 >= hgt3: shades.append(hgt1)
            elif hgt2 >= hgt1 and hgt2 >= hgt3: shades.append(hgt2)
            else: shades.append(hgt3)

        fp.close() # Close the file

        print 'Maximum height:',max_hgt

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
            surf.module_manager.scalar_lut_manager.data_range = [0.,max_hgt]
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

