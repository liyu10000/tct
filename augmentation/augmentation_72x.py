"""
数据增强，包括：随机水平翻转、随机垂直翻转、随机20度范围内的剪切、随机20%范围内的缩放、随机20%范围内的水平平移，随机20%范围内的垂直平移，
随机20度范围内的旋转。变换时，边界外像素点的填充采用“reflect”模式。图像均被缩放为256*256大小，像素值被调整到0-1之间。
"""

import os
import cv2
import numpy as np
from random import randint, uniform
import time
from multiprocessing import Pool, cpu_count
from functools import partial


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

def get_immediate_subdirectories(dir):
    return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]

class Img:
    def __init__(self, file, file_path_out):
        self.image = cv2.imread(file, 1)
        self.filename = os.path.splitext(file)[0]
        self.filetype = os.path.splitext(file)[1]
        self.file_path_out = file_path_out
        self.h = self.image.shape[0]
        self.w = self.image.shape[1]
        self.results = []  # result image objects to save
        self.i = 0  # store the index of augmented images
        self.new_images = []  # store the names of augmented images

    # flip horizontal
    def flip_horizontal(self):
        self.results.append(cv2.flip(self.image, 1))

    # flip vertical
    def flip_vertical(self):
        self.results.append(cv2.flip(self.image, 0))

    # flip (both horizontal and vertical)
    def flip(self):
        self.results.append(cv2.flip(self.image, -1))

    # rotate
    def rotate(self, degree):
        M = cv2.getRotationMatrix2D((self.w/2, self.h/2), degree, 1.0)
        result = cv2.warpAffine(self.image, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT)
        self.results.append(result)

    # translate
    def translate(self, delta_x, delta_y):
        M = np.float32([[1,0,delta_x], [0,1,delta_y]])
        result = cv2.warpAffine(self.image, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT)
        self.results.append(result)

    # crop (image center does not change, size(w, h))
    def crop_center(self, w, h):
        x = self.w / 2
        y = self.h / 2
        result = self.image[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
        self.results.append(result)

    # crop (crop image center (x, y), size (w, h))
    def crop(self, x, y, w, h):
        result = self.image[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
        self.results.append(result)

    # zoom
    def zoom(self, factor):
        # M = np.float32([[factor,0,0],[0,factor,0]])
        # result = cv2.warpAffine(self.image, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT)
        # self.results.append(result)
        zoomed = cv2.resize(self.image, None, fx=factor, fy=factor, interpolation=cv2.BORDER_REFLECT)
        if factor < 1:
            top = self.h*(1-factor)/2
            bottom = top
            left = self.w*(1-factor)/2
            right = left
            result = cv2.copyMakeBorder(zoomed, int(top), int(bottom), int(left), int(right), cv2.BORDER_REFLECT)
        else:
            x = self.w*factor/2
            y = self.h*factor/2
            w = self.w
            h = self.h
            result = zoomed[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
        self.results.append(result)

    # change brightness
    def bright(self, factor):
        self.results.append(self.image * factor)

    # resize
    def resize(self, w, h):
        result = cv2.resize(self.image, (w, h), interpolation=cv2.BORDER_REFLECT)
        self.results.append(result)

    # resize and save processed images
    def save(self, w, h):
        for result in self.results:
            result = cv2.resize(result, (w, h), interpolation=cv2.BORDER_REFLECT)
            #new_image = self.file_path_out + "/" + self.filename.rsplit('/', 1)[1] + "_" + str(self.i).zfill(2) + self.filetype
            new_image = self.file_path_out + "/" + self.filename.rsplit('/', 1)[1] + "_" + str(self.i).zfill(2) + '.jpg' 
            self.new_images.append(new_image)
            cv2.imwrite(new_image, result)
            self.i += 1

    # initiate basic images
    def base(self, w, h):
        self.rotate(90)  # 旋转90度
        self.rotate(180)  # 旋转180度
        self.rotate(270)  # 旋转270度
        self.rotate(0)
        self.save(w, h)
        return self.new_images

    # perform data augmentation
    def augment(self, w, h):
        self.flip_horizontal()  # 水平翻转
        self.flip_vertical()  # 垂直翻转
        self.flip()  # 垂直水平反转

        self.translate(self.w * uniform(-0.2, 0.0), 0)  # 随机水平平移
        self.translate(self.w * uniform(0.0, 0.2), 0)   # 随机水平平移
        self.translate(0, self.h * uniform(-0.2, 0.0))  # 随机垂直平移
        self.translate(0, self.h * uniform(0.0, 0.2))   # 随机垂直平移

        self.rotate(randint(-30, 0))  # 随机30度内旋转
        self.rotate(randint(0, 30))   # 随机30度内旋转

        self.zoom(uniform(1, 1.4))  # 随机40%放大
        self.zoom(uniform(1, 1.4))  # 随机40%放大

        new_w = self.w * 0.8
        new_h = self.h * 0.8
        self.crop(int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割
        self.crop(int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割
        self.crop(int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割
        self.crop(int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割

        self.bright(uniform(0.8, 1.0))
        self.bright(uniform(1.0, 1.2))

        self.save(w, h)  # resize and save images


def bath_augment(file_list, file_path_out, size):
    for file in file_list:
        single_augment(file, file_path_out, size)


def single_augment(file, file_path_out, size):
    if not os.path.exists(file_path_out):
        os.makedirs(file_path_out)

    img = Img(file, file_path_out)
    base = img.base(size, size)
    for new_image in base:
        new_img = Img(new_image, file_path_out)
        new_img.augment(size, size)


aug_times = {"#000000": 4,
           "#aa0000": 4,
           "#aa007f": 16,
           "#aa00ff": 16,
           "#ff0000": 16,
           "#005500": 4,
           "#00557f": 8,
           "#0055ff": 16,
           "#aa5500": 4,
           "#aa557f": 72,
           "#aa55ff": 72,
           "#ff5500": 72,
           "#ff557f": 0,
           "#ff55ff": 0,
           "#00aa00": 16,
           "#00aa7f": 72,
           "#00aaff": 16,
           "#55aa00": 32,
           "#55aa7f": 72}
        
if __name__ == '__main__':
    time1 = time.time()

    size = 224
    try:
        workers = cpu_count()
    except NotImplementedError:
        workers = 1

    file_path_in = "/home/ubuntu/Ma/data/tct0428/train/"
    file_path_out = "/home/ubuntu/Ma/data/tct0428/train-aug/"
    immediate_directories  = get_immediate_subdirectories(file_path_in)
    times =  72

    pool = Pool(processes=workers)
    for subdir in immediate_directories:
        if aug_times[subdir] == times
            file_list = scan_files(os.path.join(file_path_in, subdir), postfix=".jpg")
            pool.map(partial(single_augment, file_path_out=os.path.join(file_path_out,subdir), size=size), file_list)

    time2 = time.time()
    print("time cost = " + str(time2-time1) + "s")
