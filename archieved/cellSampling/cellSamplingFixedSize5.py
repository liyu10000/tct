# crop specified sized images from provided (x, y) (top-left) coordinates
import os
import openslide
import scipy.misc
from utils.scan_files import scan_files
from utils.scan_subdirs import scan_subdirs


def get_crops(tif_file, image_path, new_image_path, size):
    name = tif_file[-23:-4]
    image_names = scan_files(image_path)
    image_xy = []
    for image_name in image_names:
        xy_part = image_name[:-4].rsplit("_", 2)
        x = int(xy_part[-2])
        y = int(xy_part[-1])
        image_xy.append([x, y])
    
    """
    # when size is larger than original image size
    pad = int(size/4)
    slide = openslide.OpenSlide(tif_file)
    i = 0
    for xy in image_xy:
        x = max(xy[0] - pad, 0)
        y = max(xy[1] - pad, 0)
        cell = slide.read_region((x, y), 0, (size, size))
        cell = cell.convert("RGB")
        scipy.misc.imsave(new_image_path + "/" + name + "_" + str(i).zfill(6) + ".jpg", cell)
        i += 1
    print("total images in " + name + ": " + str(i))

    slide.close()
    """

    # when size is smaller than original image size
    slide = openslide.OpenSlide(tif_file)
    i = 0
    for xy in image_xy:
        x = xy[0] + 16
        y = xy[1] + 16
        cell = slide.read_region((x, y), 0, (size, size))
        cell = cell.convert("RGB")
        scipy.misc.imsave(new_image_path + "/" + name + "_" + str(i).zfill(6) + ".jpg", cell)
        i += 1
    print("total images in " + name + ": " + str(i))
    slide.close()


if __name__ == "__main__":
    image_parentdir = "/media/tsimage/Elements1/2018-04-02-acs-h-2/2018-04-02-acs-h-2-crops-gen_0_99/reviewed"
    image_dirs = scan_subdirs(image_parentdir, postfix="select")
    tif_dir = "/media/tsimage/Elements1/2018-04-02-acs-h-2/tiff"
    new_image_parentdir = "/media/tsimage/Elements/0427-normal-size224"
    size = 224
    for image_dir in image_dirs:
        name = image_dir[:-7]
        tif_file = os.path.join(tif_dir, name+".tif")
        image_path = os.path.join(image_parentdir, image_dir)
        new_image_path = os.path.join(new_image_parentdir, name)
        if not os.path.exists(new_image_path):
            os.makedirs(new_image_path)
        get_crops(tif_file, image_path, new_image_path, size)
