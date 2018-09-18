# randomly crop images from given tifs
import os
import openslide
import scipy.misc
from random import randint
from utils.scan_files import scan_files


def cellSampling(files_list, n, size, save_path):
    for file in files_list:
        filename = os.path.splitext(file)[0].rsplit("\\", 1)[1]
        try:
            slide = openslide.OpenSlide(file)
            [size_x, size_y] = slide.dimensions
            for i in range(n):
                x = randint(size, size_x-size)
                y = randint(size, size_y-size)
                cell = slide.read_region((x, y), 0, (size, size))
                cell = cell.convert("RGB")
                scipy.misc.imsave(save_path + "\\" + filename + "_" + str(i).zfill(3) + ".jpg", cell)
            slide.close()
        except:
            print(filename + " cannot be processed")


if __name__ == "__main__":
    file_path = "E:\\2018-04-08-normal\\tiff"
    files_list = scan_files(file_path, postfix=".tif")
    save_path = "D:\\data0\\2018-04-08-normal-crops"
    n = 10  # number of crops per slide
    size = 4096  # size of each crop
    cellSampling(files_list, n, size, save_path)



