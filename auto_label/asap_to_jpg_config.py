# coding: utf-8

import math
import os
import uuid
from multiprocessing import cpu_count

# 切图尺寸
import requests

PATCH_SIZE = 608
# 读取步长
DELTA = 608

# 最大可传入图片数量
MAX_INPUT_IMAGES_NUM = 50

# 切图进程数量
MATTING_PROCESS_NUM = cpu_count() - 2

# 算法处理进程数
ALGORITHM_PROCESSOR_NUM = 4

# 需排除筛查结果
EXCLUDE_ALGORITHM_TYPES = ("NORMAL",)

# 切图比例-开始
AVAILABLE_PATCH_START_RATIO = 0.05

# 切图比例-结束
AVAILABLE_PATCH_END_RATIO = 0.95

# 算法更新URL
ALGORITHM_UPDATE_ADDRESS = "http://192.168.1.98:8080/algorithm/tasks/"


def get_patch_num(w, h, step=DELTA):
    """
    计算patch数量
    :param w:
    :param h:
    :param step:
    :return:
    """
    return math.ceil(w / step) * math.ceil(h / step)


def get_random_string():
    """
    获取随机不重复字符串
    :return:
    """
    return str(uuid.uuid1()).replace("-", "")


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

        # 替换为绝对路径
        files = [os.path.abspath(item) + '\n' for item in files]

        self.files = files

    def get_files(self):
        return self.files


def update_algorithm_progress(task_id, progress):
    """
    向TCT系统更新算法进度
    :param task_id: 任务ID
    :param progress: 算法进度
    :return:
    """
    r = requests.put(ALGORITHM_UPDATE_ADDRESS + task_id, json={"progress": progress})
    print(progress, r.status_code)
