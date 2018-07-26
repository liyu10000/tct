# count the number of annotations in each category
import os
import xml.dom.minidom
import xlsxwriter

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

classes = {"NORMAL": 0, "ASCUS": 0, "LSIL": 0, "ASCH": 0, "HSIL": 0,
           "SCC": 0, "AGC1": 0, "AGC2": 0, "EC": 0, "FUNGI": 0,
           "TRI": 0, "CC": 0, "ACTINO": 0, "VIRUS": 0}

def count(files_list):
    for file in files_list:
        #print(file)
        DOMTree = xml.dom.minidom.parse(file)
        collection = DOMTree.documentElement
        annotations = collection.getElementsByTagName("object")

        for annotation in annotations:
            mark = annotation.getElementsByTagName("name")[0].firstChild.nodeValue
            if mark in classes:
                classes[mark] += 1


#file_path = "E:/data/tct_data608_0716"
file_path = os.path.join(os.getcwd(), "train")
files_list = scan_files(file_path, postfix=".xml")
print("# files: " + str(len(files_list)))
count(files_list)
print(sorted(classes.items()))

"""
# write to excel
workbook = xlsxwriter.Workbook("C:/liyu/gui/tct/res/个人统计.xlsx")
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, file_path)
row = 1
for key in classes.keys():
    worksheet.write(row, 0, key)
    worksheet.write(row, 1, classes[key])
    row += 1
workbook.close()
"""
