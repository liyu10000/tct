import tkinter

window = tkinter.Tk()

window.title("tsimage")
window.geometry("600x600")
#set the window icon
#window.wm_iconbitmap("tsimage.ico")


#create a text entry widget called ent
ent = tkinter.Entry(window)
ent.pack()


def callback():
    print("Button clicked!")

#create a button widget called btn
btn = tkinter.Button(window, text="Button", command=callback)
btn.pack()


presses = 0

#create a label widget called lbl and add into window
lbl = tkinter.Label(window, text="Label")
lbl.pack()


def showInLabel():
    global presses
    presses += 1
    lbl.configure(text=presses)
    # lbl.configure(text="button2 clicked")

btn2 = tkinter.Button(window, text="Click me", command=showInLabel)
btn2.pack()



window.mainloop()