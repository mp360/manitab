import sys
import math
import numpy as np
import pandas as pd
from scipy.integrate import trapz, simps

# import rangeSlider

# from drawnow import *

from matplotlib import dates
import matplotlib.ticker as mticker

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.widgets import Slider
from matplotlib import style

import urllib
import json

import Tkinter as tk, tkFileDialog
from Tkinter import Entry, StringVar, IntVar
import tkMessageBox
# from Tkinter import *

import ttk


import csv

import threading
import Queue
import time
import datetime



from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

LARGE_FONT = ("Verdana", 12)
MED_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
axcolor = 'lightgoldenrodyellow'
style.use("ggplot")


fig = Figure(figsize = (7.5,6.35), dpi = 100)
# fig2 = Figure()
# fig2.subplots_adjust(bottom=0.07, right=0.98, top=0.97, wspace=0, hspace=0)
fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)

# fig.set_size_inches(1.5, 1)
# fig = plt.gcf()
a = fig.add_subplot(111)

a2 = a.twinx()

binType = ""
prevPlotf = 0
prevPlota = 0
xAreaPoints = []
yAreaPoints = []

dataFile = None

globalBins = []
globalNPerBin = []

globalBinning = None

writeCsv_lock = threading.Lock()


globalSigma = 0.0
globalMu = 0.0
# q = Queue() # To use for threading in the future
fillBetFigure = None
plotButton = None
cmbBox = None
sLeft = None
sRight = None
axRight = None
axLeft = None

graphTitle = None

def saveFile():
    global writeCsv_lock
    global xAreaPoints
    global yAreaPoints
    global globalBins
    global globalNPerBin
    # writeCsv_lock.acquire()
    curTitle = graphTitle.get()
    if curTitle == "":
        curTitle = "Normal-Histogram"

    fname = tkFileDialog.asksaveasfile(defaultextension = ".csv", initialfile = curTitle)
    if fname is None:
        return

    # print(type(fname))    # FOR DEBUGGNING
    # print(fname)          # fname is type 'file'
    # print(str(fname))

    with open(fname.name, 'wb') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

        lenBins = len(globalNPerBin)
        # print(lenBins)
        if (isinstance(globalBins[len(globalBins) - 1], datetime.datetime)):
            filewriter.writerow(['NormDist x Values (Days)' , 'NormDist y Values', '__________', 'Amt Per Bin'])
        else:
            filewriter.writerow(['NormDist x Values' , 'NormDist y Values', 'Histo Bins', 'Amt Per Bin'])

        for i in range(len(xAreaPoints)):
            # print(i)
            if (isinstance(globalBins[len(globalBins) - 1], datetime.datetime)):
                if (i < lenBins):
                    # if (i == lenBins):
                    #     i = len(globalBins) - 1
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], globalBins[i].strftime('%m/%d/%Y %H:%M:%S'), globalNPerBin[i], 0])
                else:
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], None, None])
            else:
                if (i < lenBins):
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], globalBins[i], globalNPerBin[i], 0])
                else:
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], None, None])

def saveImage():
    fig.savefig('test2png.png', dpi=100)


def mergeSort(arr):
    mid = len(arr)//2
    lefthalf = arr[:mid]
    righthalf = arr[mid:]

    mergeSort(lefthalf)
    mergeSort(righthalf)

    i = 0
    j = 0
    k = 0
    while (i < len(lefthalf) and j < len(righthalf)):
        if lefthalf[i] >= righthalf[j]:
            arr[k] = (righthalf[j])
            j += 1
        else:
            arr[k] = (lefthalf[i])
            i += 1
        k += 1
    while (i < len(lefthalf)):
        arr[k] = (lefthalf[i])
        i += 1
        k += 1
    while (j < len(righthalf)):
        arr[k] = (righthalf[j])
        j += 1
        k += 1


