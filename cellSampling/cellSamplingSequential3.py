# coding=utf-8
import os
import openslide
import scipy.misc
import time
from multiprocessing import Process, Pool
from functools import partial


def getSize(file):
    try:
        slide = openslide.OpenSlide(file)
        [size_x, size_y] = slide.dimensions
        slide.close()
        return [size_x, size_y]
    except:
        print(file + " cannot be processed")
        return []


def cellSampling(file, file_out, size, size_x, size_y, num):
    # get file name
    filename = os.path.splitext(file)[0]
    try:
        slide = openslide.OpenSlide(file)
        step = int(size/2)
        x, i = 0, 0
        y = y_min = int(size_y * num / 4)
        y_max = int(size_y * (num+1) / 4)
        while y_min <= y < y_max:
            while x < size_x:
                cropped_name = file_out + "\\" + filename[3:].replace("\\", "_") + "_" + str(num) + "_" + str(i).zfill(8) + ".jpg"
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


if __name__ == "__main__":
    time1 = time.time()

    file = "C:\\liyu\\files\\slicing\\2018-03-26-16_48_30.tif"
    file_out = "C:\\liyu\\files\\slicing\\output"
    size = 512

    [size_x, size_y] = getSize(file)
    # for num in range(4):
    #     p = Process(target=cellSampling, args=(file, file_out, size, size_x, size_y, num))
    #     p.start()
    #     p.join()

    pool = Pool(processes=4)
    pool.map(partial(cellSampling, file=file, file_out=file_out, size=size, size_x=size_x, size_y=size_y), range(4))

    time2 = time.time()
    print("time cost = " + str(time2 - time1) + "s")

