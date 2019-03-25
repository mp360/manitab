import sys
import math
import numpy as np
import numpy.polynomial.polynomial as poly
from numpy import ma

import pandas as pd
from scipy.integrate import trapz, simps
import scipy.stats as ss
# import rangeSlider
# from drawnow import *

from matplotlib import dates
import matplotlib.ticker as mticker
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Cursor, MultiCursor
from matplotlib import style
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import Formatter, FixedLocator
from matplotlib import rcParams

import urllib
import json

import Tkinter as tk, tkFileDialog
from Tkinter import Entry, StringVar, IntVar, DoubleVar, Toplevel
import tkMessageBox
import tkFont

# from Tkinter import *
import ttk                 
import csv
import threading
import Queue
import time
import datetime
import itertools

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import pickle as pl

LARGE_FONT = ("Verdana", 12)
MED_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
axcolor = 'white'
# style.use("ggplot")

fig = Figure(dpi = 100)

fig.subplots_adjust(bottom = 0.0, right = .75, top = .85)
fig.subplots_adjust(wspace=.3, hspace=.35)

# fig.subplots_adjust(bottom = 0.18, right = .85, top = .85)
fig.patch.set_facecolor('#E0E0E0')
fig.patch.set_alpha(0.7)

a = fig.add_subplot(111)
a2 = a.twinx()

cursor = None
cursors = []
# a3 = fig.add_subplot(111)
# a3.set_visible(False)
canContainer = None
sessionCanvii = []

binType = "" # the type of data we have, ( dates, percentages, numbers, ...)
prevPlotA = 0 # the value of 
prevPlotB = 0
xAreaPoints = [1]
yAreaPoints = [1]
dataFile = None
globalBins = []
globalNPerBin = []
globalBinning = None
writeCsv_lock = threading.Lock() # Here in case we want to implement multithreading
totalArea = 0.0
globalSigma = 0.0
globalMu = 0.0
globalMin = 0.0
globalMax = 0.0
globalMultiplier = 1.0
globalTitleVar = None
globalSigVar = None
globalBeta = 0.0
globalEta = 0.0
canvasOffsetX = 0.0
canvasOffsetY = 0.0
logBase = 0
# q = Queue() # To use for threading in the future

fillBetFigure = None ## The fill polygon object, a shaded polygon between 
                     # gets cleared when the range changes.

plotButton = None ## Global reference to "Plot" button which is enabled only after
                  # user selects the csv file, header, data type, and number of bins

headerDropDown = None ## Global reference to the "Column Header" dropdown containing the headers
                      # that can be chosen from for this csv file.

sLeft = None   ## Global reference to the left slider (the blue slider)

sRight = None  ## Global reference to the right slider (the red slider)

axRight = None ## Global reference to the axis to draw the right (right, red) max boundary line,
               # updated when red slider is changed

axLeft = None  ## Global reference to the axis to draw the (left, blue) min boundary line,
               # updated when red slider is changed

graphTitle = None ## Global reference to the title of the graph created
globalSAreaLbl = None
leftDeviations = None
rightDeviations = None
fillAxis = None
xSpan = []
ySpan = []
overlaid = False
cancan = None
wasPlotted = False
userSetCursor = False
showTableOfStats = True

statTableTxt = None
maximizedAxis = None
toMaximize = []
toMaximizeType = None
fig_dict = {}
maximizedGeometry = (1,1,1)
pdfTypeCombobox = None
cursorPosLabel = None
listOfRefLines = []
refLines = []
textBoxes = []

def saveFile():
    global writeCsv_lock
    global xAreaPoints
    global yAreaPoints
    global globalBins
    global globalNPerBin
    global globalMu
    global globalSigma
    global fig_dict
    #TODO try-catch when document is open in another program.
    # writeCsv_lock.acquire()
    if (len(globalBins) == 0):
        tkMessageBox.showerror("Save Error", "There is no" +
            " data to save yet.")
        return

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
        if (isinstance(globalBins[len(globalBins) - 1], datetime.datetime)):
            filewriter.writerow(['Distribution x Values (Days)' , 'Distribution y Values', '__________', 'Amt Per Bin', '__', globalSigma, globalMu])
        else:
            filewriter.writerow(['Distribution x Values' , 'Distribution y Values', 'Histo Bins', 'Amt Per Bin', '__', globalSigma, globalMu])
        for i in range(len(xAreaPoints)):
            if (isinstance(globalBins[len(globalBins) - 1], datetime.datetime)):
                if (i < lenBins):
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], globalBins[i].strftime('%m/%d/%Y %H:%M:%S'), globalNPerBin[i], 0])
                else:
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], None, None])
            else:
                if (i < lenBins):
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], globalBins[i], globalNPerBin[i], 0])
                else:
                    filewriter.writerow([xAreaPoints[i], yAreaPoints[i], None, None])
# TODO ??
def saveWeibull():
    return

def saveImage():
    global graphTitle
    curTitle = graphTitle.get()
    if curTitle == "":
        curTitle = "Untitled"

    fname = tkFileDialog.asksaveasfile(defaultextension = ".png", initialfile = curTitle)
    if fname is None:
        return
    fig.savefig(fname = fname.name, dpi=100, frameon = True, facecolor = fig.patch.get_facecolor())


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    shiftedNum = int(n * multiplier)
    return shiftedNum / float(multiplier)


def updateClone(a, b):
    global prevPlotA
    global prevPlotB
    global fillBetFigure
    global axLeft
    global axRight
    global sLeft
    global sRight
    global a2
    global axcolor
    global globalMu
    global globalSigma
    global fillAxis
    global xSpan
    global ySpan
    global globalSAreaLbl
    global totalArea
    global userSetCursor
    global cancan

    if not axLeft.get_visible() and not axRight.get_visible():
        return
    userSetCursor = True

    axLeft.clear()
    axRight.clear()
    sLeft.val = a
    sRight.val = b
    if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
        axLeft.axvspan(0, sRight.val, 0, 1)
        sLeft.val = sRight.val
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvspan(0, sRight.val, 0, 1, facecolor=axcolor)
    elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
        axRight.axvspan(0, sLeft.val, 0, 1, facecolor=axcolor)
        sRight.val = sLeft.val
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
        axLeft.axvspan(0, sLeft.val, 0, 1)
    else:
        axLeft.axvspan(0, sLeft.val, 0, 1)
        axRight.axvspan(0, sRight.val, 0, 1, facecolor=axcolor)
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)

    axLeft.margins(x = 0)
    axRight.margins(x = 0)
    sLeft.valmax = max(xAreaPoints)
    sRight.valmax = max(xAreaPoints)
    axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
    axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
    axRight.grid(False)
    axLeft.set_xticks([])
    axLeft.set_yticks([])
    axRight.set_yticks([])

    prevPlotB = sRight.val
    prevPlotA = sLeft.val
    if fillBetFigure is not None and fillAxis is not None:
        # print('removing')
        # print(fillBetFigure)

        fillBetFigure.remove()
        xSpan = [a for a in xAreaPoints if a < prevPlotB and a > prevPlotA]
        ySpan = [yAreaPoints[i] for i in range(len(xAreaPoints)) if xAreaPoints[i] < prevPlotB and xAreaPoints[i] > prevPlotA]
        fillBetFigure = fillAxis.fill_between(xSpan, 0, ySpan, facecolor = '#4B0082', alpha = 0.4)
        fig.canvas.draw_idle()
        areaUnderCurve = trapz(ySpan, xSpan)
        globalSAreaLbl.set("% Curve shaded: " + '{:.3%}'.format(np.divide(areaUnderCurve,totalArea)))

def update(val):
    global prevPlotA
    global prevPlotB
    global fillBetFigure
    global axLeft
    global axRight
    global sLeft
    global sRight
    global a2
    global axcolor
    global globalMu
    global globalSigma
    global fillAxis
    global xSpan
    global ySpan
    global globalSAreaLbl
    global totalArea
    global userSetCursor

    if userSetCursor: userSetCursor = False
    if not axLeft.get_visible() and not axRight.get_visible():
        return
    
    axLeft.clear()
    axRight.clear()

    if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
        axLeft.axvspan(0, sRight.val, 0, 1)
        sLeft.val = sRight.val
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvspan(0, sRight.val, 0, 1, facecolor=axcolor)
    elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
        axRight.axvspan(0, sLeft.val, 0, 1, facecolor=axcolor)
        sRight.val = sLeft.val
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
        axLeft.axvspan(0, sLeft.val, 0, 1)
    else:
        axLeft.axvspan(0, sLeft.val, 0, 1)
        axRight.axvspan(0, sRight.val, 0, 1, facecolor=axcolor)
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)

    axLeft.margins(x = 0)
    axRight.margins(x = 0)
    sLeft.valmax = max(xAreaPoints)
    sRight.valmax = max(xAreaPoints)
    axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
    axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
    axRight.grid(False)
    axLeft.set_xticks([])
    axLeft.set_yticks([])
    axRight.set_yticks([])

    prevPlotB = sRight.val
    prevPlotA = sLeft.val
    if fillBetFigure is not None and fillAxis is not None:
        fillBetFigure.remove()
        xSpan = [a for a in xAreaPoints if a < prevPlotB and a > prevPlotA]
        ySpan = [yAreaPoints[i] for i in range(len(xAreaPoints)) if xAreaPoints[i] < prevPlotB and xAreaPoints[i] > prevPlotA]
        fillBetFigure = fillAxis.fill_between(xSpan, 0, ySpan, facecolor = '#4B0082', alpha = 0.4)
        fig.canvas.draw_idle()
        areaUnderCurve = trapz(ySpan, xSpan)
        globalSAreaLbl.set("% Curve shaded: " + '{:.3%}'.format(np.divide(areaUnderCurve,totalArea)))

def integrate(integrateY, integrateX):
    return '{:18.16f}'.format(trapz(integrateY, integrateX))


def openFile():
    global dataFile
    global plotButton
    file1 = tkFileDialog.askopenfile(mode = 'rb', title = 'Choose a file')
    if file1 is None:
        return
    else:
        try:
            pd.read_csv(file1.name)
            data = pd.read_csv(file1.name, nrows = 1)
            vals = tuple(data)
            headerDropDown['values'] = vals
            headerDropDown.current(0)
            plotButton.config(state="normal")
        except Exception, e:
            tkMessageBox.showerror("Unknown File", "The file you provided is either not of type .csv. or is empty.")
            return
    dataFile = file1.name

