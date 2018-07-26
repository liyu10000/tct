import openslide
import numpy
# import scipy.misc

def getTopTile(file):
    
    slide = openslide.OpenSlide(file)

    #get the number of tiles
    level_count = slide.level_count

    #size of original tif
    # [m,n] = slide.dimensions

    #size of the ith tile
    [mtop,ntop] = slide.level_dimensions[level_count-1]

    #get the downsizing factor of ith tile
    # slide_level_downsamples = slide.level_downsamples[level_count-1]

    #read_region(location, level, size) returns a RGBA image
    top = slide.read_region((0,0), level_count-1, (mtop,ntop))
    topTile = numpy.array(top)

    #save to image
    # scipy.misc.imsave('/mnt/c/liyu/files/tiff/small.tif', topTile)

    slide.close()
    
    return topTile
