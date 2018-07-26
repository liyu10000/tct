# coding=utf-8

import os
import xlsxwriter
from shutil import copy2


def scan_files(directory, prefix=None, postfix=None):
    files_list = []

    for root, sub_dirs, files in os.walk(directory):
        for special_file in files:
            if postfix:
                if special_file.endswith(postfix):
                    files_list.append(os.path.join(root, special_file).rsplit("\\", 1)[1])
            elif prefix:
                if special_file.startswith(prefix):
                    files_list.append(os.path.join(root, special_file))
            else:
                files_list.append(os.path.join(root, special_file))

    return files_list


def output_excel(files_list, file_path, file_name):
    workbook = xlsxwriter.Workbook(file_path + "\\" + file_name + ".xlsx")
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, file_path)
    row = 2
    for file in files_list:
        worksheet.write(row, 0, file)
        row += 1

    workbook.close()


def copy_files(files_list, fromdir, todir):
    for file in files_list:
        copy2(fromdir + "\\" + file, todir)


def batch():
    colors = {"#000000": 0,
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

    original = "D:\\data7-shenhe\\data7-shenhe-backup"
    modified = "D:\\data7-shenhe\\data7-shenhe-remain"

    for key in colors:
        orig_subdir = original + "\\" + key
        modi_subdir = modified + "\\" + key

        orig_files = scan_files(orig_subdir, postfix=".jpeg")
        modi_files = scan_files(modi_subdir, postfix=".jpeg")
        diff_files = list(set(orig_files) - set(modi_files))
        diff_files.sort()

        # output_dir = modi_subdir + "-diff"
        output_dir = modified + "\\0000shandiao"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # write the list of file names to excel
        output_excel(diff_files, output_dir, key)

        # copy the list of files to destination directory
        copy_files(diff_files, orig_subdir, output_dir)


def single():
    original = "D:\\data7-shenhe\\0000shandiao"
    modified = "D:\\data7-shenhe\\0000xiuzheng"

    orig_files = scan_files(original, postfix=".jpeg")
    modi_files = scan_files(modified, postfix=".jpeg")
    diff_files = list(set(orig_files) - set(modi_files))
    diff_files.sort()

    output_dir = original + "\\0001shandiao"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # copy the list of files to destination directory
    copy_files(diff_files, original, output_dir)


single()
