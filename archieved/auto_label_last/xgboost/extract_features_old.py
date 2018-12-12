import os
import csv
import pandas

def gen_dict(slides_path, class_i):
	"""
		slides_path: the path that contains the predicted folders
		class_i: diagnosis like "ASCUS"
	"""
	slides = os.listdir(slides_path)
	classify_dict_all = []
	segment_dict_all = []
	for slide_i in slides:
	    slide_i_csv = os.path.join(slides_path, slide_i+"/"+slide_i+".csv")
	    csv_file = pandas.read_csv(slide_i_csv)
	    classify_dict = {"ASCUS":0, "LSIL":0, "ASCH":0, "HSIL":0, "SCC":0}
	    segment_dict = {"ASCUS":0, "LSIL":0, "ASCH":0, "HSIL":0, "SCC":0}
	    classify_dict["info"] = (slide_i, class_i)
	    segment_dict["info"] = (slide_i, class_i)
	    for index, row in csv_file.iterrows():
	        classify_dict[row[u'classify'].encode("ascii", "ignore")] += 1
	        segment_dict[row[u'segment'].encode("ascii", "ignore")] += 1
	    classify_dict_all.append(classify_dict)
	    segment_dict_all.append(segment_dict)
	return segment_dict_all, classify_dict_all

def write_csv(segment_dict_all, classify_dict_all, output_file):
	with open(output_file, "w") as csv_file:
	    writer = csv.writer(csv_file)
	    writer.writerow(["slide_id", "diagnosis", 
	                     "segment", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC", 
	                     "classify", "ASCUS", "LSIL", "ASCH", "HSIL", "SCC"])
	    for segment, classify in zip(segment_dict_all, classify_dict_all):
	        writer.writerow([segment["info"][0], segment["info"][1], 
	                         "", segment["ASCUS"], segment["LSIL"], segment["ASCH"], segment["HSIL"], segment["SCC"],
	                         "", classify["ASCUS"], classify["LSIL"], classify["ASCH"], classify["HSIL"], classify["SCC"]])

if __name__ == "__main__":
	slides_path = "path/to/2018-03-15-ascus_jpg"
	class_i = "ASCUS"
	segment_dict_all,classify_dict_all = gen_dict(slides_path, class_i)
	output_file = "path/to/output.csv"
	write_csv(segment_dict_all, classify_dict_all, output_file)