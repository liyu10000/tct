import os
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, IntVar
from PIL import ImageTk, Image

from Config import cfg
from Patcher import Patcher

class Viewer:
    def __init__(self):
        self.index = None
        self.thumb_on = None  # stores the thumbnail image on first tab
        self.thumbmini_on = None  # stores the mini thumbnail image on second tab
        self.images_on = None  # stores the labeled images on second tab
        self.database = []
        self.setup()

    def setup(self):
        self.root = tk.Tk()
        self.root.title("labelview")
        self.root.state("iconic")
        # self.root.resizable(width=False, height=False)  # cannot change window size
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        
        self.tabs = ttk.Notebook(self.root)

        # thumbnail tab
        self.i = 0.8  # the fraction of image region, horizontal
        self.f = 0.4  # the fraction of file control region, vertical
        self.c = 0.4  # the fraction of checkbox region, vertical

        self.thumb_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.thumb_tab, text="thumbnail")

        # left side control panel
        self.control = ttk.Panedwindow(self.thumb_tab, orient="vertical")
        self.control.grid(row=0, column=0)

        # file flow control
        self.flowctl = ttk.Labelframe(self.control, text="file flow control", width=self.w*(1-self.i), height=self.h*self.f)
        self.control.add(self.flowctl)


        # open single file
        self.open_f = ttk.Button(self.flowctl, text="open file", command=self.load_file)
        self.open_f.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # load single csv/xml corresponding to wsi file
        self.load_l = ttk.Button(self.flowctl, text="load csv/xml", command=self.load_labels)
        self.load_l.grid(row=0, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        # open directory
        self.open_d = ttk.Button(self.flowctl, text="open dir", command=self.load_files)
        self.open_d.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # set csv/xml directory
        self.load_ld = ttk.Button(self.flowctl, text="load csv/xml dir", command=self.load_labels_dir)
        self.load_ld.grid(row=1, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        # current directory name
        self.dir_name_ = ttk.Label(self.flowctl, text="dir:")
        self.dir_name_.grid(row=2, column=0, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)
        self.dir_name = ttk.Label(self.flowctl, text="----")
        self.dir_name.grid(row=2, column=1, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)
        # display file count
        self.n_count_ = ttk.Label(self.flowctl, text="count:")
        self.n_count_.grid(row=2, column=2, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)
        self.n_count = ttk.Label(self.flowctl, text="----")
        self.n_count.grid(row=2, column=3, columnspan=1, sticky="ew", ipady=5, padx=10, pady=10)

        # display fname
        self.fname = ttk.Label(self.flowctl, text="XXXX.kfb/.tif")
        self.fname.grid(row=3, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # display lname
        self.lname = ttk.Label(self.flowctl, text="XXXX.csv/.xml")
        self.lname.grid(row=3, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        # previous
        self.prev_b = ttk.Button(self.flowctl, text="previous", command=lambda: self.update(step=-1))
        self.prev_b.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # next
        self.next_b = ttk.Button(self.flowctl, text="next", command=lambda: self.update(step=1))
        self.next_b.grid(row=4, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        

        # checkbox control panel
        self.colorctl = ttk.Labelframe(self.control, text="choose classes", width=self.w*(1-self.i), height=self.h*self.c)
        self.control.add(self.colorctl)

        # add confirm button
        self.conform = ttk.Button(self.colorctl, text="confirm", command=lambda: self.update())
        self.conform.grid(row=0, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=5)
        # add checkboxes
        self.colorblock = []
        self.checkboxes = []
        for i, class_i in enumerate(cfg.CLASSES):
            var = IntVar(value=1)
            clb = ttk.Label(self.colorctl, text="--", background=cfg.COLOURS[class_i])
            chk = ttk.Checkbutton(self.colorctl, text=class_i, variable=var)
            if i < math.ceil(len(cfg.CLASSES)/2):
                clb.grid(row=1+i, column=0, columnspan=1, sticky="ew", ipady=1, padx=10, pady=2)
                chk.grid(row=1+i, column=1, columnspan=1, sticky="w", ipady=1, padx=10, pady=2)
            else:
                clb.grid(row=1+i-math.ceil(len(cfg.CLASSES)/2), column=2, columnspan=1, sticky="ew", ipady=1, padx=10, pady=2)
                chk.grid(row=1+i-math.ceil(len(cfg.CLASSES)/2), column=3, columnspan=1, sticky="w", ipady=1, padx=10, pady=2)
            self.colorblock.append(clb)
            self.checkboxes.append(var)
        
        
        # separator
        self.separator = ttk.Separator(self.thumb_tab, orient="vertical")
        self.separator.grid(row=0, column=1, sticky="ns")

        # right side image panel
        self.display = tk.Canvas(self.thumb_tab, width=self.w*self.i, height=self.h)
        self.display.grid(row=0, column=2)



        # labeled images tab
        self.w_left_i = 256  # the size of left size panel, horizontal
        self.f_i = 0.2  # the fraction of images flow control panel, vertical
        self.c_i = 0.4  # the fraction of checkbox control panel, vertical

        self.image_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.image_tab, text="label images")

        # left side control panel
        self.control_i = ttk.Panedwindow(self.image_tab, orient="vertical")
        self.control_i.grid(row=0, column=0)

        # images flow control
        self.flowctl_i = ttk.Labelframe(self.control_i, text="images flow control", width=self.w_left_i, height=self.h*self.f_i)
        self.control_i.add(self.flowctl_i)

        # previous
        self.prev_b_i = ttk.Button(self.flowctl_i, text="previous batch", command=lambda: self.update_i(step=-1))
        self.prev_b_i.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # next
        self.next_b_i = ttk.Button(self.flowctl_i, text="next batch", command=lambda: self.update_i(step=1))
        self.next_b_i.grid(row=0, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)


        # checkbox control
        self.colorctl_i = ttk.Labelframe(self.control_i, text="choose classes", width=self.w_left_i, height=self.h*self.c_i)
        self.control_i.add(self.colorctl_i)

        # confirm button
        self.confirm_i = ttk.Button(self.colorctl_i, text="confirm", command=lambda: self.update_i(step=0))
        self.confirm_i.grid(row=0, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # set display modes: the number of images in a row
        self.M_ = ttk.Label(self.colorctl_i, text="# number:")
        self.M_.grid(row=1, column=0, columnspan=1, sticky="ew", ipady=1, padx=10, pady=5)
        self.M = ttk.Entry(self.colorctl_i)
        self.M.insert(0, "3")
        self.M.config(width=10)
        self.M.grid(row=1, column=1, columnspan=1, sticky="e", ipady=1, padx=10, pady=5)
        # set image size: the times of image size over label box
        self.N_ = ttk.Label(self.colorctl_i, text="# image size:")
        self.N_.grid(row=1, column=2, columnspan=1, sticky="ew", ipady=1, padx=10, pady=5)
        self.N = ttk.Entry(self.colorctl_i)
        self.N.insert(0, "2")
        self.N.config(width=10)
        self.N.grid(row=1, column=3, columnspan=1, sticky="e", ipady=1, padx=10, pady=5)
        # add checkboxes
        self.colorblock_i = []
        self.checkboxes_i = []
        for i,class_i in enumerate(cfg.CLASSES):
            var = IntVar(value=0)
            clb = ttk.Label(self.colorctl_i, text="--", background=cfg.COLOURS[class_i])
            chk = ttk.Checkbutton(self.colorctl_i, text=class_i, variable=var)
            if i < math.ceil(len(cfg.CLASSES)/2):
                clb.grid(row=2+i, column=0, columnspan=1, sticky="ew", ipady=1, padx=10, pady=2)
                chk.grid(row=2+i, column=1, columnspan=1, sticky="w", ipady=1, padx=10, pady=2)
            else:
                clb.grid(row=2+i-math.ceil(len(cfg.CLASSES)/2), column=2, columnspan=1, sticky="ew", ipady=1, padx=10, pady=2)
                chk.grid(row=2+i-math.ceil(len(cfg.CLASSES)/2), column=3, columnspan=1, sticky="w", ipady=1, padx=10, pady=2)
            self.colorblock_i.append(clb)
            self.checkboxes_i.append(var)


        # thumbnail display for comparison purpose
        self.thumbmini = tk.Canvas(self.control_i, width=self.w_left_i, height=self.w_left_i)
        self.control_i.add(self.thumbmini)


        # separator
        self.separator_i = ttk.Separator(self.image_tab, orient="vertical")
        self.separator_i.grid(row=0, column=1, sticky="ns")

        # right side image panel
        self.display_i = tk.Canvas(self.image_tab, width=self.w-self.w_left_i, height=self.h)
        self.display_i.grid(row=0, column=2)

        self.tabs.pack()


    def load_file(self):
        fname = filedialog.askopenfilename(filetypes=(("*.kfb files", "*.kfb"), ("*.tif files", "*.tif")))
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
        image = ImageTk.PhotoImage(resize(image, self.w*self.i, self.h))
        self.thumb_on = image
        self.display.create_image(self.w*self.i/2, self.h*0.5, image=image)


    def update_text(self):
        self.dir_name.config(text=os.path.basename(os.path.dirname(self.database[self.index]["fname"])))
        self.n_count.config(text="{} / {}".format(self.index+1, len(self.database)))
        self.fname.config(text=os.path.basename(self.database[self.index]["fname"]))
        if self.database[self.index]["lname"] is not None:
            self.lname.config(text=os.path.basename(self.database[self.index]["lname"]))
        else:
            self.lname.config(text="--------")


    def update_label_counts(self):
        if not "labels" in self.database[self.index]:
            self.database[self.index]["labels"] = self.patcher.get_labels()
        for i,class_i in enumerate(cfg.CLASSES):
            self.colorblock[i].config(text=str(len(self.database[self.index]["labels"][class_i])))


    def clear(self):
        self.dir_name.config(text="----")
        self.n_count.config(text="----")
        self.fname.config(text=".kfb/.tif")
        self.lname.config(text=".csv/.xml")
        self.thumb_on = None
        self.database = []
        for clb in self.colorblock:
            clb.config(text="--")


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


    # below are functions relative to second tab
    def load_images(self):
        checked_classes = [cfg.CLASSES[i] for i,var in enumerate(self.checkboxes_i) if var.get()]
        sub_labels = {key:value for key,value in self.database[self.index]["labels"].items() if key in checked_classes}
        sub_images = self.patcher.crop_images(sub_labels, N=int(self.N.get()))
        self.image_list = [[class_i,box,image] for class_i,boxes in sub_images.items() for box,image in boxes.items()]
        self.cursor = 0

        M = int(self.M.get())  # number of images in a row
        self.size_avg = self.w * self.i / M  # average image size to display
        rows = int(self.h / self.size_avg)  # number of rows to display
        pad = (self.h-self.size_avg*rows)/(rows+1)
        self.anchors = []  # stores the center position of images to show
        for row in range(rows):
            for i in range(M):
                self.anchors.append((int(self.size_avg/2 + self.size_avg*i), int(self.size_avg/2 + self.size_avg*row + pad*(row+1))))


    def get_cursor_of_image(self, position):
        """ get current cursor, given position (event.x, event.y) """
        distance = {}
        cursor = self.cursor
        for anchor in self.anchors:
            if cursor not in range(len(self.image_list)):
                break
            distance[(position[0]-anchor[0])**2 + (position[1]-anchor[1])**2] = cursor
            cursor += 1
        sort_dist = sorted(distance.items())
        return sort_dist[0][1]

    def get_label_by_cursor(self, cursor_of_image):
        """ get label by the index in self.image_list.
            note: label may be changed, need to reimplement: get label from self.database[self.index]["labels"].
            Will maintain an updated labels map in self.database
        """
        return self.image_list[cursor_of_image][0]

    def on_single_click(self, event):
        def show(x, y, label):
            # destroy any toplevel window if exists
            destroy()

            # creates a toplevel window
            self.tw = tk.Toplevel(self.display_i)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            win = tk.Frame(self.tw, borderwidth=0)
            label = ttk.Label(win,
                              text=label,
                              justify=tk.LEFT,
                              relief=tk.SOLID,
                              borderwidth=0)
            pad = (5, 3, 5, 3)
            label.grid(padx=(pad[0], pad[2]),
                       pady=(pad[1], pad[3]),
                       sticky=tk.NSEW)
            win.grid()
            # set the position of label to show on screen
            x_of_c, y_of_c = self.display_i.winfo_rootx(), self.display_i.winfo_rooty()
            x, y = x + x_of_c + 5, y + y_of_c - 25
            self.tw.wm_geometry("+%d+%d" % (x, y))

        def destroy():
            if hasattr(self, "tw") and self.tw:
                self.tw.destroy()
            self.tw = None

        def wait_and_hide():
            waittime = 500  # in miniseconds
            self.display_i.after(waittime, destroy)

        # get mouse position, relative to canvas
        x_can, y_can = event.x, event.y
        # get the index of image in self.image_list
        cursor_of_image = self.get_cursor_of_image((x_can, y_can))
        # get the lable of the image
        label = self.get_label_by_cursor(cursor_of_image)
        # show label on screen
        show(x_can, y_can, label)
        # hide label after some time
        wait_and_hide()


    def on_double_click(self, event):
        x_can, y_can = event.x, event.y


    def on_right_click(self, event):
        def show_label_choose(x, y, label):
            # destroy existing toplevel window if exists
            destroy()
            # creates a toplevel window
            self.tw = tk.Toplevel(self.display_i)
            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            win = tk.Frame(self.tw, borderwidth=0)
            self.radioBox = IntVar(value=cfg.CLASSES.index(label))
            # delete choice
            tk.Radiobutton(win, text="DELETE", padx=5, variable=self.radioBox, 
                                command=choice_made, value=-1).pack(anchor=tk.W)
            # choices to be change label to
            for i,class_i in enumerate(cfg.CLASSES):
                tk.Radiobutton(win, text=class_i, padx=5, variable=self.radioBox,
                                    command=choice_made, value=i).pack(anchor=tk.W)
            win.grid()
            # set the position of label to show on screen
            x_of_c, y_of_c = self.display_i.winfo_rootx(), self.display_i.winfo_rooty()
            x, y = x + x_of_c + 5, y + y_of_c - 25
            self.tw.wm_geometry("+%d+%d" % (x, y))  

        def destroy():
            if hasattr(self, "tw") and self.tw:
                self.tw.destroy()
            self.tw = None

        def choice_made():
            choice = self.radioBox.get()
            if choice == -1:
                print("delete image and label")
            else:
                print("change label to {}".format(cfg.CLASSES[choice]))
            waittime = 300  # in miniseconds
            self.display_i.after(waittime, destroy)

        # get mouse position, relative to canvas
        x_can, y_can = event.x, event.y
        # get the index of image in self.image_list
        cursor_of_image = self.get_cursor_of_image((x_can, y_can))
        # get the lable of the image
        label = self.get_label_by_cursor(cursor_of_image)
        # show label choose dialog on screen
        show_label_choose(x_can, y_can, label)
        # destroy dialog if no action is performed
        # destroy()
                    

    def update_images(self, step):
        def resize(image, size):
            w, h = image.size
            f = min(1, min(size/w, size/h))
            return image.resize((int(w*f), int(h*f)))

        # update cursor
        self.cursor += step * len(self.anchors)
        if self.cursor not in range(len(self.image_list)):
            self.cursor -= step * len(self.anchors)
            messagebox.showinfo("warning", "no more images")
            return

        # update images
        del self.images_on
        self.images_on = []
        self.display_i.delete("all")  # delete all objects before loading
        cursor = self.cursor
        for anchor in self.anchors:
            if cursor not in range(len(self.image_list)):
                break
            image = ImageTk.PhotoImage(resize(self.image_list[cursor][2], self.size_avg))
            self.images_on.append(image)
            self.display_i.create_image(anchor[0], anchor[1], image=image, tags="image_{}".format(cursor))
            self.display_i.tag_bind("image_{}".format(cursor), "<ButtonPress-1>", self.on_single_click)
            self.display_i.tag_bind("image_{}".format(cursor), "<Double-Button-1>", self.on_double_click)
            self.display_i.tag_bind("image_{}".format(cursor), "<Button-3>", self.on_right_click)
            cursor += 1

    def load_thumbnailmini(self):
        def resize(image, w, h):
            w0, h0 = image.size
            factor = min(w/w0, h/w0)
            return image.resize((int(w0*factor), int(h0*factor)))

        sub_labels = {}
        for i in range(len(self.anchors)):
            cursor = self.cursor + i
            if cursor not in range(len(self.image_list)):
                break
            class_i = self.image_list[cursor][0]
            box = self.image_list[cursor][1]
            if class_i not in sub_labels:
                sub_labels[class_i] = {}
            sub_labels[class_i][box] = self.database[self.index]["labels"][class_i][box]
        
        image = self.patcher.patch_label_mini(sub_labels)
        image = ImageTk.PhotoImage(resize(image, self.w_left_i, self.w_left_i))
        self.thumbmini_on = image
        self.thumbmini.create_image(self.w_left_i/2, self.w_left_i/2, image=image)


    def update_label_counts_i(self):
        for i,class_i in enumerate(cfg.CLASSES):
            self.colorblock_i[i].config(text=str(len(self.database[self.index]["labels"][class_i])))


    def update_i(self, step):
        if step == 0:
            self.load_images()
        if hasattr(self, "cursor"):
            self.update_images(step=step)
            self.load_thumbnailmini()
        self.update_label_counts_i()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
