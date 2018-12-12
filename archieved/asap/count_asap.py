# count the number of annotations in each category
import os
import csv
import collections
from xml.dom.minidom import parse
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


colorCounts = {"#000000": 0,
               "#aa0000": 0,
               "#aa007f": 0,
               "#aa00ff": 0,
               "#ff0000": 0,
               "#005500": 0,
               "#00557f": 0,
               "#0055ff": 0,
               "#aa5500": 0,
               "#aa557f": 0,
               "#aa55ff": 0,
               "#ff5500": 0,
               "#ff557f": 0,
               "#ff55ff": 0,
               "#00aa00": 0,
               "#00aa7f": 0,
               "#00aaff": 0,
               "#55aa00": 0,
               "#55aa7f": 0}
               
largeCounts = {"#000000": 0,
               "#aa0000": 0,
               "#aa007f": 0,
               "#aa00ff": 0,
               "#ff0000": 0,
               "#005500": 0,
               "#00557f": 0,
               "#0055ff": 0,
               "#aa5500": 0,
               "#aa557f": 0,
               "#aa55ff": 0,
               "#ff5500": 0,
               "#ff557f": 0,
               "#ff55ff": 0,
               "#00aa00": 0,
               "#00aa7f": 0,
               "#00aaff": 0,
               "#55aa00": 0,
               "#55aa7f": 0}

classes = {"#aa0000": "HSIL", "#aa007f": "ASCH", "#005500": "LSIL", "#00557f": "ASCUS", 
                       "#0055ff": "SCC", "#aa557f": "ADC", "#aa55ff": "EC", "#ff5500": "AGC1", 
                       "#ff557f": "AGC2", "#ff55ff": "AGC3", "#00aa00": "FUNGI", "#00aa7f": "TRI", 
                       "#00aaff": "CC", "#55aa00": "ACTINO", "#55aa7f": "VIRUS", "#ffffff": "NORMAL",
                       "#000000": "MC", "#aa00ff": "SC", "#ff0000": "RC", "#aa5500": "GEC"}

total = 0
large = 0
def count(files_list):
    global total  # number of files
    global large
    for file in files_list:
        DOMTree = xml.dom.minidom.parse(file)
        collection = DOMTree.documentElement
        total += 1
        annotations = collection.getElementsByTagName("Annotation")

        wrong = 0
        for annotation in annotations:
            if annotation.getAttribute("Color") in colorCounts:
                colorCounts[annotation.getAttribute("Color")] += 1
                coordinates = annotation.getElementsByTagName("Coordinate")
                x_coords = []
                y_coords = []
                for coordinate in coordinates:
                    x_coords.append(float(coordinate.getAttribute("X")))
                    y_coords.append(float(coordinate.getAttribute("Y")))                    
                x_min = int(min(x_coords))
                x_max = int(max(x_coords))
                y_min = int(min(y_coords))
                y_max = int(max(y_coords))
                if (x_max-x_min) > 608 or (y_max-y_min) > 608:
                    largeCounts[annotation.getAttribute("Color")] += 1
                    large += 1
                
            else:
                wrong += 1
                print("position: " + annotation.getAttribute("Name"))

        if wrong > 0:
            print("# wrong color = " + str(wrong) + "  -->  " + file)
            print()


def write_csv(counts, csv_path):
    with open(csv_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        for key,value in counts.items():
            csv_writer.writerow([key,classes[key], value])

# count annotations from single root directory
file_path = "/home/sakulaki/yolo-yuli/xxx/data_20180922/checked"
files_list = scan_files(file_path, postfix=".xml")
count(files_list)

write_csv(collections.OrderedDict(sorted(colorCounts.items())), "/home/sakulaki/yolo-yuli/xxx/data_20180922/summary.csv")


# # count annotations from multiple separated directories
# classes = ("01_ASCUS", "02_LSIL", "03_ASCH", "04_HSIL", "05_SCC", "06_AGC1", "07_AGC2", "08_ADC", "09_EC", "10_FUNGI", "11_TRI", "12_CC", "13_ACTINO", "14_VIRUS")
# file_path = "/media/tsimage/Elements/data"
# for class_i in classes:
#     file_path_i = os.path.join(file_path, class_i)
#     files_list = scan_files(file_path_i, postfix=".xml")
#     count(files_list)

# output results
print("# files: " + str(total))
print(colorCounts)
print("# labels large than 608: " + str(large))
print(largeCounts)

# write to excel
# workbook = xlsxwriter.Workbook("C:/liyu/gui/tct/res/个人统计.xlsx")
# worksheet = workbook.add_worksheet()
# worksheet.write(0, 0, file_path)
# row = 1
# for key in colorCounts.keys():
    # worksheet.write(row, 0, key)
    # worksheet.write(row, 1, colorCounts[key])
    # row += 1
# workbook.close()
