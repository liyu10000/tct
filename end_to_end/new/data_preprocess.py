import os
import re

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

def contains_str(full_path, strs):
	for s in strs:
		pattern = re.compile(s)
		if pattern.search(full_path):
			return True
	return False


def collect(wsi_dir):
	strs = ["normal", "NORMAL"]
	kfb_files = scan_files(wsi_dir, postfix=".kfb")
	tif_files = scan_files(wsi_dir, postfix=".tif")
	all_files = kfb_files + tif_files
	normal = []
	abnormal = []
	for f in all_files:
		if contains_str(f, strs):
			normal.append(f)
		else:
			abnormal.append(f)
	return normal, abnormal


if __name__ == "__main__":
	wsi_dir = os.getcwd()
	normal, abnormal = collect(wsi_dir)
	print(len(normal), len(abnormal))
