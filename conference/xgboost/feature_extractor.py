import os
import csv
import pickle
import random
import numpy as np
import pandas as pd
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


yolo_classes = ["LSIL", "HSIL", "SCC", "AGC", "EC", "FUNGI", "TRI", "CC", "ACTINO", "VIRUS"]
xcp_classes = ["ACTINO", "AGC", "CC", "EC", "FUNGI", "GEC", "HSIL_B", "HSIL_M", "HSIL_S", 
               "LSIL_E", "LSIL_F", "MC", "RC", "SC", "SCC_G", "SCC_R", "TRI", "VIRUS"]
yolo_det_p = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999]
xcp_det_p = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999]
xcp_cell_det_p = list(range(-1000, -200, 100)) + list(range(-200, -100, 20)) + list(range(-100, 100, 10)) \
                + list(range(100, 200, 20)) + list(range(200, 1100, 100))

# classes_map = ['ACTINO', 'AGC', 'AGC1', 'AGC2', 'ASCH', 'ASCUS', 'CC', 'EC', 
#                 'FUNGI', 'HISL', 'HSIL', 'LSIL', 'NORMAL', 'None', 'SCC', 'TRI', 'VIRUS']
classes_map = ['ACTINO', 'AGC1', 'AGC2', 'ASCH', 'ASCUS', 'CC',  
                'FUNGI', 'HSIL', 'LSIL', 'NORMAL', 'SCC', 'TRI', 'VIRUS']


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


def extract(csv_file):
    df = pd.read_csv(csv_file)

    # number of cells per class, predicted by yolo
    yolo_classes_dict = {key+"_yolo":df[df["yolo_cell_class"] == key].shape[0] for key in yolo_classes}

    # number of cells per class, predicted by yolo, grouped by det
    yolo_classes_det_dict = {}
    for c in yolo_classes:
        for p in yolo_det_p:
            yolo_classes_det_dict[c+'_yolo_'+str(p)] = df[(df["yolo_cell_class"] == c) & (df["yolo_cell_class_det"] > p)].shape[0]

    # number of cells per class, predicted by xcp
    xcp_classes_dict = {key+"_xcp":df[df["xcp_cell_class"] == key].shape[0] for key in xcp_classes}

    # number of cells per class, predicted by xcp, grouped by det
    xcp_classes_det_dict = {}
    for c in xcp_classes:
        for p in xcp_det_p:
            xcp_classes_det_dict[c+'_xcp_'+str(p)] = df[(df["xcp_cell_class"] == c) & (df["xcp_cell_class_det"] > p)].shape[0]
    
    # count: for each cell predicted by xcp, it has a list of logloss class&values, group them on class and value
    xcp_cell_classes_det_dict = {}
    for c_row in xcp_classes:
        for c_col in xcp_classes:
            for p in xcp_cell_det_p:
                key = c_row+'_'+c_col+'_'+str(p)
                if not key in xcp_cell_classes_det_dict:
                    xcp_cell_classes_det_dict[key] = 0
                xcp_cell_classes_det_dict[key] += df[(df["xcp_cell_class"] == c_row) & (df[c_col+"_det"] > p)].shape[0]

    all_dict = xcp_cell_classes_det_dict
    all_dict.update(yolo_classes_dict)
    all_dict.update(yolo_classes_det_dict)
    all_dict.update(xcp_classes_dict)
    all_dict.update(xcp_classes_det_dict)

    return all_dict


def read_header(header_file):
    header = []
    with open(header_file, 'r') as f:
        for line in f.readlines():
            header.append(line.strip())
    return header


def get_label(chosen, basename):
    for class_i,entries in chosen.items():
        for entry in entries:
            if entry[0] == basename:
                return entry[1]["label"] # '+' connected classes
    return None


