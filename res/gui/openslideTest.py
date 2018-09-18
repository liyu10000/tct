#add local binary to current working evenvironment, already added it to system search path
#import os
#os.environ['PATH'] = "C:\\Users\\tsimage\\AppData\\Local\\Programs\\Common\\openslide-win64-20171122\\bin" + ";" + os.environ['PATH']

import openslide
import numpy
import scipy.misc
# import matplotlib.pyplot as plt

import os

file = "C:\\liyu\\files\\tiff\\large.tif"
# file = "C:\\liyu\\files\\1M01 - Annotation 1\\1M01_Default_Extended.tif"

slide = openslide.OpenSlide(file)

#get the number of tiles
level_count = slide.level_count
print ("level_count = " + str(level_count))

#size of original tif
[m,n] = slide.dimensions
print (m,n)

#size of the top tile
[mtop,ntop] = slide.level_dimensions[level_count-1]
print (mtop,ntop)

# #get the downsizing factor of ith tile
# slide_level_downsamples = slide.level_downsamples[level_count-1]
# print (slide_level_downsamples)
#
# #read_region(location, level, size) returns a RGBA image
# top = slide.read_region((0,0), level_count-1, (mtop,ntop))
# topTile = numpy.array(top)
# # plt.figure()
# # plt.imshow(topTile)
# # pylab.show()
#
# scipy.misc.imsave("C:\\liyu\\files\\tiff\\small.tif", topTile)
# # print (len(topTile))

# get the dimension and level_downsample factor, save each tile to tif image
# filename = os.path.splitext(file)[0]
# filetype = os.path.splitext(file)[1]
# for i in range(level_count):
#     [mi, ni] = slide.level_dimensions[i]  # the dimension of ith tile
#     slide_level_downsamples_i = slide.level_downsamples[i]  # level_downsample of ith tile, relative to 0th
#     print(mi, ni, slide_level_downsamples_i)
#
#     # tile_i = slide.read_region((0, 0), i, (mi, ni))
#     # tile_i_array = numpy.array(tile_i)
#     #
#     # file_tile_i = filename + str(i) + filetype
#     # scipy.misc.imsave(file_tile_i, tile_i_array)

# get the corresponding tile i within the given downsample
# slide_downsamples_5 = slide.get_best_level_for_downsample(5.0)
# print(slide_downsamples_5)  # returns i that has the closest level_downsample


# test function read_region(location, level, size)
# location is relative to the 0th tile, size will be the final size
# so the output dimension should depend on location and the dowmsampling level given
# test = slide.read_region((int(m/2), int(n/2)), level_count-1, (int(mtop/2), int(ntop/2)))
# test_array = numpy.array(test)
# scipy.misc.imsave("C:\\liyu\\files\\tiff\\test.tif", test_array)

slide.close()
