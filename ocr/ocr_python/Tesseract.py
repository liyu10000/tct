"""
This program uses a python wrapper for the OCR engine tesseract: tesserocr
GitHub repo: https://github.com/sirfz/tesserocr
wheel download: https://github.com/simonflueckiger/tesserocr-windows_build/releases
"""

import sys
import re
from PIL import Image
import tesserocr


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
        # print(type(image).__name__)
        # if type(image).__name__ == "str":
        #     text = tesserocr.file_to_text(image)
        # else:
        #     text = tesserocr.image_to_text(image)
        # print(text)
        # return text
        with tesserocr.PyTessBaseAPI(path="/usr/share/tesseract-ocr/tessdata") as api:
            if type(image).__name__ == "str":
                api.SetImageFile(image)
            else:
                api.SetImage(image)
            text = api.GetUTF8Text()

            pattern = re.compile("[a-zA-Z]*[0-9]{5,}")
            m = pattern.search(text)
            if m:
                return re.compile("[a-zA-Z]*").search(m.group(0)).group(0), \
                       re.compile("[0-9]{5,}").search(m.group(0)).group(0)
            else:
                return "", ""


if __name__ == "__main__":
    image = "./res/label.jpg"
    Tesseract().detect(Image.open(image))
