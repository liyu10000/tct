import tkinter
from PIL import ImageTk, Image


class GUI:
    def __init__(self, file):
        self.root = tkinter.Tk()
        self.root.title("Tsimage")
        self.root.state('zoomed')  # full screen

        # self.root.iconify()  #change screen according to elemnts inside
        # put widgets here
        # self.root.deiconify()
        # self.root.resizable(width=False, height=False)  # cannot change window size

        self.root.update()
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()

        self.panelFrame = tkinter.Frame(self.root, background="purple", width=self.width*0.2, height=self.height)
        self.panelFrame.grid(row=0, column=0)
        self.panelFrame.pack_propagate(False)
        # self.panelFrame.pack(side=tkinter.LEFT)

        self.imageCanvas = tkinter.Canvas(self.root, width=self.width*0.8, height=self.height)
        self.imageCanvas.grid(row=0, column=1)
        self.imageCanvas.pack_propagate(False)

        self.coords = {"imageX": self.width * 0.4, "imageY": self.height * 0.5, "cursorX": -1, "cursorY": -1}

        self.file = file
        self.img_pre = ImageTk.PhotoImage(file=self.file)
        self.image = self.imageCanvas.create_image(self.coords["imageX"], self.coords["imageY"], image=self.img_pre)

        # display cursor position (relative to imageCanvas), on bottom of panelFrame
        self.imageCanvas.bind("<Motion>", self.cursor_position)
        self.cursor_display = tkinter.Label(self.panelFrame, background="purple", text="cursor: x = -1, y = -1")
        self.cursor_display.pack(side=tkinter.BOTTOM)

        # display image (center) position (relative to imageCanvas), on top of panelFrame
        # self.imageCanvas.bind("<Button>", self.image_position)
        # self.image_display = tkinter.Label(self.panelFrame, background="purple", text="image: x = -1, y = -1")
        # self.image_display.pack(side=tkinter.BOTTOM)

        self.imageCanvas.bind("<ButtonPress-1>", self.onPressToMove)
        self.imageCanvas.bind("<ButtonRelease-1>", self.onReleaseToMove)
        self.imageCanvas.bind("<B1-Motion>", self.onMovement)

        # move image with arrow keys
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)

        # self.imageFrame = tkinter.Frame(self.root, width=self.width*0.8, height=self.height)
        # self.imageFrame.grid(row=0, column=1)
        # self.imageFrame.pack_propagate(False)
        # # self.imageFrame.pack(side=tkinter.RIGHT)
        #
        # self.open = tkinter.Button(self.panelFrame, text="open")
        # self.open.pack()
        #
        # self.cursor = tkinter.Label(self.panelFrame, background="purple", text="x = -1, y = -1")
        # self.cursor.pack(side=tkinter.BOTTOM)
        #
        #
        # # load tif image
        # self.file = file
        # self.img = ImageTk.PhotoImage(Image.open(self.file))
        # self.image = tkinter.Label(self.imageFrame, image=self.img)
        # self.image.bind('<Motion>', self.cursor_position)
        # self.image.pack()

    def start(self):
        self.root.mainloop()

    def cursor_position(self, event):
        x, y = event.x, event.y
        self.cursor_display.configure(text="cursor: x = " + str(x) + ", y = " + str(y))

    # def image_position(self, event):
    #     # x = self.imageCanvas.canvasx(0)
    #     # y = self.imageCanvas.canvasy(0)
    #     # self.image_display.configure(text="image: x = " + str(x) + ", y = " + str(y))
    #     (x, y) = self.imageCanvas.coords(self.image)
    #     self.image_display.configure(text="image: x = " + str(x) + ", y = " + str(y))

    def move_up(self, event):
        y = -5
        self.imageCanvas.move(self.image, 0, y)

    def move_down(self, event):
        y = 5
        self.imageCanvas.move(self.image, 0, y)

    def move_left(self, event):
        x = -5
        self.imageCanvas.move(self.image, x, 0)

    def move_right(self, event):
        x = 5
        self.imageCanvas.move(self.image, x, 0)

    def onPressToMove(self, event):
        self.coords["cursorX"] = event.x
        self.coords["cursorY"] = event.y

    def onReleaseToMove(self, event):
        self.coords["cursorX"] = 0
        self.coords["cursorY"] = 0
        (self.coords["imageX"], self.coords["imageY"]) = self.imageCanvas.coords(self.image)

    def onMovement(self, event):
        deltaX = event.x - self.coords["cursorX"]
        deltaY = event.y - self.coords["cursorY"]
        self.imageCanvas.move(self.image, deltaX, deltaY)


if __name__ == '__main__':
    app = GUI("C:\\liyu\\files\\tiff\\large5.tif")
    app.start()