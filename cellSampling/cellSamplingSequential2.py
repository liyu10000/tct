# coding=utf-8
import os
import openslide
import scipy.misc
import time
from multiprocessing import Pool, freeze_support
from functools import partial


def cellSampling(file, file_out, size):
    # get file name
    filename = os.path.splitext(file)[0]

    # try:
    slide = openslide.OpenSlide(file)

    # size of original tif
    [size_x, size_y] = slide.dimensions

    args = []
    step = int(size/2)
    x, y, i = 0, 0, 0
    while y < 1000:
        while x < 1000:
            cropped_name = file_out + "\\" + filename[3:].replace("\\", "_") + "_" + str(i).zfill(8) + ".jpeg"
            # crop(slide, x, y, size, cropped_name)
            args.append((x, y, cropped_name))
            x += step
            i += 1
        x = 0
        y += step

    # for arg in args:
    #     crop(slide, size, arg)

    pool = Pool(processes=4)
    pool.map(partial(crop, slide=slide, size=size), args)

    slide.close()

    # except:
    #     print(filename + " cannot be processed")


def crop(slide, size, arg):
    x, y, cropped_name = arg
    cell = slide.read_region((x, y), 0, (size, size))
    cell = cell.convert("RGB")
    scipy.misc.imsave(cropped_name, cell)


if __name__ == "__main__":
    # freeze_support()

    time1 = time.time()

    file = "C:\\liyu\\files\\slicing\\2018-03-26-16_48_30.tif"
    file_out = "C:\\liyu\\files\\slicing\\output2"
    size = 512
    cellSampling(file, file_out, size)

    time2 = time.time()
    print("time cost = " + str(time2 - time1) + "s")

