# coding=utf-8

import os

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


def output_path(files_list, file_path):
    workbook = xlsxwriter.Workbook(file_path + "\\filepath.xlsx")
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, file_path)
    row = 2
    for file in files_list:
        worksheet.write(row, 0, file)
        row += 1

    workbook.close()


file_path = "C:\\liyu\\files\\xml"
files_list = scan_files(file_path, postfix=".xml")
output_path(files_list, file_path)

