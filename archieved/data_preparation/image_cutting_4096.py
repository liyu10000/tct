# coding: utf-8
import datetime
import os
from multiprocessing import Pool
import openslide
import cv2
import numpy as np
from openslide import OpenSlideUnsupportedFormatError

# 默认切图大小
PATCH_SIZE = 608
# 切图步长
STEP_DELTA = 608
# 最高像素回收值
MAX_RECOLLECTION_PIXEL = 253
# 最低像素回收值
MIN_RECOLLECTION_PIXEL = 62
# 切图比例-开始
AVAILABLE_PATCH_START_RATIO = 0.1
# 切图比例-结束
AVAILABLE_PATCH_END_RATIO = 0.9
# 切图文件格式
SUFFIX = ".tif"


class FilesScanner(object):
    """
    获取文件列表工具类
    """

    def __init__(self, files_path, suffix=None):
        """

        :param files_path: 待扫描文件路径
        :param suffix: 所需文件后缀，默认为空，即获取该路径下所有文件
        """
        self.files_path = files_path

        files = []
        if os.path.isfile(files_path):
            if suffix:
                if files_path.endswith(suffix):
                    files.append(files_path)
            else:
                files.append(files_path)

        if os.path.isdir(files_path):
            for root, dirs, filenames in os.walk(files_path):
                for filename in filenames:
                    if suffix:
                        if filename.endswith(suffix):
                            files.append(os.path.join(root, filename))
                    else:
                        files.append(os.path.join(root, filename))

        self.files = files

    def get_files(self):
        return self.files


def control_center(tifs, output_file_path):
    """
    多进程切分控制方法
    :param tifs: 待切割 tif 文件路径
    :param output_file_path: 输出 patch 文件路径
    :return: 无
    """

    for tif in tifs:
        # 读取图像
        try:
            t0 = datetime.datetime.now()
            slide = openslide.OpenSlide(tif)
            img_name = os.path.basename(tif).split(".")[0]
            print("Process %s ..." % tif)

            # 采用多线程，线程数默认为CPU核心数
            pool = Pool(processes=4)
            width, height = slide.dimensions

            # 按列读取，仅读取图像中间(指定比例)位置
            x, y, width, height = int(width * AVAILABLE_PATCH_START_RATIO), \
                                  int(height * AVAILABLE_PATCH_START_RATIO), \
                                  int(width * AVAILABLE_PATCH_END_RATIO), \
                                  int(height * AVAILABLE_PATCH_END_RATIO)

            rets = []
            output_path = os.path.join(output_file_path, img_name)
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # 切图处理
            while x < width - PATCH_SIZE:
                rets.append(pool.apply_async(worker, (tif, x, y, height, output_path)))
                x += STEP_DELTA

            pool.close()
            pool.join()

            # 切图数量统计
            patch_count = 0
            for ret in rets:
                patch_count += ret.get()

            slide.close()
            t1 = datetime.datetime.now()
            print("File - %s, Patch Count: %s, Cost Time: %s" % (tif, patch_count, (t1 - t0)))
        except OpenSlideUnsupportedFormatError as e:
            print(tif + " cannot be opened: " + e)


def worker(input_image_path, start_x, start_y, height, output_path):
    """
    按指定 patch size 和 步长 对 tif 图像进行切分
    :param input_image_path: tif文件路径
    :param start_x: 切割起点坐标-x
    :param start_y: 切割起点坐标-y
    :param height: 切割区域
    :param output_path: 输出切图路径
    :return: 无返回值
    """

    # 读取tif文件
    img_data = openslide.OpenSlide(input_image_path)
    index = 0
    while start_y < height - PATCH_SIZE:
        # 读取patch块及转换格式
        patch = img_data.read_region((start_x, start_y), 0, (PATCH_SIZE, PATCH_SIZE))
        # 图像格式转换
        patch = cv2.cvtColor(np.asarray(patch), cv2.COLOR_RGBA2BGR)
        if  np.mean(patch) > MIN_RECOLLECTION_PIXEL and np.mean(patch) < MAX_RECOLLECTION_PIXEL:
            cv2.imwrite(os.path.join(output_path, "%s_%s.jpg" % (start_x, start_y)), patch)
            index += 1
        start_y += STEP_DELTA
    return index + 1


def main(input_file_path, output_file_path):
    """
    入口方法
    :param input_file_path: 输入文件路径
    :param output_file_path: 输出文件路径
    :return:
    """
    t0 = datetime.datetime.now()

    files = FilesScanner(input_file_path, SUFFIX).get_files()

    if len(files) > 0:
        if not os.path.exists(output_file_path):
            os.makedirs(output_file_path)
        control_center(files, output_file_path)
    else:
        raise Exception("NO AVAILABLE %s FILES FOUND!" % SUFFIX)

    t1 = datetime.datetime.now()
    print("Processed Files Num: %s, Total Time Cost: %s" % (len(files), (t1 - t0)))


if __name__ == '__main__':
    # input_file_path = sys.argv[1]
    # output_file_path = sys.argv[2]

    #input_file_path = "E:\\2017-11-24-hsil"
    #output_file_path = "F:\\data0\\2017-11-24-hsil-4096"
    input_file_path = os.path.join(os.getcwd(), "tif")
    output_file_path = os.path.join(os.getcwd(), "608")

    main(input_file_path, output_file_path)
