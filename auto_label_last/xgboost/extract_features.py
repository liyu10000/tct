import os
import csv
import pandas as pd

classes = ["NORMAL", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
header = ['class_i', 
		  'ASCUS_c_09',  'LSIL_c_09',  'ASCH_c_09',  'HSIL_c_09',  'SCC_c_09',
		  'ASCUS_c_099', 'LSIL_c_099', 'ASCH_c_099', 'HSIL_c_099', 'SCC_c_099', 
		  'ASCUS_c_0999', 'LSIL_c_0999', 'ASCH_c_0999', 'HSIL_c_0999', 'SCC_c_0999', 
		  'ASCUS_c_09999', 'LSIL_c_09999', 'ASCH_c_09999', 'HSIL_c_09999', 'SCC_c_09999', 
		  'ASCUS_c_099999', 'LSIL_c_099999', 'ASCH_c_099999', 'HSIL_c_099999', 'SCC_c_099999',
		  'd_05']

def gen_csv(csv_file, diagnosis):
	csv_df = pd.read_csv(csv_file)
	item_dict = {key:0 for key in header}
	item_dict["class_i"] = classes.index(diagnosis)
	for index,row in csv_df.iterrows():
		if float(row['det.1']) > 0.9:
			item_dict[row['classify']+"_c_09"] += 1
		if float(row['det.1']) > 0.99:
			item_dict[row['classify']+"_c_099"] += 1
		if float(row['det.1']) > 0.999:
			item_dict[row['classify']+"_c_0999"] += 1
		if float(row['det.1']) > 0.9999:
			item_dict[row['classify']+"_c_09999"] += 1
		if float(row['det.1']) > 0.99999:
			item_dict[row['classify']+"_c_099999"] += 1
	w = csv_df['xmax'] - csv_df['xmin']
	h = csv_df['ymax'] - csv_df['ymin']
	item_dict['d_05'] = (w*w+h*h).pow(0.5).quantile(0.5)
	return item_dict

def gen_csv_dir(csv_path, diagnosis):
	csv_files = os.listdir(csv_path)
	item_dict_all = []
	for csv_file in csv_files:
		item_dict = gen_csv(os.path.join(csv_path, csv_file), diagnosis)
		item_dict_all.append(item_dict)
	return item_dict_all

def write_csv(item_dict_all, output_file):
	with open(output_file, "a", newline='') as csv_file:
	    writer = csv.writer(csv_file)
	    #writer.writerow(header)
	    for item_dict in item_dict_all:
	    	writer.writerow([item_dict[key] for key in header])

def extract_feature(csv_file, diagnosis):
	item_dict_all = gen_csv(csv_in, diagnosis)
	csv_file_f = os.path.splitext(csv_file)[0] + "_f.csv"
	write_csv(item_dict_all, csv_file_f)
	return csv_file_f

if __name__ == "__main__":
	# xslx_file = "C:/tsimage/tct/auto_label_last/csv_data/used_in_changsha_conf/diagnosis.xlsx"
	# diagnosis = gen_dict_for_pre40(xslx_file)

	csv_path = "C:/tsimage/tct/auto_label_last/labeled_xception/04_HSIL_csv"
	diagnosis = "HSIL"
	item_dict_all = gen_csv_dir(csv_path, diagnosis)
	output_file = "C:/tsimage/tct/auto_label_last/labeled_0814_v2.csv"
	write_csv(item_dict_all, output_file)