def makeFig(): #Create a function that makes our desired plot
    plt.ylim(80,90)                                 #Set y min and max values
    plt.title('My Live Streaming Sensor Data')      #Plot the title
    plt.grid(True)                                  #Turn the grid on
    plt.ylabel('Temp F')                            #Set ylabels
    plt.plot(tempF, 'ro-', label='Degrees F')       #plot the temperature
    plt.legend(loc='upper left')                    #plot the legend
    plt2 = plt.twinx()                                #Create a second y axis
    plt.ylim(93450,93525)                           #Set limits of second y axis- adjust to readings you are getting
    plt2.plot(pressure, 'b^-', label='Pressure (Pa)') #plot pressure data
    plt2.set_ylabel('Pressrue (Pa)')                    #label second y axis
    plt2.ticklabel_format(useOffset=False)           #Force matplotlib to NOT autoscale y axis
    plt2.legend(loc='upper right')                  #plot the legend

def update(val):
    global prevPlotf
    global prevPlota
    global fillBetFigure
    global axLeft
    global axRight
    global sLeft
    global sRight
    global a2
    global axcolor
    # sLeft.valinit = 0
    # sLeft.vline = axLeft.axvline(sLeft.val, 0, 1, color= 'r', lw = 1)
    # axLeft.axvspan(0, 3)
    # axLeft.axvline(sLeft.val, 0, 1, color= 'r', lw = 1)
    with plt.style.context('classic'):

        axLeft.clear()
        axRight.clear()

        # sLeft.valmax = 1
        # sLeft.valmin = 0
        # # axLeft.set_yticks([])

        # print(sLeft.valinit)
        # print(sLeft.val)
        # axLeft.axvline(sRight.val, 0, 1, color= 'r', lw = 2)
        # axRight.axvline(sLeft.val, 0, 1, color= 'b', lw = 2)
        # axRight.axvline(sLeft.val, 0, 1, color= 'b', lw = 1)
        if (sLeft.val > sRight.val and sLeft.val != prevPlotf):
            axLeft.axvspan(0, sRight.val, 0, 1)
            sLeft.val = sRight.val
            axLeft.axvline(sRight.val, 0, 1, color= 'r', lw = 2)
            axRight.axvspan(0, sRight.val, 0, 1, facecolor=axcolor)

        elif (sLeft.val > sRight.val and sRight.val != prevPlota):
            axRight.axvspan(0, sLeft.val, 0, 1, facecolor=axcolor)
            sRight.val = sLeft.val
            axRight.axvline(sLeft.val, 0, 1, color= 'b', lw = 2)
            axLeft.axvspan(0, sLeft.val, 0, 1)
        else:
            axLeft.axvspan(0, sLeft.val, 0, 1)
            axRight.axvspan(0, sRight.val, 0, 1, facecolor=axcolor)
            axLeft.axvline(sRight.val, 0, 1, color= 'r', lw = 2)
            axRight.axvline(sLeft.val, 0, 1, color= 'b', lw = 2)

        axLeft.margins(x = 0)
        axRight.margins(x = 0)
        axLeft.set_xlim(0, 1)
        axRight.set_xlim(0, 1)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])
        # axLeft.set_xticks([])
        # axRight.set_xticks([])
        prevPlota = sRight.val
        prevPlotf = sLeft.val
        if fillBetFigure is not None:
            fillBetFigure.remove()

            shadeT = np.linspace(prevPlotf, prevPlota, 100)

            normYs = []
            for xElem in shadeT:
                normYs = normYs + [np.reciprocal(globalSigma * math.sqrt(2 * np.pi))
                    * np.reciprocal(np.exp(0.5 * ((xElem - globalMu) / (globalSigma)) ** 2))]

            fillBetFigure = a2.fill_between(shadeT, 0, normYs, facecolor = '#4B0082', alpha = 0.4 )
            # amp = sRight.val
            # freq = sLeft.val
            # l.set_ydata(amp*np.sin(2*np.pi*freq*t))
            fig.canvas.draw_idle()


