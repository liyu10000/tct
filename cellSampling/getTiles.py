import openslide
import scipy.misc

slide = openslide.OpenSlide("C:\\liyu\\files\\tiles\\large.tif")

#get the number of tiles
level_count = slide.level_count
print ("level_count = " + str(level_count))

for i in range(2, level_count):
    [m, n] = slide.level_dimensions[i]
    print(m, n)
    tile = slide.read_region((0, 0), i, (m, n))
    tile = tile.convert("RGB")
    scipy.misc.imsave("C:\\liyu\\files\\tiles\\sample4-tile" + str(i) + ".jpg", tile)

slide.close()
