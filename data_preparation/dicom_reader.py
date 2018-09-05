import os
import cv2
import png
import pydicom
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance


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


dcms = scan_files("/media/tsimage001/TSIMAGE/CT/CT_a784d07a2d539b8a6d9448a3892a5d01/118ba86eedb66f8d2b0b30c83d3762d3", postfix=".dcm")
save_path = "/media/tsimage001/TSIMAGE/CT-png/CT_a784d07a2d539b8a6d9448a3892a5d01/118ba86eedb66f8d2b0b30c83d3762d3"
if not os.path.exists(save_path):
    os.makedirs(save_path)

count = 0
for dcm in dcms:
    # name = os.path.splitext(os.path.basename(dcm))[0]
    # img_name = os.path.join(save_path, name+".png")
    index = os.path.splitext(os.path.basename(dcm))[0].rsplit("_",1)[1][-3:]
    img_name = os.path.join(save_path, "img_{}_i.png".format(index))

    ds = pydicom.dcmread(dcm)
    shape = ds.pixel_array.shape
    # Convert to float to avoid overflow or underflow losses.
    img = ds.pixel_array.astype(float)

    # if count == 0:
    #     img = (img-img.min())/(img.max()-img.min())*255.0
    #     # img = np.clip(np.int8(img), 50, 255)
    #     plt.subplot(121)
    #     sns.distplot(img.flatten())
    #     plt.subplot(122)
    #     plt.imshow(img, cmap=plt.cm.gray)
    #     plt.show()
    #     count += 1

    # brightness = 30
    # contrast = 10
    # img = img * (contrast/127+1) - contrast + brightness
    img = (img-img.min())/(img.max()-img.min())*255.0
    # img = np.clip(img, 0, 255)
    img = np.uint8(img)

    # img = np.int8(img)
    # img = [[max(pixel-25, 0) if pixel < 200 else min(pixel+25, 255) for pixel in row] for row in img]

    # # Rescaling grey scale between 0-255
    # img = (np.maximum(img,0) / img.max()) * 255.0
    # # Convert to uint
    # img = np.uint8(img)

    # # enhance image
    # ImageEnhance.Brightness(Image.fromarray(img)).enhance(7.5).save(img_name)

    # # power law transformation (gamma correction)
    # img = cv2.pow(img, 0.6)

    # Write the PNG file
    with open(img_name, 'wb') as png_file:
        w = png.Writer(shape[1], shape[0], greyscale=True)
        w.write(png_file, img)

    # plt.imsave(img_name, ds.pixel_array, cmap=plt.cm.gray)