def openFile():
    global dataFile
    global plotButton
    # global writeCsv_lock
    # writeCsv_lock.acquire()
    file1 = tkFileDialog.askopenfile(mode = 'rb', title = 'Choose a file')

    if file1 is None:
        return
    else:
        try:
            pd.read_csv(file1.name)
            data = pd.read_csv(file1.name, nrows = 1)
            vals = tuple(data)

            cmbBox['values'] = vals
            cmbBox.current(0)
            plotButton.config(state="normal")
        except Exception, e:
            tkMessageBox.showerror("Unknown File", "The file you provided is either not of type .csv. or is empty.")
            return

    dataFile = file1.name
    # label = ttk.Label(text = file1).pack()  # prints file name on screen

    # print(file1.name)
    # writeCsv_lock.release()



class SeaofBTCapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default = "")
        tk.Tk.wm_title(self, "Sea of BTC Client")

        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff = 0)
        filemenu.add_command(label = "Save", command = lambda: saveFile())
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command = sys.exit)
        menubar.add_cascade (label = "File", menu = filemenu)

        # newMenuWin = tk.Menu(menubar, tearoff = 0)
        # newMenuWin.add_command(label = "Todo",
        #     command = lambda: myfunc())
        # menubar.add_cascade (label = "Extra Option", menu = newMenuWin)

        tk.Tk.config(self, menu = menubar)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(PageThree)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

def myfunc():
    return


# def popupmsg(param, canvas):
#     popup = tk.Tk()

#     def leavemini():
#         popup.destroy()

#     popup.wm_title("!")
#     # label = ttk.Label(popup, text = param, font = SMALL_FONT)
#     # label.pack(sticky = "n", fill = "x", pady = 10)

#     B1 = ttk.Button(popup, text = "Okay", command = leavemini)
#     B1.grid(row=0, column=1)

#     # B1.pack()
#     # e2 = ttk.Entry(popup)

#     # e2.pack()

#     # e1 = Entry(param)
#     # e2 = Entry(popup)

#     # e1.grid(row=0, column=1)


#     popup.mainloop()


    # print(param)

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "Start Page", font = LARGE_FONT)
        label.grid(sticky = "n", pady = 10, padx = 10)

        button1 = ttk.Button(self, text = "Visit Page 1",
            command = lambda: controller.show_frame(PageOne))
        # button1.pack()
        button1.grid(row=0, column=1)

        button2 = ttk.Button(self, text = "Visit Page 2",
            command = openFile)
        # button2.pack()
        button2.grid(row=0, column=2)


        button3 = ttk.Button(self, text = "Graph Page",
            command = lambda: controller.show_frame(PageThree))
        # button3.pack()
        button3.grid(row=0, column=3)



class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "PAGE 1", font = LARGE_FONT)
        label.grid(sticky = "n", pady = 10, padx = 10)

        button1 = ttk.Button(self, text = "Back to Home",
            command = lambda: controller.show_frame(StartPage))
        # button1.pack()
        button1.grid(row=0, column=1)


        button2 = ttk.Button(self, text = "To Page 2",
            command = lambda: controller.show_frame(PageTwo))
        # button2.pack()
        button2.grid(row=0, column=2)


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "PAGE 2", font = LARGE_FONT)
        label.grid(sticky = "n", pady = 10, padx = 10)

        button1 = ttk.Button(self, text = "Back to Home",
            command = lambda: controller.show_frame(StartPage))
        # button1.pack()
        button1.grid(row=0, column=1)


        button2 = ttk.Button(self, text = "To Page 1",
            command = lambda: controller.show_frame(PageOne))
        # button2.pack()
        button2.grid(row=0, column=2)


class ChooseHeadersPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "Choose Headers", font = LARGE_FONT)
        label.grid(sticky = "n", pady = 10, padx = 10)

        # # e1 = Entry(parent)
        # e2 = Entry(self)

        # # e1.grid(row=0, column=1)
        # e2.pack()

        button1 = ttk.Button(self, text = "Back to Home",
            command = lambda: controller.show_frame(StartPage))
        # button1.pack()
        button1.grid(row=0, column=1)

        button2 = ttk.Button(self, text = "To Page 1",
            command = lambda: controller.show_frame(PageOne))
        # button2.pack()
        button2.grid(row=0, column=2)

