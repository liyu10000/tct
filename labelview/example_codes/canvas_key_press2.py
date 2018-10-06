from tkinter import *
from PIL import Image, ImageTk

root = Tk()

def callback(event=None):
    print("You Pressed at: ({}, {})".format(event.x, event.y))
    print(canvas.type(CURRENT))
    canvas.focus(CURRENT)

frame = Frame(root, width=500, height=500)
frame.pack(fill=BOTH, expand=YES)

canvas = Canvas(frame)
canvas.pack(fill=BOTH, expand=YES)
canvas.bind("<d>", callback)
canvas.focus_set()

img1__ = ImageTk.PhotoImage(Image.new("RGB", (100, 100)))
image1 = canvas.create_image(60, 60, image=img1__)

img2__ = ImageTk.PhotoImage(Image.new("RGB", (150, 100)))
image2 = canvas.create_image(200, 300, image=img2__)

root.mainloop()