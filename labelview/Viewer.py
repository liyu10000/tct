import os
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, IntVar, StringVar
from PIL import ImageTk, Image

from Config import cfg
from Patcher import Patcher
from Logger import Logger


class Viewer:
    def __init__(self):
        self.index = None
        self.database = []
        self.setup()

    def setup(self):
        self.root = tk.Tk()
        self.root.title("labelview")
        self.root.state("iconic")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # self.root.resizable(width=False, height=False)  # cannot change window size
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        
        # configure ttk style
        s = ttk.Style()
        s.configure("File.TButton", foreground="blue")
        s.configure("Flow.TButton", foreground="red")
        s.configure("Save.TButton", foreground="blue")

        self.tabs = ttk.Notebook(self.root)

        # thumbnail tab
        self.i = 0.8  # the fraction of image region, horizontal
        self.f = 0.4  # the fraction of file control region, vertical
        self.c = 0.4  # the fraction of checkbox region, vertical

        self.thumb_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.thumb_tab, text="  thumbnail  ")

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
        self.open_d = ttk.Button(self.flowctl, text="open dir", style="File.TButton", command=self.load_files)
        self.open_d.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # set csv/xml directory
        self.load_ld = ttk.Button(self.flowctl, text="load csv/xml dir", style="File.TButton", command=self.load_labels_dir)
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
        self.prev_b = ttk.Button(self.flowctl, text="previous", style="Flow.TButton", command=lambda: self.update(step=-1))
        self.prev_b.grid(row=4, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # next
        self.next_b = ttk.Button(self.flowctl, text="next", style="Flow.TButton", command=lambda: self.update(step=1))
        self.next_b.grid(row=4, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)

        

        # checkbox control panel
        self.colorctl = ttk.Labelframe(self.control, text="choose classes", width=self.w*(1-self.i), height=self.h*self.c)
        self.control.add(self.colorctl)

        # add blur thumbnail image button
        self.blur = ttk.Button(self.colorctl, text="blur", command=lambda: self.update(blur=True))
        self.blur.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=5)
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
        self.s_i = 0.2  # the fraction of file info display and label file save control, vertical
        self.i_i = 0.2  # the fraction of images flow control panel, vertical
        self.c_i = 0.4  # the fraction of checkbox control panel, vertical

        self.image_tab = ttk.Frame(self.tabs)
        self.image_tab.bind("<Visibility>", self.on_visibility)  # clean and update contents when switch to this tab
        self.tabs.add(self.image_tab, text=" label images ")

        # left side control panel
        self.control_i = ttk.Panedwindow(self.image_tab, orient="vertical")
        self.control_i.grid(row=0, column=0)


        # file info display and label file save control
        self.savectl_i = ttk.Labelframe(self.control_i, text="label file write control", width=self.w_left_i, height=self.h*self.s_i)
        self.control_i.add(self.savectl_i)

        # set label file save dir
        self.label_dir = ttk.Button(self.savectl_i, text="set label file save dir", command=self.set_save_dir)
        self.label_dir.grid(row=0, column=0, columnspan=4, sticky="ew", ipady=5, padx=10, pady=10)
        # display file progress
        self.n_count_i = ttk.Label(self.savectl_i, text="file progress")
        self.n_count_i.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # save changes
        self.save_changes = ttk.Button(self.savectl_i, text="save changes", style="Save.TButton", command=self.save_labels)
        self.save_changes.grid(row=1, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)


        # images flow control
        self.flowctl_i = ttk.Labelframe(self.control_i, text="images flow control", width=self.w_left_i, height=self.h*self.i_i)
        self.control_i.add(self.flowctl_i)

        # previous
        self.prev_b_i = ttk.Button(self.flowctl_i, text="previous batch", style="Flow.TButton", command=lambda: self.update_i(step=-1))
        self.prev_b_i.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # next
        self.next_b_i = ttk.Button(self.flowctl_i, text="next batch", style="Flow.TButton", command=lambda: self.update_i(step=1))
        self.next_b_i.grid(row=0, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)


        # checkbox control
        self.colorctl_i = ttk.Labelframe(self.control_i, text="choose classes", width=self.w_left_i, height=self.h*self.c_i)
        self.control_i.add(self.colorctl_i)

        # images view progress
        self.image_pro = ttk.Label(self.colorctl_i, text="images view progress")
        self.image_pro.grid(row=0, column=0, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # confirm button
        self.confirm_i = ttk.Button(self.colorctl_i, text="confirm", command=lambda: self.update_i(step=0))
        self.confirm_i.grid(row=0, column=2, columnspan=2, sticky="ew", ipady=5, padx=10, pady=10)
        # set display modes: the number of images in a row
        self.M_ = ttk.Label(self.colorctl_i, text="# M:")
        self.M_.grid(row=1, column=0, columnspan=1, sticky="ew", ipady=1, padx=10, pady=5)
        self.M = ttk.Entry(self.colorctl_i)
        self.M.insert(0, "3")
        self.M.config(width=10)
        self.M.grid(row=1, column=1, columnspan=1, sticky="e", ipady=1, padx=10, pady=5)
        # set image size: the times of image size over label box
        self.N_ = ttk.Label(self.colorctl_i, text="# N:")
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
            clb = ttk.Label(self.colorctl_i, text="--", background='#ffffff')
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
        # self.display_i.bind("<d>", self.on_d_pressed)
        # self.display_i.focus_set()
        self.display_i.grid(row=0, column=2)


        # third tab: logging
        self.log_tab = ttk.Frame(self.tabs)
        self.logger = Logger(self.log_tab)
        self.tabs.add(self.log_tab, text="     log     ", padding=5)

        self.tabs.pack()


    def load_file(self):
        """ open wsi file dialog """
        fname = filedialog.askopenfilename(filetypes=(("*.kfb files", "*.kfb"), ("*.tif files", "*.tif")))
        if not fname:
            messagebox.showinfo("warning", "no file choosed")
        else:
            self.index = 0
            del self.database
            self.database = []
            self.database.append({"basename":os.path.splitext(os.path.basename(fname))[0], "fname":fname, "lname":None})
            self.update()
            self.logger.log_file("loaded file " + fname)


    def load_files(self):
        """ open wsi file directory dialog """
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
                self.update()
                self.logger.log_file("loaded files from " + file_dir)


    def load_labels(self):
        """ open label file dialog """
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
            self.logger.set_log_path(os.path.dirname(lname))
            self.logger.log_info("loaded label file " + lname)


    def load_labels_dir(self):
        """ open label file directory dialog """
        def nullify_lname():
            """ set lable name to None before loading new """
            for item in self.database:
                item["lname"] = None
        def choose_matched():
            """ choose only those wsi file name matches label file """
            database_new = [item for item in self.database if item["lname"] is not None]
            del self.database
            self.database = database_new

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
            self.index = 0 if self.database else None
            self.update()
            self.logger.set_log_path(file_dir)
            self.logger.log_info("loaded label files from " + file_dir)


    def update_patcher(self):
        """ initialize and update patcher """
        def need_reget_label():
            """ check if need to get label from patcher """
            # check if haven't got labels from patcher
            if not "labels" in self.database[self.index]:
                return True
            # check if have got labels from patcher, but with None label file
            # note: there is a case that this will lead to excess label getting,
            # that is, patcher.labels contains no labels.
            count = 0
            for class_i,boxes in self.database[self.index]["labels"].items():
                count += len(boxes)
            return count == 0

        # in case when patcher initialized without label file, need to reinitialize
        if need_reget_label():
            self.patcher = Patcher(self.database[self.index]["fname"], self.database[self.index]["lname"])
            self.database[self.index]["labels"] = self.patcher.get_labels()


    def load_thumbnail(self, blur):
        """ load thumbnail image, given selected classes """
        def resize(image, w, h):
            w0, h0 = image.size
            scale = min(w/w0, h/w0)
            return image.resize((int(w0*scale), int(h0*scale)))
        
        checked_classes = [cfg.CLASSES[i] for i,var in enumerate(self.checkboxes) if var.get()]
        image = self.patcher.patch_label({key:value for key,value in self.database[self.index]["labels"].items() if key in checked_classes}, blur)
        image = ImageTk.PhotoImage(resize(image, self.w*self.i, self.h))
        self.thumb_on = image  # stores the thumbnail image on first tab
        self.display.create_image(self.w*self.i/2, self.h/2, image=image)


    def update_text(self):
        """ tab1: update display text """
        self.dir_name.config(text=os.path.basename(os.path.dirname(self.database[self.index]["fname"])))
        self.n_count.config(text="{} / {}".format(self.index+1, len(self.database)))
        self.fname.config(text=os.path.basename(self.database[self.index]["fname"]))
        if self.database[self.index]["lname"] is not None:
            self.lname.config(text=os.path.basename(self.database[self.index]["lname"]))
        else:
            self.lname.config(text="--------")


    def update_label_counts(self):
        """ tab1: update label counts """
        for i,class_i in enumerate(cfg.CLASSES):
            self.colorblock[i].config(text=str(len(self.database[self.index]["labels"][class_i])))


    def clear(self):
        """ clear and update window when failed to load matching label files """
        self.dir_name.config(text="----")
        self.n_count.config(text="----")
        self.fname.config(text="----.kfb/.tif")
        self.lname.config(text="----.csv/.xml")
        self.thumb_on = None
        self.database = []
        for clb in self.colorblock:
            clb.config(text="--")


    def update(self, step=0, blur=False):
        """ update method of first tab """
        if self.index is None:
            messagebox.showinfo("error", "there is no file/label matched")
            self.clear()
            return
        if self.index+step not in range(len(self.database)):
            messagebox.showinfo("warning", "already the end")
            return
        self.index += step
        self.update_patcher()
        self.load_thumbnail(blur)
        self.update_text()
        self.update_label_counts()


    # below are functions relative to second tab
    def set_save_dir(self):
        """ set new label file saving directory, use source label file dir if not set """
        if self.index is None:
            messagebox.showinfo("error", "there is no file/label matched")
            return
        self.save_dir = filedialog.askdirectory()
        if not self.save_dir:
            messagebox.showinfo("warning", "no directory choosed, will use default")
        else:
            self.logger.log_info("set label file saving directory " + self.save_dir)


    def load_images(self):
        # update color
        self.update_color_i(finished=False)
        # get checked classes
        checked_classes = [cfg.CLASSES[i] for i,var in enumerate(self.checkboxes_i) if var.get()]
        # get images from patcher
        sub_labels = {key:value for key,value in self.database[self.index]["labels"].items() if key in checked_classes}
        self.image_list = self.patcher.crop_images(sub_labels, N=float(self.N.get()))
        self.cursor = 0  # stores the index of first image on canvas of second tab
        self.images_on = None  # stores the labeled images on second tab
        self.logger.log_info("selected classes: {}".format(checked_classes))

        # calculate anchor points for images
        M = int(self.M.get())  # number of images in a row
        self.size_avg = self.w * self.i / M  # average image size to display
        rows = int(self.h / self.size_avg)  # number of rows to display
        pad = (self.h-self.size_avg*rows)/(rows+1)
        self.anchors = []  # stores the center position of images to show
        for row in range(rows):
            for i in range(M):
                self.anchors.append((int(self.size_avg/2 + self.size_avg*i), int(self.size_avg/2 + self.size_avg*row + pad*(row+1))))


    def get_cursor_of_image(self, position):
        """ get current index of image in image_list, given position (event.x, event.y) """
        distance = {}
        cursor = self.cursor
        for anchor in self.anchors:
            if cursor not in range(len(self.image_list)):
                break
            distance[(position[0]-anchor[0])**2 + (position[1]-anchor[1])**2] = cursor
            cursor += 1
        sort_dist = sorted(distance.items())
        return sort_dist[0][1] if sort_dist else -1  # bug in canvas: still able to click when there are no images


    def get_label_by_cursor(self, cursor_of_image):
        """ 1. get key box from image_list, by index
            2. get label from labels, by key box
        """
        box = self.image_list[cursor_of_image][1]
        # search self.database[self.index]["labels"] for class_i
        for class_i,boxes in self.database[self.index]["labels"].items():
            if box in boxes:
                return class_i
        return "DELETED!!!"


    def on_single_click(self, event):
        """ on single click, display label of current image """
        def show_label():
            # destroy any toplevel window
            destroy()
            # creates a toplevel window
            self.tw = tk.Toplevel(self.display_i)
            # Leaves only the frame and removes the app window
            self.tw.wm_overrideredirect(True)
            win = tk.Frame(self.tw, borderwidth=0)
            lbl = ttk.Label(win, text=label, justify=tk.LEFT,
                            relief=tk.SOLID, borderwidth=0)
            pad = (5, 3, 5, 3)
            lbl.grid(padx=(pad[0], pad[2]), pady=(pad[1], pad[3]), sticky=tk.NSEW)
            win.grid()
            # set the position of label to show on screen
            x_of_c, y_of_c = self.display_i.winfo_rootx(), self.display_i.winfo_rooty()
            x, y = x_can + x_of_c + 5, y_can + y_of_c - 25  # x_can,y_can are defined outside
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
        if cursor_of_image == -1:
            return
        # get the lable of the image
        label = self.get_label_by_cursor(cursor_of_image)
        # show label on screen
        show_label()
        # hide label after some time
        wait_and_hide()


    def on_double_click(self, event):
        """ on double click, popup a new image window, being able change image cropping size """
        def show_image():
            # destroy existing toplevel window
            destroy()
            # create a toplevel window and configure window size
            self.tw_i = tk.Toplevel(self.display_i)
            w, h = self.image_list[cursor_of_image][2].size
            scale = min(1.0, min(self.w/w, self.h/h))
            w, h = int(w*scale), int(h*scale)
            self.tw_i.wm_geometry("{}x{}".format(w, h))
            self.tw_i_x = float(self.N.get())  # stores the times of image dimension over cell dimension
            self.tw_i.title(label+" {}x".format(self.tw_i_x))
            # add decrease and increase menu 
            menubar = tk.Menu(self.tw_i)
            sizemenu = tk.Menu(menubar, tearoff=0)
            sizemenu.add_command(label="decrease", command=lambda: resize(delta=-1))
            sizemenu.add_separator()
            sizemenu.add_command(label="increase", command=lambda: resize(delta=1))
            menubar.add_cascade(label="change size", menu=sizemenu)
            self.tw_i.config(menu=menubar)
            # add image to canvas
            self.tw_i_can = tk.Canvas(self.tw_i)
            self.tw_i_can.pack(fill=tk.BOTH, expand=tk.YES)
            self.image_tw = ImageTk.PhotoImage(self.image_list[cursor_of_image][2].resize((w, h)))
            self.tw_i_can.create_image(w//2, h//2, image=self.image_tw)

        def resize(delta):
            self.tw_i_x += delta
            if self.tw_i_x < 1.0:
                # already down to the cell, cannot cut smaller
                self.tw_i_x -= delta
                return
            image = self.patcher.get_cell_by_N(box=self.image_list[cursor_of_image][1], N=self.tw_i_x)
            w, h = image.size
            scale = min(1.0, min(self.w/w, self.h/h))
            w, h = int(w*scale), int(h*scale)
            self.tw_i.title(label+" {}x".format(self.tw_i_x))
            self.tw_i.wm_geometry("{}x{}".format(w, h))
            self.image_tw = ImageTk.PhotoImage(image.resize((w, h)))
            self.tw_i_can.delete("all")
            self.tw_i_can.config(width=w, height=h)
            self.tw_i_can.create_image(w//2, h//2, image=self.image_tw)

        def destroy():
            if hasattr(self, "tw_i") and self.tw_i:
                self.tw_i.destroy()
            self.tw_i = None

        # get mouse position, relative to canvas
        x_can, y_can = event.x, event.y
        # get the index of image in self.image_list
        cursor_of_image = self.get_cursor_of_image((x_can, y_can))
        if cursor_of_image == -1:
            return
        # get the lable of the image
        label = self.get_label_by_cursor(cursor_of_image)
        # display image
        show_image()


    def on_right_click(self, event):
        """ on double click, popup radiobox selection panel, for label change or delete """
        def show_choices():
            # destroy existing toplevel window
            destroy()
            # creates a toplevel window
            self.tw = tk.Toplevel(self.display_i)
            # Leaves only the frame and removes the app window
            self.tw.wm_overrideredirect(True)
            win = tk.Frame(self.tw, borderwidth=0)
            self.radioBox = StringVar(value=label)
            # delete choice
            tk.Radiobutton(win, text="DELETE", padx=5, variable=self.radioBox, 
                                command=choice_made, 
                                value="DELETE", fg="#ff0000", activeforeground="#ff0000").pack(anchor=tk.W)
            # choices to be change label to
            for class_i in cfg.CLASSES:
                tk.Radiobutton(win, text=class_i, padx=5, variable=self.radioBox,
                                    command=choice_made, 
                                    value=class_i).pack(anchor=tk.W)
            win.grid()
            # set the position of label to show on screen
            # first get the position of canvas (upleft) on screen
            x_of_c, y_of_c = self.display_i.winfo_rootx(), self.display_i.winfo_rooty()
            # then add the position of mouse on canvas 
            x, y = x_can + x_of_c + 5, y_can + y_of_c - 150
            # adjust x,y if tw falls out of window
            x = min(x, self.w-100)
            y = min(y, self.h-400)
            y = max(y, 10)
            self.tw.wm_geometry("+%d+%d" % (x, y))  

        def destroy():
            if hasattr(self, "tw") and self.tw:
                self.tw.destroy()
            self.tw = None

        def choice_made():
            waittime = 300  # in miniseconds
            self.display_i.after(waittime, destroy)

            # retrieve choice and make changes accordingly
            choice = self.radioBox.get()
            # detect if there are changes made
            if choice == label or (label == "DELETED!!!" and choice == "DELETE"):
                return
            box = self.image_list[cursor_of_image][1]           
            # change original label to choice
            if choice != "DELETE":
                self.database[self.index]["labels"][choice][box] = self.database[self.index]["labels"][label][box]
                outline_color = "blue"
                self.image_list[cursor_of_image][0] = choice  # update class_i in image_list
                self.logger.log_change("{} {}".format(box,label), "{}".format(choice))
            else:  # when choice == "DELETE"
                if "DELETED!!!" not in self.database[self.index]["labels"]:  # add new key to labels
                    self.database[self.index]["labels"]["DELETED!!!"] = {}
                self.database[self.index]["labels"]["DELETED!!!"][box] = self.database[self.index]["labels"][label][box]
                outline_color = "red"
                self.image_list[cursor_of_image][0] = "DELETED!!!"  # update class_i in image_list, note: new key here
                self.logger.log_delete("{} {}".format(box,label))
            # delete label
            del self.database[self.index]["labels"][label][box]
            # update label counts
            self.update_label_counts_i()
            # add surrounding rectangle to changed image on canvas
            self.image_list[cursor_of_image].append(outline_color)
            anchor = self.anchors[cursor_of_image - self.cursor]
            x0, y0 = anchor[0] - self.size_avg/2 + 1, anchor[1] - self.size_avg/2 + 1
            x1, y1 = anchor[0] + self.size_avg/2 - 1, anchor[1] + self.size_avg/2 - 1
            self.display_i.create_rectangle(x0, y0, x1, y1, outline=outline_color, width=2)
                
        # get mouse position, relative to canvas
        x_can, y_can = event.x, event.y
        # get the index of image in self.image_list
        cursor_of_image = self.get_cursor_of_image((x_can, y_can))
        if cursor_of_image == -1:
            return
        # get the lable of the image
        label = self.get_label_by_cursor(cursor_of_image)
        # # check if label has been deleted
        # if label == "DELETED!!!":
        #     messagebox.showinfo("warning", "image has been deleted")
        # show label choose dialog on screen
        show_choices()
    

    """ key press doesn't work after loading images
    def on_d_pressed(self, event):
        print("d pressed at {}, ({},{})".format(self.display_i.type(tk.CURRENT), event.x, event.y))
        if self.display_i.type(tk.CURRENT) != "image":
            return
        # get mouse position, relative to canvas
        x_can, y_can = event.x, event.y
        # get the index of image in self.image_list
        cursor_of_image = self.get_cursor_of_image((x_can, y_can))
        # get the label of the image
        label = self.get_label_by_cursor(cursor_of_image)
        if label == "DELETED!!!":
            return
        # delete label
        box = self.image_list[cursor_of_image][1] 
        if "DELETED!!!" not in self.database[self.index]["labels"]:
            self.database[self.index]["labels"]["DELETED!!!"] = {}
        self.database[self.index]["labels"]["DELETED!!!"][box] = self.database[self.index]["labels"][label][box]
        outline_color = "red"
        self.image_list[cursor_of_image][0] = "DELETED!!!"  # update class_i in image_list, note: new key here
        self.logger.log_delete("{} {}".format(box,label))
        del self.database[self.index]["labels"][label][box]
        # update label counts
        self.update_label_counts_i()
        # add surrounding rectangle to changed image on canvas
        self.image_list[cursor_of_image].append(outline_color)
        anchor = self.anchors[cursor_of_image - self.cursor]
        x0, y0 = anchor[0] - self.size_avg/2 + 1, anchor[1] - self.size_avg/2 + 1
        x1, y1 = anchor[0] + self.size_avg/2 - 1, anchor[1] + self.size_avg/2 - 1
        self.display_i.create_rectangle(x0, y0, x1, y1, outline=outline_color, width=2)
    """


    def update_images(self, step):
        """ update display images on canvas """
        def resize(image, size):
            w, h = image.size
            scale = min(1, min(size/w, size/h))
            return image.resize((int(w*scale), int(h*scale)))

        # update color, when last batch of images are displayed
        if self.cursor + 2*len(self.anchors) >= len(self.image_list):
            self.update_color_i(finished=True)

        # update cursor, stay unchanged if running to the end
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
            # add bounding rectangle for changed images, on canvas
            if len(self.image_list[cursor]) > 3:
                outline_color = self.image_list[cursor][-1]  # get the last color, should i only store one instead?
                x0, y0 = anchor[0] - self.size_avg/2 + 1, anchor[1] - self.size_avg/2 + 1
                x1, y1 = anchor[0] + self.size_avg/2 - 1, anchor[1] + self.size_avg/2 - 1
                self.display_i.create_rectangle(x0, y0, x1, y1, outline=outline_color, width=2)                
            cursor += 1


    def load_thumbnailmini(self):
        """ load mini thumbnail image, in bottom left corner """
        def resize(image, w, h):
            w0, h0 = image.size
            scale = min(w/w0, h/w0)
            return image.resize((int(w0*scale), int(h0*scale)))

        sub_labels = {}
        for i in range(len(self.anchors)):
            cursor = self.cursor + i
            if cursor not in range(len(self.image_list)):
                break
            class_i = self.image_list[cursor][0]
            if class_i == "DELETED!!!":  # omit deleted labels
                continue
            box = self.image_list[cursor][1]
            if class_i not in sub_labels:
                sub_labels[class_i] = {}
            sub_labels[class_i][box] = self.database[self.index]["labels"][class_i][box]
        
        image = self.patcher.patch_label(sub_labels, blur=True)
        image = ImageTk.PhotoImage(resize(image, self.w_left_i, self.w_left_i))
        self.thumbmini_on = image  # stores the mini thumbnail image on second tab
        self.thumbmini.create_image(self.w_left_i/2, self.w_left_i/2, image=image)


    def update_label_counts_i(self, clear=False):
        """ update label counts in second tab """
        if clear:
            for clb in self.colorblock_i:
                clb.config(text="--")
        else:
            for i,clb in enumerate(self.colorblock_i):
                clb.config(text=str(len(self.database[self.index]["labels"][cfg.CLASSES[i]])))
            # for i,class_i in enumerate(cfg.CLASSES):
            #     self.colorblock_i[i].config(text=str(len(self.database[self.index]["labels"][class_i])))

    def update_text_i(self, clear=False):
        """ update 1. file view progress and 2. image view progress """
        if clear:
            self.n_count_i.config(text="no progress")
        else:
            self.n_count_i.config(text="files: {} / {}".format(self.index+1, len(self.database)))
        if hasattr(self, "cursor"):
            self.image_pro.config(text="images in view: {} / {}".format(self.cursor+1, len(self.image_list)))
        else:
            self.image_pro.config(text="no progress")

    def update_color_i(self, finished=False, clear=False):
        """ change colorbox color
        :param finished: the status of viewing images. Change color to shallow yellow if started viewing, green if finished.
        :param clear: the command to reset color to white, at tab changes
        """
        if clear:
            for clb in self.colorblock_i:
                clb.configure(background="#ffffff")
            return
        color = "#00ff00" if finished else "#ffff99"
        checked_classes = [i for i,var in enumerate(self.checkboxes_i) if var.get()]
        for i,clb in enumerate(self.colorblock_i):
            if i in checked_classes:
                clb.configure(background=color)


    def update_i(self, step):
        """ update method for second tab """
        if self.index is None:
            messagebox.showinfo("error", "there is no file/label matched")
            return
        if step == 0:
            self.load_images()
        if hasattr(self, "cursor"):
            self.update_images(step=step)
            self.load_thumbnailmini()
        self.update_text_i()
        self.update_label_counts_i()


    def save_labels(self, index=None):
        """ upload labels changes to patcher """
        if hasattr(self, "patcher"):
            if index is None:
                if self.index is None:
                    return
                else:
                    index = self.index
            if index not in range(len(self.database)):  # happens when failed to load new label files
                return
            self.patcher.set_labels(self.database[index]["labels"])
            if self.database[index]["lname"] is None:  # happens when no label file is loaded
                return
            # use the same directory if new label file dir is not set
            if not hasattr(self, "save_dir") or not self.save_dir:
                self.save_dir = os.path.dirname(self.database[index]["lname"])
            label_file = os.path.join(self.save_dir, self.database[index]["basename"]+".xml")
            self.patcher.write_labels(label_file)
            self.logger.log_save(self.database[index]["basename"])


    def on_visibility(self, event):
        """ clear up and update second tab upon tab switch, when self.index changed in first tab """
        if not hasattr(self, "old_index"):
            self.old_index = None
            self.save_dir = None
        if self.old_index != self.index:
            self.thumbmini.delete("all")  # delete thumbnail image
            self.display_i.delete("all")  # delete all images on canvas
            self.update_color_i(clear=True)  # reset background color in colorboxes
            if self.old_index is not None:  # save labels to label file
                self.save_labels(self.old_index)
            if self.index is None:  # happens when failed to load new label files
                self.update_text_i(clear=True)
                self.update_label_counts_i(clear=True)  # clear label counts on second tab
            else:
                self.update_text_i()
                self.update_label_counts_i()  # update label counts on second tab
                self.logger.log_open(self.database[self.index]["basename"])
            self.old_index = self.index


    def on_close(self):
        """ actions performed when window closed """
        self.save_labels(self.index)
        self.logger.on_close()
        del self.database
        self.root.destroy()


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
