"""
数据增强，包括：随机水平翻转、随机垂直翻转、随机20度范围内的剪切、随机20%范围内的缩放、随机20%范围内的水平平移，随机20%范围内的垂直平移，
随机20度范围内的旋转。变换时，边界外像素点的填充采用“reflect”模式。图像均被缩放为256*256大小，像素值被调整到0-1之间。
"""

import os
import cv2
import numpy as np
from random import randint, uniform
import time


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


class Img:
    def __init__(self, file, file_path_out):
        self.image = cv2.imread(file, 1)
        self.filename = os.path.splitext(file)[0]
        self.filetype = os.path.splitext(file)[1]
        self.file_path_out = file_path_out
        self.h = self.image.shape[0]
        self.w = self.image.shape[1]
        self.results = [self.image]  # result image objects to save

    # flip horizontal
    def flip_horizontal(self, image):
        self.results.append(cv2.flip(image, 1))

    # flip vertical
    def flip_vertical(self, image):
        self.results.append(cv2.flip(image, 0))

    # flip (both horizontal and vertical)
    def flip(self, image):
        self.results.append(cv2.flip(image, -1))

    # rotate
    def rotate(self, image, degree):
        M = cv2.getRotationMatrix2D((self.w/2, self.h/2), degree, 1.0)
        result = cv2.warpAffine(image, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT)
        self.results.append(result)

    # translate
    def translate(self, image, delta_x, delta_y):
        M = np.float32([[1,0,delta_x], [0,1,delta_y]])
        result = cv2.warpAffine(image, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT)
        self.results.append(result)

    # crop (image center does not change, size(w, h))
    def crop_center(self, image, w, h):
        x = self.w / 2
        y = self.h / 2
        result = image[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
        self.results.append(result)

    # crop (crop image center (x, y), size (w, h))
    def crop(self, image, x, y, w, h):
        result = image[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
        self.results.append(result)

    # zoom
    def zoom(self, image, factor):
        # M = np.float32([[factor,0,0],[0,factor,0]])
        # result = cv2.warpAffine(self.image, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT)
        # self.results.append(result)
        zoomed = cv2.resize(image, None, fx=factor, fy=factor, interpolation=cv2.BORDER_REFLECT)
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
    def bright(self, image, factor):
        self.results.append(image * factor)

    # resize
    def resize(self, image, w, h):
        result = cv2.resize(image, (w, h), interpolation=cv2.BORDER_REFLECT)
        self.results.append(result)

    # resize and save processed images
    def save(self, w, h):
        i = 0
        for result in self.results:
            result = cv2.resize(result, (w, h), interpolation=cv2.BORDER_REFLECT)
            new_image = self.file_path_out + "\\" + self.filename.rsplit('\\', 1)[1] + "_" + str(i).zfill(2) + self.filetype
            cv2.imwrite(new_image, result)
            i += 1

    # perform data augmentation
    def augment(self, w, h):

        # initiate basic images
        self.rotate(self.image, 90)  # 旋转90度
        self.rotate(self.image, 180)  # 旋转180度
        self.rotate(self.image, 270)  # 旋转270度

        # do the rest operations
        for i in range(4):
            self.flip_horizontal(self.results[i])  # 水平翻转
            self.flip_vertical(self.results[i])  # 垂直翻转
            self.flip(self.results[i])  # 垂直水平反转

            self.translate(self.results[i], self.w * uniform(-0.2, 0.2), 0)  # 随机水平平移
            self.translate(self.results[i], self.w * uniform(-0.2, 0.2), 0)  # 随机水平平移
            self.translate(self.results[i], 0, self.h * uniform(-0.2, 0.2))  # 随机垂直平移
            self.translate(self.results[i], 0, self.h * uniform(-0.2, 0.2))  # 随机垂直平移

            self.rotate(self.results[i], randint(-30, 0))  # 随机30度内旋转
            self.rotate(self.results[i], randint(0, 30))  # 随机30度内旋转

            self.zoom(self.results[i], uniform(1, 1.4))  # 随机40%放大
            self.zoom(self.results[i], uniform(1, 1.4))  # 随机40%放大

            new_w = self.w * 0.8
            new_h = self.h * 0.8
            self.crop(self.results[i], int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割
            self.crop(self.results[i], int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割
            self.crop(self.results[i], int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割
            self.crop(self.results[i], int(uniform(new_w / 2, self.w - new_w / 2)), int(uniform(new_h / 2, self.h - new_h / 2)), new_w, new_h)  # 随机切割

            self.bright(self.results[i], uniform(0.8, 1.0))
            self.bright(self.results[i], uniform(1.0, 1.2))

        self.save(w, h)  # resize and save images


def single_augment(file, file_path_out, size):
    img = Img(file, file_path_out)
    img.augment(size, size)


def batch_augment(file_list, file_path_out, size):
    for file in file_list:
        single_augment(file, file_path_out, size)


if __name__ == '__main__':
    time1 = time.time()

    file_path_in = "C:\\liyu\\files\\tiff\\newtest"
    file_list = scan_files(file_path_in, postfix=".jpeg")
    file_path_out = "C:\\liyu\\files\\tiff\\newtest\\output"
    size = 512

    batch_augment(file_list, file_path_out, size)

    time2 = time.time()
    print("time cost = " + str(time2-time1) + "s")
