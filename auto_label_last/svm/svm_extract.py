import os
import pandas as pd

classes = ["NORMAL", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
train_txt = "C:/tsimage/tct/auto_label_last/svm/train.txt"
label_txt = "C:/tsimage/tct/auto_label_last/svm/label.txt"

def collect_feature(csv_file):
	csv_df = pd.read_csv(csv_file)
	item_dict = {key:0 for key in classes}
	for index,row in csv_df.iterrows():
		item_dict[row['classify']] += 1
	return item_dict

def write_lines(txt_file, lines):
	with open(txt_file, "a") as txt:
		for line in lines:
			txt.write(line+"\n")

def main(csv_dir, mapping):
	for sub_dir,diagnosis in mapping:
		csv_files = os.listdir(os.path.join(csv_dir, sub_dir))
		train_lines = []
		label_lines = []
		for csv_file in csv_files:
			item_dict = collect_feature(os.path.join(csv_dir, sub_dir+"/"+csv_file))
			train_lines.append(" ".join([str(item_dict[class_i]) for class_i in classes]))
			label_lines.append(str(classes.index(diagnosis)))
		write_lines(train_txt, train_lines)
		write_lines(label_txt, label_lines)

if __name__ == "__main__":
	train_txt = "C:/tsimage/tct/auto_label_last/svm/train_test.txt"
	label_txt = "C:/tsimage/tct/auto_label_last/svm/label_test.txt"

	# # labeled
	# csv_dir = "C:/tsimage/tct/auto_label_last/labeled_xception"
	# mapping = [("01_ASCUS_csv", "ASCUS"), ("02_LSIL_csv", "LSIL"), ("03_ASCH_csv", "ASCH"), ("04_HSIL_csv", "HSIL")]

	# # unlabeled
	# csv_dir = "C:/tsimage/tct/auto_label_last/unlabeled_xception"
	# mapping = [("2018-03-15-ascus_csv", "ASCUS"), ("2018-03-26-normal_csv", "NORMAL"), ("ASCH_csv", "ASCH"), ("HSIL_csv", "HSIL"), ("LSIL_csv", "LSIL")]

	# # normal
	# csv_dir = "C:/tsimage/tct/auto_label_last/normal_xception"
	# mapping = [("2018-06-11-normal_csv", "NORMAL"), ("NORMAL_AWS_csv", "NORMAL")]

	# test
	csv_dir = "C:/tsimage/tct/auto_label_last/test0814"
	mapping = [("2018-08-13-test_csv", "NORMAL")]
	main(csv_dir, mapping)