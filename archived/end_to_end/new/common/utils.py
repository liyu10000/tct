import datetime
import math
import os
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy

import cv2
import numpy as np
import openslide

from config.config import cfg
from common.tslide.tslide import TSlide

import uuid


def image_format(image, width=cfg.algo.DEFAULT_WIDTH, height=cfg.algo.DEFAULT_HEIGHT):
    """
    将图像格式化成指定大小
    :param image: 图像 numpy
    :param width: 格式化默认宽
    :param height: 格式化默认高
    :return:
    """
    h, w, _ = image.shape
    dh, dw = max(0, height - h), max(0, width - w)
    top, bottom = dh // 2, dh - dh // 2
    left, right = dw // 2, dw - dw // 2
    image = cv2.copyMakeBorder(image, top=top, bottom=bottom, left=left, right=right, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))

    h, w, _ = image.shape
    image = image[h // 2 - height // 2: h // 2 + height // 2, w // 2 - width // 2: w // 2 + width // 2]
    # cv2.imwrite('/tmp/metadata/cells/2/%s.jpg' % str(uuid.uuid4()), image)
    return image


def generate_cell_image(image_path, names, points):
    """
    根据 darknet 细胞分割结果获取独立的细胞图像
    :param image_path: 图像路径
    :param names: 图像文件名列表
    :param points: 对应坐标点集
    :return:
    """

    cells = []
    for name in names:
        image = os.path.join(image_path, name + '.jpg')
        image = cv2.imread(image)

        lst = points[name]
        for point in lst:
            print(point)
            label, accuracy, (x, y, w, h) = point
            x, y, w, h = int(x), int(y), int(w), int(h)
            cell = image[y: y + h, x: x + w]
            cells.append(image_format(cell))

            # cv2.imwrite('/tmp/metadata/cells/2/%s.jpg' % str(uuid.uuid4()), cell)
            #
            # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 4)
            # cv2.putText(image, label, (x, y), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 1)

        # cv2.imwrite('/tmp/metadata/cells/2/%s.jpg' % name, image)

    return cells


def calculate_patch_num(w, h, delta=cfg.slice.DELTA):
    """
    计算切图数量
    :param w:
    :param h:
    :param delta:
    :return:
    """
    return math.ceil(w / delta) * math.ceil(h / delta)


class FilesScanner(object):
    """
    获取文件列表工具类
    """

    def __init__(self, files_path, postfix=None):
        """

        :param files_path: 待扫描文件路径
        :param postfix: 所需文件后缀，默认为空，即获取该路径下所有文件
        """
        self.files_path = files_path

        files = []
        if os.path.isfile(files_path):
            if postfix:
                if files_path.endswith(postfix):
                    files.append(files_path)
            else:
                files.append(files_path)

        if os.path.isdir(files_path):
            for root, dirs, filenames in os.walk(files_path):
                for filename in filenames:
                    if postfix:
                        if filename.endswith(postfix):
                            files.append(os.path.join(root, filename))
                    else:
                        files.append(os.path.join(root, filename))
        # 替换为绝对路径
        files = [os.path.abspath(item) for item in files]

        self.files = files

    def get_files(self):
        return self.files


def get_available_gpus():
    """
    获取 GPU 编号
    """
    from tensorflow.python.client import device_lib as _device_lib
    local_device_protos = _device_lib.list_local_devices()
    return [x.name.split(':')[-1] for x in local_device_protos if x.device_type == 'GPU']


def worker(image, start_x, start_y, height, patch_width, patch_height, delta, patch_save_path):
    """
    按行切图，并保存为图像文件，每个 worker 只负责处理一行
    :param image: 图像文件地址
    :param start_x: 切图起点坐标-x
    :param start_y: 切图起点坐标-y
    :param height: 切图最大高度
    :param patch_width: 切图尺寸-宽
    :param patch_height: 切图尺寸-高
    :param delta: 切图步长
    :param patch_save_path:
    :return: 切图数量
    """

    # 结果队列
    queue = []

    try:
        slide = openslide.OpenSlide(image)
    except:
        slide = TSlide(image)

    # # 获取图像宽，高
    # width, height = slide.dimensions

    try:
        while start_y < height:
            # 读取patch块
            patch = slide.read_region((start_x, start_y), 0, (patch_width, patch_height))

            # 图像格式转换
            patch = cv2.cvtColor(np.asarray(patch), cv2.COLOR_RGBA2BGR)

            # 过滤
            patch_gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
            if cv2.Laplacian(patch_gray, cv2.CV_64F).var() > cfg.slice.THRESH:
                # 生成文件路径
                save_path = os.path.join(patch_save_path, "%s_%s.jpg" % (start_x, start_y))
                # 文件写入
                cv2.imwrite(save_path, patch)
                cv2.imwrite('/tmp/metadata/cells/1/%s_%s.jpg' % (start_x, start_y), patch)

                queue.append(save_path)

            start_y += delta

        return queue
    except:
        raise


class ImageSlice(object):
    """
    切图工具类
    """

    def __init__(self, input_file_path, output_file_path):
        """

        :param input_file_path: 输入文件路径, 文件路径或文件夹路径
        :param output_file_path: 输出文件路径
        """
        self.images = FilesScanner(input_file_path).get_files()
        self.output_path = output_file_path

    def get_slices(self):
        """

        :return: [切图存放路径,]
        """
        # 处理成功任务列表
        done = []
        # 处理失败任务列表
        fail = []

        for image in self.images:
            t0 = datetime.datetime.now()

            # 获取病理图像文件名，假如文件名中有空格的话，以 "_" 替换
            img_name = os.path.basename(image).split(".")[0].replace(" ", "_")
            print("Image Process %s ..." % image)

            try:
                slide = None
                if image.endswith(".tif"):
                    slide = openslide.OpenSlide(image)

                if image.endswith(".kfb"):
                    slide = TSlide(image)

                if slide:
                    _width, _height = slide.dimensions

                    output_path = os.path.join(self.output_path, img_name)
                    # 假如目标路径存在，删除文件然后重新写入
                    if os.path.exists(output_path):
                        shutil.rmtree(output_path)

                    os.makedirs(output_path, exist_ok=True)

                    # 创建进程池
                    executor = ProcessPoolExecutor(max_workers=cfg.slice.SLICE_PROCESS_NUM)

                    t1 = datetime.datetime.now()
                    print("Adding Job to Pool...")

                    # 按行读取，仅读取图像中间(指定比例)位置
                    x, y, width, height = int(_width * cfg.slice.AVAILABLE_PATCH_START_RATIO), \
                                          int(_height * cfg.slice.AVAILABLE_PATCH_START_RATIO), \
                                          int(_width * cfg.slice.AVAILABLE_PATCH_END_RATIO), \
                                          int(_height * cfg.slice.AVAILABLE_PATCH_END_RATIO)

                    # 收集任务结果
                    tasks = []
                    while x < width:
                        tasks.append(executor.submit(worker, image, x, y, height, cfg.slice.WIDTH, cfg.slice.HEIGHT, cfg.slice.DELTA, output_path))
                        x += cfg.slice.DELTA

                    t2 = datetime.datetime.now()
                    job_count = len(tasks)
                    print("Done, cost: %s, Total Job Count: %s, Worker Count: %s" % ((t2 - t1), job_count, cfg.slice.SLICE_PROCESS_NUM))

                    # 计数器
                    patch_count = 0
                    for future in as_completed(tasks):
                        queue = future.result()
                        count = len(queue)

                        patch_count += count
                        job_count -= 1
                        print("One Job Done, Got %s patches, last Job Count: %s" % (count, job_count))

                    t3 = datetime.datetime.now()
                    print("File - %s, Size: (%s, %s), Got Patch Num %s, Total cost time: %s" % (img_name, _width, _height, patch_count, t3 - t0))
                    print(".jpg files saved path: %s" % output_path)

                    done.append(output_path)
                else:
                    fail.append({'name': img_name, 'err': 'unsupported file format'})
            except Exception as e:
                raise
                fail.append({'name': image, 'err': str(e)})

        return {'done': done, 'fail': fail}


def worker_in_memory(image, start_x, start_y, height, patch_width, patch_height, delta):
    """
    按行切图，并保存为图像文件，每个 worker 只负责处理一行
    :param image: 图像文件地址
    :param start_x: 切图起点坐标-x
    :param start_y: 切图起点坐标-y
    :param height: 切图最大高度
    :param patch_width: 切图尺寸-宽
    :param patch_height: 切图尺寸-高
    :param delta: 切图步长
    :return: 切图数量
    """

    # 结果队列
    queue = {}

    try:
        slide = openslide.OpenSlide(image)
    except:
        slide = TSlide(image)

    try:
        while start_y < height:
            # 读取patch块
            patch = slide.read_region((start_x, start_y), 0, (patch_width, patch_height))

            # 图像格式转换
            patch = cv2.cvtColor(np.asarray(patch), cv2.COLOR_RGBA2BGR)
            key = '%s_%s' % (start_x, start_y)
            queue[key] = patch

            start_y += delta

        return queue
    except:
        raise


class ImageSliceInMemory(object):
    """
    切图工具类
    """

    def __init__(self, input_file_path):
        """

        :param input_file_path: 输入文件路径, 文件路径或文件夹路径
        """
        self.images = FilesScanner(input_file_path).get_files()

    def get_slices(self):
        """

        :return: [切图存放路径,]
        """

        for image in self.images:
            t0 = datetime.datetime.now()

            # 获取病理图像文件名，假如文件名中有空格的话，以 "_" 替换
            img_name = os.path.basename(image).split(".")[0].replace(" ", "_")
            print("Image Process %s ..." % image)

            try:
                slide = None
                if image.endswith(".tif"):
                    slide = openslide.OpenSlide(image)

                if image.endswith(".kfb"):
                    slide = TSlide(image)

                if slide:
                    _width, _height = slide.dimensions

                    # 创建进程池
                    executor = ProcessPoolExecutor(max_workers=cfg.slice.SLICE_PROCESS_NUM)

                    t1 = datetime.datetime.now()
                    print("Adding Job to Pool...")

                    # 获取中心位置坐标
                    center_x, center_y = _width / 2, _height / 2

                    # 计算左上坐标
                    width = (cfg.center.PATCH_NUM - 1) * cfg.center.DELTA + cfg.center.PATCH_WIDTH
                    height = (cfg.center.PATCH_NUM - 1) * cfg.center.DELTA + cfg.center.PATCH_HEIGHT

                    print(width, height)

                    x = center_x - width / 2
                    y = center_y - height / 2

                    # 修正坐标
                    x = x if x >= 0 else 0
                    y = y if y >= 0 else 0

                    # 计算重点位置
                    width = x + width
                    height = y + height

                    x, y, width, height = int(x), int(y), int(width), int(height)

                    # 收集任务结果
                    tasks = []
                    while x < width:
                        tasks.append(executor.submit(worker_in_memory, image, x, y, height, cfg.center.PATCH_WIDTH, cfg.center.PATCH_HEIGHT, cfg.center.DELTA))
                        x += cfg.center.DELTA

                    t2 = datetime.datetime.now()
                    job_count = len(tasks)
                    print("Done, cost: %s, Total Job Count: %s, Worker Count: %s" % ((t2 - t1), job_count, cfg.slice.SLICE_PROCESS_NUM))

                    results = {}
                    # 计数器
                    patch_count = 0
                    for future in as_completed(tasks):
                        queue = future.result()
                        results.update(deepcopy(queue))

                        count = len(queue)
                        patch_count += count
                        job_count -= 1
                        print("One Job Done, Got %s patches, last Job Count: %s" % (count, job_count))

                    t3 = datetime.datetime.now()
                    print("File - %s, Size: (%s, %s), Got Patch Num %s, Total cost time: %s" % (img_name, _width, _height, patch_count, t3 - t0))

                    return cfg.code.success, results
            except Exception as e:
                return cfg.code.fail, str(e)


if __name__ == '__main__':
    input_file_path = '/home/sakulaki/yolo-yuli/one_stop_test/tif/XB1800118.tif'
    # 切图及保存
    # output_file_path = '/home/tsimage/Development/data/output/'
    # worker = ImageSlice(input_file_path, output_file_path)
    # print(worker.get_slices())

    # 切图并返回numpy数组
    worker = ImageSliceInMemory(input_file_path)
    results = worker.get_slices()
    print(len(results))
    print(results[0]['x'], results[0]['y'], type(results[0]['image']))

    # print(FilesScanner('/home/tsimage/Development/data/tifs/01.tif').get_files())
