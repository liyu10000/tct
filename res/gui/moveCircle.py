# use a Tkinter canvas to draw a circle, move it with the arrow keys

try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk


class MyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("move circle with arrow keys")
        # create a canvas to draw on
        self.cv = tk.Canvas(self, width=400, height=400, bg='white')
        self.cv.grid()
        # create a square box with upper left corner (x,y)
        self.x = 120
        self.y = 120
        size = 150
        box = (self.x, self.y, self.x + size, self.y + size)
        # create a circle that fits the box
        self.circle = self.cv.create_oval(box, fill='red')
        # bind arrow keys to movement
        self.bind('<Up>', self.move_up)
        self.bind('<Down>', self.move_down)
        self.bind('<Left>', self.move_left)
        self.bind('<Right>', self.move_right)

    def move_up(self, event):
        # move_increment is 5 pixels
        y = -5
        # move circle by increments x, y
        self.cv.move(self.circle, 0, y)

    def move_down(self, event):
        y = 5
        self.cv.move(self.circle, 0, y)

    def move_left(self, event):
        x = -5
        self.cv.move(self.circle, x, 0)

    def move_right(self, event):
        x = 5
        self.cv.move(self.circle, x, 0)


app = MyApp()
app.mainloop()