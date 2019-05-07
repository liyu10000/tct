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

# # 11 classes merge agc1 agc2 adc as agc
# classes = {"ASCUS":0, "LSIL":1, "HSIL":2, "SCC":3, "AGC":4, 
#            "EC":5, "FUNGI":6, "TRI":7, "CC":8, "ACTINO":9, "VIRUS":10}

# # 18 classes (separate all sub classes and add SC & PH)
# classes = {"ACTINO":0, "AGC_A":1, "AGC_B":2, "ASCUS":3, "CC":4, "EC":5, "FUNGI":6, "HSIL_B":7, "HSIL_M":8, "HSIL_S":9, "LSIL_E":10, "LSIL_F":11, "PH":12, "SC":13, "SCC_G":14, "SCC_R":15, "TRI":16, "VIRUS":17}


# 13 classes, add SC and PH
classes = {"ACTINO":9, "AGC_A":0, "AGC_B":0, "ASCUS":4, "CC":6, "EC":3, "FUNGI":8, "HSIL_B":1, "HSIL_M":1, "HSIL_S":1, "LSIL_E":5, "LSIL_F":5, "PH":11, "SC":12, "SCC_G":2, "SCC_R":2, "TRI":10, "VIRUS":7}


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
    
def _gen_txt(xml_name, txt_path):
    txt_name = os.path.splitext(os.path.basename(xml_name))[0] + ".txt"
    # if os.path.isfile(os.path.join(txt_path, txt_name)):
    #     return
    txt_file = open(os.path.join(txt_path, txt_name), "w")
    tree = ET.parse(xml_name)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)
    
    for object_i in root.iter("object"):
        name = object_i.find("name").text
        if not name in classes:
            continue
        index = classes[name]
        bndbox = object_i.find('bndbox')
        box = (float(bndbox.find('xmin').text), 
               float(bndbox.find('xmax').text), 
               float(bndbox.find('ymin').text), 
               float(bndbox.find('ymax').text))
        box_new = ((box[0]+box[1])/2.0/w, (box[2]+box[3])/2.0/h, (box[1]-box[0])/w, (box[3]-box[2])/h)
        txt_file.write(str(index) + " " + " ".join([str(a) for a in box_new]) + "\n")
    txt_file.close()


# def gen_txt(path, dirs=("train", "valid", "test")):
#     for d in dirs:
#         xml_names = scan_files(os.path.join(path, d), postfix=".xml")
#         print("generating txts for", d, "number of files", len(xml_names))
#         txt_name = os.path.join(path, d+".txt")
#         with open(txt_name, "w") as txt_file:
#             for i,xml_name in enumerate(xml_names):
#                 if i % 50000 == 0:
#                     print(i)
#                 _gen_txt(xml_name, os.path.dirname(xml_name))
#                 txt_file.write(os.path.splitext(xml_name)[0] + ".bmp\n")
                
def batch_gen_txt(xml_names, txt_path):
    for xml_name in xml_names:
        _gen_txt(xml_name, txt_path)
        
        
def gen_txt(path):
    files = scan_files(path, postfix=".xml")
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=4)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_gen_txt, batch, path))

    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))

    
if __name__ == "__main__":
    #generate txt_list for a folder
    path = "/home/ssd_array0/Data/batch6.5_1216/pos"
    gen_txt(path)
