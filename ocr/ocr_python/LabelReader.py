import sys
from tslide.tslide import TSlide

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
            slide = TSlide(wsi_name)
            # print(slide.associated_images.items())
            label = slide.associated_images["label"].convert("RGB")  # RGB Image instance
            # w, h = label.size
            # label.crop((0, 0, w, h//2)).save("./res/half.jpg")
            # label.save("./res/label.jpg")
            slide.close()
            return label
        return None


if __name__ == "__main__":
    wsi_name = "./res/C174539.kfb"
    LabelReader().read_label(wsi_name)