import os
import csv
import pandas as pd

classes = ["NORMAL", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
header = ['class_i', 
		  'ASCUS_s', 'LSIL_s', 'ASCH_s', 'HSIL_s', 'SCC_s', 
		  'ASCUS_c', 'LSIL_c', 'ASCH_c', 'HSIL_c', 'SCC_c', 
		  'ASCUS_c_09', 'LSIL_c_09', 'ASCH_c_09', 'HSIL_c_09', 'SCC_c_09', 
		  'ASCUS_c_099', 'LSIL_c_099', 'ASCH_c_099', 'HSIL_c_099', 'SCC_c_099', 
		  'ASCUS_c_0999', 'LSIL_c_0999', 'ASCH_c_0999', 'HSIL_c_0999', 'SCC_c_0999', 
		  'w_mean', 'h_mean', 'v_mean',
		  'w_01', 'w_02', 'w_03', 'w_04', 'w_05', 'w_06', 'w_07', 'w_08', 'w_09',
		  'h_01', 'h_02', 'h_03', 'h_04', 'h_05', 'h_06', 'h_07', 'h_08', 'h_09',
		  'd_01', 'd_02', 'd_03', 'd_04', 'd_05', 'd_06', 'd_07', 'd_08', 'd_09',
		  'v_01', 'v_02', 'v_03', 'v_04', 'v_05', 'v_06', 'v_07', 'v_08', 'v_09',]

def gen_dict_for_pre40(xlsx_file):
	excel = pd.read_excel(xlsx_file)
	excel_dict = {}
	for index, row in excel.iterrows():
	    excel_dict[row[u'病理号']] = row[u'细胞学诊断']
	return excel_dict

def gen_csv(csv_path, diagnosis):
	csv_files = os.listdir(csv_path)
	item_dict_all = []
	for csv_file in csv_files:
		csv_df = pd.read_csv(os.path.join(csv_path, csv_file))
		item_dict = {key:0 for key in header}
		if type(diagnosis).__name__ == "dict":
			class_i = diagnosis[csv_file.split(".")[0]]
			if not class_i in classes:
				continue
			item_dict["class_i"] = classes.index(class_i)
		elif type(diagnosis).__name__ == "str":
			item_dict["class_i"] = classes.index(diagnosis)
		else:
			break
		for index,row in csv_df.iterrows():
			item_dict[row['segment']+"_s"] += 1
			item_dict[row['classify']+"_c"] += 1
			if float(row['det.1']) > 0.9:
				item_dict[row['classify']+"_c_09"] += 1
			if float(row['det.1']) > 0.99:
				item_dict[row['classify']+"_c_099"] += 1
			if float(row['det.1']) > 0.999:
				item_dict[row['classify']+"_c_0999"] += 1
		w = csv_df['xmax'] - csv_df['xmin']
		h = csv_df['ymax'] - csv_df['ymin']
		item_dict['w_mean'] = w.mean()
		item_dict['h_mean'] = h.mean()
		item_dict['v_mean'] = (w*h).mean()
		percentile = [x*0.1 for x in range(1, 10)]
		for index, p in enumerate(percentile):
			item_dict['w_0{}'.format(index+1)] = w.quantile(p)
			item_dict['h_0{}'.format(index+1)] = w.quantile(p)
			item_dict['d_0{}'.format(index+1)] = (w*w+h*h).pow(0.5).quantile(p)
			item_dict['v_0{}'.format(index+1)] = (w*h).quantile(p)
		item_dict_all.append(item_dict)
	return item_dict_all

def write_csv(item_dict_all, output_file):
	with open(output_file, "a", newline='') as csv_file:
	    writer = csv.writer(csv_file)
	    #writer.writerow(header)
	    for item_dict in item_dict_all:
	    	writer.writerow([item_dict[key] for key in header])


if __name__ == "__main__":
	# xslx_file = "C:/tsimage/tct/auto_label_last/csv_data/used_in_changsha_conf/diagnosis.xlsx"
	# diagnosis = gen_dict_for_pre40(xslx_file)

	csv_path = "C:/tsimage/tct/auto_label_last/csv_data/csv_file_0810/HSIL_csv"
	diagnosis = "HSIL"
	item_dict_all = gen_csv(csv_path, diagnosis)
	output_file = "C:/tsimage/tct/auto_label_last/data_new.csv"
	write_csv(item_dict_all, output_file)
