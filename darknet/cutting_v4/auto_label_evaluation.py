import os
import re
import copy
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


classes = ["AGC", "HSIL-SCC_G", "SCC_R", "EC", "ASCUS", "LSIL", "CC", "VIRUS", "FUNGI", "ACTINO", "TRI", "PH", "SC"]
tolerate = {"AGC":["AGC"], 
            "HSIL-SCC_G":["HSIL-SCC_G", "SCC_R"], 
            "SCC_R":["HSIL-SCC_G", "SCC_R"], 
            "EC":["EC"], 
            "ASCUS":["ASCUS", "LSIL"], 
            "LSIL":["ASCUS", "LSIL"], 
            "CC":["CC"], 
            "VIRUS":["VIRUS"], 
            "FUNGI":["FUNGI"], 
            "ACTINO":["ACTINO"], 
            "TRI":["TRI"], 
            "PH":["PH"], 
            "SC":["SC"]}
categorize = {'HSIL_M': 'HSIL-SCC_G', 'EC': 'EC', 'AGC_B': 'AGC', 'PH': 'PH', 'FUNGI': 'FUNGI', 'AGC_A': 'AGC', 'SCC_R': 'SCC_R', 'ASCUS': 'ASCUS', 'VIRUS': 'VIRUS', 'TRI': 'TRI', 'HSIL_S': 'HSIL-SCC_G', 'SC': 'SC', 'SCC_G': 'HSIL-SCC_G', 'LSIL_F': 'LSIL', 'HSIL_B': 'HSIL-SCC_G', 'ACTINO': 'ACTINO', 'LSIL_E': 'LSIL', 'CC': 'CC'}
use_thres = {"AGC":0.9, 
            "HSIL-SCC_G":0.9, 
            "SCC_R":0.9, 
            "EC":0.9, 
            "ASCUS":0.0, 
            "LSIL":0.0, 
            "CC":0.9, 
            "VIRUS":0.9, 
            "FUNGI":0.9, 
            "ACTINO":0.9, 
            "TRI":0.95, 
            "PH":0.9, 
            "SC":0.9}


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


def is_overlapped(coords1, coords2, thres=0.5):
    iou = calc_iou(coords1, coords2)
    return iou > thres


def read_label(txt_name, size=608):
    labels = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            label = classes[int(tokens[0])]
            cx, cy = float(tokens[1]), float(tokens[2])
            w, h = float(tokens[3]), float(tokens[4])
            x, y = int((cx - w/2) * size), int((cy - h/2) * size)
            w, h = int(w * size), int(h * size)
            labels.append((label, (x, y, w, h)))
    return labels


def batch_read_label(txt_names):
    patch_info_map = {}
    for txt_name in txt_names:
        name = os.path.splitext(os.path.basename(txt_name))[0]
        labels = read_label(txt_name)
        patch_info_map[name] = labels
    return patch_info_map


def map_patch_info(txt_names):
    """ parse and collect label info from txt file names
    :param txt_names: list of txt file names
    :return: {name:[(label, (x, y, w, h)),],}
    """
    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(txt_names), batch_size):
        batch = txt_names[i : i+batch_size]
        tasks.append(executor.submit(batch_read_label, batch))
    
    patch_info_map = {}
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        result = future.result()  # get the returning result from calling fuction
        patch_info_map.update(result)
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
        
    return patch_info_map


def map_cell_info(img_names):
    """ parse and collect label info from cell file names 
    :param img_names: cell file names
    :return: {name:[(label, (x, y, w, h), pred),],}
    """
    cell_info_map = {}
    p = re.compile("1-p(\d.\d+)_(.*)_x(-?\d+)_y(-?\d+)_w(\d+)_h(\d+)")
    for i,img_name in enumerate(img_names):
        if i % 10000 == 0:
            print("processed ", i)
        label = os.path.basename(os.path.dirname(img_name))
        basename = os.path.basename(img_name)
        m = p.search(basename)
        if not m:
            print("cannot interpret", basename)
            continue
        pred = float(m.group(1))
        name = m.group(2)
        x = int(m.group(3))
        y = int(m.group(4))
        w = int(m.group(5))
        h = int(m.group(6))
        if not name in cell_info_map:
            cell_info_map[name] = []
        cell_info_map[name].append((label, (x, y, w, h), pred))
    return cell_info_map


