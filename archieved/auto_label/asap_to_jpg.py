# coding: utf-8
from concurrent.futures import ProcessPoolExecutor, as_completed

import datetime
import os
import sys

import cv2
import numpy as np
import openslide
from asap_to_jpg_config import PATCH_SIZE, DELTA, AVAILABLE_PATCH_START_RATIO, AVAILABLE_PATCH_END_RATIO, get_patch_num, \
    get_random_string, MATTING_PROCESS_NUM

from tslide.tslide import TSlide


def worker(input_file_path, start_x, start_y, height, patch_save_path):
    """
    :param input_file_path: 输入文件路径
    :param start_x:
    :param start_y:
    :param height:
    :param patch_save_path:
    :return:
    """
    count = 0
    try:
        slide = openslide.OpenSlide(input_file_path)
    except:
        slide = TSlide(input_file_path)

    while start_y < height:
        # 读取patch块
        patch = slide.read_region((start_x, start_y), 0, (PATCH_SIZE, PATCH_SIZE))

        # 图像格式转换
        patch = cv2.cvtColor(np.asarray(patch), cv2.COLOR_RGBA2BGR)
        # 生成文件名及保存路径
        #name = get_random_string()
        save_path = os.path.join(patch_save_path, "{}_{}.jpg".format(start_x,start_y))
        # 文件写入
        cv2.imwrite(save_path, patch)

        start_y += DELTA
        count += 1

    return count


def asap_to_image(input_file_path, output_file_path):
    """

    :param input_file_path: 输入文件路径
    :param output_file_path: 输出文件路径
    :return:
    """
    t0 = datetime.datetime.now()

    try:
        slide = openslide.OpenSlide(input_file_path)
    except:
        slide = TSlide(input_file_path)

    if slide:
        img_name = os.path.basename(input_file_path).split(".")[0]
        print("Process %s ..." % img_name)

        width, height = slide.dimensions

        # 按列读取，仅读取图像中间(指定比例)位置
        x, y, width, height = int(width * AVAILABLE_PATCH_START_RATIO), \
                              int(height * AVAILABLE_PATCH_START_RATIO), \
                              int(width * AVAILABLE_PATCH_END_RATIO), \
                              int(height * AVAILABLE_PATCH_END_RATIO)
        patch_num = get_patch_num(width - x, height - y)

        output_path = os.path.join(output_file_path, img_name)
        os.makedirs(output_path, exist_ok=True)

        tasks = []

        # 创建线程池
        executor = ProcessPoolExecutor(max_workers=MATTING_PROCESS_NUM)

        t00 = datetime.datetime.now()
        print("Adding Job to Pool...")
        # 切图处理
        while x < width:
            tasks.append(executor.submit(worker, input_file_path, x, y, height, output_path))
            x += DELTA
        t01 = datetime.datetime.now()
        print("Done, cost: %s" % (t01 - t00))

        print("Total Job Count: %s, Worker Count: %s" % (len(tasks), MATTING_PROCESS_NUM))
        job_count = len(tasks)
        patch_count = 0
        for future in as_completed(tasks):
            count = future.result()
            patch_count += count
            job_count -= 1
            print("One Job Done, Got %s patches, last Job Count: %s" % (count, job_count))

        t1 = datetime.datetime.now()
        print("File - %s, Size: (%s, %s), Calculate Patch Num %s, Got Patch Num %s, Total cost time: %s" % (
        img_name, width, height, patch_num, patch_count, t1 - t0))


if __name__ == '__main__':
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    asap_to_image(input_file_path, output_file_path)
