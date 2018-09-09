import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image

from LabelReader import LabelReader
from Tesseract import Tesseract


class OCRGui:
    def __init__(self):
        self.gui_setup()
        self.index = None
        self.database = []

    def gui_setup(self):
        self.root = tk.Tk()
        self.root.title("OCR")
        self.w1 = 512  # image width
        self.w2 = 270  # panel width
        self.h = 512   # image height
        self.root.geometry("{}x{}".format(self.w1+self.w2, self.h))
        self.root.resizable(width=False, height=False)  # cannot change window size

        self.imageCanvas = tk.Canvas(self.root, width=self.w1, height=self.h)
        self.imageCanvas.grid(row=0, column=0)

        self.panelFrame = tk.Frame(self.root, width=self.w2, height=self.h)
        self.panelFrame.grid(row=0, column=1)

        #create a button widget for open file
        self.open_f = tk.Button(self.panelFrame, text="open file", command=self.load_file)
        self.open_f.grid(row=0, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=10)
        #create a button widget for open dir
        self.open_d = tk.Button(self.panelFrame, text="open dir", command=self.load_files)
        self.open_d.grid(row=0, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=10)

        #create a label widget for wsi name
        self.wsi = tk.Label(self.panelFrame, text="filename:")
        self.wsi.grid(row=1, column=1, columnspan=1, sticky=tk.E, ipady=5, padx=5, pady=10)
        #create a label widget for wsi name text
        self.wsiText = tk.Label(self.panelFrame, text="XXXXXXXX.kfb")
        self.wsiText.grid(row=1, column=2, columnspan=2, sticky=tk.W, ipady=5, padx=5, pady=10)

        #create a label widget for label
        self.label = tk.Label(self.panelFrame, text="label:")
        self.label.grid(row=2, column=1, columnspan=1, sticky=tk.E, ipady=5, padx=5, pady=10)
        #create a text entry widget for label text
        self.labelText = tk.Entry(self.panelFrame)
        self.labelText.insert(0, "XXXXXXXX")
        self.labelText.grid(row=2, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=10)

        #create a button widget for previous
        self.previous = tk.Button(self.panelFrame, text="previous", command=lambda: self.update(step=-1))
        self.previous.grid(row=3, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=10)
        #create a button widget for next
        self.next = tk.Button(self.panelFrame, text="next", command=lambda: self.update(step=1))
        self.next.grid(row=3, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=10)

        #create a button widget for rename
        self.rename = tk.Button(self.panelFrame, text="rename", command=lambda: self.update(step=0,rename=True))
        self.rename.grid(row=4, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=5)
        #create a button widget for rename and next
        self.proceed = tk.Button(self.panelFrame, text="rename and next", command=lambda: self.update(step=1,rename=True))
        self.proceed.grid(row=4, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5)


    def load_file(self):
        fname = filedialog.askopenfilename(filetypes=(("wsi files", "*.kfb"),))
        if not fname:
            messagebox.showinfo("warning", "no file choosed")
        else:
            self.index = 0
            del self.database
            self.database = []
            self.database.append({"old_name":fname, "label":"", "image":None})
            self.update()

    def load_files(self):
        file_dir = filedialog.askdirectory()
        if not file_dir:
            messagebox.showinfo("warning", "no directory choosed")
        else:
            self.index = None
            del self.database
            self.database = []
            for fname in os.listdir(file_dir):
                if fname.endswith(".kfb"):
                    self.database.append({"old_name":os.path.join(file_dir, fname), "label":"", "image":None})
            if not self.database:
                messagebox.showinfo("warning", "no kfb file exists")
            else:
                self.index = 0
                self.update()


    def update(self, step=0, rename=False):
        if self.index == None:
            messagebox.showinfo("error", "three is no kfb file loaded")
            return
        if rename:
            self.rename_label()
        if step == -1:
            self.load_image(self.index-1)
        elif step == 0:
            self.load_image(self.index)
        elif step == 1:
            self.load_image(self.index+1)
        self.show_label()

    def load_image(self, i):
        def get_label(wsi_name, image):
            label = Tesseract().find_label(os.path.basename(wsi_name))
            if not label:
                w, h = image.size
                label = Tesseract().detect(image.crop((0, 0, w, h//3)))
            return label
        if i > len(self.database)-1 or i < 0:
            messagebox.showinfo("warning", "already the end")
            return
        if self.database[i]["image"]:
            image = self.database[i]["image"]
        else:
            image = LabelReader().read_label(wsi_name=self.database[i]["old_name"])
            self.database[i]["label"] = get_label(self.database[i]["old_name"], image)
            image = ImageTk.PhotoImage(image.resize((self.w1, self.h)))
            self.database[i]["image"] = image
        self.imageCanvas.create_image(self.w1//2, self.h//2, image=image)
        self.index = i

    def rename_label(self):
        self.database[self.index]["label"] = self.labelText.get()
        # replace file name here
        directory = os.path.dirname(self.database[self.index]["old_name"])
        basename = self.database[self.index]["label"] + ".kfb"
        new_name = os.path.join(directory, basename)
        os.rename(self.database[self.index]["old_name"], new_name)
        print("renamed {} to {}".format(self.database[self.index]["old_name"], new_name))
        self.database[self.index]["old_name"] = new_name

    def show_label(self):
        self.labelText.delete(0, tk.END)
        self.labelText.insert(0, self.database[self.index]["label"])
        self.wsi.config(text="{} / {}:".format(self.index+1, len(self.database)))
        self.wsiText.config(text=os.path.basename(self.database[self.index]["old_name"]))
    

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    OCRGui().run()