def evaluate(patch_info_map, cell_info_map, iou_thres=0.5):
    """ evaluate prediction and calculate recall rate 
    :param patch_info_map: {name:[(label, (x, y, w, h)),],}
    :param cell_info_map: {name:[(label, (x, y, w, h), pred),],}
    :param iou_thres: threshold for same target prediction
    """
    summary = {label:{"patches":set(), 
                      "recall":0, 
                      "recall-thres":0,
                      "marked":0, 
                      "predicted":0, 
                      "predicted-thres":0} for label in classes}
    for name in patch_info_map:
        label_boxes = patch_info_map[name]
        patch_tolerate = set()
        for label_box in label_boxes:
            label = label_box[0]
            summary[label]["marked"] += 1
            summary[label]["patches"].add(name)
            patch_tolerate.update(tolerate[label])
            
        if not name in cell_info_map:
            continue
            
        label_box_preds = cell_info_map[name]
        for label_box_pred in label_box_preds:
            label_clas = label_box_pred[0]
            coords2 = label_box_pred[1]
            pred = label_box_pred[2]

            # classification classes: MC, RC, GEC
            if not label_clas in categorize:
                continue

            label_p = categorize[label_clas]
            summary[label_p]["predicted"] += 1
            pred_thres = use_thres[label_p]
            if pred > pred_thres:
                summary[label_p]["predicted-thres"] += 1

            for label_box in label_boxes:
                coords1 = label_box[1]
                if is_overlapped(coords1, coords2, iou_thres):
                    if label_p in patch_tolerate:
                        summary[label]["recall"] += 1
                        if pred > pred_thres:
                            summary[label]["recall-thres"] += 1
    for label in summary:
        summary[label]["patches"] = len(summary[label]["patches"])
    return summary


def collect_all_labels(patch_info_map, cell_info_map, iou_thres=0.5):
    """ collect all credible cells 
    :param patch_info_map: {name:[(label, (x, y, w, h)),],}
    :param cell_info_map: {name:[(label, (x, y, w, h), pred),],}
    :param iou_thres: threshold for same target prediction
    :return: {name:[(label, (x, y, w, h)),],}
    """
    all_labels = copy.deepcopy(patch_info_map)
    for name in cell_info_map:
        label_boxes = patch_info_map[name]
        patch_labels = [label_box[0] for label_box in label_boxes]
        patch_tolerate = set()
        for patch_label in patch_labels:
            patch_tolerate.update(tolerate[patch_label])
        
        label_box_preds = cell_info_map[name]
        for label_box_pred in label_box_preds:
            label_clas = label_box_pred[0]
            coords2 = label_box_pred[1]
            pred = label_box_pred[2]
            
            if not label_clas in categorize:
                continue
            
            label_p = categorize[label_clas]
            if not label_p in patch_tolerate or pred < use_thres[label_p]:
                continue
                
            overlapped = False
            for label_box in label_boxes:
                coords1 = label_box[1]
                overlapped = is_overlapped(coords1, coords2, iou_thres)
                if overlapped:
                    break
            if not overlapped:
                all_labels[name].append((label_p, coords2))
    return all_labels
                
            
def write_labels(labels_list, txt_path, size=608):
    """ write labels into label txts of labelme format 
    :param labels_list: [(name, [(label, (x, y, w, h)),]),]
    :param txt_path: path to write txt file to
    """
    for name_labels in labels_list:
        name = name_labels[0]
        labels = name_labels[1]
        txt_name = os.path.join(txt_path, name+".txt")
        with open(txt_name, 'w') as f:
            for label_box in labels:
                index = classes.index(label_box[0])
                x, y, w, h = label_box[1]
                cx, cy = (x + w/2) / size, (y + h/2) / size
                w, h = w / size, h / size
                f.write("{} {} {} {} {}\n".format(index, cx, cy, w, h))
                
                
def write_all_labels(all_labels, txt_path):
    """ write labels into label txts of labelme format 
    :param all_labels: {name:[(label, (x, y, w, h)),],}
    :param txt_path: path to write txt file to
    """
    all_labels_list = [(key,value) for key,value in all_labels.items()]
    print("# txts to write", len(all_labels_list))
    
    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(all_labels_list), batch_size):
        batch = all_labels_list[i : i+batch_size]
        tasks.append(executor.submit(write_labels, batch, txt_path))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))
    
    
def main(patch_path, cell_path):
    txt_names = scan_files(patch_path, postfix=".txt")
    print("# txts", len(txt_names))
    
    patch_info_map = map_patch_info(txt_names)
    
    img_names = scan_files(cell_path, postfix=".bmp")
    print("# cells", len(img_names))
          
    cell_info_map = map_cell_info(img_names)
    
          
          
if __name__ == "__main__":
    patch_path = ""
    cell_path = ""
    
    main(patch_path, cell_path)