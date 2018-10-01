import tkinter as tk
import tkinter.ttk as ttk


class CanvasTooltip:
    '''
    It creates a tooltip for a given canvas tag or id as the mouse is
    above it.

    This class has been derived from the original Tooltip class I updated
    and posted back to StackOverflow at the following link:

    https://stackoverflow.com/questions/3221956/
           what-is-the-simplest-way-to-make-tooltips-in-tkinter/
           41079350#41079350

    Alberto Vassena on 2016.12.10.
    '''

    def __init__(self, canvas, tag_or_id,
                 *,
                 bg='#FFFFEA',
                 pad=(5, 3, 5, 3),
                 text='canvas info',
                 waittime=400,
                 wraplength=250):
        self.waittime = waittime  # in miliseconds, originally 500
        self.wraplength = wraplength  # in pixels, originally 180
        self.canvas = canvas
        self.text = text
        self.canvas.tag_bind(tag_or_id, "<Enter>", self.onEnter)
        self.canvas.tag_bind(tag_or_id, "<Leave>", self.onLeave)
        self.canvas.tag_bind(tag_or_id, "<ButtonPress>", self.onLeave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def onEnter(self, event=None):
        self.schedule()

    def onLeave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.canvas.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.canvas.after_cancel(id_)

    def show(self, event=None):
        def tip_pos_calculator(canvas, label,
                               *,
                               tip_delta=(10, 5), pad=(5, 3, 5, 3)):

            c = canvas

            s_width, s_height = c.winfo_screenwidth(), c.winfo_screenheight()

            width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
                             pad[1] + label.winfo_reqheight() + pad[3])

            mouse_x, mouse_y = c.winfo_pointerxy()

            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)

            if offscreen:

                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top

            if offscreen_again:
                # No further checks will be done.

                # TIP:
                # A further mod might automagically augment the
                # wraplength when the tooltip is too high to be
                # kept inside the screen.
                y1 = 0

            return x1, y1

        bg = self.bg
        pad = self.pad
        canvas = self.canvas

        # creates a toplevel window
        self.tw = tk.Toplevel(canvas.master)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = tk.Frame(self.tw,
                       background=bg,
                       borderwidth=0)
        label = ttk.Label(win,
                          text=self.text,
                          justify=tk.LEFT,
                          background=bg,
                          relief=tk.SOLID,
                          borderwidth=0,
                          wraplength=self.wraplength)

        label.grid(padx=(pad[0], pad[2]),
                   pady=(pad[1], pad[3]),
                   sticky=tk.NSEW)
        win.grid()

        x, y = tip_pos_calculator(canvas, label)

        self.tw.wm_geometry("+%d+%d" % (x, y))

    def hide(self):
        if self.tw:
            self.tw.destroy()
        self.tw = None


