import tkinter as tk
from PIL import ImageTk, Image

class OCRGui:
    def __init__(self):
        self.images = {}

        self.root = tk.Tk()
        self.root.title("OCR")
        self.w1 = 512  # image width
        self.w2 = 256  # panel width
        self.h = 512   # image height
        self.root.geometry("{}x{}".format(self.w1+self.w2, self.h))
        self.root.resizable(width=False, height=False)  # cannot change window size

        self.imageCanvas = tk.Canvas(self.root, width=self.w1, height=self.h)
        self.imageCanvas.grid(row=0, column=0)

        self.panelFrame = tk.Frame(self.root, width=self.w2, height=self.h)
        self.panelFrame.grid(row=0, column=1)

        #create a button widget for open file
        self.open_f = tk.Button(self.panelFrame, text="open file", command=self.on_click)
        self.open_f.grid(row=0, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=20)

        #create a button widget for open dir
        self.open_d = tk.Button(self.panelFrame, text="open dir", command=self.on_click)
        self.open_d.grid(row=0, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=20)

        #create a label widget for label prefix
        self.prefix = tk.Label(self.panelFrame, text="prefix:")
        self.prefix.grid(row=1, column=1, columnspan=1, sticky=tk.E, ipady=5, padx=5, pady=10)

        #create a text entry widget for label prefix text
        self.prefixText = tk.Entry(self.panelFrame)
        self.prefixText.grid(row=1, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=10)

        #create a label widget for label number
        self.number = tk.Label(self.panelFrame, text="number:")
        self.number.grid(row=2, column=1, columnspan=1, sticky=tk.E, ipady=5, padx=5, pady=10)

        #create a text entry widget for label number text
        self.numberText = tk.Entry(self.panelFrame)
        self.numberText.grid(row=2, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=10)

        #create a button widget for previous
        self.previous = tk.Button(self.panelFrame, text="previous", command=self.on_click)
        self.previous.grid(row=3, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=20)

        #create a button widget for save and next
        self.next = tk.Button(self.panelFrame, text="save and next", command=self.on_click)
        self.next.grid(row=3, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=5, pady=20)


    def load_image(self, image_name):
        image = ImageTk.PhotoImage(Image.open(image_name).resize((self.w1, self.h)))
        self.imageCanvas.create_image(self.w1//2, self.h//2, image=image)
        self.images[image_name] = image

    def on_click(self):
        print("button clicked")
        self.load_image("./label.jpg")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    OCRGui().run()