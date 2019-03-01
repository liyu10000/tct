import os
import shutil

csv_path = os.path.join(os.getcwd(), "NORMAL_AWS_jpg")
out_path = os.path.join(os.getcwd(), "NORMAL_AWS_csv")
if not os.path.exists(out_path):
	os.makedirs(out_path)
csv_files = os.listdir(csv_path)

for csv_file in csv_files:
    csv_file = os.path.join(csv_path, csv_file+'/'+csv_file+'_c.csv')
    print(csv_file)
    shutil.copy2(csv_file, out_path)