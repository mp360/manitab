import Tkinter as tk# Tkinter -> tkinter in Python 3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib
import matplotlib.pyplot as plt 
import scipy.stats as ss
import ttk                 

matplotlib.use("TkAgg")
cancan = None
graphList = []
maximizedAxis = None
toMaximize = []
graphTypeDict = {}
toMaximizeType = None
maximizedGeometry = (1,1,1)
figure = None
LARGE_FONT = ("Verdana", 12)

class FancyFigureCanvas(FigureCanvasTkAgg):
    popup_menu = None
    def __init__(self, x, parent, *args, **kwargs):
        FigureCanvasTkAgg.__init__(self, x, parent, *args, **kwargs)

        self.popup_menu = tk.Menu(parent, tearoff=0)
        self.popup_menu.add_command(label="Maximize", command= self.toggle_slider_vis)
        self.popup_menu.add_command(label="Select All")
        popup_menu = self.popup_menu

    def toggle_slider_vis(self):
        if len(graphList) > 0 and None not in graphList:
            for axis in graphList:
                axis.set_visible(not axis.get_visible())
            if not graphList[0].get_visible(): 
                allAxes = figure.get_axes()
                for ax in allAxes:
                    if ax == maximizedAxis:
                        ax.clear()
                if toMaximizeType == 'weibull plot':
                    c = toMaximize[1]
                    x = toMaximize[2]                    
                    # maximizedAxis.set_xscale("log", nonposx='clip')

                    weibull = ss.weibull_min(c)
                    (quantiles, values), (slope, intercept, r) = ss.probplot(x, dist=weibull)
                    maximizedAxis.plot(values, quantiles,'ob')
                    maximizedAxis.plot(quantiles * slope + intercept, quantiles, 'r')
                    ticks_perc=[1, 5, 10, 20, 50, 80, 90, 95, 99, 99.9]
                    ticks_quan=[ss.weibull_min.ppf(i/100., c) for i in ticks_perc]
                    maximizedAxis.yaxis.set_ticklabels(ticks_perc)	#Set the text values of the tick labels.
                    maximizedAxis.yaxis.set_ticks(ticks_quan)
                self.popup_menu.entryconfigure(0, label="Restore")
            else:
                self.popup_menu.entryconfigure(0, label="Maximize")
            maximizedAxis.set_visible(not maximizedAxis.get_visible())

        self.draw()

def on_press(event):
    global toMaximize
    global toMaximizeType
    if event.button != 3: return
    try:
        if maximizedAxis.get_visible() and event.inaxes in [maximizedAxis]:
            cancan.popup_menu.tk_popup(root.winfo_x() + int(event.x), root.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y), 0)
        elif event.inaxes in graphList:
            for axis in graphList:
                if event.inaxes in [axis]:
                    toMaximize = graphTypeDict[axis]
                    toMaximizeType = graphTypeDict[axis][0]

            print 'this is entry \n'
            print toMaximize
            print("UES")
            # if axRight.get_visible():
            cancan.popup_menu.tk_popup(root.winfo_x() + int(event.x), root.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y), 0)
        # else:
            # cancan.popup_menu.tk_popup(root.winfo_x() + int(event.x), root.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y), 0)

        # TODO self.filemenu2.delete(0) # deletes first item in menu
        # self.filemenu2.delete("Stop") # delete item with the label "Stop"
    finally:
        cancan.popup_menu.grab_release()

class SeaofBTCapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        
        self.frames = {}
        for F in [StartPage]:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")
        self.show_frame(StartPage)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# def plot_axes(ax, geometry=(1,1,1)):
#     #create new figure.
#     global figure
#     global cancan
#     global maximizedAxis
#     newFig = Figure(dpi = 100)
    
#     if figure is not None:
#         figure.delaxes(ax)
#         for plot in figure.get_axes():
#             newFig.add_axes(plot)
#     cancan.fig = newFig
#     figure = newFig

#     if ax.get_geometry() != geometry :
#         maximizedGeometry = ax.get_geometry()
#         ax.change_geometry(*geometry)

#     ax = figure.add_axes(ax)
#     maximizedAxis = ax
#     return figure
def plot_axes(ax, geometry=(1,1,1)):
    #create new figure.
    global figure
    global cancan
    global maximizedAxis
    global maximizedGeometry
    
    if figure is not None:
        figure.delaxes(ax)
        for plot in figure.get_axes():
            plot.set_visible(not plot.get_visible())
        if ax.get_geometry() != geometry :
            maximizedGeometry = ax.get_geometry()
            ax.change_geometry(*geometry)
        ax = figure.add_axes(ax)
        maximizedAxis = ax
        cancan.draw()
    return

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        global cancan
        global maximizedAxis
        global graphList
        global figure
        tk.Frame.__init__(self, parent)
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        figure = Figure( dpi = 100)
        a1 = figure.add_subplot(111)
        a1.set_visible(False)
        maximizedAxis = a1
        # a1 = figure.add_subplot(112)
        
        buttContainer = tk.Frame(self, width=50, height=200)

        label = ttk.Label(buttContainer, text = "Graph Page", font = LARGE_FONT)
        label.grid(sticky = "ne", row = 0, column= 1, pady = 8, padx = 8)

        canContainer = tk.Frame(self, width=200, height=200)
        canvas = FancyFigureCanvas(figure, canContainer)
        connection_id = canvas.mpl_connect('button_press_event', on_press)
        cancan = canvas
        # TODO: RESIZE CANVAS

        can = canvas.get_tk_widget()

        canContainer.grid(row = 0, column = 0, sticky = "nsew", ipadx = 5, ipady = 5)
        buttContainer.grid(row = 0, column = 1, sticky = "nsew", pady = 5, padx = 5)

        can.grid(row = 0, column = 0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
        canvas._tkcanvas.grid(row = 0, column = 0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)


        nsample=500
        c = 1.79
        # a.set_xscale("log", nonposx='clip')

        ax2 = figure.add_subplot(221)
        a = figure.add_subplot(222)
        ax3 = figure.add_subplot(223)
        ax4 = figure.add_subplot(224)

        graphTypeDict[ax2] = ['weibull pdf']
        graphTypeDict[ax3] = ['survival fn']
        graphTypeDict[ax4] = ['hazard fn']

        graphList += [a,ax2,ax3,ax4]

        button1 = ttk.Button(buttContainer, text = "Back to Home",
            command = lambda: plot_axes(a, maximizedGeometry))
        button1.grid(row=1+13, column=2)

        x=ss.weibull_min.rvs(c, size=nsample)
        weibull = ss.weibull_min(c)
        (quantiles, values), (slope, intercept, r) = ss.probplot(x, dist=weibull)
        a.plot(values, quantiles,'ob')
        a.plot(quantiles * slope + intercept, quantiles, 'r')
        ticks_perc=[1, 5, 10, 20, 50, 80, 90, 95, 99, 99.9]
        ticks_quan=[ss.weibull_min.ppf(i/100., c) for i in ticks_perc]

        graphTypeDict[a] = ['weibull plot', c, x]
        # a.set_yticks(ticks_quan) #,ticks_perc)
        # a.grid(False)
        a.yaxis.set_ticklabels(ticks_perc)	#Set the text values of the tick labels.
        a.yaxis.set_ticks(ticks_quan)

        canContainer.grid_rowconfigure(0, weight = 1)
        canContainer.grid_columnconfigure(0, weight = 1)
        cancan.draw()



root = SeaofBTCapp()
root.mainloop()