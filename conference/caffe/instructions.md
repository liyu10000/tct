### prepare lmdb data
1. write image paths to txt file
	find full/path/to/image > test.txt
2. append label to each line
	sed -i 's/$/ 0/g' test.txt
3. merge and shuffle txts
	cat *.txt >> all.txt
	shuf -o all.txt all.txt
4. convert to lmdb file
	convert_imageset --resize_height=224 --resize_width=224 /path/to/images /path/to/txt /path/to/lmdb

