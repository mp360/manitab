import Tkinter as tk
import matplotlib
import matplotlib.pyplot
from matplotlib import style
style.use('ggplot')
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,      NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import Slider, Button, RadioButtons
import random

class GUIplot(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)


        printButton = tk.Button(self, text="Plot1", command=lambda:  self.printMessage(canvas,a))
        printButton.grid(row=0, column=0, sticky='w')
        f = Figure()
        f.subplots_adjust(left=0.03, bottom=0.07, right=0.98, top=0.97, wspace=0, hspace=0)
        a = f.add_subplot(111)

        axLeft = f.add_axes([0.2, 0.5, 0.6, 0.03], facecolor='b')
        axRight = f.add_axes([0.2, 0.1, 0.6, 0.03], facecolor='r')
        # axLeft = plt.axes([0.35, 0.15, 0.65, 0.03], facecolor=axcolor)
        # axRight = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='r')
        sLeft = Slider(axLeft, 'Time', 0, 30, valinit=0)
        sRight = Slider(axRight, 'Time', 0, 30, valinit=0, color = 'b')

        axLeft.clear()
        axRight.clear()

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().grid(row=1)
        canvas._tkcanvas.config(bg='blue', width= 50, height = 50)
        canvas.show()
        canvas.blit()
    def printMessage(self,canvas,a):
        a.clear()
        my_random_x = random.sample(range(100),10)
        my_random_y = random.sample(range(100),10)
        a.plot(my_random_x,my_random_y,'*')
        canvas.draw()
        print("Wow")

GUIplot1 = GUIplot()
GUIplot1.title('PlotFunction')
w, h = GUIplot1.winfo_screenwidth(), GUIplot1.winfo_screenheight()
GUIplot1.geometry("%dx%d+0+0" % (w, h))
GUIplot1.mainloop()