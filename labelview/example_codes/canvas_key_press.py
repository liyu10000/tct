from tkinter import *

class MyCanvas(Frame):

    def __init__(self, root):
        Frame.__init__(self, root)

        self.canvas = Canvas(self)
        self.canvas.pack(fill=BOTH, expand=1)

        # standard bindings
        self.canvas.bind("<Double-Button-1>", self.set_focus)
        self.canvas.bind("<Button-1>", self.set_cursor)
        self.canvas.bind("<Key>", self.handle_key)

        # add a few items to the canvas
        self.canvas.create_text(50, 50, text="hello")
        self.canvas.create_text(50, 100, text="world")

    def highlight(self, item):
        # mark focused item.  note that this code recreates the
        # rectangle for each update, but that's fast enough for
        # this case.
        bbox = self.canvas.bbox(item)
        self.canvas.delete("highlight")
        if bbox:
            i = self.canvas.create_rectangle(
                bbox, fill="white",
                tag="highlight"
                )
            self.canvas.lower(i, item)

    def has_focus(self):
        return self.canvas.focus()

    def has_selection(self):
        # hack to work around bug in Tkinter 1.101 (Python 1.5.1)
        return self.canvas.tk.call(self.canvas._w, 'select', 'item')

    def set_focus(self, event):
        if self.canvas.type(CURRENT) != "text":
            return

        self.highlight(CURRENT)

        # move focus to item
        self.canvas.focus_set() # move focus to canvas
        self.canvas.focus(CURRENT) # set focus to text item
        self.canvas.select_from(CURRENT, 0)
        self.canvas.select_to(CURRENT, END)

    def set_cursor(self, event):
        # move insertion cursor
        item = self.has_focus()
        if not item:
            return # or do something else

        # translate to the canvas coordinate system
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        self.canvas.icursor(item, "@%d,%d" % (x, y))
        self.canvas.select_clear()

    def handle_key(self, event):
        # widget-wide key dispatcher
        item = self.has_focus()
        if not item:
            return

        insert = self.canvas.index(item, INSERT)

        if event.char >= " ":
            # printable character
            if self.has_selection():
                self.canvas.dchars(item, SEL_FIRST, SEL_LAST)
                self.canvas.select_clear()
            self.canvas.insert(item, "insert", event.char)
            self.highlight(item)

        elif event.keysym == "BackSpace":
            if self.has_selection():
                self.canvas.dchars(item, SEL_FIRST, SEL_LAST)
                self.canvas.select_clear()
            else:
                if insert > 0:
                    self.canvas.dchars(item, insert-1, insert)
            self.highlight(item)

        # navigation
        elif event.keysym == "Home":
            self.canvas.icursor(item, 0)
            self.canvas.select_clear()
        elif event.keysym == "End":
            self.canvas.icursor(item, END)
            self.canvas.select_clear()
        elif event.keysym == "Right":
            self.canvas.icursor(item, insert+1)
            self.canvas.select_clear()
        elif event.keysym == "Left":
            self.canvas.icursor(item, insert-1)
            self.canvas.select_clear()

        else:
            pass # print event.keysym

# try it out (double-click on a text to enable editing)
c = MyCanvas(Tk())
c.pack()

mainloop()