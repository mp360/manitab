# switch fig canvas
import numpy as np
from Tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Test1:

    def __init__(self, data):
        self.data = data

    def dosomething(self):
        try: 
            self.canvas.get_tk_widget().destroy()
        except:
            pass    
        data=np.arange(100)  # data to plot

        fig2 = Figure(figsize=(12, 4))
        fig2.subplots_adjust(bottom = 0.0, right = .75, top = .85)
        fig2.subplots_adjust(wspace=.3, hspace=.35)
        oldFig = fig2

        # self.figure = Figure(figsize=(12, 4))
        self.figure = fig2

        self.axes = self.figure.add_subplot(111)
        self.im = self.axes.plot(data)
        self.canvas = FigureCanvasTkAgg(oldFig, master=windows)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)

    def dosomethingelse(self):
        self.axes.plot(np.arange(100)+10*(np.random.rand(100)-0.5),'-r')
        self.figure.canvas.show()

data=np.arange(100)  # data to plot
test1=Test1(data)

window = Tk()
windows = Frame(window)
windows.pack(side = "top", fill = "both", expand = True)

# frame.grid()
menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Do something", command=test1.dosomething)
filemenu.add_command(label="Do somethingelse", command=test1.dosomethingelse)
menubar.add_cascade(label="Tool", menu=filemenu)

window.config(menu=menubar)
window.mainloop()
