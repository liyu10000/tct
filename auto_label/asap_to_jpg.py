# coding: utf-8

import datetime
import os
import sys
from multiprocessing import Pool, Manager
from time import sleep

import cv2
import numpy as np
import openslide
from asap_to_jpg_config import PATCH_SIZE, DELTA, AVAILABLE_PATCH_START_RATIO, AVAILABLE_PATCH_END_RATIO, get_patch_num, \
    get_random_string

from tslide.tslide import TSlide


def control_center(tifs, output_file_path):
    """
    多线程切分控制方法
    :param tifs: 待切割 tif 文件路径
    :param output_path: 输出 patch 文件路径
    :return: 无
    """

    t0 = datetime.datetime.now()
    for tif in tifs:
        # 读取图像
        try:
            try:
                slide = openslide.OpenSlide(tif)
            except:
                slide = TSlide(tif)

            if slide:
                t1 = datetime.datetime.now()
                img_name = os.path.basename(tif).split(".")[0]
                print("Process %s ..." % img_name)

                # 采用多进程，线程数默认为CPU核心数
                pool = Pool()

                # 统计切图数量
                in_queue = Manager().Queue()

                width, height = slide.dimensions

                # 按列读取，仅读取图像中间(指定比例)位置
                x, y, width, height = int(width * AVAILABLE_PATCH_START_RATIO), \
                                      int(height * AVAILABLE_PATCH_START_RATIO), \
                                      int(width * AVAILABLE_PATCH_END_RATIO), \
                                      int(height * AVAILABLE_PATCH_END_RATIO)
                patch_num = get_patch_num(width - x, height - y)

                output_path = os.path.join(output_file_path, img_name)
                os.makedirs(output_path, exist_ok=True)

                # 切图处理
                while x < width:
                    pool.apply_async(patch_worker, (tif, x, y, height, output_path, in_queue))
                    x += DELTA

                while in_queue.qsize() + 10 < patch_num:
                    sleep(3)
                    print("%s / %s" % (in_queue.qsize(), patch_num))

                pool.close()
                pool.join()

                print("Calculate Patch Num %s, InCome Patch Num %s" % (patch_num, in_queue.qsize()))

                t2 = datetime.datetime.now()
                print("File - %s, Size: (%s, %s), Total cost time: %s" % (img_name, width, height, t2 - t1))
        except Exception as e:
            print(str(e))

        # 关闭句柄
        slide.close()

    t3 = datetime.datetime.now()
    print("TIF FILES NUM %s, TOTAL TIME COST %s" % (len(tifs), (t3 - t0)))


def patch_worker(input_image_path, start_x, start_y, height, patch_save_path, in_queue):
    """
    按指定 patch size 和 步长 对 tif 图像进行切分
    :param patch_save_path: 切图保存路径
    :param in_queue: 统计切图数量队列
    :param input_image_path: tif文件路径
    :param start_x: 切割起点坐标-x
    :param start_y: 切割起点坐标-y
    :param height: 切割区域
    :return: 无返回值
    """

    # 读取tif文件
    try:
        img_data = openslide.OpenSlide(input_image_path)
    except:
        img_data = TSlide(input_image_path)

    while start_y < height:
        # 读取patch块
        patch = img_data.read_region((start_x, start_y), 0, (PATCH_SIZE, PATCH_SIZE))

        # 图像格式转换
        patch = cv2.cvtColor(np.asarray(patch), cv2.COLOR_RGBA2BGR)

        # 检查图像是否可用
        patch_gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
        if cv2.Laplacian(patch_gray, cv2.CV_64F).var() > 10.0:
            in_queue.put(1)

            # 生成文件名及保存路径
            #name = get_random_string()
            save_path = os.path.join(patch_save_path, "{}_{}.jpg".format(start_x,start_y))
            # 文件写入
            cv2.imwrite(save_path, patch)

        start_y += DELTA

    # 关闭句柄
    img_data.close()


def asap_to_image(input_file_path, output_file_path):
    files = []
    if os.path.isfile(input_file_path):
        files.append(input_file_path)
    else:
        for root, dirs, filenames in os.walk(input_file_path):
            for filename in filenames:
                if filename.endswith(".tif") or filename.endswith(".kfb"):
                    files.append(os.path.join(root, filename))

    if len(files) > 0:
        control_center(files, output_file_path)


if __name__ == '__main__':
    # input_file_path = sys.argv[1]
    # output_file_path = sys.argv[2]

    input_file_path = "/home/sakulaki/yolo-yuli/one_stop_test/yantian_tif"
    output_file_path = "/home/sakulaki/yolo-yuli/one_stop_test/yantian_kfb/jpg"

    asap_to_image(input_file_path, output_file_path)
