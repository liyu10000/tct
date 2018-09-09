import os
import re
import pandas as pd

# folder path that contains the label jpgs
label_dir = "17-yang-chen"
# a list file that contains all the jpg paths
label_list = "labels.list"
# write into the list file
os.system("find {} -name '*.jpg' > {}".format(label_dir, label_list))
# an output file that will contains the ocr results, we need to parse it
label_output = "labels"
# run ocr
os.system("tesseract {} {}".format(label_list, label_output))
# the ocr output will be a .txt file
label_output += ".txt"

# read from label_list file into a python list
with open(label_list, "r") as list_f:
	#print(list_f.readlines())
	label_names_old = list_f.readlines()
label_names_old = [os.path.basename(i.strip())[:19] for i in label_names_old]

# search for label
with open(label_output, "r") as output_f:
	pattern = re.compile("1\d{5,}")
	label_names_new = []
	for line in output_f:
		m = pattern.search(line)
		if m:
			label_names_new.append(m.group(0))

# pad two lists to the same length
label_names_new += [''] * (len(label_names_old) - len(label_names_new))

# since ocr is not always correct, we need to check it manually
csv_file = "results.csv"
df = pd.DataFrame({"old":label_names_old, "new":label_names_new})
df.to_csv(csv_file)

# check and correct results.csv, i will use it to rename files
df2 = pd.read_csv(csv_file)
for row in df.iterrows():
	os.rename(os.path.join(label_dir, row['old']+".kfb"), os.path.join(label_dir, row['new']+".kfb"))