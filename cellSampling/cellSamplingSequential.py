# coding=utf-8
import os
import openslide
import scipy.misc
import time


def cellSampling(file, file_out, size):
    # get file name
    filename = os.path.splitext(file)[0]

    try:
        slide = openslide.OpenSlide(file)

        # size of original tif
        [size_x, size_y] = slide.dimensions
        # print(size_x, size_y)

        step = int(size/2)
        x, y, i = 0, 0, 0
        while y < size_y:
            while x < size_x:
                cropped_name = file_out + "\\" + filename[3:].replace("\\", "_") + "_" + str(i).zfill(8) + ".jpeg"
                cell = slide.read_region((x, y), 0, (size, size))
                cell = cell.convert("RGB")
                scipy.misc.imsave(cropped_name, cell)
                x += step
                i += 1
            x = 0
            y += step

        slide.close()

    except:
        print(filename + " cannot be processed")


time1 = time.time()

file = "C:\\liyu\\files\\slicing\\2018-03-26-16_48_30.tif"
file_out = "C:\\liyu\\files\\slicing\\output"
size = 512
cellSampling(file, file_out, size)

time2 = time.time()
print("time cost = " + str(time2 - time1) + "s")