#_______________________________________________________________________________________________________
class MercatorLatitudeScale(mscale.ScaleBase):
    """
    Scales data in range -pi/2 to pi/2 (-90 to 90 degrees) using
    the system used to scale latitudes in a Mercator projection.

    The scale function:
      ln(tan(y) + sec(y))

    The inverse scale function:
      atan(sinh(y))

    Since the Mercator scale tends to infinity at +/- 90 degrees,
    there is user-defined threshold, above and below which nothing
    will be plotted.  This defaults to +/- 85 degrees.

    source:
    http://en.wikipedia.org/wiki/Mercator_projection
    """
    # Axis used after rank regression is done on data.

    # The scale class must have a member ``name`` that defines the
    # string used to select the scale.  For example,
    # ``gca().set_yscale("mercator")`` would be used to select this
    # scale.
    name = 'mercator'

    # def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
    def __init__(self, axis, thresh=1, *args, **kwargs):

        """
        Any keyword arguments passed to ``set_xscale`` and
        ``set_yscale`` will be passed along to the scale's
        constructor.

        thresh: The degree above which to crop the data.
        """
        mscale.ScaleBase.__init__(self)
        if thresh > 1:
            raise ValueError("thresh must be less than pi/2")
        self.thresh = thresh

    def get_transform(self):
        """
        Override this method to return a new instance that does the
        actual transformation of the data.

        The MercatorLatitudeTransform class is defined below as a
        nested class of this one.
        """
        return self.MercatorLatitudeTransform(self.thresh)

    def set_default_locators_and_formatters(self, axis):
        """
        Override to set up the locators and formatters to use with the
        scale.  This is only required if the scale requires custom
        locators and formatters.  Writing custom locators and
        formatters is rather outside the scope of this example, but
        there are many helpful examples in ``ticker.py``.

        In our case, the Mercator example uses a fixed locator from
        -90 to 90 degrees and a custom formatter class to put convert
        the radians to degrees and put a degree symbol after the
        value::
        """
        class DegreeFormatter(Formatter):
            def __call__(self, x, pos=None):
                return "%g" % (x * 100)

        # axis.set_major_locator(FixedLocator(
        #     np.radians(np.arange(-90, 90, 10))))

        axis.set_major_locator(FixedLocator(
            np.array([.01, .05, .10, .50, .90, .99]) ))

        axis.set_minor_locator(FixedLocator(np.array(list(np.arange(.01, .10, .01)) + list(np.arange(.10, .99, .10)) + [.99])))
        axis.set_major_formatter(DegreeFormatter())
        # axis.set_minor_formatter(DegreeFormatter())

    def limit_range_for_scale(self, vmin, vmax, minpos):
        """
        Override to limit the bounds of the axis to the domain of the
        transform.  In the case of Mercator, the bounds should be
        limited to the threshold that was passed in.  Unlike the
        autoscaling provided by the tick locators, this range limiting
        will always be adhered to, whether the axis range is set
        manually, determined automatically or changed through panning
        and zooming.
        """
        vmin = 0.007438631040187271
        vmax = 0.9980521961829169    
        return max(vmin, -self.thresh), min(vmax, self.thresh)

    class MercatorLatitudeTransform(mtransforms.Transform):
        # There are two value members that must be defined.
        # ``input_dims`` and ``output_dims`` specify number of input
        # dimensions and output dimensions to the transformation.
        # These are used by the transformation framework to do some
        # error checking and prevent incompatible transformations from
        # being connected together.  When defining transforms for a
        # scale, which are, by definition, separable and have only one
        # dimension, these members should always be set to 1.
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True

        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh

        def transform_non_affine(self, a):
            """
            This transform takes an Nx1 ``numpy`` array and returns a
            transformed copy.  Since the range of the Mercator scale
            is limited by the user-specified threshold, the input
            array must be masked to contain only valid values.
            ``matplotlib`` will handle masked arrays and remove the
            out-of-range data from the plot.  Importantly, the
            ``transform`` method *must* return an array that is the
            same shape as the input array, since these values need to
            remain synchronized with values in the other dimension.
            """
            masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
            if masked.mask.any():
                # return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
                # return np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in masked])
                # print(np.array([np.log(np.log(1/(1-xi))) for xi in masked]))
                return np.array([np.log(np.log(1/(1-xi))) for xi in masked])

            else:
                # return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))
                # return  np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in a])
                # print(np.array([np.log(np.log(1/(1-xi))) for xi in masked]))
                return np.array([np.log(np.log(1/(1-xi))) for xi in masked])

        def inverted(self):
            """
            Override this method so matplotlib knows how to get the
            inverse transform for this transform.
            """
            return MercatorLatitudeScale.InvertedMercatorLatitudeTransform(
                self.thresh)

    class InvertedMercatorLatitudeTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True

        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh

        def transform_non_affine(self, a):
            # return np.array([1 + (-1*(np.exp(np.exp( (1-np.exp(-1*((xi/p2)**p0))) )))**(-1) ) for xi in a])
            # return np.arctan(np.sinh(a))
            return np.array([1 + (-1*(np.exp(np.exp(xi)))**(-1) ) for xi in a])

        def inverted(self):
            return MercatorLatitudeScale.MercatorLatitudeTransform(self.thresh)
mscale.register_scale(MercatorLatitudeScale)
#________________________________________________________________________________________________________

class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""
    tuples = None
    headers = None
    container = None
    def __init__(self, headerL, tupleVals, parent):
        self.tuples = tupleVals
        tuples = self.tuples
        self.headers = headerL
        headers = self.headers
        self.tree = None
        self.parent = parent
        # self.container = thisFrame
        # container = self.container
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        # s = """\click on header to sort by that column to change width of column drag boundary"""
        # msg = ttk.Label(wraplength="4i", justify="left", anchor="n", padding=(10, 2, 10, 6), text=s)
        # msg.pack(fill='x')
        container1 = self.parent
        container = ttk.Frame(container1)
        # create a treeview with dual scrollbars
        B1 = ttk.Button(container, text="Okay", command=self.dostuff)
        B1.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        self.tree = ttk.Treeview(container1, columns=self.headers, show="headings")
        vsb = ttk.Scrollbar(container1, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(container1, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container1)
        vsb.grid(column=1, row=0, sticky='ns', in_=container1)
        hsb.grid(column=0, row=1, sticky='ew', in_=container1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def dostuff(self):
        return

    def _build_tree(self):
        for col in self.headers:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col, width=tkFont.Font().measure(col.title()))

        for item in self.tuples:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.headers[ix],width=None)<col_w:
                    self.tree.column(self.headers[ix], width=col_w)
def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    print([tree.item(child)['values'] for child in tree.get_children('')])
    print(data)
    data.sort(reverse=descending)
    print(data)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))
#__________________________________________________________________________________
class InformativeCursor(Cursor):
    def onmove(self, event):
        global cursorPosLabel
        global globalMultiplier
        global logBase
        if event.xdata != None and event.ydata != None:
            if globalMultiplier > 1.0:
                cursorPosLabel.set(str(truncate(event.xdata, 5)) +'e+' + str(logBase) +  ', ' + str(truncate(event.ydata, 5)))
            else:
                cursorPosLabel.set(str(truncate(event.xdata, 5)) + ', ' + str(truncate(event.ydata, 5)))

        """on mouse motion draw the cursor if visible"""
        if self.ignore(event):
            return
        if not self.canvas.widgetlock.available(self):
            return
        if event.inaxes != self.ax:
            self.linev.set_visible(False)
            self.lineh.set_visible(False)

            if self.needclear:
                self.canvas.draw()
                self.needclear = False
            return
        self.needclear = True
        if not self.visible:
            return
        self.linev.set_xdata((event.xdata, event.xdata))

        self.lineh.set_ydata((event.ydata, event.ydata))
        self.linev.set_visible(self.visible and self.vertOn)
        self.lineh.set_visible(self.visible and self.horizOn)
        try:
            self._update()
        except:
            self.canvas.draw_idle()

#___________________________________________________________________________________________________
class FancyFigureCanvas(FigureCanvasTkAgg, tk.Listbox):
    popup_menu = None
    axpopup = None
    maximized = False
    gridlines_enabled = False
    thisFigure = None
    addable_menu = None
    clickedAxes = None
    cursorLocation = None
    popup_multi = None
    removable_menu = None

    def __init__(self, x, parent, *args, **kwargs):
        FigureCanvasTkAgg.__init__(self, x, parent, *args, **kwargs)
        global axRight
        global axLeft
        global fig

        self.cursorLocation = None
        self.clickedAxes = None
        self.thisFigure = x
        thisFigure = self.thisFigure
        self.popup_menu = tk.Menu(parent, tearoff=0)
        self.popup_menu.add_command(label="Show Slider", command=self.toggle_slider_vis)
        self.popup_menu.add_command(label = "Hide Table of Stats", command =self.toggle_table_of_stats)
        self.popup_menu.add_command(label="Hide Histogram", command=self.dostuff)
        self.popup_menu.add_command(label="Save as Image", command=saveImage)

        self.addable_menu = tk.Menu(parent, tearoff = 0)
        self.addable_menu.add_command(label = "Reference Line", command=self.ref_line_wrapper)
        self.addable_menu.add_command(label = "Chart Title", command= self.set_graph_title1)
        addable_menu = self.addable_menu
        self.popup_menu.add_cascade(label="Add", menu = self.addable_menu)
        # self.popup_menu.add_command(label = "")
        self.removable_menu = tk.Menu(parent, tearoff = 0)
        self.removable_menu.add_command(label = "Reference Lines", command=self.rem_ref_lines)
        self.removable_menu.add_command(label = "Secondary Axis Ticks", command= self.dostuff)
        removable_menu = self.removable_menu
        self.popup_menu.add_cascade(label="Remove", menu = self.removable_menu)
        popup_menu = self.popup_menu

        self.popup_multi = tk.Menu(parent, tearoff=0)
        self.popup_multi.add_command(label="Maximize", command= self.maximize_wrapper)
        self.popup_multi.add_cascade(label="Add", menu = self.addable_menu)
        self.popup_multi.add_command(label="See All Stats", command = self.dostuff)
        popup_multi = self.popup_multi

        self.axpopup = tk.Menu(parent, tearoff=0)
        self.axpopup.add_command(label="Hide", command = self.toggle_slider_vis)
        self.axpopup.add_command(label="Set Cursor Values", command=self.set_slider_values)
        axpopup = self.axpopup


    

    def toggle_slider_vis(self):
        global showTableOfStats
        if axRight != None and axLeft != None:
            axRight.set_visible(not axRight.get_visible())
            axLeft.set_visible(not axLeft.get_visible())
            if not axRight.get_visible(): 
                if not showTableOfStats:
                    fig.subplots_adjust(bottom = 0.18, right = .85, top = .85)
                else:
                    fig.subplots_adjust(bottom = 0.18, right = .75, top = .85)
                # a2.set_xlim(min(x), (max(x)))#tocomment
                self.popup_menu.entryconfigure(0, label="Show Slider")
            else:
                if not showTableOfStats:
                    fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
                else:
                    fig.subplots_adjust(bottom = 0.25, right = .75, top = .85)
                # fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
                self.popup_menu.entryconfigure(0, label="Hide Slider")
        self.draw()

    
    def toggle_table_of_stats(self):
        global statTableTxt
        global showTableOfStats
        if axRight != None and axLeft != None:
            # clear canvas and redraw
            statTableTxt.set_visible(not statTableTxt.get_visible())
            showTableOfStats = statTableTxt.get_visible()
            if not statTableTxt.get_visible():
                if not axRight.get_visible():
                    fig.subplots_adjust(bottom = 0.18, right = .85, top = .85)
                else:
                    fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
                    # fig.subplots_adjust(bottom = 0.18, right = .75, top = .85)
                self.popup_menu.entryconfigure(1, label = "Show Table of Stats")
            else:
                if not axRight.get_visible():
                    fig.subplots_adjust(bottom = 0.18, right = .75, top = .85)
                else:
                    fig.subplots_adjust(bottom = 0.25, right = .75, top = .85)
                self.popup_menu.entryconfigure(1, label="Hide Table of Stats")
        self.draw()
                


    def dostuff(self):
        return 


    def rem_ref_lines(self):
        global refLines
        global listOfRefLines
        global textBoxes
        global cancan
        global fig_dict
        refLines = fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['refLines']
        textBoxes = fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['textBoxes']
        for refLine in refLines:
            refLine.remove()
        for entryBox in listOfRefLines:
            entryBox.destroy()
        for txt in textBoxes:
            txt.remove()

        listOfRefLines = []
        refLines = []
        textBoxes = []
        fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['refLines'] = []
        fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['textBoxes'] = []
        cancan.draw_idle()
    def maximize_wrapper(self):
        maximize_axes(self.clickedAxes, maximizedGeometry)
    
    def ref_line_wrapper(self):
        popupmsg('Add Reference Line 1')

    def set_graph_title1(self):
        popupmsg('Figure Title')
    
    def set_graph_title2(self):
        popupmsg('Graph Title')

    def set_slider_values(self):
        if axRight != None and axLeft != None:
            popupmsg("Select your Limits")

