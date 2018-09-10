## ocr_python
	use tesseract as ocr engine, pytesseract/tesserocr as python wrapper

### Install

#### Linux
 - install tesseract: follow tesseract github, require leptonica installation   
 	note: need to add tesseract path to system path, usually in _/usr/share/tesseract-ocr_
 - install tesserocr: [Github repo](https://github.com/sirfz/tesserocr), [wheel download](https://github.com/simonflueckiger/tesserocr-windows_build/releases)
 - install pytesseract: _pip install pytesseract_ (add pytesseract module to python search path, if necessary)

#### Windows
 - install tesseract: go find proper [installer](https://digi.bib.uni-mannheim.de/tesseract/)   
 	note: need to add tesseract path to system path, usually in _C:\Program Files (x86)\Tesseract-OCR_
 - install tesserocr: haven't figured out yet
 - install pytesseract: _pip install pytesseract_

### Usage
 - under ocr_python folder, run _python3 OcrGui.py_ (Linux), or _python OcrGui.py_ (Windows)

#### pack ocr_python into executable   
 - pyinstaller OCRGui.py --hidden-import="PIL._tkinter_finder"