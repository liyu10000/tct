import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image

from Config import *
from Patcher import Patcher

class Viewer:
	def __init__(self):
		self.database = {}
		self.setup()
		self.load_thumbnail(classes)

	def setup(self):
		self.root = tk.Tk()
		self.root.title("labelview")
		self.root.state("zoomed")
		self.w = self.root.winfo_screenwidth()
		self.h = self.root.winfo_screenheight()

		self.control = tk.Frame(self.root, width=self.w*0.2, height=self.h)
		self.control.grid(row=0, column=0)

		self.display = tk.Canvas(self.root, width=self.w*0.8, height=self.h)
		self.display.grid(row=0, column=1)
		# self.thumbnail = tk.Canvas(self.display, width=self.w*0.8, height=self.h)


	def load_thumbnail(self, classes):
		def resize(image, w, h):
			w0, h0 = image.size
			factor = min(w/w0, h/w0)
			return image.resize((int(w0*factor), int(h0*factor)))
		self.patcher = Patcher("C:\\tsimage\\tct\\labelview\\res\\test.tif", "C:\\tsimage\\tct\\labelview\\res\\test_clas.csv")
		image = self.patcher.patch_label(classes)
		image = ImageTk.PhotoImage(resize(image, self.w*0.8, self.h))
		if classes:
			self.database[tuple(classes)] = image
		else:
			self.database[("base",)] = image
		self.display.create_image(self.w*0.4, self.h*0.5, image=image)

	def run(self):
		self.root.mainloop()


if __name__ == "__main__":
	viewer = Viewer()
	viewer.run()
