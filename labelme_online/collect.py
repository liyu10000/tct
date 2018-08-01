import requests
import json
import xlsxwriter
from datetime import datetime
from info import url, all_headers

def get_table(url, header):
	res = requests.get(url, headers=header)
	data = json.loads(res.text)["data"]
	table = data[0]["table"]
	return table

def format_table(table):
	table_new = []
	table_new.append([item["label"] for item in table["header"]])
	for row in table["data"]:
		row_new = [0] * len(table_new[0])
		for index,item in enumerate(table["header"]):
			row_new[index] = row[item["prop"]]
		table_new.append(row_new)
	row_sum = ["-", "总计"]
	for i in range(2, len(table_new[0])):
		num = 0
		for num_row in range(1, len(table_new)):
			num += table_new[num_row][i]
		row_sum.append(num)
	table_new.append(row_sum)
	return table_new

def gen_xlsx(table_individual, table_summary, xlsx_name):
	workbook = xlsxwriter.Workbook(xlsx_name)
	worksheet = workbook.add_worksheet("individual")
	for i in range(len(table_individual)):
		for j in range(len(table_individual[i])):
			worksheet.write(i, j, table_individual[i][j])
	worksheet = workbook.add_worksheet("summary")
	for i in range(len(table_summary)):
		for j in range(len(table_summary[i])):
			worksheet.write(i, j, table_summary[i][j])
	workbook.close()

def collect_data(url, all_headers):
	table_individual = []
	table_summary = []
	for name,header in all_headers:
		table = get_table(url, header)
		table_new = format_table(table)
		table_individual.append([name])
		table_individual += table_new
		table_summary.append([name]+table_new[-1][2:])
		print("collected data from {}".format(name))
	table_summary.insert(0, ["name"]+table_individual[1][2:])
	xlsx_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx"
	gen_xlsx(table_individual, table_summary, xlsx_name)

if __name__ == "__main__":
	collect_data(url, all_headers)
