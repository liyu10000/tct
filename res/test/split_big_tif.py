# coding: utf-8
import random
import time

import openslide
import os
import datetime
import sys
from multiprocessing import Pool

# patch 文件大小
PATCH_SIZE = 512
# 读取步长
DELTA = 256

# 进程数量
PROCESSOR_NUM = 2


def patch_worker(input_image_path, start_x, start_y, height, output_patch_path):
    '''
    按指定 patch size 和 步长 对 tif 图像进行切分
    :param input_image_path: tif文件路径
    :param start_x: 切割起点坐标-x
    :param start_y: 切割起点坐标-y
    :param height: 切割区域
    :param output_patch_path: 输出文件路径
    :return: 无返回值
    '''

    # 读取tif文件
    img_data = openslide.OpenSlide(input_image_path)
    while start_y < height:
        # 读取patch块
        patch = img_data.read_region((start_x, start_y), 0, (PATCH_SIZE, PATCH_SIZE)).convert("RGB")
        # 保存图像
        patch.save(os.path.join(output_patch_path, "%s_%s.jpg" % (start_x, start_y)), "JPEG", quality=100)
        start_y += DELTA


def control_center(input_image_path, output_path):
    '''
    多线程切分控制方法
    :param input_image_path: 待切割 tif 文件路径
    :param output_path: 输出 patch 文件路径
    :return: 无
    '''

    img_name = os.path.basename(input_image_path)

    # 采用多线程，线程数默认为CPU核心数
    pool = Pool()

    # 读取 tif 文件
    slide = openslide.OpenSlide(input_image_path)
    if slide:
        print("Process %s ..." % img_name)
        width, height = slide.dimensions

        output_patch_path = os.path.join(output_path, img_name.split(".")[0])
        # 生成输出 patch 文件路径
        if not os.path.exists(output_patch_path):
            os.makedirs(output_patch_path)

        # 按列读取，仅读取图像中间(1/4,1/4)至(3/4,3/4)位置
        x, y = int(width / 4), int(height / 4)
        width = 2 * x
        height = 2 * y

        t0 = datetime.datetime.now()
        while x < width:
            pool.apply_async(patch_worker, (input_image_path, x, y, height, output_patch_path,))
            x += DELTA

        pool.close()
        pool.join()
        t1 = datetime.datetime.now()
        print("File - %s | Size: (%s, %s) | Total cost time: %s" % (img_name, width, height, t1 - t0))
    else:
        print("%s is not recognized" % img_name)


def get_unprocessed_files(files_dir, output_path):
    '''
    获取未处理文件进行分割处理
    :param files_dir: tif 文件存放路径
    :param output_path: patch 文件存放路径
    :return:
    '''

    done = os.listdir(output_path)
    files = os.listdir(files_dir)

    for name in files:
        if name.split(".")[0] not in done:
            input_file_path = os.path.join(files_dir, name)
            control_center(input_file_path, output_path)
        else:
            print("%s is Done" % name)


if __name__ == '__main__':
    # input_file_path = sys.argv[1]
    # output_path = sys.argv[2]
    input_file_path = "/media/tsimage/Elements1/test"
    output_path = "/media/tsimage/Elements1/test"
    get_unprocessed_files(input_file_path, output_path)
