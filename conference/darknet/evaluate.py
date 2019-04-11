import os
import cv2
import pickle
import numpy as np
from datetime import datetime
from multiprocessing import Process, Queue
from darknet.darknet import load_net, load_meta, detect, detect_numpy


img_list_file = "/home/ssd_array0/Data/batch6.4_1216/valid-gnet2.txt"
pkl_file = "/home/ssd_array0/Develop/liyu/gnet2-final.pkl"

gpus = '01234567'


classes = ["AGC", "HSIL-SCC_G", "SCC_R", "EC", "ASCUS", "LSIL", "CC", "VIRUS", "FUNGI", "ACTINO", "TRI", "PH", "SC"]
thres_pred = {"AGC":0.5, "HSIL-SCC_G":0.5, "SCC_R":0.5, "EC":0.5, "ASCUS":0.5, 
            "LSIL":0.5, "CC":0.5, "VIRUS":0.5, "FUNGI":0.5, "ACTINO":0.5, 
            "TRI":0.5, "PH":0.5, "SC":0.5}
thres_iou = 0.5


def read_img_list(img_list_file):
    names = []
    with open(img_list_file, 'r') as f:
        for line in f.readlines():
            img = line.strip()
            txt = os.path.splitext(img)[0] + '.txt'
            names.append([img, txt])
    return names


def read_label(txt_name, size=608):
    labels = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            label = classes[int(tokens[0])]
            cx, cy = float(tokens[1])*size, float(tokens[2])*size
            w, h = float(tokens[3])*size, float(tokens[4])*size
            x, y = cx - w / 2, cy - h / 2
            labels.append((label, (x, y, w, h)))
    return labels


def calc_iou(coords1, coords2):
    """ calculate IOU between two rectangles 
    :param coords1: (x, y, w, h), x, y refer to top left corner
    :param coords2: (x, y, w, h)
    """
    x1 = max(coords1[0], coords2[0])
    y1 = max(coords1[1], coords2[1])
    x2 = min(coords1[0]+coords1[2], coords2[0]+coords2[2])
    y2 = min(coords1[1]+coords1[3], coords2[1]+coords2[3])
    
    # no intercept
    if x1 >= x2 or y1 >= y2:
        return 0.0
    
    # calculate IOU
    area_intercept = (x2 - x1) * (y2 - y1)
    area_1 = coords1[2] * coords1[3]
    area_2 = coords2[2] * coords2[3]
    return area_intercept / (area_1 + area_2 - area_intercept)


def process_one_txt(txt_name, predictions, results):
    """ process one sample, calculate TP, FP, FN of each class
    :param txt_name: full path name of label txt
    :predictions: [[label, probability, (x, y, w, h)],]
    :results: {"ASCUS":{"TP":3, "FP":2, "FN":4, "TP-b":1, "FP-b":1, "FN-b":1}, "LSIL":{...}, ...}
    """
    labels = read_label(txt_name)
    predicted = set()
    for pred in predictions:
        for i,label in enumerate(labels):
            # if pred[0] == label[0] and pred[1] > thres_pred[pred[0]] and calc_iou(pred[2], label[1]) > thres_iou:
            if pred[1] > thres_pred[pred[0]] and calc_iou(pred[2], label[1]) > thres_iou:
                if pred[0] == label[0]:
                    results[pred[0]]["TP"] += 1
                    predicted.add(i)
                else:
                    results[pred[0]]["FP"] += 1
                results[pred[0]]
    unpredicted = set(range(len(labels))) - predicted
    for i in unpredicted:
        results[labels[i][0]]["FN"] += 1


def process(image):
    hlsImg = image.astype(np.float32)
    hlsImg = hlsImg / 255.0
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_BGR2HLS)
    hlsImg[:, :, 2] = 1.5 * hlsImg[:, :, 2]
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    # _, hlsImg[:, :, 2] = cv2.threshold(hlsImg[:, :, 2], 1, 1, cv2.THRESH_TRUNC)
    hlsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)
    hlsImg = hlsImg * 255
    image = hlsImg.astype(np.uint8)

    image = cv2.medianBlur(image, 5)
    image = cv2.GaussianBlur(image, (3,3), 1)
    return image