# # write a huge line to a single file, too slow
# def write_csv(csv_name, header, label, all_dict):
#     # header = ["classes"] + header
#     line = [label] + [all_dict[key] for key in header]
#     with open(csv_name, 'a', newline='') as csv_file:
#         writer = csv.writer(csv_file)
#         writer.writerow(line)

# def main(csv_dir, csv_name, header, chosen):
#     csv_files = scan_files(csv_dir, postfix=".csv")
#     for csv_file in csv_files:
#         label = get_label(chosen, os.path.splitext(os.path.basename(csv_file))[0])
#         all_dict = extract(csv_file)
#         write_csv(csv_name, header, label, all_dict)
#         print("processed ", csv_file)



# write all the features into a txt, one per wsi
def write_txt(csv_file, chosen, header, save_path):
    label = get_label(chosen, os.path.splitext(os.path.basename(csv_file))[0])
    all_dict = extract(csv_file)
    basename = os.path.splitext(os.path.basename(csv_file))[0]
    txt_name = os.path.join(save_path, basename+".txt")
    with open(txt_name, 'w') as f:
        f.write(str(label) + '\n')
        for key in header:
            f.write(str(all_dict[key]) + '\n')
    print("processed", csv_file)


def batch_write_txt(csv_files, chosen, header, save_path):
    for csv_file in csv_files:
        write_txt(csv_file, chosen, header, save_path)


def csvs_to_txts(csv_path, chosen, header, save_path):
    csv_files = scan_files(csv_path, postfix=".csv")
    print("processed # files: {}".format(len(csv_files)))

    # for csv_file in csv_files:
    #     write_txt(csv_file, chosen, header, save_path)

    executor = ProcessPoolExecutor(max_workers=cpu_count()-2)
    tasks = []

    batch_size = 10
    for i in range(0, len(csv_files), batch_size):
        batch = csv_files[i : i+batch_size]
        tasks.append(executor.submit(batch_write_txt, batch, chosen, header, save_path))

    job_count = len(tasks)
    for future in as_completed(tasks):
        job_count -= 1
        print("Remaining job count {}".format(job_count))


def collect_labels(txt_path):
    txt_files = scan_files(txt_path, postfix=".txt")
    all_labels = dict()
    for txt_file in txt_files:
        with open(txt_file, 'r') as f:
            labels = f.readline().strip().split('+')
            for label in labels:
                if not label in all_labels:
                    all_labels[label] = 0
                all_labels[label] += 1
    print(all_labels)
    return all_labels


def txts_to_csv(txt_path, csv_file):
    def read_feature_from_txt(txt_file):
        label_and_features = []
        with open(txt_file, 'r') as f:
            label = f.readline()
            tokens = label.strip().split('+')
            features = []
            for line in f.readlines():
                features.append(line.strip())
            for token in tokens:
                if not token in classes_map:
                    continue
                i = classes_map.index(token)
                label_and_features.append([i] + features)
        return label_and_features

    txt_files = scan_files(txt_path, postfix=".txt")
    label_and_features = []
    for txt_file in txt_files:
        label_and_features += read_feature_from_txt(txt_file)
    print(len(txt_files), len(label_and_features))


    random.shuffle(label_and_features)

    with open(csv_file, 'w', newline='') as c:
        writer = csv.writer(c)
        for line in label_and_features:
            writer.writerow(line)


if __name__ == "__main__":
    # # open saved chosen file
    # with open("./chosen.pkl", 'rb') as f:
    #     chosen = pickle.load(f)

    # header_file = "header.txt"

    # header = read_header(header_file)
    # print(len(header))


    # # csv_dir = "./big_features"
    # # csv_name = "features.csv"
    # # main(csv_dir, csv_name, header, chosen)


    # csv_path = "./big_features"
    # txt_path = "./txt_features"
    # csvs_to_txts(csv_path, chosen, header, txt_path)

    # txt_path = "./txt_features"
    # collect_labels(txt_path)

    txt_path = "./txt_features"
    csv_file = "features.csv"
    txts_to_csv(txt_path, csv_file)