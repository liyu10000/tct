import os
import cv2
import csv
import pandas as pd

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

def laplacian(image):
	return cv2.Laplacian(image, cv2.CV_64F).var()

def label_blur(image_path, save_path):
	os.makedirs(save_path, exist_ok=True)
	image_names = scan_files(image_path, postfix=".jpg")
	label_blur_array = []
	for image_name in image_names:
		image = cv2.imread(image_name)
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		var = laplacian(gray)
		print("{}: {}".format(os.path.basename(image_name), var))
		label_blur_array.append((os.path.basename(image_name), var))
		# cv2.putText(image, "{:.2f}".format(var), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
		# cv2.imwrite(os.path.join(save_path, os.path.basename(image_name)), image)
	return label_blur_array

def write_csv(label_blur_array, image_path):
	with open(image_path+".csv", "w", newline="") as csv_file:
		writer =csv.writer(csv_file, delimiter=",")
		writer.writerow(("jpg", "var"))
		for label_blur in label_blur_array:
			writer.writerow(label_blur)
	return image_path+".csv"

def analyze(csv_file):
	df = pd.read_csv(csv_file)
	df.describe()
	df["var"].hist()


if __name__ == "__main__":
	image_path = "/home/sakulaki/yolo-yuli/detect_blur/clear_sparse"
	save_path = "/home/sakulaki/yolo-yuli/detect_blur/clear_sparse_result"
	label_blur_array = label_blur(image_path, save_path)
	write_csv(label_blur_array, image_path)
	#analyze(label_blur_array)