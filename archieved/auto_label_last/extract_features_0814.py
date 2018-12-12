import os
import csv
import pandas as pd

classes = ["NORMAL", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC"]
header = ['name', 'class_i', 
		  'ASCUS_s', 	 'LSIL_s', 	   'ASCH_s',	 'HSIL_s',	   'SCC_s',
		  'ASCUS_s_005', 'LSIL_s_005', 'ASCH_s_005', 'HSIL_s_005', 'SCC_s_005',
		  'ASCUS_s_01',  'LSIL_s_01',  'ASCH_s_01',  'HSIL_s_01',  'SCC_s_01',
		  'ASCUS_s_02',  'LSIL_s_02',  'ASCH_s_02',  'HSIL_s_02',  'SCC_s_02',
		  'ASCUS_s_03',  'LSIL_s_03',  'ASCH_s_03',  'HSIL_s_03',  'SCC_s_03',
		  'ASCUS_s_04',  'LSIL_s_04',  'ASCH_s_04',  'HSIL_s_04',  'SCC_s_04',
		  'ASCUS_s_05',  'LSIL_s_05',  'ASCH_s_05',  'HSIL_s_05',  'SCC_s_05',
		  'ASCUS_s_06',  'LSIL_s_06',  'ASCH_s_06',  'HSIL_s_06',  'SCC_s_06',
		  'ASCUS_s_07',  'LSIL_s_07',  'ASCH_s_07',  'HSIL_s_07',  'SCC_s_07',
		  'ASCUS_s_08',  'LSIL_s_08',  'ASCH_s_08',  'HSIL_s_08',  'SCC_s_08',
		  'ASCUS_s_09',  'LSIL_s_09',  'ASCH_s_09',  'HSIL_s_09',  'SCC_s_09',
		  'ASCUS_s_099', 'LSIL_s_099', 'ASCH_s_099', 'HSIL_s_099', 'SCC_s_099',	  
		  'ASCUS_c', 	 'LSIL_c', 	   'ASCH_c',     'HSIL_c',     'SCC_c', 
		  'ASCUS_c_01',  'LSIL_c_01',  'ASCH_c_01',  'HSIL_c_01',  'SCC_c_01',
		  'ASCUS_c_02',  'LSIL_c_02',  'ASCH_c_02',  'HSIL_c_02',  'SCC_c_02',
		  'ASCUS_c_03',  'LSIL_c_03',  'ASCH_c_03',  'HSIL_c_03',  'SCC_c_03',
		  'ASCUS_c_04',  'LSIL_c_04',  'ASCH_c_04',  'HSIL_c_04',  'SCC_c_04',
		  'ASCUS_c_05',  'LSIL_c_05',  'ASCH_c_05',  'HSIL_c_05',  'SCC_c_05',
		  'ASCUS_c_06',  'LSIL_c_06',  'ASCH_c_06',  'HSIL_c_06',  'SCC_c_06',
		  'ASCUS_c_07',  'LSIL_c_07',  'ASCH_c_07',  'HSIL_c_07',  'SCC_c_07',
		  'ASCUS_c_08',  'LSIL_c_08',  'ASCH_c_08',  'HSIL_c_08',  'SCC_c_08',
		  'ASCUS_c_09',  'LSIL_c_09',  'ASCH_c_09',  'HSIL_c_09',  'SCC_c_09',
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

def gen_csv(csv_file, diagnosis):
	csv_df = pd.read_csv(csv_file)
	item_dict = {key:0 for key in header}
	item_dict['name'] = os.path.splitext(os.path.basename(csv_file))[0][:-2]
	if type(diagnosis).__name__ == "dict":
		class_i = diagnosis[csv_file.split(".")[0]]
		if not class_i in classes:
			return {}
		item_dict["class_i"] = classes.index(class_i)
	elif type(diagnosis).__name__ == "str":
		item_dict["class_i"] = classes.index(diagnosis)
	else:
		return {}
	for index,row in csv_df.iterrows():
		item_dict[row['segment']+"_s"] += 1
		item_dict[row['classify']+"_c"] += 1
		if float(row['det']) > 0.05:
			item_dict[row['segment']+"_s_005"] += 1
		if float(row['det']) > 0.99:
			item_dict[row['segment']+"_s_099"] += 1
		percentile = [x*0.1 for x in range(1, 10)]
		for index, p in enumerate(percentile):
			if float(row['det']) > p:
				item_dict[row['segment']+'_s_0{}'.format(index+1)] += 1
			if float(row['det.1']) > p:
				item_dict[row['classify']+'_c_0{}'.format(index+1)] += 1
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
	return item_dict

def gen_csv_dir(csv_path, diagnosis):
	csv_files = os.listdir(csv_path)
	item_dict_all = []
	for csv_file in csv_files:
		item_dict = gen_csv(os.path.join(csv_path, csv_file), diagnosis)
		item_dict_all.append(item_dict)
	return item_dict_all

def write_csv_no_index(item_dict_all, output_file):
	with open(output_file, "a", newline='') as csv_file:
	    writer = csv.writer(csv_file)
	    new_header = ['name','class_i','ASCUS_s','LSIL_s','ASCH_s','HSIL_s','SCC_s','ASCUS_c','LSIL_c','ASCH_c','HSIL_c','SCC_c']
	    writer.writerow(new_header)
	    for item_dict in item_dict_all:
	    	writer.writerow([item_dict[key] for key in new_header])

def write_csv_index(item_dict, output_file):
	with open(output_file, "w", newline='') as csv_file:
	    writer = csv.writer(csv_file)
	    writer.writerow(["index"]+header)
	    writer.writerow([1]+[item_dict[key] for key in header])

def extract_feature(csv_file, diagnosis):
	item_dict = gen_csv(csv_file, diagnosis)
	if len(item_dict) == 0:
		return ""
	csv_file_f = os.path.splitext(csv_file)[0] + "_f.csv"
	write_csv_index(item_dict, csv_file_f)
	return csv_file_f

if __name__ == "__main__":
	# # batch collect
	# # collect changsha40
	# # xslx_file = "C:/tsimage/tct/auto_label_last/csv_data/used_in_changsha_conf/diagnosis.xlsx"
	# # diagnosis = gen_dict_for_pre40(xslx_file)

	# collect from class_i folder
	csv_path = "C:/tsimage/tct/auto_label_last/test0814/2018-08-13-test_csv"
	diagnosis = "NORMAL"
	item_dict_all = gen_csv_dir(csv_path, diagnosis)
	output_file = "C:/tsimage/tct/auto_label_last/test_result_0814.csv"
	write_csv_no_index(item_dict_all, output_file)

	# # individual collect
	# csv_file_c2 = "2018-03-15-14_54_10_c2.csv"
	# csv_file_f = extract_feature(csv_file_c2, diagnosis="NORMAL")
