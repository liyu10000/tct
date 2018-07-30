import os

path = os.path.join(os.getcwd(), "2018-03-15-ascus-608")

for sub_dir in os.listdir(path):
	os.rename(os.path.join(path, sub_dir), os.path.join(path, sub_dir.replace(" ", "-")))
	print(sub_dir + " has changed")