class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        global dataFile
        global plotButton
        global errLabel
        global cmbBox
        global curHeader
        global globalBinning
        global sLeft
        global sRight
        global axLeft
        global axRight
        global axcolor
        global graphTitle
        # global writeCsv_lock
        tk.Frame.__init__(self, parent)
        # self.rowconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)

        content = tk.Frame(self)

        buttContainer = tk.Frame(self, width=50, height=200)

        # content.grid(column = 0, row = 0, padx = (10,10))
        # sliderContainer = tk.Frame(buttContainer, width=200, height=150)

        canContainer = tk.Frame(self, width=200, height=150)

        # genControlsCont = tk.Frame(self)

        canvas = FigureCanvasTkAgg(fig, canContainer)
        # canvasS = FigureCanvasTkAgg(fig2, buttContainer)
        # TODO: RESIZE CANVAS
        can = canvas.get_tk_widget()
        # canS = canvas.get_tk_widget()

        canContainer.grid(row = 1, column = 0, sticky = "nsew", pady = (3,5), padx = (3,5), ipadx = 5, ipady = 5)
        # sliderContainer.grid(row = 3, column = 3, sticky = "ew")
        buttContainer.grid(row = 1, column = 2, sticky = "nsew", pady = 5, padx = 5)
        # genControlsCont.grid(row = 2, column = 2, sticky = "ew")
        can.grid(row = 2, column = 0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
        canvas._tkcanvas.grid(row = 2, column = 0, rowspan = 1, sticky = "nsew", padx = (3,5), pady = (3,5), ipadx = 5, ipady = 5)
        # canS.grid(row = 2, column = 0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
        # canvasS._tkcanvas.config(bg='blue', width= 200, height = 100)
        # canvasS._tkcanvas.grid(row = 3, column = 3, columnspan = 5, sticky = "nsew", padx = (3,5), pady = (3,5), ipadx = 5, ipady = 5)

        # canContainer.grid_rowconfigure(0, weight = 2)
        # canContainer.grid_columnconfigure(0, weight = 2)

        self.binning = IntVar()
        globalBinning = self.binning
        self.myHeader = StringVar()
        curHeader = self.myHeader
        self.myType = StringVar()
        label = ttk.Label(buttContainer, text = "Graph Page", font = LARGE_FONT)
        label.grid(sticky = "n", row = 0, column= 1, pady = 10, padx = 10)


        headerLabel = ttk.Label(buttContainer, text = "Column Header:", font = SMALL_FONT)
        headerLabel.grid(sticky = "e", row = 1, column= 1, padx = 2, pady = 4)

        typeLabel = ttk.Label(buttContainer, text = "Data Type:", font = SMALL_FONT)
        typeLabel.grid(sticky = "e", row = 3, column= 1, padx = 2, pady = 4)

        binningLabel = ttk.Label(buttContainer, text = "No. Bins:", font = SMALL_FONT)
        binningLabel.grid(sticky = "e", row = 2, column= 1, padx = 2, pady = 4)

        cmbBox = ttk.Combobox(buttContainer, state="readonly", values = (" --"),
            textvariable = self.myHeader)
        # cmbBox.pack()
        cmbBox.grid(row=1, column=2, sticky = "ew")
        cmbBox.current(0)

        cmbBox2 = ttk.Combobox(buttContainer, state="readonly",
            values=("Date (mm/dd/yyyy)", "Number", "Percent"), textvariable = self.myType)
        # cmbBox.pack()
        cmbBox2.grid(row=3, column=2, sticky = "ew")
        cmbBox2.current(0)

        cmbBox3 = ttk.Combobox(buttContainer, state="readonly",
            values = tuple([i + 1 for i in range(50)]), textvariable = self.binning)
        # cmbBox.pack()
        cmbBox3.grid(row=2, column=2, sticky = "ew")
        cmbBox3.current(19)

        self.myTitle = StringVar()
        graphTitle = self.myTitle
        name = ttk.Entry(buttContainer, textvariable = self.myTitle)
        name.grid( row=4, column=2, columnspan=2, sticky="ew", pady=5, padx=5)
        titleLabel = ttk.Label(buttContainer, text = "Graph Title:", font = SMALL_FONT)
        titleLabel.grid(sticky = "e", row = 4, column= 1, padx = 2, pady = 4)

        button1 = ttk.Button(buttContainer, text = "Back to Home",
            command = lambda: controller.show_frame(StartPage))
        # button1.pack()
        button1.grid(row=6, column=2)

        button2 = ttk.Button(buttContainer, text = "Choose A Data File",
            command = openFile)
        # button2.pack()
        button2.grid(row=0, column=2)

        # button3 = ttk.Button(buttContainer, text = "Show Fullscreen",
        #     command = lambda: popupmsg(self))
        # # button3.pack()
        # button3.grid(row=5, column=1)


        plotButton = ttk.Button(buttContainer, text = "Plot",
            command = lambda: self.plot(canvas))
        plotButton.config(state="disabled")
        # plotButton.pack()
        plotButton.grid(row=5, column=2)

        # MOVE TO PLOT
        # with plt.style.context('classic'):
        #     axLeft = fig.add_axes([0.2, 0.08, 0.6, 0.03], facecolor=axcolor)
        #     axRight = fig.add_axes([0.2, 0.05, 0.6, 0.03], facecolor='r')
        #     # axLeft = plt.axes([0.35, 0.15, 0.65, 0.03], facecolor=axcolor)
        #     # axRight = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='r')
        #     sLeft = Slider(axLeft, 'Time', 0, 30, valinit=0)
        #     sRight = Slider(axRight, 'Time', 0, 30, valinit=0, color = axcolor)

        #     axLeft.clear()
        #     axRight.clear()
        #     axLeft.set_xticks([])
        # sLeft.on_changed(update)
        # sRight.on_changed(update)
        # buttContainer.grid_rowconfigure(0, weight = 3)
        # buttContainer.grid_columnconfigure(0, weight = 3)

        canContainer.grid_rowconfigure(0, weight = 1)
        canContainer.grid_columnconfigure(0, weight = 1)
        buttContainer.grid_columnconfigure(1, weight = 1)
        buttContainer.rowconfigure(0, weight = 1)

        canvas.draw()

    def showFullScreen(self, canvas):
        return

    def plot(self,canvas):

        global writeCsv_lock
        global xAreaPoints
        global yAreaPoints
        global globalBins
        global globalNPerBin
        global dataFile
        global a
        global a2
        global binType
        global curHeader
        global globalBinning
        global graphTitle

        # if dataFile == None:
        # if self.myType.get() == "":
            # print("YES")
        binType = self.myType.get()

        try:
            numBins = globalBinning.get()
            gotten = curHeader.get()
            if dataFile is not None:

                # print(self.myType.get())

                dframe = pd.read_csv(dataFile)
                # print(type(dframe.sort_values(gotten)))
                dframe = dframe.sort_values(gotten)
                # print(dframe.head())
                # print(cmbBox2.get())
                a3 = None
                if (self.myType.get() == "Date (mm/dd/yyyy)"):

                    allAxes = fig.get_axes()

                    for ax in allAxes:
                        # print(ax)
                        ax.clear()
                        ax.remove()

                    a = fig.add_subplot(111)
                    a2 = a.twinx()

                    l = dframe[gotten].dropna().values.tolist()

                    converted_dates = map(datetime.datetime.strptime, l, len(l)*['%m/%d/%Y'])
                    x_axis = (converted_dates)
                    # print("gothere")
                    formatter = dates.DateFormatter('%m/%d/%Y')

                    dframe[gotten] = pd.to_datetime(dframe[gotten].dropna())
                    stats = dframe[gotten].dropna().describe()
                    # print(stats)
                    earliestMax = stats.iloc[4]
                    recentMax = stats.iloc[5]

                    # d1 = datetime.datetime.strptime(earliestMax, '%m/%d/%Y')
                    # d2 = datetime.datetime.strptime(recentMax, '%m/%d/%Y')
                    # lastDate = abs((d2 - d1).days)
                    dateDiffList = []
                    for xDate in converted_dates:
                        # print(abs((xDate - earliestMax).days))
                        dateDiffList += [abs((xDate - earliestMax).days)]

                    datesDF = pd.DataFrame(dateDiffList, columns = [gotten])
                    # print(datesDF.head())
                    stats = datesDF.describe()
                    # print(stats)


                    mu = stats.iloc[1][gotten]
                    variance = stats.iloc[2][gotten] ** 2
                    sigma = math.sqrt(variance)
                    mn = stats.iloc[3][gotten]
                    mx = stats.iloc[7][gotten]

                    globalSigma = sigma
                    globalMu = mu

                    x = np.linspace(mn, mx, 100 + 2 * int(math.sqrt(mx - mn)))
                    # x = np.linspace(mn - 3 * sigma, mx + 3 * sigma, 100 + 5 * int(math.sqrt(mx - mn)))

                    y = []
                    for xElem in x:
                        y = y + [np.reciprocal(stats.iloc[2][gotten] * math.sqrt(2 * np.pi))
                            * np.reciprocal(np.exp(0.5 * ((xElem - stats.iloc[1][gotten]) / (stats.iloc[2][gotten])) ** 2))]

                    # y_axis = range(0,len(x_axis))
                    # a.plot( x_axis, y_axis, '-' )

                    n, bins, patches = a.hist(dframe[gotten].dropna(), numBins,
                        facecolor = '#00A3E0', edgecolor = 'k', align = 'mid')# n, bins, patches = a.hist(l, 100, #facecolor = 'red', edgecolor = 'yellow', align = 'mid')
                    a.set_ylim(0, 1.5 * (max(n)))# a2.axes.yaxis.set_ticklabels([]) -- - no y - axis labels


                    globalBins = dates.num2date(bins)
                    globalNPerBin = n
                    # print((globalBins[len(globalBins) - 1].strftime('%m/%d/%Y')))
                    # print(len(globalBins))
                    # print(len(globalNPerBin))

                    # print(globalBins)

                    # print((globalBins))

                    # print(type(globalNPerBin[0]))

                    a.tick_params(axis = 'x', rotation = 25)

                    a3 = fig.add_subplot(111, label="3", frame_on=False)

                    a3.plot(x, y, label = 'newNorm', lw = 2.0, color = '#8B0000')

                    a3.grid(False)
                    a3.set_ylim(0, 1.5 * (max(y)))
                    a3.tick_params(axis = 'y', labelcolor = '#8B0000')
                    a3.tick_params(axis = 'x', labelcolor = '#8B0000')
                    a3.set_ylabel("Normal Values")
                    # toTurn.set_rotation(270)
                    a3.set_xlabel("Days")
                    a.set_xlabel("Date Divisions")
                    a.set_ylabel("Frequency")
                    a3.xaxis.set_label_position('top')
                    a3.yaxis.set_label_position('right')
                    a2.set_yticks([])
                    a3.xaxis.tick_top()
                    a3.yaxis.tick_right()


                    a.legend(bbox_to_anchor=(0, 1.08, 1, .102), loc=3,
                            ncol=1, borderaxespad=0)

                    # print('{:18.16f}'.format(trapz(y, x)))

                    title = graphTitle.get()
                    a.set_title(title, y = 1.1)

                    canvas.draw()
                    xAreaPoints = x
                    yAreaPoints = y

                else:
                    allAxes = fig.get_axes()

                    for ax in allAxes:
                        # print(ax)
                        ax.clear()
                        ax.remove()
                    a = fig.add_subplot(111)
                    a2 = a.twinx()

                    stats = dframe[gotten].dropna().describe()
                    # print(stats)

                    mu = stats.iloc[1]
                    variance = stats.iloc[2] ** 2
                    sigma = math.sqrt(variance)
                    mn = stats.iloc[3]
                    mx = stats.iloc[7]

                    globalSigma = sigma
                    globalMu = mu

                    x = np.linspace(mn , mx, 100 + 5 * int(math.sqrt(mx - mn)))
                    # x = np.linspace(mn - 3 * sigma, mx + 3 * sigma, 400 )
                    #x = np.linspace(mn - 3 * sigma, mx + 3 * sigma, 100 + 5 * int(math.sqrt(mx - mn)))
                    # x = np.linspace(mn, mx, 100 + 5 * int(math.sqrt(mx - mn)))

                    y = []
                    for xElem in x:
                        y = y + [np.reciprocal(sigma * math.sqrt(2 * np.pi))
                            * np.reciprocal(np.exp(0.5 * ((xElem - mu) / (sigma)) ** 2))]

                    a.grid(False)
                    a.yaxis.grid()
                    n, bins, patches = a.hist(dframe[gotten].dropna(), numBins,
                        facecolor = '#00A3E0', edgecolor = 'k', align = 'mid')# n, bins, patches = a.hist(l, 100, #facecolor = 'red', edgecolor = 'yellow', align = 'mid')
                    a.set_ylim(0, 1.5 * (max(n)))# a2.axes.yaxis.set_ticklabels([]) -- - no y - axis labels
                    # print(y)
                    # print(x)
                    globalBins = bins
                    globalNPerBin = n

                    useBins = bins
                    if (numBins >= 30):
                        l = []
                        for i in range(0, len(bins), 2):
                            l += [bins[i]]
                        useBins = l


                    a.set_xticks(useBins)
                    a.tick_params(axis = 'x', rotation = 35)
                    a2.plot(x, y, label = 'newNorm', lw = 2.0, color = '#8B0000')
                    fillBetFigure = a2.fill_between(x, 0, y, facecolor = '#4B0082', alpha = 0.4)

                    # a2.axes.yaxis.set_ticklabels(np.linspace(min(n), max(n), 1000))
                    a2.grid(False)
                    a2.set_ylim(0, 1.5 * (max(y)))

                    a2.tick_params(axis = 'y', labelcolor = '#8B0000')
                    # toTurn = a2.set_ylabel("Normal Values", rotation = 270, x = 1.08)
                    a2.set_ylabel("Normal Values")
                    # toTurn.set_rotation(270)
                    a.set_xlabel("Numeric Divisions")
                    a.set_ylabel("Frequency")

                    a.legend(bbox_to_anchor=(0, 1.08, 1, .102), loc=3,
                            ncol=1, borderaxespad=0)

                    # print('{:18.16f}'.format(trapz(y, x)))
                    title = graphTitle.get()
                    a.set_title(title, y = 1.08)

                    canvas.draw()

                    # print(len(xAreaPoints))
                    xAreaPoints = x
                    yAreaPoints = y
                    # print(len(xAreaPoints))

        except ValueError, e:
            tkMessageBox.showerror("Data NA Error", "Data at header " + str(gotten)
                + " in file " + str(dataFile) + " is missing or invalid.\n\n" + " Error:" + str(e))
            return
        except TypeError, e:
            tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
                gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
            return
        except KeyError, e:
            tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
                gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
            return
        # writeCsv_lock.acquire()
        # openFile()

        # writeCsv_lock.release()

# def hide_me(event):
#     event.widget.pack_forget()



# writeCsv_lock.release()
app = SeaofBTCapp()
# app.geometry("720x720")

# ani = animation.FuncAnimation(fig, animate, interval = 5000)
app.mainloop() # tkinter functionality



        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.draw()
        # toolbar.update() ERRORS
        # canvas._tkcanvas.pack(side = "top", fill = "both", expand = True)