def maximize_axes(ax, geometry=(1,1,1)):
    #create new figure.
    global fig
    global cancan
    global maximizedAxis
    global maximizedGeometry
    global axLeft
    global axRight


    if (fig is not None and ax is not None):
        fig.delaxes(ax)
        for axis in fig.get_axes():
            if axis is not a and axis is not a2 and axis !=axRight and axis != axLeft:
                axis.set_visible(not axis.get_visible())
        if ax.get_geometry() != geometry: # need to restore, current axis of geometry
            temp = ax.get_geometry() # store original geometry, used as geometry next time
            ax.change_geometry(*geometry) # change the geometry
            maximizedGeometry = temp
        ax = fig.add_axes(ax) # add new axis to figure
        maximizedAxis = ax
        cancan.draw()

        if geometry == (1,1,1):
            cancan.popup_multi.entryconfigure(0, label="Restore")
        else: 
            cancan.popup_multi.entryconfigure(0, label="Maximize")

    return




def on_graph_hover(event):
    print( event.inaxes)
    cursor = InformativeCursor(event.inaxes, useblit=True, color='red', linewidth=.5)
    print(cursor)


def on_press(event):
    global a
    global a2
    global fig
    global canvasOffsetX
    global canvasOffsetY
    global axRight
    global axLeft
    global canContainer
    global cancan

    if event.button != 3: return
    try:
        print(app.winfo_x(), app.winfo_y())
        print(cancan.get_width_height())
        print(event)
        print(event.inaxes is a)
        print(event.inaxes is a2)
        # TODO rectify menu position when a left sidebar is present.
        cancan.clickedAxes = event.inaxes
        print event.inaxes
        cancan.cursorLocation = (event.xdata, event.ydata)
        print(event.inaxes)
        print(event.inaxes in fig.get_axes())
        if axRight.get_visible() and event.inaxes in [axRight, axLeft]:
            print("UES")
            print(cancan.axpopup.winfo_height())
            cancan.axpopup.tk_popup(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY, 0)
        elif (cancan.clickedAxes != None and not a.get_visible() and
                event.inaxes != axLeft and event.inaxes != axRight and 
                not a2.get_visible() and event.inaxes != a and event.inaxes != a2):
            # cancan.addable_menu.add_command(label = "Figure Title", command = cancan.set_graph_title1)
            cancan.addable_menu.entryconfigure(1,command = cancan.set_graph_title2)
            cancan.popup_multi.tk_popup(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY, 0)
        else:
            cancan.addable_menu.entryconfigure(1, command = cancan.set_graph_title1)
            cancan.popup_menu.tk_popup(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY, 0)
        # TODO self.filemenu2.delete(0) # deletes first item in menu
        # self.filemenu2.delete("Stop") # delete item with the label "Stop"
    finally:
        cancan.popup_menu.grab_release()
        cancan.axpopup.grab_release()
        cancan.popup_multi.grab_release()

def popupmsg(purpose):
    global leftDeviations
    global rightDeviations
    global globalMu
    global globalSigma
    global graphTitle
    global cancan
    global listOfRefLines

    def validate():
        start = lValue.get()
        end = rValue.get()
        finished = False
        try:
            a = min(xAreaPoints)
            b = max(xAreaPoints)
            
            if stType.get():
                if (leftDeviations.get() == u"-1\u03c3"):
                    a = globalMu - globalSigma
                elif (leftDeviations.get() == u"-2\u03c3"):
                    a = globalMu - 2*globalSigma
                elif (leftDeviations.get() == u"\u03bc"):
                    a = globalMu
                elif (leftDeviations.get() == u"+1\u03c3"):
                    a = globalMu + globalSigma
                elif (leftDeviations.get() == u"+2\u03c3"):
                    a = globalMu + 2*globalSigma
                if a > max(xAreaPoints): a = max(xAreaPoints)
                if a < min(xAreaPoints): a = min(xAreaPoints)

                if (rightDeviations.get() == u"+1\u03c3"):
                    b = globalMu + globalSigma
                elif (rightDeviations.get() == u"+2\u03c3"):
                    b = globalMu + 2*globalSigma
                elif (rightDeviations.get() == u"\u03bc"):
                    b = globalMu
                elif (rightDeviations.get() == u"-1\u03c3"):
                    b = globalMu - globalSigma
                elif (rightDeviations.get() == u"-2\u03c3"):
                    b = globalMu - 2*globalSigma
                if b > max(xAreaPoints): b = max(xAreaPoints)
                if b < min(xAreaPoints): b = min(xAreaPoints)
            elif numType.get():
                if start not in ['<', '<<']:
                    a = float(start)
                if end not in ['>>', '>']:
                    b = float(end)
            else:
                # show error, need identify which type of shading it is.
                tkMessageBox.showerror("Limit Type not chosen", "Please check the type of limit you would like to use.\n")
                return 
            if a > b:
                tkMessageBox.showerror("Invalid Limits", "Please check that the value for cursor A is less than or equal to" +
                 " the value for cursor B.\n")
                return 
            if len(xAreaPoints) > 0 and (a < min(xAreaPoints) or b > max(xAreaPoints)):
                tkMessageBox.showerror("Invalid Limit Value", "One or more limit values are invalid. Please check that the value for cursor A and" +
                 " cursor B are within the range of the dataset.\n")
                return 
            userSetCursor = True
            updateClone(a, b)
            popup.destroy()
            
        except ValueError, e:
            print(start)
            if start == '' or end == '':
                tkMessageBox.showerror("Missing Limits", "Please enter a float value for cursor A and cursor B.\n")
            else:             
                tkMessageBox.showerror("Invalid Limit Values", "One or more limit values are invalid. Please check that you have entered a float value.\n")
            # return 

    def toggle_access(purpose):
        if (purpose == 'Switch Ref Line Axes'):
            checkedX = toMarkX.get()
            checkedY = toMarkY.get()
            if checkedX == checkedY:
                chkToMarkX.config(state='normal')
                chkToMarkY.config(state='normal')
            elif checkedY:
                chkToMarkX.config(state='disabled')
                axToMarkVar.set('Y location 1: ')
                entryVar.set(str(cancan.cursorLocation[1]))
            elif checkedX:
                chkToMarkY.config(state='disabled')
                axToMarkVar.set('X location 1: ')
                entryVar.set(str(cancan.cursorLocation[0]))

        elif (purpose == 'Switch Shading Limit Type'):
            checkedST = stType.get()
            checkedNum = numType.get()
            if checkedST == checkedNum:
                chkStdevShading.config(state='normal')
                lLimCmb.config(state="normal")
                rLimCmb.config(state="normal")
                chkNumShading.config(state='normal')
                lValue.config(state="normal")
                rValue.config(state="normal")
            elif checkedST:
                chkNumShading.config(state='disabled')
                lValue.config(state="disabled")
                rValue.config(state="disabled")
            elif checkedNum:
                chkStdevShading.config(state='disabled')
                lLimCmb.config(state="disabled")
                rLimCmb.config(state="disabled")

    def addFigureTitle():
        print(cancan.clickedAxes)
        cancan.thisFigure.suptitle(graphTitle.get(), fontsize=14, fontweight='bold')
        cancan.draw_idle()
        popup.destroy()
        return

    def addChartTitle():
        print(cancan.clickedAxes)
        cancan.clickedAxes.set_title(graphTitle.get(), y =1.04)
        cancan.draw_idle()
        popup.destroy()
        return

    def dostuff():
        return

    def addMoreRefLines(frame, addButton):
        global listOfRefLines
        if len(listOfRefLines) < 5:
            name = ttk.Entry(frame)
            name.grid(row=4 + (len(listOfRefLines)), column=2, columnspan=2, sticky="ew", pady=5, padx=5)

            listOfRefLines += [name]

            if toMarkX.get():
                axChosen = 'X'
            elif toMarkY.get():
                axChosen = 'Y'

            l = ttk.Label(frame, text = str(axChosen) + " location " + str(len(listOfRefLines)) + ": ", font = SMALL_FONT)
            l.grid(sticky = "e", row=3 + (len(listOfRefLines)), column= 1, padx = 2, pady = 4)
        if len(listOfRefLines) >= 5:
            addButton.config(state = 'disabled')
        return

    def on_closing1():
        global listOfRefLines
        listOfRefLines = []
        popup.destroy()

    def prime_nxt_popup(purpose, hiddenWidgs, shownWidgs):
        print(hiddenWidgs)
        tmpHiddenWidgs = []
        tmpShownWidgs = []

        if purpose == 'Add Reference Line 1':
            if not toMarkX.get() and not toMarkY.get():
                tkMessageBox.showerror("", "Please choose if you would like to mark X locations or Y locations.\n")
                return
            for widg in hiddenWidgs:
                widg.grid()
                tmpHiddenWidgs += [widg]
            for widg in shownWidgs:
                widg.grid_remove()
                tmpShownWidgs += [widg]
            hiddenWidgs = tmpHiddenWidgs
            shownWidgs = tmpShownWidgs
            B1.config(command = plotAllRefLines)

    def plotAllRefLines():
        global listOfRefLines
        global xAreaPoints
        global yAreaPoints
        global fig
        global cancan
        global refLines
        global textBoxes
        global globalMultiplier

        try:
            for entry in listOfRefLines:
                print(entry)
                entryGet = entry.get()
                a = 0.0
                if entryGet == '': continue

                if entryGet in ['>>', '>']:
                    if toMarkX.get():
                        a = max(xAreaPoints)
                    elif toMarkY.get():
                        a = max(yAreaPoints)
                elif entryGet in ['<<', '<']:
                    if toMarkX.get():
                        a = min(xAreaPoints)
                    elif toMarkY.get():
                        a = min(yAreaPoints)
                else:
                    a = float(entryGet)

                print(a)
                if toMarkY.get():
                    if len(yAreaPoints) > 0 and (a > max(cancan.clickedAxes.get_yticks()) or a < 0):
                        # ALERT line not graphed
                        continue
                elif toMarkX.get():
                    if len(xAreaPoints) > 0 and (a > max(xAreaPoints) or a < min(xAreaPoints)):
                        continue
                        # ALERT line not graphed

                # elif len(xAreaPoints) > 0 and (a < min(xAreaPoints)):
                #     a = min(xAreaPoints)
                    # tkMessageBox.showerror("Invalid Limit Value", "One or more limit values are invalid. Please check that the value for cursor A and" +
                    # " cursor B are within the range of the dataset.\n")
                
                modTicks = []


                # fig_dict[fig]['dictOfAxes'][a3] = {}
                # fig_dict[fig]['dictOfAxes'][a3]['refLines'] = []
                    

                if toMarkX.get():
                    for i in cancan.clickedAxes.get_yticks():
                        if i != max(cancan.clickedAxes.get_yticks()):
                            modTicks += [i]
                    # refLines += [cancan.clickedAxes.axvline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]
                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['refLines'] += \
                        [cancan.clickedAxes.axvline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]

                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['textBoxes'] += \
                        [cancan.clickedAxes.text(a, max(modTicks) , str(truncate(a, 3)), style='italic', rotation=270,
                            bbox={'lw':0.0 ,'boxstyle':'round', 'facecolor':'white', 'alpha':0.6, 'pad':0.15})]
                else:
                    for i in cancan.clickedAxes.get_xticks():
                        if i != max(cancan.clickedAxes.get_xticks()):
                            modTicks += [i]
                    # refLines += [cancan.clickedAxes.axhline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]
                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['refLines'] += \
                        [cancan.clickedAxes.axhline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]
                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['refLines'] += \
                        [cancan.clickedAxes.text(max(modTicks), a, str(truncate(a, 3)), style='italic', rotation=0,
                            bbox={'lw':0.0 ,'boxstyle':'round', 'facecolor':'white', 'alpha':0.6, 'pad':0.15})]

                print(refLines)
                # refLines += [cancan.clickedAxes.axvline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]


                # print(cancan.clickedAxes.text(a, max(modTicks) , str(truncate(a, 3)), style='italic', rotation = 270,
                #         bbox={'lw':0.0 ,'boxstyle':'round', 'facecolor':'white', 'alpha':0.6, 'pad':0.15}))

            cancan.draw_idle()
            listOfRefLines = []
            popup.destroy()
        except ValueError, e:
            tkMessageBox.showerror("Invalid Limit Values", "One or more values are invalid. Please check that you have entered float values.\n")


    popup = Toplevel()
    print(popup)
    frame = ttk.Frame(popup, width=300, height=100)
    frame.grid( row=0, column=0, sticky="ew", pady=5, padx=5)

    popup.grab_set()
    popup.resizable(0,0)
    popup.wm_title(purpose)
    hiddenWidgs = []
    shownWidgs = []

    if purpose == 'Table':
        # popup = tk.Tk()

        car_header = ['car', 'repair','misc','jala']
        car_list = [
        ('Hyundai', 'brakes') ,
        ('Honda', 'light') ,
        ('Lexus', 'battery') ,
        ('Benz', 'wiper') ,
        ('Ford', 'tire') ,
        ('Chevy', 'air') ,
        ('Chrysler', 'piston') ,
        ('Toyota', 'brake pedal') ,
        ('BMW', 'seat')
        ]

        listbox = MultiColumnListbox(car_header, car_list, popup)

    if purpose == 'Add Reference Line 1':
        toMarkX = IntVar()
        toMarkX.set(0)
        chkToMarkX = ttk.Checkbutton(frame, text='Mark X Locations', variable=toMarkX, command = lambda: toggle_access('Switch Ref Line Axes'))
        chkToMarkX.grid( row=2, column=2, sticky="e", pady=5, padx=5)

        toMarkY = IntVar()
        toMarkY.set(0)
        chkToMarkY = ttk.Checkbutton(frame, text='Mark Y Locations', variable=toMarkY, command = lambda: toggle_access('Switch Ref Line Axes'))
        chkToMarkY.grid( row=2, column=3, sticky="e", pady=5, padx=5)

        axToMarkVar = StringVar() # set during toggling of the axes.
        # axToMarkVar.set('X location 1: ')

        entryVar = StringVar()
        entryVar.set(str(cancan.cursorLocation[0]))
        locEntry = ttk.Entry(frame, textvariable = entryVar)
        # if cursorPos != None: locEntry.set(cursorPos[0])
        # locEntry.insert(0, cancan.cursorLocation[0])
        locEntry.grid(row=4, column=2, columnspan=2, sticky="ew", pady=5, padx=5)
        listOfRefLines += [locEntry]

        instructLabel = ttk.Label(frame, textvariable = axToMarkVar, font = SMALL_FONT)
        instructLabel.grid(sticky = "e", row=4, column= 1, padx = 2, pady = 4)

        makeAnotherLineButton = ttk.Button(frame, text="+")
        makeAnotherLineButton.grid(row=9, column=1, columnspan =3, sticky="ew", pady=5, padx=5)
        makeAnotherLineButton.config(command = lambda: addMoreRefLines(frame, makeAnotherLineButton))

        shownWidgs += [chkToMarkX, chkToMarkY]
        hiddenWidgs += [makeAnotherLineButton, instructLabel, locEntry]
        for widgs in hiddenWidgs:
            widgs.grid_remove()

        B1 =  ttk.Button(popup, text="Okay")
        # B1 = ttk.Button(popup, text="Okay", command = prime_nxt_popup(purpose))
        B1.grid(row=15, column=3,  sticky="ew", pady=5, padx=5)
        B1.config(command = lambda: prime_nxt_popup(purpose, hiddenWidgs, shownWidgs))

        popup.protocol("WM_DELETE_WINDOW", on_closing1)
    
    if purpose == 'Graph Title':
        name = ttk.Entry(frame, textvariable = graphTitle)
        graphTitle.set(cancan.clickedAxes.get_title())
        name.grid(row=4, column=2, columnspan=2, sticky="ew", pady=5, padx=5)
        titleLabel = ttk.Label(frame, text = "Graph Title:", font = SMALL_FONT)
        titleLabel.grid(sticky = "e", row=4, column= 1, padx = 2, pady = 4)

        B1 = ttk.Button(popup, text="Okay", command = addChartTitle)
        B1.grid(row=5, column=3, sticky="ew", pady=5, padx=5)
    if purpose == 'Figure Title':
        name = ttk.Entry(frame, textvariable = graphTitle)
        name.grid(row=4, column=2, columnspan=2, sticky="ew", pady=5, padx=5)
        titleLabel = ttk.Label(frame, text = "Figure Title:", font = SMALL_FONT)
        titleLabel.grid(sticky = "e", row=4, column= 1, padx = 2, pady = 4)

        B1 = ttk.Button(popup, text="Okay", command = addFigureTitle)
        B1.grid(row=5, column=3, sticky="ew", pady=5, padx=5)
    if purpose == 'Select your Limits':
        stType = IntVar()
        stType.set(0)
        chkStdevShading = ttk.Checkbutton(frame, text='Use StDev from Mean', variable=stType, command = lambda: toggle_access('Switch Shading Limit Type'))
        chkStdevShading.grid( row=2, column=2, sticky="e", pady=5, padx=5)

        numType = IntVar()
        numType.set(0)
        chkNumShading = ttk.Checkbutton(frame, text='Use Specific Values', variable=numType, command = lambda: toggle_access('Switch Shading Limit Type'))
        chkNumShading.grid( row=2, column=3, sticky="e", pady=5, padx=5)

        # custom Left limit Combobox of the normal shader
        leftDeviations = StringVar()
        lLimCmb = ttk.Combobox(frame, state="readonly",
            values=("<<", u"-2\u03c3", u"-1\u03c3", u"\u03bc", u"+1\u03c3", u"+2\u03c3"), textvariable = leftDeviations)
        lLimCmb.grid( row=3, column=2, sticky="e", pady=5, padx=5)
        lLimCmb.current(0)

        # custom Right limit of the normal shader
        rightDeviations = StringVar()
        rLimCmb = ttk.Combobox(frame, state="readonly",
            values=(">>", u"-2\u03c3", u"-1\u03c3",  u"\u03bc", u"+1\u03c3", u"+2\u03c3"), textvariable = rightDeviations)
        rLimCmb.grid( row=4, column=2, sticky="e", pady=5, padx=5)
        rLimCmb.current(0)

        leftValue = IntVar()
        rightValue = IntVar()

        leftValue.set('<<')
        rightValue.set('>>')

        lValue = ttk.Entry(frame, textvariable = leftValue) # validate = 'key', validatecommand = vcmd)
        lValue.grid(row=3, column=3, sticky="ew", pady=5, padx=5)

        rValue = ttk.Entry(frame, textvariable = rightValue ) # validate = 'key', validatecommand = vcmd)
        rValue.grid(row=4, column=3, sticky="ew", pady=5, padx=5)

        labelL = ttk.Label(frame, text='L:', font=MED_FONT)
        labelL.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

        labelR = ttk.Label(frame, text='R:', font=MED_FONT)
        labelR.grid(row=4, column=1, sticky="ew", pady=5, padx=5)
        B1 = ttk.Button(popup, text="Okay", command = validate)
        B1.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
    popup.mainloop()


