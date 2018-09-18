# coding: utf-8
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed

import datetime
import os
import sys

import cv2
import numpy as np
import openslide
from config import PATCH_SIZE, DELTA, AVAILABLE_PATCH_START_RATIO, AVAILABLE_PATCH_END_RATIO, get_patch_num, \
    get_random_string, MATTING_PROCESS_NUM, FilesScanner, update_algorithm_progress

from tslide.tslide import TSlide

# 获取当前文件路径
CURRENT_WORKING_PATH = os.path.dirname(os.path.abspath(__file__))

# 设置工作目录
os.chdir(CURRENT_WORKING_PATH)

# 算法运行
MINITEST_CFG_DATA = {
    "classes": 5,
    # /home/sakulaki/enhancement_608_01/train.txt
    "train": "/home/sakulaki/enhancement_608_01/train.txt",
    # /home/tsimage/darknet/predict.txt
    "valid": os.path.join(CURRENT_WORKING_PATH, "predict.txt"),
    # "/home/tsimage/darknet/data/minitest.names",
    "names": os.path.join(CURRENT_WORKING_PATH, "data/minitest.names"),
    "backup": "backup",
}

PREDICT_IMAGES_FILE_PATH = os.path.join(CURRENT_WORKING_PATH, "predict.txt")
CONFIGURE_FILE_PATH = os.path.join(CURRENT_WORKING_PATH, "cfg/minitest.data")
YOLO_V3_CFG_FILE_PATH = os.path.join(CURRENT_WORKING_PATH, "cfg/yolov3-minitest.cfg")
YOLO_V3_BACKUP_CFG_FILE_PATH = os.path.join(CURRENT_WORKING_PATH, "backup/yolov3-minitest.backup")
RESULT_FILE_DIR = os.path.join(CURRENT_WORKING_PATH, "results")
CLASSES = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]


def init_cell_seg(jpg_files):
    # 生成预测文件路径列表文件
    with open(PREDICT_IMAGES_FILE_PATH, 'w') as f:
        f.writelines(jpg_files)

    # 将配置参数写入文件
    with open(CONFIGURE_FILE_PATH, 'w') as o:
        for key, value in MINITEST_CFG_DATA.items():
            o.write("%s = %s\n" % (key, value))


def get_predictions_result(result_dir, classes, det):
    results_file_list = os.listdir(result_dir)
    # class & result file name
    dict_class_file = {}
    dict_class_predict_info = {}
    dict_class_pic_box_info = {}

    for file_name in results_file_list:
        for class_name in CLASSES:
            if -1 != file_name.find(class_name):
                dict_class_file[class_name] = file_name

    for class_name in dict_class_file:
        file_name = dict_class_file[class_name]
        file_path = result_dir + "/" + file_name
        with open(file_path) as file_object:
            predict_info = file_object.read()
        dict_class_predict_info[class_name] = predict_info

    for class_name in CLASSES:
        all_predict_info = dict_class_predict_info[class_name].split("\n")
        dict_pic_box_info = {}
        for predict_info in all_predict_info:
            predict_info_list = predict_info.split(" ")
            if len(predict_info_list) == 6:
                if float(predict_info_list[1]) > det:
                    box_info = predict_info_list[1] + " " + predict_info_list[2] + " " + \
                               predict_info_list[3] + " " + predict_info_list[4] + " " + \
                               predict_info_list[5]
                    pic_box = [box_info, box_info]
                    if predict_info_list[0] in dict_pic_box_info:
                        temp_pic_box = dict_pic_box_info[predict_info_list[0]]
                        temp_pic_box.append(box_info)
                        dict_pic_box_info[predict_info_list[0]] = temp_pic_box
                    else:
                        dict_pic_box_info[predict_info_list[0]] = pic_box
        dict_class_pic_box_info[class_name] = dict_pic_box_info

    dict_pic_info = {}
    for index, class_name in enumerate(CLASSES):
        dict_pic_box = dict_class_pic_box_info[class_name]
        for pic_name in dict_pic_box:
            class_box_list = dict_pic_box[pic_name]
            for i, class_box in enumerate(class_box_list):
                class_box_list[i] = str(index) + " " + class_box_list[i]
            if not (pic_name in dict_pic_info):
                dict_pic_info[pic_name] = class_box_list
            else:
                dict_pic_info[pic_name] = dict_pic_info[pic_name] + class_box_list

    return dict_pic_info


def get_predict_lst(results_dir, det):
    lst = os.listdir(results_dir)
    results = {}
    for file in lst:
        class_name = os.path.basename(file).split(".")[0].split("_")[-1]
        vals = []
        with open(os.path.join(results_dir, file)) as f:
            for line in f.readlines():
                items = line.replace("\r", "").replace("\n", "").split(" ")
                if float(items[1]) > det:
                    vals.append(items[1:])

        results[class_name] = vals

    return results


def cell_segmentation(det_thresh=0.05):
    os.system("./darknet detector valid %s %s %s" % (
    CONFIGURE_FILE_PATH, YOLO_V3_CFG_FILE_PATH, YOLO_V3_BACKUP_CFG_FILE_PATH))
    # dict_pic_info = get_predictions_result(RESULT_FILE_DIR, classes, det_thresh)
    # return val, dict_pic_info

    return get_predict_lst(RESULT_FILE_DIR, det_thresh)


def get_result_tag(results):
    tag = ""
    count = 0
    for key, value in results.items():
        if len(value) > count:
            count = len(value)
            tag = key

    return tag


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
        name = get_random_string()
        save_path = os.path.join(patch_save_path, "%s.jpg" % name)
        # 文件写入
        cv2.imwrite(save_path, patch)

        start_y += DELTA
        count += 1

    return count


def main(input_file_path, task_id, output_file_path="output"):
    """

    :param task_id:
    :param input_file_path: 输入文件路径
    :param output_file_path: 输出文件路径
    :return:
    """
    # 创建输出文件目录
    os.makedirs(os.path.join(CURRENT_WORKING_PATH, output_file_path), exist_ok=True)

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

        # 创建进程池
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
            print("One Job Done, Got %s patches, rest Job Count: %s" % (count, job_count))

        t1 = datetime.datetime.now()
        print("File - %s, Size: (%s, %s), Calculate Patch Num %s, Got Patch Num %s, Total cost time: %s" % (
        img_name, width, height, patch_num, patch_count, t1 - t0))
        print("Algorithm Analysing Engine Start...")
        patch_lst = FilesScanner(output_path).get_files()
        delta = 200
        batches = [patch_lst[i: i + delta] for i in range(0, len(patch_lst), delta)]

        results = {}
        t = len(batches)
        for i, batch in enumerate(batches):
            print("init_cell_seg...")
            init_cell_seg(batch)
            print("cell_segmentation...")
            result = cell_segmentation(det_thresh=0.1)
            for key, value in result.items():
                if key in results:
                    results[key].extend(value)
                else:
                    results[key] = value

            progress = "%.2f" % ((i + 1) / t)
            print(progress)
            # update_algorithm_progress(task_id, progress)

        os.system("rm -rf %s" % output_path.replace(" ", "\ "))

        return get_result_tag(results), results


if __name__ == '__main__':
    input_file_path = sys.argv[1]
    task_id = str(uuid.uuid4())

    tag, lst = main(input_file_path, task_id)
    print(tag)
