import os
from xlrd import open_workbook
from utils.scan_files import scan_files

def rename():
	i=0
	path="C:/test/files"
	filelist=os.listdir(path)  #该文件夹下所有的文件（包括文件夹）
	for file in filelist:  #遍历所有文件
		Olddir=os.path.join(path,file)  #原来的文件路径
		if os.path.isdir(Olddir):  #如果是文件夹则跳过
			continue
		filename=os.path.splitext(file)[0]  #文件名
		filetype=os.path.splitext(file)[1]  #文件扩展名
		Newdir=os.path.join(path,filename+str(i)+filetype)  #新的文件路径
		os.rename(Olddir,Newdir)  #重命名
		i=i+1


def read_excel():
    excel_name = "C:/Users/tsimage/Desktop/大会.xlsx"
    excel = open_workbook(excel_name)
    sheet1 = excel.sheet_by_index(0)
    n_rows = sheet1.nrows
    n_cols = sheet1.ncols
    values = []
    for row in range(n_rows):
        values.append(sheet1.cell(row, n_cols-1).value)
    return values


def for_dahui():
    labels = read_excel()
    file_path = "D:\\2018-04-24\\tiff"
    file_names = scan_files(file_path, postfix=".tif")
    print(len(labels), len(file_names))
    for i in range(len(labels)):
        os.rename(file_names[i], os.path.join(file_path, str(labels[i]) + ".tif"))

def add_postfix():
    file_path = "D:\\2018-04-24\\tiff"
    file_names = scan_files(file_path, postfix=".jpg")
    for file_name in file_names:
        os.rename(file_name, file_name[:-4] + "-label.jpg")

if __name__ == "__main__":
    add_postfix()