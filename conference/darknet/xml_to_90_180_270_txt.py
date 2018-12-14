import os
import xml.etree.ElementTree as ET

from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


# # 6 classes
# classes = {"ASCUS":0, "LSIL":0, "ASCH":1, "HSIL":1, "SCC":2, "AGC1":1, "AGC2":1,
           # "ADC":1, "EC":1, "FUNGI":4, "TRI":2, "CC":0, "ACTINO":5, "VIRUS":3}

# 14 classes
#classes = {"ASCUS":0, "LSIL":1, "ASCH":2, "HSIL":3, "SCC":4, "AGC1":5, "AGC2":6,
#           "ADC":7, "EC":8, "FUNGI":9, "TRI":10, "CC":11, "ACTINO":12, "VIRUS":13}

# # 12 classes merge agc1 agc2 adc as agc
# classes = {"ASCUS":0, "LSIL":1, "ASCH":2, "HSIL":3, "SCC":4, "AGC":5, 
#            "EC":6, "FUNGI":7, "TRI":8, "CC":9, "ACTINO":10, "VIRUS":11}

# 11 classes merge agc1 agc2 adc as agc
classes = {"ASCUS":0, "LSIL":1, "HSIL":2, "SCC":3, "AGC":4, 
           "EC":5, "FUNGI":6, "TRI":7, "CC":8, "ACTINO":9, "VIRUS":10}

# # 4 classes
# classes = {"MC":0, "SC":1, "RC":2, "GEC":3}

# # 5 classes
# classes = {"ASCUS":0, "LSIL":1, "ASCH":2, "HSIL":3, "SCC":4}

# # 1 class
# classes = {"ASCUS":0}

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
    
def gen_txt_90_180_270(xml_name, txt_save_path):
    tree = ET.parse(xml_name)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)
    

    boxes = []
    for object_i in root.iter("object"):
        name = object_i.find("name").text
        if not name in classes:
            continue
        index = classes[name]
        bndbox = object_i.find('bndbox')
        box = [float(bndbox.find('xmin').text), float(bndbox.find('xmax').text), float(bndbox.find('ymin').text), float(bndbox.find('ymax').text)]
        boxes.append([classes[name]] + box)


    labels = {"90":[], "180":[], "270":[]}
    for box in boxes:
        xmin, xmax, ymin, ymax = box[1:]

        # 90
        xmin_90 = ymin
        ymin_90 = w - xmax
        xmax_90 = ymax
        ymax_90 = w - xmin
        labels["90"].append([box[0], xmin_90, xmax_90, ymin_90, ymax_90])

        # 180
        xmin_180 = w - xmax
        ymin_180 = h - ymax
        xmax_180 = w - xmin
        ymax_180 = h - ymin
        labels["180"].append([box[0], xmin_180, xmax_180, ymin_180, ymax_180])

        # 270
        xmin_270 = h - ymax
        ymin_270 = xmin
        xmax_270 = h - ymin
        ymax_270 = xmax
        labels["270"].append([box[0], xmin_270, xmax_270, ymin_270, ymax_270])


    basename = os.path.splitext(os.path.basename(xml_name))[0]
    for degree,boxes in labels.items():
        txt_name = os.path.join(txt_save_path, basename+'_'+str(degree)+".txt")
        with open(txt_name, 'w') as f:
            for box in boxes:
                box_new = [box[0], (box[1]+box[2])/2.0/w, (box[3]+box[4])/2.0/h, (box[2]-box[1])/w, (box[4]-box[3])/h]
                f.write(" ".join([str(a) for a in box_new]) + "\n")


def batch_gen_txt_90_180_270(xml_names, txt_save_path):
    for xml_name in xml_names:
        gen_txt_90_180_270(xml_name, txt_save_path)


def worker(path_in, path_out, postfix):
    files = scan_files(path_in, postfix=postfix)
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=cpu_count())
    tasks = []

    batch_size = 1000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_gen_txt_90_180_270, batch, path_out))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))

    
if __name__ == "__main__":
    path_in = "/home/ssd0/Develop/liyu/batch6_1216_labels/train"
    path_out = "/home/hdd_array0/batch_1216_rotate_c"
    postfix = ".xml"

    worker(path_in, path_out, postfix)
