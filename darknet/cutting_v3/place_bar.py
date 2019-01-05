import os
import cv2
import numpy as np


classes_to_place_bar = [2, 3, 4]


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


def read_labels(txt_name, size=608):
    boxes = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            labeli = int(tokens[0])
            if not labeli in classes_to_place_bar:
                continue
            cx, cy = size*float(tokens[1]), size*float(tokens[2])
            w, h = size*float(tokens[3]), size*float(tokens[4])
            x_min, y_min = int(cx - w / 2), int(cy - h / 2)
            x_max, y_max = int(cx + w / 2), int(cy + h / 2)
            boxes.append([x_min, y_min, x_max, y_max])
    return boxes


def find_bar(boxes, size=608, bar_size=200):
    if len(boxes) == 0:
        return -1

    d1s, d2s, d3s, d4s = [], [], [], []
    for box in boxes:
        d1s.append(size - bar_size - box[3])
        d2s.append(size - bar_size - box[2])
        d3s.append(box[1] - bar_size)
        d4s.append(box[0] - bar_size)
    distance = [max(d1s), max(d2s), max(d3s), max(d4s)]
    bar_i = distance.index(max(distance))

    # print(distance)

    return bar_i if distance[bar_i] > 0 else -1


def place_bar(img_name, save_path, size=608, bar_size=200):
    txt_name = os.path.splitext(img_name)[0] + ".txt"
    boxes = read_labels(txt_name)
    bar_i = find_bar(boxes)

    img = cv2.imread(img_name)
    if bar_i == 0:
        img[size-bar_size:, :, :] = 255
    elif bar_i == 1:
        img[:, size-bar_size:, :] = 255
    elif bar_i == 2:
        img[:bar_size, :, :] = 255
    elif bar_i == 3:
        img[:, :bar_size, :] = 255

    img_name_new = os.path.join(save_path, os.path.basename(img_name))
    os.makedirs(os.path.dirname(img_name_new), exist_ok=True)
    cv2.imwrite(img_name_new, img)


def main(src_path, postfix, dst_path):
    img_names = scan_files(src_path, postfix=postfix)
    print("# files", len(img_names))

    for img_name in img_names:
        place_bar(img_name, dst_path)


if __name__ == "__main__":
    src_path = "/home/hdd0/Develop/xxx/train-samples"
    dst_path = "/home/hdd0/Develop/xxx/train-samples-bar"
    postfix = ".bmp"

    main(src_path, postfix, dst_path)
