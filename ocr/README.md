# ocr_python
<pre>
	use tesseract as ocr engine, pytesseract/tesserocr as python wrapper
</pre>

### Install

#### Linux
 - install tesseract: follow [tesseract](https://github.com/tesseract-ocr/tesseract) github, require leptonica installation   
 	note: need to add tesseract path to system path, usually in _/usr/share/tesseract-ocr_
 <pre>
 	sudo apt install g++
	sudo apt install autoconf automake libtool
	sudo apt install pkg-config
	sudo apt install libpng-dev
	sudo apt install libjpeg8-dev
	sudo apt install libtiff5-dev
	sudo apt install zlib1g-dev

	sudo apt install libleptonica-dev

	sudo apt install tesseract-ocr libtesseract-dev

	// add tesseract path
</pre>

 - install tesserocr: follow [tesserocr](https://github.com/sirfz/tesserocr) github, or [wheel download](https://github.com/simonflueckiger/tesserocr-windows_build/releases)
 - install pytesseract: _pip install pytesseract_ (add pytesseract module to python search path, if necessary)

#### Windows
 - install tesseract: go find proper [installer](https://digi.bib.uni-mannheim.de/tesseract/)   
 	note: need to add tesseract path to system path, usually in _C:\Program Files (x86)\Tesseract-OCR_
 - install tesserocr: haven't figured out yet
 - install pytesseract: _pip install pytesseract_

### Usage
 - under ocr_python folder, run _python3 OcrGui.py_ (Linux), or _python OcrGui.py_ (Windows)

#### pack ocr_python into executable
<pre>
	pyinstaller OCRGui.py --hidden-import="PIL._tkinter_finder" (to be continued...)
</pre>



# ocr_java
 - use tesseract as ocr engine, [tess4j](https://github.com/nguyenq/tess4j) as java JNA wrapper
 - project is developed in eclipse, with [maven support](http://www.vogella.com/tutorials/EclipseMaven/article.html)

### Install

#### Windows
 - install eclipse and make the project to maven project

#### Linux
 - haven't figured out yet