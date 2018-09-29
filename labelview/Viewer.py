import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, IntVar
from PIL import ImageTk, Image

from Config import cfg
from Patcher import Patcher

class Viewer:
    def __init__(self):
        self.index = None
        self.image_on = None  # stores the image to show on gui
        self.database = []
        self.setup()

    def setup(self):
        self.root = tk.Tk()
        self.root.title("labelview")
        self.root.state("iconic")
        # self.root.resizable(width=False, height=False)  # cannot change window size
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.f = 0.8  # the fraction of image region
        self.b = 0.3  # the fraction of button region
        
        self.tabs = ttk.Notebook(self.root)

        self.thumb_tab = ttk.Frame(self.tabs)
        # left side control panel
        self.control = ttk.Frame(self.thumb_tab, width=self.w*(1-self.f), height=self.h)
        self.control.grid(row=0, column=0)

        # button control panel
        # open single file
        open_f = ttk.Button(self.control, text="open file", command=self.load_file)
        open_f.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # load single csv/xml corresponding to wsi file
        load_l = ttk.Button(self.control, text="load csv/xml", command=self.load_labels)
        load_l.grid(row=0, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        # open directory
        open_d = ttk.Button(self.control, text="open dir", command=self.load_files)
        open_d.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # set csv/xml directory
        load_ld = ttk.Button(self.control, text="load csv/xml dir", command=self.load_labels_dir)
        load_ld.grid(row=1, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        # current directory name
        self.dir_name_ = ttk.Label(self.control, text="dir:")
        self.dir_name_.grid(row=2, column=0, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)
        self.dir_name = ttk.Label(self.control, text="----")
        self.dir_name.grid(row=2, column=1, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)
        # display file count
        self.n_count_ = ttk.Label(self.control, text="count:")
        self.n_count_.grid(row=2, column=2, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)
        self.n_count = ttk.Label(self.control, text="----")
        self.n_count.grid(row=2, column=3, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)

        # display fname
        self.fname = ttk.Label(self.control, text="XXXX.kfb/.tif")
        self.fname.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # display lname
        self.lname = ttk.Label(self.control, text="XXXX.csv/.xml")
        self.lname.grid(row=3, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        # previous
        prev_b = ttk.Button(self.control, text="previous", command=lambda: self.update(step=-1))
        prev_b.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=30)
        # next
        next_b = ttk.Button(self.control, text="next", command=lambda: self.update(step=1))
        next_b.grid(row=4, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=30)

        # checkbox control panel
        # checkbox hint
        c_hint = ttk.Label(self.control, text="choose classes here:")
        c_hint.grid(row=5, column=0, columnspan=2, sticky="e", ipady=5, padx=10, pady=10)
        # add confirm button
        conform = ttk.Button(self.control, text="confirm", command=lambda: self.update())
        conform.grid(row=5, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # add checkboxes
        self.colorblock = []
        self.checkboxes = []
        for i, class_i in enumerate(cfg.CLASSES):
            var = IntVar(value=1)
            clb = ttk.Label(self.control, text="-", background=cfg.COLOURS[class_i])
            chk = ttk.Checkbutton(self.control, text=class_i, variable=var)
            if i < len(cfg.CLASSES)//2:
                clb.grid(row=6+i, column=0, columnspan=1, sticky="ew", ipady=1, padx=10, pady=2)
                chk.grid(row=6+i, column=1, columnspan=1, sticky="w", ipady=1, padx=10, pady=2)
            else:
                clb.grid(row=6+i-len(cfg.CLASSES)//2, column=2, columnspan=1, sticky="ew", ipady=1, padx=10, pady=2)
                chk.grid(row=6+i-len(cfg.CLASSES)//2, column=3, columnspan=1, sticky="w", ipady=1, padx=10, pady=2)
            self.colorblock.append(clb)
            self.checkboxes.append(var)
        

        # separator
        separator = ttk.Separator(self.thumb_tab, orient="vertical")
        separator.grid(row=0, column=1, sticky="ns")


        # right side image panel
        self.display = tk.Canvas(self.thumb_tab, width=self.w*self.f, height=self.h)
        self.display.grid(row=0, column=2)

        self.tabs.add(self.thumb_tab, text="thumbnail")

        self.image_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.image_tab, text="label images")
        self.tabs.pack()


    def load_file(self):
        fname = filedialog.askopenfilename(filetypes=(("kfb files", "*.kfb"), ("tif files", "*.tif")))
        if not fname:
            messagebox.showinfo("warning", "no file choosed")
        else:
            self.index = 0
            del self.database
            self.database = []
            self.database.append({"basename":os.path.splitext(os.path.basename(fname))[0], "fname":fname, "lname":None})
            self.update_text()


    def load_files(self):
        file_dir = filedialog.askdirectory()
        if not file_dir:
            messagebox.showinfo("warning", "no directory choosed")
        else:
            self.index = None
            del self.database
            self.database = []
            fnames = os.listdir(file_dir)
            fnames.sort()
            for fname in fnames:
                if fname.endswith(".kfb") or fname.endswith(".tif"):
                    self.database.append({"basename":os.path.splitext(fname)[0], "fname":os.path.join(file_dir, fname), "lname":None})
            if not self.database:
                messagebox.showinfo("warning", "no kfb file exists")
            else:
                self.index = 0
                self.update_text()


    def load_labels(self):
        if self.index is None:
            messagebox.showinfo("error", "no kfb/tif file loaded")
            return
        lname = filedialog.askopenfilename(filetypes=(("csv files", "*.csv"), ("xml files", "*.xml")))
        if not lname:
            messagebox.showinfo("warning", "no file choosed")
        elif not self.database[self.index]["basename"] in os.path.basename(lname):
            messagebox.showinfo("warning", "label file does not match with kfb/tif file")
        else:
            self.database[self.index]["lname"] = lname
            self.update()


    def load_labels_dir(self):
        def nullify_lname():
            for item in self.database:
                item["lname"] = None
        def choose_matched():
            database_new = [item for item in self.database if item["lname"] is not None]
            del self.database
            self.database = database_new
            if self.database:
                self.index = 0
            else:
                self.index = None

        if self.index is None:
            messagebox.showinfo("error", "no kfb/tif file loaded")
            return
        file_dir = filedialog.askdirectory()
        if not file_dir:
            messagebox.showinfo("warning", "no directory choosed")
        else:
            nullify_lname()
            lnames = os.listdir(file_dir)
            lnames.sort()
            for lname in lnames:
                if lname.endswith(".csv") or lname.endswith(".xml"):
                    for i,item in enumerate(self.database):
                        if item["basename"] in os.path.basename(lname):
                            self.database[i]["lname"] = os.path.join(file_dir, lname)
                            break
            choose_matched()
            self.update()


    def load_thumbnail(self, classes):
        def resize(image, w, h):
            w0, h0 = image.size
            factor = min(w/w0, h/w0)
            return image.resize((int(w0*factor), int(h0*factor)))
        self.patcher = Patcher(self.database[self.index]["fname"], self.database[self.index]["lname"])
        image = self.patcher.patch_label(classes)
        image = ImageTk.PhotoImage(resize(image, self.w*self.f, self.h))
        self.image_on = image
        self.display.create_image(self.w*self.f/2, self.h*0.5, image=image)


    def update_text(self):
        self.dir_name.config(text=os.path.basename(os.path.dirname(self.database[self.index]["fname"])))
        self.n_count.config(text="{} / {}".format(self.index+1, len(self.database)))
        self.fname.config(text=os.path.basename(self.database[self.index]["fname"]))
        if self.database[self.index]["lname"] is not None:
            self.lname.config(text=os.path.basename(self.database[self.index]["lname"]))
        else:
            self.lname.config(text="--------")


    def update_label_counts(self):
        self.database[self.index]["labels"] = self.patcher.get_labels()
        for i,class_i in enumerate(cfg.CLASSES):
            self.colorblock[i].config(text=str(len(self.database[self.index]["labels"][class_i])))


    def clear(self):
        self.dir_name.config(text="----")
        self.n_count.config(text="----")
        self.fname.config(text=".kfb/.tif")
        self.lname.config(text=".csv/.xml")
        self.image_on = None
        self.database = []
        for clb in self.colorblock:
            clb.config(text="-")


    def update(self, step=0):
        if self.index is None:
            messagebox.showinfo("error", "there is no file/label matched")
            self.clear()
            return
        if self.index+step not in range(len(self.database)):
            messagebox.showinfo("warning", "already the end")
            return
        self.index += step
        checked_classes = [cfg.CLASSES[i] for i,var in enumerate(self.checkboxes) if var.get()]
        self.load_thumbnail(checked_classes)
        self.update_text()
        self.update_label_counts()

    def load_images(self):
    	pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
