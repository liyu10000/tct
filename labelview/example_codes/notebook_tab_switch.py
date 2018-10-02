import tkinter as tk
from tkinter import ttk

class MyFrame(ttk.Frame):
    def __init__(self, master, name):
        ttk.Frame.__init__(self, master)
        self.name = name
        self.pack()

    def update(self):
        # Update the contents of the frame...
        print("Updating %s" % self.name)

class App():
    def __init__(self):
        root = tk.Tk()

        nb = ttk.Notebook(root)

        f1_name = "Tab1"
        f2_name = "Tab2"
        f1 = MyFrame(nb, f1_name)
        f2 = MyFrame(nb, f2_name)

        nb.add(f1, text=f1_name)
        nb.add(f2, text=f2_name)

        def tab_switch(event):
            if event.widget.identify(event.x, event.y) == "label":
                index = event.widget.index("@%d,%d" % (event.x, event.y))
                title = event.widget.tab(index, "text")

                if title == f1_name:
                    f1.update()
                elif title == f2_name:
                    f2.update()
                # and so on...

        nb.bind("<Button-1>", tab_switch)
        nb.pack(fill="both", expand=True)

        f1.update()  # Initial update of first displayed tab

        root.geometry("200x200")
        root.mainloop()

App()