import random
import tkinter
from tkinter import ttk
from tkinter import messagebox

class App(object):

    def __init__(self):
        self.root = tkinter.Tk()
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        random_theme = random.choice(available_themes)
        self.style.theme_use(random_theme)
        self.root.title(random_theme)

        frm = ttk.Frame(self.root)
        frm.pack(expand=True, fill='both')
    # create a Combobox with themes to choose from
        self.combo = ttk.Combobox(frm, values=available_themes)
        self.combo.pack(padx=32, pady=8)
    # make the Enter key change the style
        self.combo.bind('<Return>', self.change_style)
    # make a Button to change the style
        button = ttk.Button(frm, text='OK')
        button['command'] = self.change_style
        button.pack(pady=8)

    def change_style(self, event=None):
        """set the Style to the content of the Combobox"""
        content = self.combo.get()
        try:
            self.style.theme_use(content)
        except tkinter.TclError as err:
            messagebox.showerror('Error', err)
        else:
            self.root.title(content)

app = App()
app.root.mainloop()