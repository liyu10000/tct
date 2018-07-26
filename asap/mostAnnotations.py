# search for tif/xml files with the most number of categories
from xml.dom.minidom import parse
import xml.dom.minidom
from utils.scan_files import scan_files

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
categoryCounts = []


def select_most(files_list):
    for file in files_list:
        DOMTree = xml.dom.minidom.parse(file)
        collection = DOMTree.documentElement
        annotations = collection.getElementsByTagName("Annotation")

        for annotation in annotations:
            if annotation.getAttribute("Color") in colorCounts:
                colorCounts[annotation.getAttribute("Color")] += 1

        n = 0
        for color, count in colorCounts.items():
            if count > 0:
                n += 1
        if len(categoryCounts) < 10:
            categoryCounts.append((file, n))
            if len(categoryCounts) == 10:
                sorted(categoryCounts, key=lambda x: x[1], reverse=True)
        else:
            i = 0
            for filename, count in categoryCounts:
                if count > n:
                    i += 1
            categoryCounts.insert(i, (file, n))
            del categoryCounts[-1]
        for color in colorCounts:
            colorCounts[color] = 0


file_path = "E:\\data7"
files_list = scan_files(file_path, postfix=".xml")
print("# files: " + str(len(files_list)))
select_most(files_list)

for filename, count in categoryCounts:
    print(filename, count)

