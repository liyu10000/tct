import os


classes = [i for i in range(11)]
count = {key:0 for key in classes}


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


def count_label(txt_fname):
    with open(txt_fname, 'r') as f:
        for line in f.readlines():
            count[int(line.strip().split()[0])] += 1


def main(txt_path):
    txt_fnames = scan_files(txt_path, postfix=".txt")
    print("total # txts: {}".format(len(txt_fnames)))
    
    for i,txt_fname in enumerate(txt_fnames):
        if i % 10000 == 0:
            print(i)
            print(count)
        # print(txt_fname)
        count_label(txt_fname)
    
    
if __name__ == "__main__":
    txt_path = "/home/hdd_array0/batch6_1216/VOC2012/images"
    main(txt_path)
    print(count)