def patch_allocator(names, o_queue):
    N = len(names)
    for name in names:
        o_queue.put(name+[N])  # (img_name, txt_name, N)


def patch_loader(i_queue, o_queue):
    while True:
        item = i_queue.get()
        img = cv2.imread(item[0])
        # img = process(img)
        o_queue.put((item[1], img, item[2]))  # (txt_name, img, N)


def patch_predictor(gpu, i_queue, o_queue):

    os.environ["CUDA_VISIBLE_DEVICES"] = gpu

    # initialize yolov3 model
    thresh = 0.1
    hier_thresh = 0.5
    nms = 0.45

    config_file = "/home/ssd_array0/Develop/liyu/darknet/cfg/gnet2.net".encode('utf-8')
    weights_file = "/home/ssd_array0/Develop/liyu/darknet/backup/gnet2/gnet2.backup".encode('utf-8')
    datacfg_file = "/home/ssd_array0/Develop/liyu/darknet/cfg/gnet2.data".encode('utf-8')

    try:
        net = load_net(config_file, weights_file, 0)
        meta = load_meta(datacfg_file)
    except:
        print("[ERROR] failed to load yolov3 model")
        return

    while True:
        item = i_queue.get()

        patch = item[1]
        predictions = detect_numpy(net, meta, patch, thresh, hier_thresh, nms)

        predictions_ = []
        for pred in predictions:
            label = pred[0]
            probability = pred[1]
            cx, cy, w, h = pred[2]
            x, y = int(cx - w/2), int(cy - h/2)
            w, h = int(w), int(h)
            w, h = min(w, w+x), min(h, h+y)
            x, y = max(0, x), max(0, y)
            predictions_.append([label, probability, (x, y, w, h)])

        o_queue.put((item[0], predictions_, item[2]))  # (txt_name, predictions, N)

        del item


def finalizer(i_queue):
    results_raw = {key:{"TP":0, "FP":0, "FN":0} for key in classes}
    results_ref = {key:{"recall":0.0, "precision":0.0} for key in classes}

    f = open(pkl_file, 'wb')
    
    count = 0
    while True:
        item = i_queue.get()
        N = item[2]
        process_one_txt(item[0], item[1], results_raw)

        count += 1
        if count % 800 == 0:
            print(datetime.now(), "  -->  ", "processed ", count, " / ", N, results_raw)
        if count % 10000 == 0 or count == 20000:
            for key in results_raw:
                TP = results_raw[key]["TP"]
                FP = results_raw[key]["FP"]
                FN = results_raw[key]["FN"]
                results_ref[key]["recall"] = TP / (TP + FN) if TP+FN != 0 else None
                results_ref[key]["precision"] = TP / (TP + FP) if TP+FP != 0 else None
            
            pickle.dump(results_ref, f)
            print("\n", datetime.now(), "  -->  ", "processed ", count, " / ", N, results_ref, "\n")
            if count == 20000:
                f.close()
                print("\n", datetime.now(), "  -->  ", "program finished.")


def start_processes(all_processes):
    for ps in all_processes:
        for p in ps:
            p.start()


def join_processes(all_processes):
    for ps in all_processes:
        for p in ps:
            p.join()


q_names = Queue(maxsize=1024)
q_images = Queue(maxsize=512)
q_predictions = Queue(maxsize=1024)

p_allocators = []
p_loaders = []
p_predictors = []
p_finalizers = []

names = read_img_list(img_list_file)
p_allocators.append(Process(target=patch_allocator, args=(names, q_names)))
for i in range(len(gpus)*2):
    p_loaders.append(Process(target=patch_loader, args=(q_names, q_images)))
for gpu in gpus:
    p_predictors.append(Process(target=patch_predictor, args=(gpu, q_images, q_predictions)))
p_finalizers.append(Process(target=finalizer, args=(q_predictions,)))

pps = [p_allocators, p_loaders, p_predictors, p_finalizers]

start_processes(pps)
join_processes(pps)