import os
import tkinter as tk
import tkinter.scrolledtext as tkst
from datetime import datetime


class Logger:
	def __init__(self, master):
		self.master = master  # parent container, usually tk.Frame
		self.save_path = "./" # local log file saving path
		self.cache = ""  # cache lines
		self.logtxt = tkst.ScrolledText(self.master, wrap='word')
		self.logtxt.pack(fill=tk.BOTH, expand=tk.YES)
		self.master.pack()

	def set_log_path(self, save_path):
		self.save_path = save_path # set log file saving path

	def log(self, line, flush=False):
		self.cache += line
		if flush:
			with open(os.path.join(self.save_path,"log.txt"), 'a') as f:
				f.write(self.cache)
			self.cache = ""  # empty cache after flushing
		self.logtxt.insert('end', line)

	def log_file(self, msg):
		line = "\n\n[INFO] {}\n".format(msg)
		self.log(line)

	def log_info(self, msg):
		line = "[INFO] {}\n".format(msg)
		self.log(line)

	def log_open(self, msg):
		line = "\n{}\n[OPEN] {}\n".format(datetime.now(), msg)
		self.log(line, flush=True)

	def log_delete(self, msg):
		line = "[DELETE] {}\n".format(msg)
		self.log(line)

	def log_change(self, msg1, msg2):
		line = "[CHANGE] {} [to] {}\n".format(msg1, msg2)
		self.log(line)

	def log_save(self, msg):
		line = "[SAVE] {}\n".format(msg)
		self.log(line)

	def on_close(self):
		if self.cache:
			with open(os.path.join(self.save_path,"log.txt"), 'a') as f:
				f.write(self.cache)
			self.cache = ""  # empty cache after flushing


if __name__ == "__main__":	
	root = tk.Tk()
	frame = tk.Frame(root)
	logger = Logger(frame)
	logger.log_open('file')
	logger.log("this is a test")
	logger.log_change('old', 'new')
	logger.log_open('new file')
	root.mainloop()