class SeaofBTCapp(tk.Tk):
    def __init__(self, *args, **kwargs):
        global cancan
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default = "mlogo.ico")
        tk.Tk.wm_title(self, "Graphing Program")

        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky = "nsew")
        
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff = 0)
        filemenu.add_command(label = "Export to CSV", command = lambda: saveFile())
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command = sys.exit)
        menubar.add_cascade (label = "File", menu = filemenu)

        modemenu = tk.Menu(menubar, tearoff = 0)
        modemenu.add_command(label = "Reliability Analysis", command = lambda: weibullPPF(cancan)) ### TODO weibull analyzis
        modemenu.add_separator()
        modemenu.add_command(label = "Diff of Means")
        menubar.add_cascade (label = "Stats", menu = modemenu)


        graphmenu = tk.Menu(menubar, tearoff = 0)
        graphmenu.add_command(label = "Histogram/Probability Distribution", command = lambda: pdfPriming(cancan)) ### TODO
        graphmenu.add_separator()
        menubar.add_cascade (label = "Graph", menu = graphmenu)

        wkspmenu = tk.Menu(menubar, tearoff = 0)
        wkspmenu.add_command(label = "Save Workspace", command = lambda: saveWorkspace()) ### TODO weibull analyzis
        wkspmenu.add_separator()
        wkspmenu.add_command(label = "Open Workspace", command = lambda: openWorkspace())
        menubar.add_cascade (label = "Workspace...", menu = wkspmenu)

        tk.Tk.config(self, menu = menubar)
        self.show_frame(PageThree)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "Start Page", font = LARGE_FONT)
        label.grid(sticky = "n", pady = 10, padx = 10)

        button1 = ttk.Button(self, text = "Visit Page 1",
            command = lambda: controller.show_frame(PageOne))
        button1.grid(row=0, column=1)

        button2 = ttk.Button(self, text = "Visit Page 2",
            command = openFile)
        button2.grid(row=0, column=2)

        button3 = ttk.Button(self, text = "Graph Page",
            command = lambda: controller.show_frame(PageThree))
        button3.grid(row=0, column=3)


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "PAGE 1", font = LARGE_FONT)
        label.grid(sticky = "n", pady = 10, padx = 10)

        button1 = ttk.Button(self, text = "Back to Home",
            command = lambda: controller.show_frame(StartPage))
        button1.grid(row=0, column=1)

        button2 = ttk.Button(self, text = "To Page 2",
            command = lambda: controller.show_frame(PageTwo))
        button2.grid(row=0, column=2)


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text = "PAGE 2", font = LARGE_FONT)
        label.grid(sticky = "n", pady = 10, padx = 10)

        button1 = ttk.Button(self, text = "Back to Home",
            command = lambda: controller.show_frame(StartPage))
        button1.grid(row=0, column=1)

        button2 = ttk.Button(self, text = "To Page 1",
            command = lambda: controller.show_frame(PageOne))
        button2.grid(row=0, column=2)

def reset(event):
    sLeft.reset()
    sRight.reset()


def weib(x,lamb,k):
    return (k / lamb) * (x / lamb)**(k-1) * np.exp(-(x/lamb)**k)

def saveWorkspace():
    global fig_dict
    global fillBetFigure

    if fig_dict[fig]['loaded']:
        if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
            fig_dict[fig]['slider_axes'][2] = fillBetFigure
    else:
        if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
            fig_dict[fig]['slider_axes'] += [fillBetFigure]

    pl.dump(fig_dict,file('savedWkspc1.pickle','wb'))
    return

def init_fig_dict(axes):
    global fig_dict
    fig_dict[fig]['dictOfAxes'][axes] = {}
    fig_dict[fig]['dictOfAxes'][axes]['refLines'] = []
    fig_dict[fig]['dictOfAxes'][axes]['textBoxes'] = []
    fig_dict[fig]['dictOfAxes'][axes]['addAxes'] = {}
    fig_dict[fig]['dictOfAxes'][axes]['specsTable'] = {}
    # # TODO TODO TODO
    # fig_dict[fig] = {}
    # fig_dict[fig]['fig_next'] = None
    # fig_dict[fig]['sessionType'] = 'RELA'
    # fig_dict[fig]['numAxes'] = 4
    # fig_dict[fig]['csv_src'] = dataFile
    # fig_dict[fig]['slider_axes'] = [axLeft, axRight]
    # fig_dict[fig]['dictOfAxes'] = {}