if __name__ == '__main__':

    import random

    def further_text():
        info_text = ('\n\nGo over any rectangle with your mouse pointer to see it '
                     'changing to yellow and stay on it long enough (less than '
                     'a second) to let it show its own customized '
                     'CanvasTooltip instance.\n\n'

                     'Click once using the mouse left button over a rectangle '
                     'to start dragging it to the desired new position and '
                     'release the left button when you are done.\n\n'

                     'Double click inside the canvas using the mouse left '
                     'button to redraw a new set of rectangles.\n\n'
                     'HtH. ;) Alberto Vassena')

        # texts generated at http://lorem-ipsum.perbang.dk/
        short_text = ('Lorem ipsum dolor sit amet, mauris tellus, '
                      'porttitor torquent eu. Magna aliquet lorem, '
                      'cursus sit ac, in in. Dolor aliquet, cum integer. '
                      'Proin aliquet, porttitor pulvinar mauris. Tellus '
                      'lectus, amet cras, neque lacus quis. Malesuada '
                      'nibh. Eleifend nam, in eget a. Nec turpis, erat '
                      'wisi semper')
        medium_text = ('Lorem ipsum dolor sit amet, suspendisse aenean '
                       'ipsum sollicitudin, pellentesque nunc ultrices ac '
                       'ut, arcu elit turpis senectus convallis. Ac orci '
                       'pretium sed gravida, tortor nulla felis '
                       'consectetuer, mauris egestas est erat. Ut enim '
                       'tellus at diam, ac sagittis vel proin. Massa '
                       'eleifend orci tortor sociis, scelerisque in pede '
                       'metus phasellus, est tempor gravida nam, ante '
                       'fusce sem tempor. Mi diam auctor vel pede, mus '
                       'non mi luctus luctus, lectus sit varius repellat '
                       'eu')
        long_text = ('Lorem ipsum dolor sit amet, velit eu nam cursus '
                     'quisque gravida sollicitudin, felis arcu interdum '
                     'error quam quis massa, et velit libero ligula est '
                     'donec. Suspendisse fringilla urna ridiculus dui '
                     'volutpat justo, quisque nisl eget sed blandit '
                     'egestas, libero nullam magna sem dui nam, auctor '
                     'vehicula nunc arcu vel sed dictum, tincidunt vitae '
                     'id tristique aptent platea. Lacus eros nec proin '
                     'morbi sollicitudin integer, montes suspendisse '
                     'augue lorem iaculis sed, viverra sed interdum eget '
                     'ut at pulvinar, turpis vivamus ac pharetra nulla '
                     'maecenas ut. Consequat dui condimentum lectus nulla '
                     'vitae, nam consequat fusce ac facilisis eget orci, '
                     'cras enim donec aenean sed dolor aliquam, elit '
                     'lorem in a nec fringilla, malesuada curabitur diam '
                     'nonummy nisl nibh ipsum. In odio nunc nec porttitor '
                     'ipsum, nunc ridiculus platea wisi turpis praesent '
                     'vestibulum, suspendisse hendrerit amet quis vivamus '
                     'adipiscing elit, ut dolor nec nonummy mauris nec '
                     'libero, ad rutrum id tristique facilisis sed '
                     'ultrices. Convallis velit posuere mauris lectus sit '
                     'turpis, lobortis volutpat et placerat leo '
                     'malesuada, vulputate id maecenas at a volutpat '
                     'vulputate, est augue nec proin ipsum pellentesque '
                     'fringilla. Mattis feugiat metus ultricies repellat '
                     'dictum, suspendisse erat rhoncus ultricies in ipsum, '
                     'nulla ante pellentesque blandit ligula sagittis '
                     'ultricies, sed tortor sodales pede et duis platea')

        text = random.choice([short_text, medium_text, long_text,
                              info_text, info_text, info_text])

        return 'Further info: ' + text


    class MyCanvas(tk.Canvas):

        def clear(self):
            self.delete('rectangle')

        def draw(self):
            width, height = int(self['width']), int(self['height'])

            colors = ('blue', 'green', 'red',
                      'brown', 'cyan', 'magenta',
                      'violet', 'black', 'white')

            self.tooltips = []

            mask = '{} rectangle #{}.\n'
            for i in range(20):
                x, y = random.randint(0, width - 1), random.randint(0, height - 1)
                w, h = random.randint(5, 100), random.randint(5, 100)
                tag = 'R{}'.format(i)
                color = random.choice(colors)
                text = mask.format(color.capitalize(), tag[1:]) + further_text()

                id_ = self.create_rectangle(x, y, x + w, y + h,
                                            fill=color,
                                            activefill='yellow',
                                            tags=('rectangle', tag))

                tooltip = CanvasTooltip(self, id_, text=text)

                self.tooltips.append(tooltip)

        def redraw(self, event):
            self.clear()
            self.draw()

        def onClick(self, event):
            coords = self.canvasx(event.x, 1), self.canvasy(event.y, 1)
            found = self.find_closest(*coords)[0]

            if found:
                self.target = found
                self.drag_x, self.drag_y = coords
                self.tag_raise(found)

            else:
                self.target, self.drag_x, self.drag_y = None, None, None

        def onDrag(self, event):
            if self.target is None:
                return

            coords = self.canvasx(event.x, 1), self.canvasy(event.y, 1)

            self.move(self.target,
                      coords[0] - self.drag_x,
                      coords[1] - self.drag_y)

            self.drag_x, self.drag_y = coords

        def onRelease(self, event):
            self.target, self.drag_x, self.drag_y = None, None, None


    def main():
        root = tk.Tk()
        frame = ttk.Frame(root)

        c = frame.canvas = MyCanvas(frame.master, width=800, height=600)
        c.draw()
        c.bind('<Double-Button-1>', c.redraw)
        c.tag_bind('rectangle', '<Button-1>', c.onClick)
        c.tag_bind('rectangle', '<B1-Motion>', c.onDrag)
        c.tag_bind('rectangle', '<ButtonRelease-1>', c.onRelease)
        c.grid(column=0, row=0, padx=(0, 0), pady=(0, 0))

        frame.grid()
        root.mainloop()


    main()