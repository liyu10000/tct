package: 
	tesseract

install:
	1. install dependency package(install if necessary, could build from source): leptonica
	2. sudo apt install tesseract-ocr

usage:
	1. run a single image: 
		tesseract path/to/image output
	2. run multiple images in one tesseract run:
		tesseract path_to_images.list output
		
tips: 
	1. generate path_to_images.list:
		find images_dir -name "*.jpg" > path_to_images.list
	2. the output will actually be output.txt