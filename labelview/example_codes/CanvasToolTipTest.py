import tkinter as tk
import tkinter.ttk as ttk
from random import choice

from CanvasToolTipNew import CanvasTooltip

class CanvasToolTipTest:
    def __init__(self):
        self.setup()

    def setup(self):
        self.root = tk.Tk()
        self.root.title("CanvasToolTipTest")
        self.w = 512  # image width
        self.h = 512   # image height
        self.root.geometry("{}x{}".format(self.w, self.h))
        self.root.resizable(width=False, height=False)  # cannot change window size

        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h)

        id_ = self.canvas.create_rectangle(50, 100, 200, 400,
                                            fill='green',
                                            tags='tag1')
        texts = ['23', 'gewgwg', '2rg']

        CanvasTooltip(self.canvas, 'tag1', text=choice(texts))
        self.canvas.pack()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    test = CanvasToolTipTest()
    test.run()