class PageThree(tk.Frame):
    buttContainer = None
    toolbarContainer = None
    def __init__(self, parent, controller):
        global dataFile
        global plotButton
        global errLabel
        global headerDropDown
        global curHeader
        global globalBinning
        global sLeft
        global sRight
        global axLeft
        global axRight
        global axcolor
        global graphTitle
        global globalMu
        global globalTitleVar
        global globalSigVar
        global globalSAreaLbl
        global leftDeviations
        global rightDeviations
        global cancan
        global pdfTypeCombobox
        global cursor
        global a 
        global a2
        global cursorPosLabel
        global canvasOffsetX
        global canvasOffsetY
        global fig
        global statTableTxt
        global canContainer

        def toggle_this_frame_vis( container, expandButton):
            global fig
            if not toExpand.get():
                buttContainer.grid(row=0, column=3, rowspan=2, sticky="nsew", pady=5, padx=5)
                expandButton.configure(text='-')
            else:
                buttContainer.grid_forget()
                expandButton.configure(text='+')

        def load_workspace_figure():
            global axRight
            global axLeft
            global sRight
            global sLeft
            print(canContainer)
            # canvas = FancyFigureCanvas(fig2, canContainer)
            # connection_id = canvas.mpl_connect('button_press_event', on_press) #uncomment
            # cancan = canvas
            # cancan.axpopup.entryconfig(1, state='disabled')
            # cancan.addable_menu.entryconfig(0, state = 'disabled')
            # if a.get_visible() and a2.get_visible():
            #     cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)
            # can = canvas.get_tk_widget()
            # canContainer.grid(row=1, column=1, sticky = "nsew", ipadx = 5, ipady = 5)

            try: 
                cancan.get_tk_widget().destroy()
                cancan = None
            except:
                pass    

            # axes2.plot(data)
            # cancan = FancyFigureCanvas(fig2, canContainer)
            # can = cancan.get_tk_widget()
            # can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)

        
        # TODO: this function will open any kind of graph session. Will take in a clicked Axis.
        def go_to_next_slide():
            global axRight
            global axLeft
            global sRight
            global sLeft
            global a
            global fig
            global cursor
            global cancan
            global fig_dict
            global xAreaPoints
            global yAreaPoints
            global globalNPerBin
            global globalBins
            global fillBetFigure
            global fillAxis
            global totalArea
            global dataFile
            global globalMin
            global globalMax
            global globalMu
            global globalSigma
            global globalMultiplier
            print(canContainer)
            # canvas = FancyFigureCanvas(fig2, canContainer)
            # connection_id = canvas.mpl_connect('button_press_event', on_press) #uncomment
            # cancan = canvas
            # cancan.axpopup.entryconfig(1, state='disabled')
            # cancan.addable_menu.entryconfig(0, state = 'disabled')
            # if a.get_visible() and a2.get_visible():
            #     cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)
            # can = canvas.get_tk_widget()
            # canContainer.grid(row=1, column=1, sticky = "nsew", ipadx = 5, ipady = 5)

            try: 
                cancan.get_tk_widget().destroy()
                cancan = None
            except:
                pass    
            # data=np.arange(100)  # data to plot
            # pl.dump(fig_dict,file('savedWkspc1.pickle','wb'))

            # TODO TODO TODO
            # nxt_fig = fig_dict[fig]['fig_next']
            # dictOfAxes = fig_dict[fig]['dictOfAxes'][ax]['reflines']
            
            # fig_dict[fig] = {}
            # fig_dict[fig]['fig_next'] = None
            # fig_dict[fig]['sessionType'] = 'PDF'
            # fig_dict[fig]['numAxes'] = 1
            # fig_dict[fig]['csv_src'] = dataFile
            # fig_dict[fig]['slider_axes'] = [axLeft, axRight]
            # fig_dict[fig]['dictOfAxes'] = {}
            # init_fig_dict(a2)
            # # fig_dict[fig]['dictOfAxes'][a3] = {}
            # # fig_dict[fig]['dictOfAxes'][a3]['refLines'] = []
            # fig_dict[fig]['dictOfAxes'][a2]['addAxes'] += [a]
            # # fig_dict[fig]['dictOfAxes'][a3]['specsTable'] = {}
            output = file('savedWkspc1.pickle','rb')
            fig_dict = pl.load(output)
            output.close()
            keys = sorted(fig_dict.keys())
            fig = keys[0]
            fig_dict[fig]['loaded'] = True
            dataFile = fig_dict[fig]['csv_src']
            if len(fig_dict[fig]['slider_axes']) == 3:
                axLeft, axRight, fillBetFigure = fig_dict[fig]['slider_axes']
            elif len(fig_dict[fig]['slider_axes']) == 2:
                axLeft, axRight = fig_dict[fig]['slider_axes']

            if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
                topAxis = fig_dict[fig]['dictOfAxes'].keys()[0]
                globalMin = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mn']
                globalMu = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mu']
                globalMax = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mx']
                globalSigma = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['sigma']
                globalMultiplier = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['multiplier']
                fillAxis = topAxis
                print fig_dict[fig]['csv_src']
                for line in topAxis.get_lines():
                    if '_' not in line.get_label():
                        xAreaPoints = line.get_xdata()
                        yAreaPoints = line.get_ydata()
                        totalArea = trapz(yAreaPoints, xAreaPoints)
                        break
                addAxesDict = fig_dict[fig]['dictOfAxes'][topAxis]['addAxes']
                for axkey in addAxesDict.keys():
                    for artist in axkey.get_children():
                        if artist.get_label() == 'histogram':
                            list_a, list_b = zip(*addAxesDict[axkey])
                            globalNPerBin = list(list_b)
                            globalBins = list(list_a)
                            break
                print(globalNPerBin)
                print(globalBins)
                # xAreaPoints = topAxis.get_xdata()
                # yAreaPoints = topAxis.get_ydata()

            # fig = None
            # fig = Figure(dpi = 100)
            # fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
            # fig.subplots_adjust(wspace=.3, hspace=.35)
            # fig.patch.set_facecolor('#E0E0E0')
            # fig.patch.set_alpha(0.7)
            # a = fig.add_subplot(111)
            # a2 = a.twinx()



            # cursorChange_id = canvas.mpl_connect('axes_enter_event', on_graph_hover)
            # canContainer.bind('<Button-3>', on_press_area)
            # axes2.plot(data)
            cancan = FancyFigureCanvas(fig, canContainer)
            can = cancan.get_tk_widget()
            can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
            cancan._tkcanvas.grid(row=0, column=0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)
            connection_id = cancan.mpl_connect('button_press_event', on_press) #uncomment
            cancan.axpopup.entryconfig(1, state='disabled')
            cancan.addable_menu.entryconfig(0, state = 'disabled')

            # if a.get_visible() and a2.get_visible():
            #     cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)

            # TODO figure out if to use separate sliders or to make new AxLeft, AxRight for each new figure created.
            with plt.style.context('classic'):
                sLeft = Slider(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')
                sRight = Slider(axRight, 'Time', 0, 1, valinit=0, color = axcolor)
                axLeft.clear()
                axRight.clear()
                axRight.grid(False)
                axLeft.set_xticks([])
                axLeft.set_yticks([])
                axRight.set_yticks([])
            sLeft.on_changed(update)
            sRight.on_changed(update)
            # cancan.toggle_slider_vis()
            cancan.toggle_slider_vis()
            cancan.toggle_slider_vis()

        tk.Frame.__init__(self, parent)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=200)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=200)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        fig = Figure(dpi = 100)
        fig.subplots_adjust(bottom = 0.0, right = .75, top = .85)
        fig.subplots_adjust(wspace=.3, hspace=.35)
        # fig.subplots_adjust(bottom = 0.18, right = .85, top = .85)
        fig.patch.set_facecolor('#E0E0E0')
        fig.patch.set_alpha(0.7)
        a = fig.add_subplot(111)
        a2 = a.twinx()

        # content = tk.Frame(self)
        toolbarContainer = tk.Frame(self, width=200, height=20)

        # width=toolbarContainer.winfo_width()
        # height=toolbarContainer.winfo_height()
        expandButtonFrame = tk.Frame(self)
        buttContainer = tk.Frame(self, width=50, height=200)
        canContainer = tk.Frame(self, width=200, height=200)
        canvas = FancyFigureCanvas(fig, canContainer)
        connection_id = canvas.mpl_connect('button_press_event', on_press) #uncomment
        # cursorChange_id = canvas.mpl_connect('axes_enter_event', on_graph_hover)
        # canContainer.bind('<Button-3>', on_press_area)

        cancan = canvas
        cancan.axpopup.entryconfig(1, state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')
        # fig.subplots_adjust(bottom = 0.0, right = .75, top = .85)

        # fig.subplots_adjust(wspace=.3, hspace=.35)

        if a.get_visible() and a2.get_visible():
            cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)

        # TODO: RESIZE CANVAS
        can = canvas.get_tk_widget()

        canContainer.grid(row=1, column=1, sticky = "nsew", ipadx = 5, ipady = 5)
        toolbarContainer.grid(row=0, column=1, sticky = "nsew", pady = 5, padx = 5)
        expandButtonFrame.grid(row=0, column = 2, sticky = 'nsew')
        buttContainer.grid(row=0, column=3, rowspan = 2, sticky = "nsew", pady = 5, padx = 5)
        can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
        canvas._tkcanvas.grid(row=0, column=0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)

        # label to show the position of the cursor
        self.cursorPosLabel = StringVar()
        cursorPosLabel = self.cursorPosLabel
        _cursorPosLabel= ttk.Label(self, text = "Inputs", textvariable = self.cursorPosLabel, font = SMALL_FONT, background = 'lightgoldenrodyellow', 
            borderwidth=1, relief = 'solid', padding = (5,5, 5,5))
        _cursorPosLabel.grid(sticky = "nw", row=1, column= 1, pady = 8, padx = 8)

        # rax = fig.add_axes([0.05, 0.7, 0.15, 0.15], facecolor=axcolor)
 
        # rax.set_xticks([])
        # rax.set_yticks([])
        # _cursorPosLabel.grid(sticky = "ne", row=1+11, column=1, columnspan = 2, padx = 4, pady = 4)

        # sigLabel = ttk.Label(buttContainer, background = "white", textvariable = self.sigmaVar, font = MED_FONT, borderwidth=1, relief = 'solid', padding = (5,5, 5,5), width = 18)
        # sigLabel.grid(sticky = "ne", row=1+9, column=1, columnspan = 2, padx = 4, pady = 4)

        self.binning = IntVar()
        globalBinning = self.binning
        self.myHeader = StringVar()
        curHeader = self.myHeader
        self.myType = StringVar()
        label = ttk.Label(buttContainer, text = "Inputs", font = LARGE_FONT)
        label.grid(sticky = "ne", row=1+0, column= 1, pady = 8, padx = 8)
        # label.bind('<Button-1>', )

        crossHairsImg = tk.PhotoImage(file="crosHairs.gif")
        # create the image button, image is above (top) the optional text
        crosHairsButton = ttk.Button(toolbarContainer, image=crossHairsImg, command = lambda: self.toggleCrossHairs())
        crosHairsButton.grid(sticky = "w", row=0, column= 0)
        crosHairsButton.image = crossHairsImg

        tableImg = tk.PhotoImage(file="table.gif")
        # create the image button, image is above (top) the optional text
        tableButton = ttk.Button(toolbarContainer, image=tableImg, command = lambda: self.open_table_wrapper()) 
        tableButton.grid(sticky = "w", row=0, column= 1)
        tableButton.image = tableImg

        prevGraphButton = ttk.Button(toolbarContainer, image=tableImg, command = lambda: go_to_next_slide()) 
        prevGraphButton.grid(sticky = "w", row=0, column= 2)
        

        headerLabel = ttk.Label(buttContainer, text = "Column Header:", font = SMALL_FONT)
        headerLabel.grid(sticky = "e", row=1+1, column= 1, padx = 2, pady = 4)
        headerDropDown = ttk.Combobox(buttContainer, state="readonly", values = (" --"),
            textvariable = self.myHeader)
        headerDropDown.grid(row=1+1, column=2, sticky = "ew")
        headerDropDown.current(0)

        binningLabel = ttk.Label(buttContainer, text = "No. Bins:", font = SMALL_FONT)
        binningLabel.grid(sticky = "e", row=1+2, column= 1, padx = 2, pady = 4)
        cmbBox3 = ttk.Combobox(buttContainer, state="readonly",
            values = tuple([i + 1 for i in range(50)]), textvariable = self.binning)
        cmbBox3.grid(row=1+2, column=2, sticky = "ew")
        cmbBox3.current(19)

        typeLabel = ttk.Label(buttContainer, text = "Data Type:", font = SMALL_FONT)
        typeLabel.grid(sticky = "e", row=1+3, column= 1, padx = 2, pady = 4)
        cmbBox2 = ttk.Combobox(buttContainer, state="readonly",
            values=("Date (mm/dd/yyyy)", "Number", "Percent"), textvariable = self.myType)
        cmbBox2.grid(row=1+3, column=2, sticky = "ew")
        cmbBox2.current(0)

        # combobox to choose the type of pdf the user would like to see plotted.
        self.typePDF = StringVar()
        distTypeLabel = ttk.Label(buttContainer, text = "Distribution Type:", font = SMALL_FONT)
        distTypeLabel.grid(sticky = "e", row=1+4, column= 1, padx = 2, pady = 4)
        pdfTypeCombobox = ttk.Combobox(buttContainer, state="readonly",
            values=("Weibull Distribution", "Normal Distribution", 'Lognormal Distribution', 'Loglogistic Distribution', 'Logistic Distribution'), textvariable = self.typePDF)
        pdfTypeCombobox.grid( row=1+4, column=1, columnspan = 2, sticky="e")
        pdfTypeCombobox.current(0)


        button1 = ttk.Button(buttContainer, text = "Back to Home",
            command = lambda: controller.show_frame(StartPage))
        button1.grid(row=1+13, column=2)

        button2 = ttk.Button(buttContainer, text = "Import A Data File",
            command = openFile)
        button2.grid(row=1+0, column=2)

        self.shadedAreaPCT = StringVar()
        globalSAreaLbl = self.shadedAreaPCT
        self.sigmaVar = StringVar()
        self.stats2Var = StringVar()
        self.titleVar = StringVar()
        globalSigVar = self.sigmaVar
        globalTitleVar = self.titleVar
        globalStats2 = self.stats2Var
        self.titleVar.set('STATS')
        graphTitle = StringVar()


        # setting variables to be passed through their widgets.
        self.sigmaVar.set(u"\u03c3 = " + str(globalSigma) + "\n" + u"\u03bc = " + str(globalMu) + "\nmin = " + str(globalMin) + "\nmax = " + str(globalMax) )
        self.shadedAreaPCT.set("% Curve shaded = 0.0%")

        # label "STATS" for the Stats Summary box.
        statsLabel = ttk.Label(buttContainer, text = "Table of Stats", font = MED_FONT)
        statsLabel.grid(sticky = "e", row=1+8, column= 1, columnspan = 2, padx = 20, pady = 4)

        # label to show the standard deviation and mean of the data.
        sigLabel = ttk.Label(buttContainer, background = "white", textvariable = self.sigmaVar, font = MED_FONT, borderwidth=1, relief = 'solid', padding = (5,5, 5,5), width = 18)
        sigLabel.grid(sticky = "ne", row=1+9, column=1, columnspan = 2, padx = 4, pady = 4)

        # label to show the percentage of the curve that's been shaded.
        areaPCTLabel = ttk.Label(buttContainer, textvariable = self.shadedAreaPCT, font = MED_FONT)
        areaPCTLabel.grid(sticky = "e", row=1+10, column=1, columnspan = 2, padx = 2, pady = 4)

        binningLabel = ttk.Label(buttContainer, text = "No. Bins:", font = SMALL_FONT)
        binningLabel.grid(sticky = "e", row=1+2, column= 1, padx = 2, pady = 4)
           
        plotButton = ttk.Button(buttContainer, text = "New Plot", command = lambda: self.plotDecider())#self.weibullPPF(canvas))#self.plotDecider(canvas))
        plotButton.config(state="disabled")
        plotButton.grid(row=1+12, column=2)

        toExpand = IntVar()

        contractImg = tk.PhotoImage(file="contract.gif")
        # create the image button, image is above (top) the optional text
        chkExpand = ttk.Checkbutton(expandButtonFrame, image=contractImg, variable = toExpand, style = 'Toolbutton')
        chkExpand.configure(command = lambda: toggle_this_frame_vis(buttContainer, chkExpand))
        chkExpand.grid(sticky = "e", row=0, column= 0)
        chkExpand.image = contractImg

        props = dict(boxstyle='round', facecolor='lightblue', lw = .25)
        statTableTxt = fig.text(x = .85, y=.75, s = globalSigVar.get(), bbox = props, fontsize = 9)

        #MOVE TO PLOT
        # CREATE THE SLIDER, AND CONFIGURE.
        with plt.style.context('classic'):
            axLeft = fig.add_axes([0.15, 0.08, 0.67, 0.03], facecolor=axcolor)
            axRight = fig.add_axes([0.15, 0.05, 0.67, 0.03], facecolor='#8B0000')

            sLeft = Slider(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')
            sRight = Slider(axRight, 'Time', 0, 1, valinit=0, color = axcolor)

            axLeft.clear()
            axRight.clear()
            axRight.grid(False)
            axLeft.set_xticks([])
            axLeft.set_yticks([])
            axRight.set_yticks([])

        sLeft.on_changed(update)
        sRight.on_changed(update)

        cancan.toggle_slider_vis()

        canContainer.grid_rowconfigure(0, weight = 1)
        canContainer.grid_columnconfigure(0, weight = 1)
        
        # width=toolbarContainer.winfo_reqwidth()
        height=toolbarContainer.winfo_reqheight()

        canvasOffsetY = height
        print(height)
        # canvasOffsetX = width
        # print(width, height)
        self.toolbarContainer = toolbarContainer
        self.buttContainer = buttContainer
        buttContainer = self.buttContainer
        toolbarContainer = self.toolbarContainer
        cancan.draw()

    def set_up_new_figure(self):
        global axRight
        global axLeft
        global sRight
        global sLeft
        global a
        global fig
        global cursor
        global cancan
        global fig_dict
        global xAreaPoints
        global yAreaPoints
        global globalNPerBin
        global globalBins
        global fillBetFigure
        global fillAxis
        global totalArea
        global dataFile
        global globalMin
        global globalMax
        global globalMu
        global globalSigma
        global globalMultiplier
        print(canContainer)
        try: 
            cancan.get_tk_widget().destroy()
            cancan = None
        except:
            pass    
        # fig = None
        fig = Figure(dpi = 100)
        fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
        fig.subplots_adjust(wspace=.3, hspace=.35)
        fig.patch.set_facecolor('#E0E0E0')
        fig.patch.set_alpha(0.7)
        a = fig.add_subplot(111)
        a2 = a.twinx()

        # cursorChange_id = canvas.mpl_connect('axes_enter_event', on_graph_hover)
        # canContainer.bind('<Button-3>', on_press_area)
        # axes2.plot(data)
        cancan = FancyFigureCanvas(fig, canContainer)
        can = cancan.get_tk_widget()
        can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
        cancan._tkcanvas.grid(row=0, column=0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)
        connection_id = cancan.mpl_connect('button_press_event', on_press) #uncomment
        cancan.axpopup.entryconfig(1, state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        # if a.get_visible() and a2.get_visible():
        #     cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)

        # TODO figure out if to use separate sliders or to make new AxLeft, AxRight for each new figure created.
        with plt.style.context('classic'):
            axLeft = fig.add_axes([0.15, 0.08, 0.67, 0.03], facecolor=axcolor)
            axRight = fig.add_axes([0.15, 0.05, 0.67, 0.03], facecolor='#8B0000')
            sLeft = Slider(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')
            sRight = Slider(axRight, 'Time', 0, 1, valinit=0, color = axcolor)
            axLeft.clear()
            axRight.clear()
            axRight.grid(False)
            axLeft.set_xticks([])
            axLeft.set_yticks([])
            axRight.set_yticks([])
        sLeft.on_changed(update)
        sRight.on_changed(update)
        cancan.toggle_slider_vis()
        return cancan

    def open_table_wrapper(self):
        popupmsg('Table')

    def toggleCrossHairs(self):
        global cursor
        global cursors
        if len(cursors) > 0:
            for c in cursors:
                c.horizOn = not c.horizOn
                c.vertOn = not c.vertOn
        elif cursor is not None:
            cursor.horizOn = not cursor.horizOn
            cursor.vertOn = not cursor.vertOn

    def plotDecider(self):
        global dataMultiplier
        global globalMultiplier
        global logBase
        global refLines
        global listOfRefLines
        global textBoxes
        global fig_dict
        globalMultiplier = 1.0
        logBase = 0
        pdfType = pdfTypeCombobox.get()
        canvas = self.set_up_new_figure()

        print(pdfType)
        for refLine in refLines:
            refLine.remove()
        for entryBox in listOfRefLines:
            entryBox.destroy()
        for txt in textBoxes:
            txt.remove()
        listOfRefLines = []
        refLines = []
        # fig_dict[fig]['dictOfAxes'][axes]['refLines'] = []

        textBoxes = []
        self.plot(canvas,pdfType)


    def plot(self,canvas,graphType):
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
        global sLeft
        global sRight
        global axLeft
        global axRight
        global axcolor
        global fillBetFigure
        global fillAxis
        global totalArea
        global globalSigVar
        global globalTitleVar
        global leftDeviations
        global rightDeviations
        global globalSigma
        global globalMu
        global cursor
        global globalMultiplier
        global logBase
        global fig_dict

        binType = self.myType.get()
        try:

            numBins = globalBinning.get()
            gotten = curHeader.get()
            if dataFile is not None:
                dframe = pd.read_csv(dataFile)
                dframe = dframe.sort_values(gotten)
                a3 = None
                if (self.myType.get() == "Date (mm/dd/yyyy)"):
                    allAxes = fig.get_axes()
                    for ax in allAxes:
                        if ax != axLeft and ax != axRight:
                            ax.clear()
                            # if fig in fig_dict and fig_dict[fig]['loaded']:
                            ax.remove()

                    a = fig.add_subplot(111)
                    a2 = a.twinx()

                    l = dframe[gotten].dropna().values.tolist()

                    converted_dates = map(datetime.datetime.strptime, l, len(l)*['%m/%d/%Y'])
                    x_axis = (converted_dates)
                    formatter = dates.DateFormatter('%m/%d/%Y')

                    dframe[gotten] = pd.to_datetime(dframe[gotten].dropna())
                    stats = dframe[gotten].dropna().describe()
                    earliestMax = stats.iloc[4]
                    recentMax = stats.iloc[5]

                    dateDiffList = []
                    for xDate in converted_dates:
                        dateDiffList += [abs((xDate - earliestMax).days)]

                    datesDF = pd.DataFrame(dateDiffList, columns = [gotten])
                    stats = datesDF.describe()
                    print(datesDF[gotten].dtype)

                    mu = stats.iloc[1][gotten]
                    variance = stats.iloc[2][gotten] ** 2
                    sigma = math.sqrt(variance)
                    mn = stats.iloc[3][gotten]
                    mx = stats.iloc[7][gotten]
                    # print(stats)
                    # print(mx)
                    globalMax = mx
                    globalMin = mn
                    globalSigma = sigma
                    globalMu = mu
                    globalSigVar.set(u"\u03c3 = " + str(truncate(sigma, 3)) + "\n" + u"\u03bc = " + str(truncate(mu, 3)) +"\nmin = " + str(mn) +  "\nmax = " + str(mx) )
                    a3 = fig.add_subplot(111, label="3", frame_on=False)
                    cursor = InformativeCursor(a3, useblit=True, color='red', linewidth=.5)

                    n, bins, patches = a.hist(dframe[gotten].dropna(), numBins,
                        facecolor = '#00A3E0', edgecolor = 'k', align = 'mid', label = 'histogram')
                    for patch in patches:
                        print a.get_label()

                    x = np.linspace(mn, mx, 300 + 5 * int(math.sqrt(mx - mn)))
                    y = []
                    if graphType == 'Weibull Distribution':
                        p0, p1, p2=ss.weibull_min.fit(datesDF[gotten].dropna().tolist(), floc=0)
                        y = ss.weibull_min.pdf(x, p0, p1, p2)
                        a3.plot(x, y, label = 'weibull distribution', lw = 1.0, color = '#8B0000')
                        print(a3.get_label())
                        graphTitle.set('Weibull PDF of ' + str(gotten))

                    elif graphType == 'Normal Distribution':
                        for xElem in x:
                            y = y + [np.reciprocal(stats.iloc[2][gotten] * math.sqrt(2 * np.pi))
                                * np.reciprocal(np.exp(0.5 * ((xElem - stats.iloc[1][gotten]) / (stats.iloc[2][gotten])) ** 2))]
                        graphTitle.set('Normal PDF of ' + str(gotten))
                        a3.plot(x, y, label = 'normal distribution', lw = 1.0, color = '#8B0000')

                    elif graphType == 'Lognormal Distribution':
                        s, p1, p2 = ss.lognorm.fit([i for i in datesDF[gotten].dropna().tolist() if i > 0.0], floc = 0)
                        print(s, p1, p2)
                        print(globalSigma, globalMu)
                        y = ss.lognorm.pdf(x, s, p1, p2)
                        print('gothere')
                        a3.plot(x, y, color = '#8B0000', lw=1.0, label='lognormal distribution')
                        graphTitle.set('Lognormal PDF of ' + str(gotten))

                    elif graphType == 'Loglogistic Distribution':
                        c, p1, p2 = ss.fisk.fit([i for i in datesDF[gotten].dropna().tolist() if i > 0.0], floc = 0)
                        print(c,p1, p2)
                        print(globalSigma, globalMu)
                        y = ss.fisk.pdf(x, c, p1, globalMu)
                        a3.plot(x, y, color = '#8B0000', lw=1.0, label='loglogistic distribution')                       
                        graphTitle.set('Loglogistic PDF of ' + str(gotten))

                    elif graphType == 'Logistic Distribution':
                        p0, p1 =ss.logistic.fit(datesDF[gotten].dropna().tolist(), floc=globalMu)
                        print(p0, p1)
                        y = ss.logistic.pdf(x, p0, p1)
                        a3.plot(x, y, label = 'logistic distribution', lw = 1.0, color = '#8B0000')
                        graphTitle.set('Logistic PDF of ' + str(gotten))
                    
                    # if fig not in fig_dict and not fig_dict[fig]['loaded']:
                    fig_dict[fig] = {}
                    fig_dict[fig]['fig_next'] = None
                    fig_dict[fig]['sessionType'] = 'PDF'
                    fig_dict[fig]['numAxes'] = 1
                    fig_dict[fig]['csv_src'] = dataFile
                    fig_dict[fig]['slider_axes'] = [axLeft, axRight]
                    fig_dict[fig]['dictOfAxes'] = {}
                    fig_dict[fig]['loaded'] = False
                    init_fig_dict(a3)

                    # fig_dict[fig]['dictOfAxes'][a3] = {}
                    # fig_dict[fig]['dictOfAxes'][a3]['refLines'] = []
                    # fig_dict[fig]['dictOfAxes'][a3]['specsTable'] = {}
                    fig_dict[fig]['dictOfAxes'][a3]['specsTable']['mn'] = globalMin
                    fig_dict[fig]['dictOfAxes'][a3]['specsTable']['mu'] = globalMu 
                    fig_dict[fig]['dictOfAxes'][a3]['specsTable']['mx'] = globalMax
                    fig_dict[fig]['dictOfAxes'][a3]['specsTable']['sigma'] = globalSigma
                    fig_dict[fig]['dictOfAxes'][a3]['specsTable']['multiplier'] = globalMultiplier



                    a.set_ylim(0, 1.5 * (max(n)))
                    globalBins = dates.num2date(bins)
                    globalNPerBin = n
                    fig_dict[fig]['dictOfAxes'][a3]['addAxes'][a] = zip(globalBins, globalNPerBin)

                    # TODO begin graph from x = 0 

                    a.tick_params(axis = 'x', rotation = 25)

                    fillAxis = a3
                    xAreaPoints = x
                    yAreaPoints = y
                    fillBetFigure = a3.fill_between(x, 0, y, facecolor = '#4B0082', alpha = 0)

                    sLeft.valmax = max(x)
                    sRight.valmax = max(x)
                    axLeft.set_xlim(min(x), max(x))
                    axRight.set_xlim(min(x), max(x))

                    a3.grid(False)
                    a3.set_ylim(0, 1.5 * (max(y)))

                    a3.tick_params(axis = 'y', labelcolor = '#8B0000')
                    a3.tick_params(axis = 'x', labelcolor = '#8B0000')
                    a3.set_ylabel("Distribution Values")
                    a3.set_xlabel("Days")
                    a.set_xlabel(str(gotten))
                    a.set_ylabel("Frequency")
                    a3.xaxis.set_label_position('top')
                    a3.yaxis.set_label_position('right')
                    a2.set_yticks([])
                    a3.xaxis.tick_top()
                    a3.yaxis.tick_right()

                    a.legend(bbox_to_anchor=(0, 1.08, 1, .102), loc=3,
                            ncol=1, borderaxespad=0)

                    totalArea = trapz(y, x)

                    cancan.thisFigure.suptitle(graphTitle.get(), fontsize=14, fontweight='bold')

                    canvas.draw()
                else:
                    allAxes = fig.get_axes()
                    for ax in allAxes:
                        if ax != axLeft and ax != axRight:
                            print ax
                            # if fig in fig_dict and fig_dict[fig]['loaded']:
                            ax.clear()
                            ax.remove()

                            # ax.remove()

                    a = fig.add_subplot(111)
                    a2 = a.twinx()
                    cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)

                    stats = dframe[gotten].dropna().describe()
                    print(dframe[gotten].dtype)
                    mu = stats.iloc[1]
                    variance = stats.iloc[2] ** 2
                    sigma = math.sqrt(variance)
                    mn = stats.iloc[3]
                    mx = stats.iloc[7]

                    logBase = 0
                    if mu * 5 > 2147483647.0:
                        ## Treat as a large number dataset.
                        muCopy = mu
                        while muCopy >= 10.0:
                            globalMultiplier *= 10.0
                            muCopy /= 10.0
                            logBase += 1
                    print(globalMultiplier)

                    globalMax = mx / globalMultiplier
                    globalMin = mn / globalMultiplier
                    globalSigma = sigma / globalMultiplier
                    globalMu = mu / globalMultiplier
                    globalSigVar.set(u"\u03c3 = " + str(truncate(sigma, 3)) + "\n" + u"\u03bc = " + str(truncate(mu, 3)) +"\nmin = " + str(mn) +  "\nmax = " + str(mx) )

                    n, bins, patches = a.hist((dframe[gotten].dropna() / globalMultiplier).tolist(), numBins,
                        facecolor = '#00A3E0', edgecolor = 'k', align = 'mid', label = 'histogram')
                    a.set_ylim(0, 1.5 * (max(n)))

                    x = np.linspace(globalMin , globalMax, 300 + 5 * int(math.sqrt(globalMax - globalMin)))
                    y = []
                    xdata = (dframe[gotten].dropna()/globalMultiplier).tolist()
                    if graphType == 'Weibull Distribution':
                        xdata = (dframe[gotten].dropna()/globalMultiplier).tolist()
                        # print(type(xdata))
                        p0, p1, p2 = ss.weibull_min.fit(xdata, floc=0)
                        print(p0, p1, p2)
                        y = ss.weibull_min.pdf(x, p0, p1, p2)
                        a2.plot(x, y, label = 'weibull distribution', lw = 1.0, color = '#8B0000')
                        graphTitle.set('Weibull PDF of ' + str(gotten))

                    elif graphType == 'Normal Distribution':
                        for xElem in x:
                            y = y + [np.reciprocal(globalSigma * math.sqrt(2 * np.pi))
                                * np.reciprocal(np.exp(0.5 * ((xElem - globalMu) / (globalSigma)) ** 2))]
                        a2.plot(x, y, label = 'normal distribution', lw = 1.0, color = '#8B0000')
                        graphTitle.set('Normal PDF of ' + str(gotten))

                    elif graphType == 'Lognormal Distribution':
                        s, p1, p2 = ss.lognorm.fit([i for i in xdata if i > 0.0], floc = 0)
                        print(s, p1, p2)
                        print(globalSigma, globalMu)
                        y = ss.lognorm.pdf(x, s, p1, p2)
                        print('gothere')
                        a2.plot(x, y, color = '#8B0000', lw=1.0, label='lognormal distribution')
                        graphTitle.set('Lognormal PDF of ' + str(gotten))
                    elif graphType == 'Loglogistic Distribution':
                        c, p1, p2 = ss.fisk.fit([i for i in xdata if i > 0.0], floc = 0)
                        print(c,p1, p2)
                        print(globalSigma, globalMu)
                        y = ss.fisk.pdf(x, c, p1, globalMu)
                        a2.plot(x, y, color = '#8B0000', lw=1.0, label='loglogistic distribution')
                        graphTitle.set('Loglogistic PDF of ' + str(gotten))
                    elif graphType == 'Logistic Distribution':
                        p0, p1 =ss.logistic.fit(xdata, floc=globalMu)
                        print(p0, p1)
                        y = ss.logistic.pdf(x, p0, p1)
                        a2.plot(x, y, label = 'logistic distribution', lw = 1.0, color = '#8B0000')
                        graphTitle.set('Logistic PDF of ' + str(gotten))
                    
       
                    fig_dict[fig] = {}
                    fig_dict[fig]['fig_next'] = None
                    fig_dict[fig]['sessionType'] = 'PDF'
                    fig_dict[fig]['numAxes'] = 1
                    fig_dict[fig]['csv_src'] = dataFile
                    fig_dict[fig]['slider_axes'] = [axLeft, axRight]
                    fig_dict[fig]['dictOfAxes'] = {}
                    fig_dict[fig]['loaded'] = False
                    init_fig_dict(a2)

                    # fig_dict[fig]['dictOfAxes'][a3] = {}
                    # fig_dict[fig]['dictOfAxes'][a3]['refLines'] = []
                    # fig_dict[fig]['dictOfAxes'][a3]['specsTable'] = {}
                    fig_dict[fig]['dictOfAxes'][a2]['specsTable']['mn'] = globalMin
                    fig_dict[fig]['dictOfAxes'][a2]['specsTable']['mu'] = globalMu 
                    fig_dict[fig]['dictOfAxes'][a2]['specsTable']['mx'] = globalMax
                    fig_dict[fig]['dictOfAxes'][a2]['specsTable']['sigma'] = globalSigma
                    fig_dict[fig]['dictOfAxes'][a2]['specsTable']['multiplier'] = globalMultiplier
                    a.grid(False)
                    # a.yaxis.grid()


                    globalBins = bins
                    globalNPerBin = n
                    fig_dict[fig]['dictOfAxes'][a2]['addAxes'][a] = zip(globalBins, globalNPerBin)

                    useBins = bins
                    if (numBins >= 30):
                        l = []
                        for i in range(0, len(bins), 2):
                            l += [bins[i]]
                        useBins = l


                    a.set_xticks(useBins)
                    a.tick_params(axis = 'x', rotation = 35)
                        
                    fillAxis = a2
                    xAreaPoints = x
                    yAreaPoints = y
                    fillBetFigure = a2.fill_between(x, 0, y, facecolor = '#4B0082', alpha = 0)

                    sLeft.valmax = max(x)
                    sRight.valmax = max(x)
                    axLeft.set_xlim(min(x), max(x))
                    axRight.set_xlim(min(x), max(x))
                    
                    a2.set_label('Normal PDF')
                    a2.grid(False)
                    a2.set_ylim(0, 1.5 * (max(y)))
                    apxBinDif = (max(xAreaPoints)-min(xAreaPoints))/numBins
                    a.set_xlim(min(xAreaPoints)-apxBinDif ,max(xAreaPoints) + apxBinDif)

                    # a2.set_xlim(min(x), (max(x))) #ToCOMMENT

                    a2.tick_params(axis = 'y', labelcolor = '#8B0000')
                    a2.set_ylabel("Distribution Values")
                    # a.set_xlabel("Numeric Divisions")

                    if (globalMultiplier > 1.0):
                        a.set_xlabel(str(gotten)+" (1e+%d)" % (logBase))
                    else:
                        a.set_xlabel("Numeric Divisions")

                    a.set_ylabel("Frequency")
                    a2.yaxis.tick_right()

                    a.legend(bbox_to_anchor=(0, 1.08, 1, .102), loc=3,
                            ncol=1, borderaxespad=0)
                    # graphTitle.set('Normal PDF of ' + str(gotten))
                    cancan.thisFigure.suptitle(graphTitle.get(), fontsize=14, fontweight='bold')
                    
                    totalArea = trapz(y, x)
                    canvas.draw()
                cancan.axpopup.entryconfig(1,state='normal')
                cancan.addable_menu.entryconfig(0, state = 'normal')
                wasPlotted = True
        except ValueError, e:
            tkMessageBox.showerror("Data NA Error", "Data at header " + str(gotten)
                + " in file " + str(dataFile) + " is missing or invalid.\n\n" + " Error:" + str(e))
            canvas.draw()
            cancan.axpopup.entryconfig(1,state='disabled')
            cancan.addable_menu.entryconfig(0, state = 'disabled')

            wasPlotted = False
            return
        except TypeError, e:
            tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
                gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
            canvas.draw()
            cancan.axpopup.entryconfig(1,state='disabled')
            cancan.addable_menu.entryconfig(0, state = 'disabled')

            wasPlotted = False
            return
        except KeyError, e:
            tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
                gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
            canvas.draw()
            cancan.axpopup.entryconfig(1,state='disabled')
            cancan.addable_menu.entryconfig(0, state = 'disabled')

            wasPlotted = False
            return

# TODO FIX 
def weibullPPF(canvas):
    global a
    global a2
    global fig
    global axLeft
    global axRight
    global sRight
    global sLeft
    global multiCursor
    global cancan
    global cursor
    global cursors
    global maximizedGeometry 
    global maximizedAxis
    global fig_dict
    global dataFile
    
    maximizedAxis = None
    maximizedGeometry = (1,1,1)
    cancan.popup_multi.entryconfigure(0, label="Maximize")

    if a is not None and a.get_visible():
        cancan.addable_menu.add_command(label = "Figure Title", command = cancan.set_graph_title1)
    cancan.axpopup.entryconfig(1,state='disabled')
    cancan.addable_menu.entryconfig(0, state = 'disabled')
    
    for axis in fig.get_axes():
        if axis != axRight and axis != axLeft:
            axis.clear()
            if axis is not a and axis is not a2:
                axis.remove()
            else:
                axis.set_visible(False)
    # fig2 = Figure(dpi = 100)
    # fig2.subplots_adjust(bottom = 0.0, right = .75, top = .85)
    # fig2.subplots_adjust(wspace=.3, hspace=.35)

    # fig2.add_axes(axRight)




    # TODO TODO TODO
    fig_dict[fig] = {}
    fig_dict[fig]['fig_next'] = None
    fig_dict[fig]['sessionType'] = 'RELA'
    fig_dict[fig]['numAxes'] = 4
    fig_dict[fig]['csv_src'] = dataFile
    fig_dict[fig]['slider_axes'] = [axLeft, axRight]
    fig_dict[fig]['dictOfAxes'] = {}
      


    # # fig_dict[fig]['dictOfAxes'][a3] = {}
    # # fig_dict[fig]['dictOfAxes'][a3]['refLines'] = []
    # fig_dict[fig]['dictOfAxes'][a3]['addAxes'] += [a]
    # # fig_dict[fig]['dictOfAxes'][a3]['specsTable'] = {}

    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    for axes in [ax1, ax2, ax3, ax4]:
        init_fig_dict(axes)

    print(fig_dict)


    # nxt_fig = fig_dict[fig]['fig_next']
    # dictOfAxes = fig_dict[fig]['dictOfAxes'][ax]['reflines']
    # TODO TODO TODO

    # p0, p1, p2 = ss.weibull_min.fit(dframe[gotten].dropna().tolist(), floc=0)
    # # y = ss.weibull_min.pdf(x, p0, p1, p2)
    # # a2.plot(x, y, label = 'newWeibull', lw = 1.0, color = '#8B0000')
    cursor = None
    # multiCursor = MultiCursor(cancan, (ax1, ax2, ax3, ax4), color='r', lw=1)
    # fig_dict[fig] 


    cursors = [
        InformativeCursor(ax1, useblit=True, color='red', linewidth=.5),
        InformativeCursor(ax3, useblit=True, color='red', linewidth=.5),
        InformativeCursor(ax4, useblit=True, color='red', linewidth=.5),
        InformativeCursor(ax2, useblit=True, color='red', linewidth=.5)
    ]


    # x=ss.weibull_min.rvs(c, size=nsample)
    # x = (5,16,16,17,28,30,39,39,43,45,51,53,58,61,66,68,68,72,72,77,78,80,81,90,96,100,109,110,131,153,165,180,186,188,207,219,265,285,285,308,334,340,342,370,397,445,482,515,545,583,596,630,670,675,733,841,852,915,941,979,995,1032,1141,1321,1386,1407,1571,1586,1799)
    x = (1037,1429,680,291,1577,90,1090,142,1297,1113,1153,150,837,890,269,468,1476,827,519,1100,1307,1360,919,373,563,978,650,362,383,272)
    # x = (0,1,4,7,10,6,14,18,5,12,23,10,3,3,7,3,26,1,2,25,29,29,29,28,2,3,12,32,34,36,29,37,9,16,41,3,6,3,9,18,49,35,17,3,59,2,5,2,1,1,5,9,10,13,3,1,18,17,2,17,22,25,25,25,6,6,2,26,38,22,4,24,41,41,1,44,2,45,2,46,49,50,4,54,38,59)
    x = (69,64,38,63,65,49,69,68,43,70,81,63,63,52,48,61,42,35,63,56,55,67,63,65,46,53,69,68,43,55,42,64,65,65,55,66,60,67,53,62,67,72,48,68,67,61,60,62,38,50,63,64,43,34,66,62,52,47,63,68,45,41,66,62,60,66,38,53,37,54,60,48,52,70,50,62,65,58,62,64,63,58,64,52,35,63,70,51,40,69,36,71,62,60,44,54,66,49,72,68,62,71,70,61,71,59,67,60,69,57,39,62,50,43,70,66,61,81,58,63,60,62,42,69,63,45,68,39,66,63,49,64,65,64,67,65,37)
    # x = (16, 17, 16, 18, 19, 17, 34, 53, 75, 93, 120)
    p0, p1, p2 = ss.weibull_min.fit(x, floc=0)
    sortedX = sorted(x)
    medianRanks = []
    for i,v in enumerate(sortedX):
        print(i)
        medianRanks += [(i + 1 - 0.3)/(len(x) + 0.4)]

    # TODO add all labels to each graph
    mn = min(sortedX)
    mx = max(sortedX)
    xSpan = np.linspace(0.0001, mx, 300 + 5 * int(math.sqrt(mx - mn)))
    y = ss.weibull_min.pdf(xSpan, p0, p1, p2)
    ax1.plot(xSpan, y, 
        label = 'weibull distribution', 
        lw = 1.0, 
        color = '#8B0000')
    ax1.set_ylim(0, 1.5 * (max(y)))
    ax1.set_title('Weibull Distribution', y =1.04)
    ax1.set_xlabel("Time, (t)")
    ax1.set_ylabel("f(t)")

    xSpan2 = np.linspace(mn, mx, 300 + 5 * int(math.sqrt(mx - mn)))
    unrelValuesFull = [1-np.exp(-1*((xi/p2)**p0)) for xi in xSpan2]
    unrelValues= [1-np.exp(-1*((xi/p2)**p0)) for xi in sortedX]
    ax2.plot(sortedX, medianRanks,'ob', 
        markersize = 2.3, 
        label = 'weibull probability plot')
    ax2.plot(xSpan2, unrelValuesFull, color = '#8B0000', lw = 1.0)
    ax2.set_yscale('mercator')
    ax2.set_xscale('log')

    ax2.set_axisbelow(True)
    ax2.grid(True, which = 'both')
    ax2.set_title('Weibull Probability Plot', y =1.04)
    ax2.set_xlabel("Time, (t)")
    ax2.set_ylabel("Unreliability F(t)")

    ax3.plot(xSpan, [np.exp(-1*((xi/p2)**p0)) for xi in xSpan], 
        label = 'weibull survival (reliability) function', 
        color = '#8B0000', lw = 1.0)
    ax3.set_title('Survival Function', y =1.04)
    ax3.set_xlabel("Time, (t)")
    ax3.set_ylabel("Reliability 1-F(t)")
    ax3.set_ylim(0, max(ax3.get_ylim()))

    ax4.plot(xSpan, [(p0/p2)*(xi/p2)**(p0 - 1) for xi in xSpan], 
        label = 'weibull failure rate (hazard) function', 
        lw = 1.0, 
        color = '#8B0000')
    ax4.set_title('Hazard Function', y =1.04)
    ax4.set_xlabel("Time, (t)")
    ax4.set_ylabel("Failure Rate (fr/time)")
    ax4.set_ylim(0, max(ax4.get_ylim()))

    # report estimated correlation coefficient
    covar = 0.0
    xVarSum = 0.0
    yVarSum = 0.0
    corrCoef = 0.0
    avgX = sum(sortedX)/len(sortedX)
    avgY = sum(unrelValues) / len(sortedX)
    for i, val in enumerate(unrelValues):
        # xi = np.log(sortedX[i])
        xi = sortedX[i]
        # yi = np.log(np.log(1/(1-val)))
        yi = val
        xVarSum += (xi - avgX)**2 
        yVarSum += (yi - avgY)**2 
        covar += (xi - avgX) * (yi - avgY)
    corrCoef = covar/(np.sqrt(xVarSum * yVarSum))
    print 'CorrCoff ' + str(corrCoef)
    cancan.draw()


def pdfPriming(canvas):
    global fig
    global axLeft
    global axRight
    global cursor
    global cursors
    global cancan
    print(cursors)
    if len(cursors) > 0:
        cancan.addable_menu.delete("Figure Title")
    cancan.axpopup.entryconfig(1,state='disabled')
    cancan.addable_menu.entryconfig(0, state = 'disabled')
    cursors = []
    for axis in fig.get_axes():
        if axis != axRight and axis != axLeft:
            axis.clear()
            if axis is not a and axis is not a2:
                axis.remove()
            else: 
                axis.set_visible(True)
                cursor = InformativeCursor(axis, useblit=True, color='red', linewidth=.5)

    # canvas.axes = [a, a2]
    # canvas.figure = fig
    canvas.draw()

app = SeaofBTCapp()
app.mainloop() # tkinter functionality

# TODO update side inputs bar on change to reliability analysis
