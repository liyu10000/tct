import os

# get full path by basename, read basename from txt
basenames = []
with open("yaozhong_6k.txt", 'r') as f:
    for line in f.readlines():
        basenames.append(line.strip())
        
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

yaozhong_6k = []
all_files = scan_files("/mnt/DATA", postfix=".kfb") + scan_files("/mnt/DATA", postfix=".tif")
for basename in basenames:
    for file in all_files:
        if basename in file:
            yaozhong_6k.append(file)
            break

with open("yaozhong_6k_fullpath.txt", 'w') as f:
    for file_path in yaozhong_6k:
        f.write(file_path+'\n')