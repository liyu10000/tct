import sys
from ctypes import *
from PIL import Image


class LabelReader:
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

    def read_label(self, wsi_name):
        if self.os == "linux":
            from tslide.tslide import TSlide
            slide = TSlide(wsi_name)
            # print(slide.associated_images.items())
            image = slide.associated_images["label"].convert("RGB")  # RGB Image instance
            # w, h = image.size
            # image.crop((0, 0, w, h//2)).save("./res/half.jpg")
            # image.save("./res/label.jpg")
            slide.close()
            return image
        else:
            _lib = WinDLL("./lib/ImageOperationLib.dll")

            _lib.GetLableInfoPathFunc.argtypes = [c_char_p, POINTER(POINTER(c_ubyte)), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
            _lib.GetLableInfoPathFunc.restype = c_int
            path = c_char_p(wsi_name.encode("utf-8"))
            imageData = POINTER(c_ubyte)()
            length = c_int()
            width = c_int()
            height = c_int()
            res = c_int()
            res = _lib.GetLableInfoPathFunc(path, byref(imageData), byref(length), byref(width), byref(height))
            if res:
                # with open("./res/label_win.jpg", "wb") as f:
                #     f.write(string_at(imageData, length.value))
                import numpy as np
                narray = np.ctypeslib.as_array(imageData, shape=(length.value,))
                from io import BytesIO
                buf = BytesIO(narray)
                # Image.open(buf).save("./res/label_win.jpg")
                return Image.open(buf)
        return None


if __name__ == "__main__":
    wsi_name = "./res/C174539.kfb"
    LabelReader().read_label(wsi_name)