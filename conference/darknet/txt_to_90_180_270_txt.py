import os
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed



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
    
def gen_txt_90_180_270(txt_name, txt_save_path, size=608):
    boxes = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split()
            index = int(tokens[0])
            cx, cy = float(tokens[1])*size, float(tokens[2])*size
            w, h = float(tokens[3])*size, float(tokens[4])*size
            xmin, ymin = cx - w/2, cy - h/2
            xmax, ymax = xmin + w, ymin + h
            boxes.append([index, xmin, xmax, ymin, ymax])

    w, h = size, size            
            
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


    basename = os.path.splitext(os.path.basename(txt_name))[0]
    for degree,boxes in labels.items():
        txt_name = os.path.join(txt_save_path, basename+'_'+str(degree)+".txt")
        with open(txt_name, 'w') as f:
            for box in boxes:
                box_new = [box[0], (box[1]+box[2])/2.0/w, (box[3]+box[4])/2.0/h, (box[2]-box[1])/w, (box[4]-box[3])/h]
                f.write(" ".join([str(a) for a in box_new]) + "\n")


def batch_gen_txt_90_180_270(txt_names, txt_save_path):
    for txt_name in txt_names:
        gen_txt_90_180_270(txt_name, txt_save_path)


def worker(path_in, path_out):
    files = scan_files(path_in, postfix=".txt")
    print("# files:", len(files))

    executor = ProcessPoolExecutor(max_workers=8)
    tasks = []

    batch_size = 10000
    for i in range(0, len(files), batch_size):
        batch = files[i : i+batch_size]
        tasks.append(executor.submit(batch_gen_txt_90_180_270, batch, path_out))
    
    job_count = len(tasks)
    for future in as_completed(tasks):
        # result = future.result()  # get the returning result from calling fuction
        job_count -= 1
        print("One Job Done, Remaining Job Count: %s" % (job_count))

    
if __name__ == "__main__":
    path_in = "/home/ssd_array0/Data/batch6.5_1216/original"
    path_out = "/home/ssd_array0/Data/batch6.5_1216/rotate"

    worker(path_in, path_out)
