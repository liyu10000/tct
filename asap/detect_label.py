# used open-soucre ocr package: tesseract
# links to install and use tesseract: 
# https://github.com/tesseract-ocr/tesseract
# https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage

import re
import xlsxwriter

folders = ("17-yang-chen", "17-yang-mo", "17-yin-chen", "17-yin-mo", "18-yang-chen", "18-yang-mo", "18-yin-chen")

def read_labels(folder):
    ocr_txt = "E:/data-yantian/{}.txt".format(folder)
    file = open(ocr_txt, "r")
    labels = []
    for line in file:
        line = line.strip()
        if line:
            m = re.search("[0-9]{5,}", line)
            if m != None:
                label = m.group(0)
                print("{} contains {}".format(line.strip(), label))
                if len(label) > 6:
                    label = label[1:]
                labels.append("C"+label)
    file.close()
    return labels

def write_labels(folders):
    xlsx = "E:/data-yantian/labels.xlsx"
    workbook = xlsxwriter.Workbook(xlsx)
    worksheet = workbook.add_worksheet()
    folder_i = 0
    for folder in folders:
        worksheet.write(0,folder_i,folder)
        labels = read_labels(folder)
        for i,label in enumerate(labels):
            worksheet.write(i+1,folder_i,label)
        folder_i += 1
    workbook.close()

write_labels(folders)