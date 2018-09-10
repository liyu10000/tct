"""
install tessract:
Linux: follow github
Windows: https://digi.bib.uni-mannheim.de/tesseract/

install tesserocr:
This program uses a python wrapper for the OCR engine tesseract: tesserocr
GitHub repo: https://github.com/sirfz/tesserocr
wheel download: https://github.com/simonflueckiger/tesserocr-windows_build/releases

install pytesseract:
pip3 install pytesseract
"""

import sys
import re
from PIL import Image

class Tesseract:
    def __init__(self):
        self.detect_os()

    def detect_os(self):
        if sys.platform == "linux" or sys.platform == "linux2":
            self.os = "linux"
        elif sys.platform == "win32":
            self.os = "windows"
        else:
            print("operating system not supported")
            sys.exit(-1)

    def detect(self, image):
        try:
            try:
                import tesserocr
                with tesserocr.PyTessBaseAPI(path="/usr/share/tesseract-ocr/tessdata") as api:
                    if type(image).__name__ == "str":
                        api.SetImageFile(image)
                    else:
                        api.SetImage(image)
                    text = api.GetUTF8Text()
            except:
                import pytesseract
                if type(image).__name__ == "str":
                    text = pytesseract.image_to_string(Image.open(image))
                else:
                    text = pytesseract.image_to_string(image)
        except:
            print("tesseract not properly installed, program exits.")
            sys.exit(-1)
        return self.find_label(text)
            
    def find_label(self, text):
        pattern = re.compile("[a-zA-Z]*[0-9]{5,}")
        m = pattern.search(text)
        return m.group(0) if m else ""


if __name__ == "__main__":
    image = "./res/label.jpg"
    label = Tesseract().detect(Image.open(image))
    print(label)
