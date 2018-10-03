from tkinter import *

class ResizeWindow:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("800x600")
        self.myframe = Frame(self.root)
        self.myframe.pack(fill=BOTH, expand=YES)
        
        self.mycanvas = Canvas(self.myframe, bg="red", highlightthickness=0, width=800, height=500)
        self.mycanvas.pack()
        self.mybutton = Button(self.myframe, text="decrease", command=self.decrease)
        self.mybutton.pack(side=LEFT)
        self.mybutton = Button(self.myframe, text="increase", command=self.increase)
        self.mybutton.pack(side=RIGHT)
        
        # tag all of the drawn widgets
        self.mycanvas.addtag_all("all")

    def decrease(self):
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        print(win_w, win_h)
        win_w_new = int(win_w/2)
        win_h_new = int(win_h/2)
        self.root.geometry("{}x{}".format(win_w_new, win_h_new))
        self.mycanvas.config(width=win_w_new, height=win_h_new-50)
        self.mycanvas.delete("all")
        self.mycanvas.create_rectangle(10, 10, win_w_new-10, win_h_new-60, fill="blue")

    def increase(self):
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        print(win_w, win_h)
        win_w_new = int(win_w*2)
        win_h_new = int(win_h*2)
        self.root.geometry("{}x{}".format(win_w_new, win_h_new))
        self.mycanvas.config(width=win_w_new, height=win_h_new-50)
        self.mycanvas.delete("all")
        self.mycanvas.create_rectangle(10, 10, win_w_new-10, win_h_new-60, fill="blue")

    def run(self):
        self.root.mainloop()



if __name__ == "__main__":
    ResizeWindow().run()