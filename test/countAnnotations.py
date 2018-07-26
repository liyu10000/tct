#coding=utf-8

import os  

from xml.dom.minidom import parse
import xml.dom.minidom

import xlsxwriter
 
def scan_files(directory,prefix=None,postfix=None):  
    files_list=[]  
      
    for root, sub_dirs, files in os.walk(directory):  
        for special_file in files:  
            if postfix:  
                if special_file.endswith(postfix):  
                    files_list.append(os.path.join(root,special_file))  
            elif prefix:  
                if special_file.startswith(prefix):  
                    files_list.append(os.path.join(root,special_file))  
            else:  
                files_list.append(os.path.join(root,special_file))  
                            
    return files_list


colorCounts = {	"#000000":0,
			"#aa0000":0,
			"#aa007f":0,
			"#aa00ff":0,
			"#ff0000":0,
			"#005500":0,
			"#00557f":0,
			"#0055ff":0,
			"#aa5500":0,
			"#aa557f":0,
			"#aa55ff":0,
			"#ff5500":0,
			"#ff557f":0,
			"#ff55ff":0,
			"#00aa00":0,
			"#00aa7f":0,
			"#00aaff":0,
			"#55aa00":0,
			"#55aa7f":0}


def count(files_list):
	for file in files_list:
		DOMTree = xml.dom.minidom.parse(file)
		collection = DOMTree.documentElement

		annotations = collection.getElementsByTagName("Annotation")
		total = 0;
		wrong = 0;
		for annotation in annotations:
			total += 1
			if annotation.getAttribute("Color") in colorCounts:
				colorCounts[annotation.getAttribute("Color")] += 1
			else:
                print("position: " + annotation.getAttribute("Name"))
                wrong += 1

    if (wrong > 0):
        print("wrong color = " + str(wrong) + "  -->  " + file)


file = "D:\\liangxinrong"
files_list = scan_files(file, postfix=".xml")
count(files_list)

print(colorCounts)


#write to excel
workbook = xlsxwriter.Workbook("C:\\liyu\\个人统计.xlsx")
worksheet = workbook.add_worksheet()

worksheet.write(0, 0, file)

row = 1
for key in colorCounts.keys():
    worksheet.write(row, 0, key)
    worksheet.write(row, 1, colorCounts[key])
    row += 1

workbook.close()
