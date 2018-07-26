import xlsxwriter


txt_file = "C:\\Users\\tsimage\\Desktop\\深圳市人民医院\\A4-3.txt"
excel_file = "C:\\Users\\tsimage\\Desktop\\深圳市人民医院\\A4-3.xlsx"
n = 3  # number of columns

with open(txt_file, encoding="utf-8") as f:
    lines = f.readlines()
print("total lines: " + str(int(len(lines)/n)))

workbook = xlsxwriter.Workbook(excel_file)
worksheet = workbook.add_worksheet()
for row in range(int(len(lines)/n)):
    for col in range(n):
        worksheet.write(row, col, lines[row*n+col])

workbook.close()
