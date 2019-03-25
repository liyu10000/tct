import os
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed


classes = [4, 5]  # ASCUS, LSIL


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
    
def gen_txt_vh_flip(txt_name, txt_save_path, size=608):
    boxes = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            index = int(tokens[0])
            if not index in classes:
                return
            cx, cy = float(tokens[1])*size, float(tokens[2])*size
            w, h = float(tokens[3])*size, float(tokens[4])*size
            xmin, ymin = cx - w/2, cy - h/2
            xmax, ymax = xmin + w, ymin + h
            boxes.append([index, xmin, xmax, ymin, ymax])

    w, h = size, size            
            
    labels = {"v":[], "h":[]}
    for box in boxes:
        xmin, xmax, ymin, ymax = box[1:]

        # vertical flip
        xmin_v = xmin
        ymin_v = h - ymax
        xmax_v = xmax
        ymax_v = h - ymin
        labels["v"].append([box[0], xmin_v, xmax_v, ymin_v, ymax_v])

        # horizontal flip
        xmin_h = w - xmax
        ymin_h = ymin
        xmax_h = w - xmin
        ymax_h = ymax
        labels["h"].append([box[0], xmin_h, xmax_h, ymin_h, ymax_h])


    basename = os.path.splitext(os.path.basename(txt_name))[0]
    for op,boxes in labels.items():
        txt_name = os.path.join(txt_save_path, basename+'_'+op+".txt")
        with open(txt_name, 'w') as f:
            for box in boxes:
                box_new = [box[0], (box[1]+box[2])/2.0/w, (box[3]+box[4])/2.0/h, (box[2]-box[1])/w, (box[4]-box[3])/h]
                f.write(" ".join([str(a) for a in box_new]) + "\n")


def batch_gen_txt_vh_flip(txt_names, txt_save_path):
    for txt_name in txt_names:
        gen_txt_vh_flip(txt_name, txt_save_path)


def worker(path_in, path_out):
    files = scan_files(path_in, postfix=".txt")
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=2)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_gen_txt_vh_flip, batch, path_out))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))

    
if __name__ == "__main__":
    path_in = "/home/ssd_array0/Data/batch6.4_1216/rotate-added"
    path_out = "/home/ssd_array0/Data/batch6.4_1216/flip"

    worker(path_in, path_out)
