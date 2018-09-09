# import sys
# sys.path.append("C:\\Users\\tsimage\\Downloads\\openslide-win64-20171122\\bin")
# print(sys.path)

import openslide
import numpy
import scipy.misc
# import matplotlib.pyplot as plt

# slide = openslide.OpenSlide("/mnt/c/liyu/files/tiff/large.tif")
slide = openslide.OpenSlide("C:\\liyu\\files\\tiff\\large.tif")

#get the number of tiles
level_count = slide.level_count
print ("level_count = " + str(level_count))

#size of original tif
[m,n] = slide.dimensions
print (m,n)

#size of the ith tile
[mtop,ntop] = slide.level_dimensions[level_count-1]
print (mtop,ntop)

#get the downsizing factor of ith tile
slide_level_downsamples = slide.level_downsamples[level_count-1]
print (slide_level_downsamples)

#read_region(location, level, size) returns a RGBA image
top = slide.read_region((0,0), level_count-1, (mtop,ntop))
topTile = numpy.array(top)
# plt.figure()
# plt.imshow(topTile)
# pylab.show()

# scipy.misc.imsave('/mnt/c/liyu/files/tiff/small.tif', topTile)
scipy.misc.imsave("C:\\liyu\\files\\tiff\\small.tif", topTile)
print (len(topTile))

slide.close()
