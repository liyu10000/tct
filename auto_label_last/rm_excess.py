import os
import shutil

def rm_excess(save_path):
	tif_names = os.listdir(save_path)
	for tif_name in tif_names:
		subdir = os.path.join(save_path, tif_name)
		orig_dir = os.path.join(subdir, tif_name)
		if os.path.exists(orig_dir):
			shutil.rmtree(orig_dir)
		clas_dir = os.path.join(subdir, tif_name+"_classify")
		if os.path.exists(clas_dir):
			shutil.rmtree(clas_dir)
		print("processed ", tif_name)

if __name__ == "__main__":
	save_path = "/home/sakulaki/yolo-yuli/last_step/01_ASCUS_jpg"
	rm_excess(save_path)