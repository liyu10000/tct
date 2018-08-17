# randomly crop images from given tifs
import os
import openslide
import scipy.misc
from random import randint


def scan_files(directory, prefix=None, postfix=None):
    files_list = []
    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root, special_file))
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root, special_file))
            else:
                files_list.append(os.path.join(root, special_file))
    return files_list


def cellSampling(files_list, n, size):
    for file in files_list:
        # get file name
        filename = os.path.splitext(file)[0]

        try:
            slide = openslide.OpenSlide(file)

            # size of original tif
            [size_x, size_y] = slide.dimensions

            for i in range(n):
                x = randint(size, size_x-size)
                y = randint(size, size_y-size)
                cell = slide.read_region((x, y), 0, (size, size))
                # cell_array = numpy.array(cell)
                cell = cell.convert("RGB")
                scipy.misc.imsave("F:\\0515-2018-04-08-normal-size256\\" + filename[3:].replace("\\", "_") + "_" + str(i).zfill(6) + ".jpg", cell)

            slide.close()

        except:
            print(filename + " cannot be processed")


file_path = "D:\\2018-04-08-normal\\tiff"
files_list = scan_files(file_path, postfix=".tif")
n = 10  # number of crops per slide
size = 256  # size of each crop
cellSampling(files_list, n, size)



