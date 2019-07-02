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
from Tkinter import Entry, StringVar, IntVar, DoubleVar, Toplevel, Variable
import tkMessageBox
import tkFont
from PIL import ImageTk, Image

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

import cPickle as pl

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
sessionType = None
canContainer = None
sessionCanvii = []

dataType = "" # the type of data we have, ( dates, percentages, numbers, ...)
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
cursorState = None
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
headerDropDownVar = None

buttContainer = None
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
programmaticDeletionFlag = False


statTableTxt = None
maximizedAxis = None
toMaximize = []
toMaximizeType = None
fig_dict = {}
current_tabs_dict = {}
maximizedGeometry = (1,1,1)
pdfTypeCombobox = None
cursorPosLabel = None
listOfRefLines = []
refLines = []
textBoxes = []

relaWidgs = []
pdfWidgs = []
anovaWidgs = []
curWidgs = None
symbolsDict = {
    'mu': u"\u03bc",
    'sigma': u"\u03c3",
    'corr_coeff': 'r'
}

# Saving and Reloading
sliderCreatedOnce = False
notebookFrame = None
sliderCIDs = [None, None]
anovaButtonTxt1 = None
thisWkspcName = None

with open('savedWkspc1.pickle', 'wb') as handle:
    pl.dump(fig_dict, handle, protocol=pl.HIGHEST_PROTOCOL)

def saveFile():
    global writeCsv_lock
    global xAreaPoints
    global yAreaPoints
    global globalBins
    global globalNPerBin
    global globalMu
    global globalSigma
    global fig_dict
    global fig
    #TODO try-catch when document is open in another program.
    # writeCsv_lock.acquire()

    if fig not in fig_dict: 
        tkMessageBox.showerror("Save Error", "There is no" +
            " data to save yet.")
        return

    if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
        if (len(globalBins) == 0):
            tkMessageBox.showerror("Save Error", "There is no" +
                " data to save yet.")
            return

    curTitle = str(fig._suptitle.get_text())
    if curTitle == "":
        curTitle = "Untitled Data"

    try:
        fname = tkFileDialog.asksaveasfile(defaultextension = ".csv", initialfile = curTitle)
        if fname is None:
            return
    except IOError, e:
        tkMessageBox.showerror("File In Use", "A file of the same name is currently in use in another program. Close this file and try again.")
        return

    # print(type(fname))    # FOR DEBUGGNING
    print(fname.name)          # fname is type 'file'
    # print(str(fname))

    with open(fname.name, 'wb') as csvfile:

        filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        if fig_dict[fig]['numAxes'] == 4 and fig_dict[fig]['sessionType'] == 'RELA':
            data_order = []
            data_order2 = []
            all_data = []
            for topAxis in fig_dict[fig]['dictOfAxes'].keys():
                # this_min = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mn']

                specs = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']
                # this_max = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mx']
                # this_mu = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mu']
                # this_sigma = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['sigma']
                # globalMultiplier = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['multiplier']
                # axis_scale = topAxis.get_yscale()
                # if len(fig_dict[fig]['dictOfAxes'][topAxis]['axesScales']) == 0: 
                for line in topAxis.get_lines():
                    print(line)
                    if '_' not in line.get_label():
                        xPoints = line.get_xdata()                        
                        yPoints = line.get_ydata()
                        if 'probability plot' in line.get_label():
                            print line.get_label()
                            
                            xPoints, yPoints = excel_plottable_prob_plot(specs, line.get_xdata(), line.get_ydata(), str(line.get_label()))

                        print type(xPoints)
                        data_order2 += [ str(topAxis.get_xlabel()), str(topAxis.get_ylabel()) ]
                        data_order += [str(topAxis.get_title()) + ':' + str(line.get_label()) + ' x', str(topAxis.get_title()) + ':' + str(line.get_label())  + ' y']
                        all_data += [xPoints, yPoints]
                    else: 
                        continue
        
            zipped_row_data = itertools.izip_longest(*all_data)
            data_order += ['RELA']
            filewriter.writerow(data_order)
            filewriter.writerow(data_order2)
            for tup in zipped_row_data:
                filewriter.writerow(list(tup))

        elif fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
            lenBins = len(globalNPerBin)

            if (isinstance(globalBins[len(globalBins) - 1], datetime.datetime)):
                filewriter.writerow(['Distribution x Values (Days)' , 'Distribution y Values', '__________', 'Amt Per Bin', '__', globalSigma, globalMu, 'PDF'])
            else:
                filewriter.writerow(['Distribution x Values' , 'Distribution y Values', 'Histo Bins', 'Amt Per Bin', '__', globalSigma, globalMu, 'PDF'])
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

    if not axLeft.get_visible() and not axRight.get_visible() or fillAxis == None:
        return
    userSetCursor = True

    axLeft.clear()
    axRight.clear()
    sLeft.val = a
    sRight.val = b
    minVal = min(fillAxis.get_xlim())

    if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
        axLeft.axvspan(minVal, sRight.val, 0, 1)
        sLeft.val = sRight.val
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
    elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
        axRight.axvspan(minVal, sLeft.val, 0, 1, facecolor=axcolor)
        sRight.val = sLeft.val
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
        axLeft.axvspan(minVal, sLeft.val, 0, 1)
    else:
        axLeft.axvspan(minVal, sLeft.val, 0, 1)
        axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)

    axLeft.margins(x = 0)
    axRight.margins(x = 0)
    sLeft.valmax = max(xAreaPoints)
    sRight.valmax = max(xAreaPoints)
    sLeft.valmin = min(xAreaPoints)
    sRight.valmin = min(xAreaPoints)
    # axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
    # axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
    axLeft.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
    axRight.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
    axRight.grid(False)
    axLeft.set_xticks([])
    axLeft.set_yticks([])
    axRight.set_yticks([])

    prevPlotB = sRight.val
    prevPlotA = sLeft.val
    if fillBetFigure is not None and fillAxis is not None:
        fillBetFigure.remove()
        xSpan = [a for a in xAreaPoints if a <= prevPlotB and a >= prevPlotA]
        ySpan = [yAreaPoints[i] for i in range(len(xAreaPoints)) if xAreaPoints[i] <= prevPlotB and xAreaPoints[i] >= prevPlotA]
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
    if not axLeft.get_visible() and not axRight.get_visible() or fillAxis == None:
        return
    
    axLeft.clear()
    axRight.clear()
    minVal = min(fillAxis.get_xlim())

    if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
        axLeft.axvspan(minVal, sRight.val, 0, 1)
        sLeft.val = sRight.val
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
    elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
        axRight.axvspan(minVal, sLeft.val, 0, 1, facecolor=axcolor)
        sRight.val = sLeft.val
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
        axLeft.axvspan(minVal, sLeft.val, 0, 1)
    else:
        axLeft.axvspan(minVal, sLeft.val, 0, 1)
        axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
        axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
        axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)

    axLeft.margins(x = 0)
    axRight.margins(x = 0)
    sLeft.valmax = max(xAreaPoints)
    sRight.valmax = max(xAreaPoints)
    sLeft.valmin = min(xAreaPoints)
    sRight.valmin = min(xAreaPoints)
    # axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
    # axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
    axLeft.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
    axRight.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
    axRight.grid(False)
    axLeft.set_xticks([])
    axLeft.set_yticks([])
    axRight.set_yticks([])

    prevPlotB = sRight.val
    prevPlotA = sLeft.val
    if fillBetFigure is not None and fillAxis is not None:
        fillBetFigure.remove()
        xSpan = [a for a in xAreaPoints if a <= prevPlotB and a >= prevPlotA]
        ySpan = [yAreaPoints[i] for i in range(len(xAreaPoints)) if xAreaPoints[i] <= prevPlotB and xAreaPoints[i] >= prevPlotA]
        fillBetFigure = fillAxis.fill_between(xSpan, 0, ySpan, facecolor = '#4B0082', alpha = 0.4)
        fig.canvas.draw_idle()
        areaUnderCurve = trapz(ySpan, xSpan)
        globalSAreaLbl.set("% Curve shaded: " + '{:.3%}'.format(np.divide(areaUnderCurve,totalArea)))

def integrate(integrateY, integrateX):
    return '{:18.16f}'.format(trapz(integrateY, integrateX))

def slider_config_for_table_not_present_four_graphs():
    global statTableTxt
    global showTableOfStats
    global axRight
    global axLeft
    global sLeft
    global sRight
    global fillAxis
    global fig_dict
    global fig
    global sliderCreatedOnce
    if fillAxis != None:
        if fig in fig_dict and fig_dict[fig]['loaded'] and not sliderCreatedOnce:
            fig.delaxes(axLeft)
            fig.delaxes(axRight)
            sliderCreatedOnce = True
        else:
            axLeft.remove()
            axRight.remove()
        axLeft = fig.add_axes([0.12, 0.08, 0.756, 0.03], facecolor=axcolor)
        axRight = fig.add_axes([0.12, 0.05, 0.756, 0.03], facecolor='#8B0000')
        axLeft.clear()
        axRight.clear()
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])
        sRight.set_axes(axRight)
        sLeft.set_axes(axLeft)

        minVal = min(fillAxis.get_xlim())

        if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
            axLeft.axvspan(minVal, sRight.val, 0, 1)
            sLeft.val = sRight.val
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
        elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
            axRight.axvspan(minVal, sLeft.val, 0, 1, facecolor=axcolor)
            sRight.val = sLeft.val
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
        else:
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)


        axLeft.margins(x = 0)
        axRight.margins(x = 0)
        sLeft.valmax = max(xAreaPoints)
        sRight.valmax = max(xAreaPoints)
        sLeft.valmin = min(xAreaPoints)
        sRight.valmin = min(xAreaPoints)

        # axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
        # axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
        axLeft.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])

def slider_config_for_table_present_four_graphs():
    global statTableTxt
    global showTableOfStats
    global axRight
    global axLeft
    global sLeft
    global sRight
    global fillAxis
    global fig
    global fig_dict
    global sliderCreatedOnce

    if fillAxis != None:
        if fig in fig_dict and fig_dict[fig]['loaded'] and not sliderCreatedOnce:
            fig.delaxes(axLeft)
            fig.delaxes(axRight)
            sliderCreatedOnce = True
        else:
            axLeft.remove()
            axRight.remove()
        axLeft = fig.add_axes([0.12, 0.08, 0.657, 0.03], facecolor=axcolor)
        axRight = fig.add_axes([0.12, 0.05, 0.657, 0.03], facecolor='#8B0000')
        axLeft.clear()
        axRight.clear()
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])
        sRight.set_axes(axRight)
        sLeft.set_axes(axLeft)

        minVal = min(fillAxis.get_xlim())

        if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
            axLeft.axvspan(minVal, sRight.val, 0, 1)
            sLeft.val = sRight.val
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
        elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
            axRight.axvspan(minVal, sLeft.val, 0, 1, facecolor=axcolor)
            sRight.val = sLeft.val
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
        else:
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)

        axLeft.margins(x = 0)
        axRight.margins(x = 0)
        sLeft.valmax = max(xAreaPoints)
        sRight.valmax = max(xAreaPoints)
        sLeft.valmin = min(xAreaPoints)
        sRight.valmin = min(xAreaPoints)

        # axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
        # axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
        axLeft.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])

def slider_config_for_table_not_present_one_graph():
    global statTableTxt
    global showTableOfStats
    global axRight
    global axLeft
    global sLeft
    global sRight
    global fillAxis
    global fig
    global fig_dict
    global sliderCreatedOnce
    if fillAxis != None:
        if fig in fig_dict and fig_dict[fig]['loaded'] and not sliderCreatedOnce:
            fig.delaxes(axLeft)
            fig.delaxes(axRight)
            sliderCreatedOnce = True
        else:
            axLeft.remove()
            axRight.remove()
        axLeft = fig.add_axes([0.12, 0.08, 0.73, 0.03], facecolor=axcolor)
        axRight = fig.add_axes([0.12, 0.05, 0.73, 0.03], facecolor='#8B0000')
        axLeft.clear()
        axRight.clear()
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])
        sRight.set_axes(axRight)
        sLeft.set_axes(axLeft)
        minVal = min(fillAxis.get_xlim())

        if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
            axLeft.axvspan(minVal, sRight.val, 0, 1)
            sLeft.val = sRight.val
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
        elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
            axRight.axvspan(minVal, sLeft.val, 0, 1, facecolor=axcolor)
            sRight.val = sLeft.val
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
        else:
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)

        axLeft.margins(x = 0)
        axRight.margins(x = 0)
        sLeft.valmax = max(xAreaPoints)
        sRight.valmax = max(xAreaPoints)
        sLeft.valmin = min(xAreaPoints)
        sRight.valmin = min(xAreaPoints)

        # axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
        # axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
        axLeft.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])

def slider_config_for_table_present_one_graph():
    global statTableTxt
    global showTableOfStats
    global axRight
    global axLeft
    global sLeft
    global sRight
    global fillAxis
    global fig
    global fig_dict
    global sliderCreatedOnce
    if fillAxis != None:
        if fig in fig_dict and fig_dict[fig]['loaded'] and not sliderCreatedOnce:
            fig.delaxes(axLeft)
            fig.delaxes(axRight)
            sliderCreatedOnce = True
        else:
            axLeft.remove()
            axRight.remove()

        axLeft = fig.add_axes([0.12, 0.08, 0.625, 0.03], facecolor=axcolor)
        axRight = fig.add_axes([0.12, 0.05, 0.625, 0.03], facecolor='#8B0000')

        axLeft.clear()
        axRight.clear()
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])
        sRight.set_axes(axRight)
        sLeft.set_axes(axLeft)

        minVal = min(fillAxis.get_xlim())

        if (sLeft.val > sRight.val and sLeft.val != prevPlotA):
            axLeft.axvspan(minVal, sRight.val, 0, 1)
            sLeft.val = sRight.val
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
        elif (sLeft.val > sRight.val and sRight.val != prevPlotB):
            axRight.axvspan(minVal, sLeft.val, 0, 1, facecolor=axcolor)
            sRight.val = sLeft.val
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
        else:
            axLeft.axvspan(minVal, sLeft.val, 0, 1)
            axRight.axvspan(minVal, sRight.val, 0, 1, facecolor=axcolor)
            axLeft.axvline(sRight.val, 0, 1, color= '#8B0000', lw = 2)
            axRight.axvline(sLeft.val, 0, 1, color= '#00A3E0', lw = 2)

        axLeft.margins(x = 0)
        axRight.margins(x = 0)
        sLeft.valmax = max(xAreaPoints)
        sRight.valmax = max(xAreaPoints)
        sLeft.valmin = min(xAreaPoints)
        sRight.valmin = min(xAreaPoints)
        # axLeft.set_xlim(min(xAreaPoints), max(xAreaPoints))
        # axRight.set_xlim(min(xAreaPoints), max(xAreaPoints))
        axLeft.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.set_xlim(min(fillAxis.get_xlim()), max(fillAxis.get_xlim()))
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])

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
            if len(set(vals)) != len(vals):
                tkMessageBox.showerror("Invalid Column Headers", "Please make sure the first row of data file contains unique names for each column header.")
                return
            headerDropDownVar.set(vals)
            headerDropDown['values'] = vals
            headerDropDown.current(0)
            plotButton.config(state="normal")
        except Exception, e:
            tkMessageBox.showerror("Unknown File", "The file you provided is either not of type .csv. or is empty.")
            return
    dataFile = file1.name

#___Normal Scale____________________________________________________________________________________________________
class NormProbScale(mscale.ScaleBase):
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

    # The scale class must have a member ``name`` that defines the
    # string used to select the scale.  For example,
    # ``gca().set_yscale("mercator")`` would be used to select this
    # scale.
    name = 'normal'

    # def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
    def __init__(self, axis, subplot=None, thresh=1, *args, **kwargs):

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

        # axis.set_minor_locator(FixedLocator(
        #     np.array(list(np.arange(.01, .10, .01)) + list(np.arange(.10, .99, .10)) + [.99]) ))
    
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

        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True

        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh

        def transform_non_affine(self, a):
            global globalMu
            global globalSigma

  
            masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
            if masked.mask.any():
                # return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
                # return np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in masked])
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                return ss.norm.ppf(masked, globalMu, globalSigma)
            else:   
                # return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))
                # return  np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in a])
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                return ss.norm.ppf(masked, globalMu, globalSigma)

        def inverted(self):
            """
            Override this method so matplotlib knows how to get the
            inverse transform for this transform.
            """
            return NormProbScale.InvertedMercatorLatitudeTransform(
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

            global globalMu
            global globalSigma
            # return np.array([1 + (-1*(np.exp(np.exp( (1-np.exp(-1*((xi/p2)**p0))) )))**(-1) ) for xi in a])
            # return np.arctan(np.sinh(a))
            # return np.array([1 + (-1*(np.exp(np.exp(xi)))**(-1) ) for xi in a])
            return ss.norm.cdf(a, globalMu, globalSigma)

        def inverted(self):
            return NormProbScale.MercatorLatitudeTransform(self.thresh)

#___Exponential Scale____________________________________________________________________________________________________
class ExponentialProbScale(mscale.ScaleBase):
    name = 'exponential'

    # def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
    def __init__(self, axis, subplot=None, thresh=1, *args, **kwargs):

        mscale.ScaleBase.__init__(self)
        if thresh > 1:
            raise ValueError("thresh must be less than pi/2")
        self.thresh = thresh

    def get_transform(self):

        return self.MercatorLatitudeTransform(self.thresh)

    def set_default_locators_and_formatters(self, axis):

        class DegreeFormatter(Formatter):
            def __call__(self, x, pos=None):
                return "%g" % (x * 100)

        # axis.set_major_locator(FixedLocator(
        #     np.radians(np.arange(-90, 90, 10))))

        # axis.set_minor_locator(FixedLocator(
        #     np.array(list(np.arange(.01, .10, .01)) + list(np.arange(.10, .99, .10)) + [.99]) ))
    
        axis.set_major_locator(FixedLocator(
            np.array([.01, .05, .10, .50, .90, .99]) ) )

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

        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True

        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh

        def transform_non_affine(self, a):
            global globalMu
            global globalSigma

            # print a

            masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
            if masked.mask.any():
                # return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
                # return np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in masked])
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                # return ss.norm.ppf(masked, globalMu, globalSigma)
                return np.array([np.log(xi) for xi in masked])

            else:   
                # return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))
                # return  np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in a])
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                # print  np.array([np.log(1-xi) for xi in masked])
                return np.array([np.log(xi) for xi in masked])

                # return np.array([np.log(1-xi) for xi in masked])

        def inverted(self):
            """
            Override this method so matplotlib knows how to get the
            inverse transform for this transform.
            """
            return ExponentialProbScale.InvertedMercatorLatitudeTransform(
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

            global globalMu
            global globalSigma
            # return np.array([1 + (-1*(np.exp(np.exp( (1-np.exp(-1*((xi/p2)**p0))) )))**(-1) ) for xi in a])
            # return np.arctan(np.sinh(a))
            # return np.array([1 + (-1*(np.exp(np.exp(xi)))**(-1) ) for xi in a])
            # return ss.norm.cdf(a, globalMu, globalSigma)
            # return np.array([1 + -1*(np.exp(xi)) for xi in a])
            return np.array([np.exp(xi) for xi in a])

        def inverted(self):
            return ExponentialProbScale.MercatorLatitudeTransform(self.thresh)
#___Lognormal Scale____________________________________________________________________________________________________
class LognormalProbScale(mscale.ScaleBase):
    name = 'lognormal'

    # def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
    def __init__(self, axis, subplot=None, thresh=1, *args, **kwargs):

        mscale.ScaleBase.__init__(self)
        if thresh > 1:
            raise ValueError("thresh must be less than pi/2")
        self.thresh = thresh
        self.specialAxis = subplot

    def get_transform(self):

        return self.MercatorLatitudeTransform(self.thresh, self.specialAxis)

    def set_default_locators_and_formatters(self, axis):

        class DegreeFormatter(Formatter):
            def __call__(self, x, pos=None):
                return "%g" % (x * 100)

        # axis.set_major_locator(FixedLocator(
        #     np.radians(np.arange(-90, 90, 10))))

        # axis.set_minor_locator(FixedLocator(
        #     np.array(list(np.arange(.01, .10, .01)) + list(np.arange(.10, .99, .10)) + [.99]) ))
    
        axis.set_major_locator(FixedLocator(
            np.array([.01, .05, .10, .50, .90, .99]) ) )

        axis.set_minor_locator(FixedLocator(np.array(list(np.arange(.01, .10, .01)) + list(np.arange(.10, .99, .10)) + [.99])))
        axis.set_major_formatter(DegreeFormatter())
        # axis.set_minor_formatter(DegreeFormatter())

    # def limit_range_for_scale(self, vmin, vmax, minpos):
    #     """
    #     Override to limit the bounds of the axis to the domain of the
    #     transform.  In the case of Mercator, the bounds should be
    #     limited to the threshold that was passed in.  Unlike the
    #     autoscaling provided by the tick locators, this range limiting
    #     will always be adhered to, whether the axis range is set
    #     manually, determined automatically or changed through panning
    #     and zooming.
    #     """

    #     vmin = 0.007438631040187271
    #     vmax = 0.990 

    #     return max(vmin, -self.thresh), min(vmax, self.thresh)

    class MercatorLatitudeTransform(mtransforms.Transform):

        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True

        def __init__(self, thresh, specialAxis):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh
            self.specialAxis = specialAxis

        def transform_non_affine(self, a):
            global globalMu_Lnorm
            global globalSigma_Lnorm
            global fig
            global fig_dict
            masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
            if masked.mask.any():
                # return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
                # return np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in masked])
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                # return ss.norm.ppf(masked, globalMu, globalSigma)
                print self.specialAxis
                
                if fig in fig_dict and self.specialAxis in fig_dict[fig]['dictOfAxes']:
                    
                    loc = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['loc'][0]
                    shape = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['shape'][0]
                    scale = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['scale'][0]

                    return ss.lognorm.ppf(masked, shape, loc=loc, scale=scale)
                else:
                    raise AttributeError('axis ' + self.specialAxis + 'does not have shape, loc, and scale parameters in memory')

            else:   
                # return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))
                # return  np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in a])
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                # print  np.array([np.log(1-xi) for xi in masked])

                if fig in fig_dict and self.specialAxis in fig_dict[fig]['dictOfAxes']:
                    
                    loc = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['loc'][0]
                    shape = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['shape'][0]
                    scale = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['scale'][0]

                    return ss.lognorm.ppf(masked, shape, loc=loc, scale=scale)
                else:
                    raise AttributeError('axis ' + self.specialAxis + 'does not have shape, loc, and scale parameters in memory')

                # return np.array([np.log(xi) for xi in masked])

                # return np.array([np.log(1-xi) for xi in masked])

        def inverted(self):
            """
            Override this method so matplotlib knows how to get the
            inverse transform for this transform.
            """
            return LognormalProbScale.InvertedMercatorLatitudeTransform(
                self.thresh, self.specialAxis)

    class InvertedMercatorLatitudeTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True


        def __init__(self, thresh, specialAxis):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh
            self.specialAxis = specialAxis
        def transform_non_affine(self, a):

            global globalMu
            global globalSigma
            global fig
            global fig_dict
            # return np.array([1 + (-1*(np.exp(np.exp( (1-np.exp(-1*((xi/p2)**p0))) )))**(-1) ) for xi in a])
            # return np.arctan(np.sinh(a))
            # return np.array([1 + (-1*(np.exp(np.exp(xi)))**(-1) ) for xi in a])
            # return ss.norm.cdf(a, globalMu, globalSigma)
            # return np.array([1 + -1*(np.exp(xi)) for xi in a])

            if fig in fig_dict and self.specialAxis in fig_dict[fig]['dictOfAxes']:
                
                loc = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['loc'][0]
                shape = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['shape'][0]
                scale = fig_dict[fig]['dictOfAxes'][self.specialAxis]['specsTable']['scale'][0]

                return ss.lognorm.cdf(a, shape, loc=loc, scale=scale)
            else:
                raise AttributeError('axis ' + self.specialAxis + 'does not have shape, loc, and scale parameters in memory')
            # return np.array([np.exp(xi) for xi in a])

        def inverted(self):
            return LognormalProbScale.MercatorLatitudeTransform(self.thresh, self.specialAxis)

class MercatorLatitudeScale(mscale.ScaleBase):

    # Axis used after rank regression is done on data.

    # The scale class must have a member ``name`` that defines the
    # string used to select the scale.  For example,
    # ``gca().set_yscale("mercator")`` would be used to select this
    # scale.
    name = 'mercator'

    # def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
    def __init__(self, axis, subplot=None, thresh=1, *args, **kwargs):


        mscale.ScaleBase.__init__(self)
        if thresh > 1:
            raise ValueError("thresh must be less than pi/2")
        self.thresh = thresh

    def get_transform(self):

        return self.MercatorLatitudeTransform(self.thresh)

    def set_default_locators_and_formatters(self, axis):

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

            masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
            if masked.mask.any():
                # return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
                # return np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in masked])
                # print(np.array([np.log(np.log(1/(1-xi))) for xi in masked]))
                #_______________________

                return np.array([np.log(np.log(1/(1-xi))) for xi in masked])

            else:
                # return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))
                # return  np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in a])
                # print(np.array([np.log(np.log(1/(1-xi))) for xi in masked]))
                return np.array([np.log(np.log(1/(1-xi))) for xi in masked])

        def inverted(self):

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
mscale.register_scale(NormProbScale)
mscale.register_scale(ExponentialProbScale)
mscale.register_scale(LognormalProbScale)

#________________________________________________________________________________________________________

class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""
    tuples = None
    headers = None
    container = None
    def __init__(self, headerL, tupleVals, parent, mode = None, colnum = None):
        self.tuples = tupleVals
        tuples = self.tuples
        self.headers = headerL
        headers = self.headers
        self.tree = None
        self.parent = parent
        # self.container = thisFrame
        # container = self.container
        self.colnum = colnum
        self.mode = mode
        self._setup_widgets(self.mode)
        # if len(self.headers):
        self._build_tree()

    def _set_data(self, headerL, tupleVals):
        if self.tree != None:
            self.tuples = tupleVals
            self.headers = headerL
            self._build_tree()

    def _setup_widgets(self, mode):
        # s = """\click on header to sort by that column to change width of column drag boundary"""
        # msg = ttk.Label(wraplength="4i", justify="left", anchor="n", padding=(10, 2, 10, 6), text=s)
        # msg.pack(fill='x')

        if mode == 'single_column' and self.colnum != None:
            # groupTitle = ttk.Label(self.parent, text = "Group 1", font = MED_FONT)
            # groupTitle.grid(sticky = "nw", row=0, column= 0, padx = 10)
            self.tree = ttk.Treeview(self.parent, columns=self.headers, show="headings", selectmode='browse')
            self.tree.grid(row=1, column = self.colnum, sticky='ew',in_=self.parent, columnspan=1, rowspan=9, padx=10, pady=3)
            self.tree.grid_propagate(False)

        elif not mode:
            container1 = self.parent
            container = ttk.Frame(container1)
            # create a treeview with dual scrollbars
            B1 = ttk.Button(container, text="Okay", command= self.dostuff)
            B1.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
            self.tree = ttk.Treeview(container1, columns=self.headers, show="headings")
            vsb = ttk.Scrollbar(container1, orient="vertical", command=self.tree.yview)
            hsb = ttk.Scrollbar(container1, orient="horizontal", command=self.tree.xview)
            self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            self.tree.grid(column=0, row=0, sticky='nsew', in_=container1)
            vsb.grid(column=1, row=0, sticky='ns', in_=container1)
            hsb.grid(column=0, row=1, sticky='ew', in_=container1)

            container1.grid_columnconfigure(0, weight=1)
            container1.grid_rowconfigure(0, weight=1)

        # self.treeFrame = Frame(self,width = 300, height = 400)
        # self.treeFrame.grid(row=4, column=3,columnspan=3,rowspan=9, padx=10, pady=3)
        # self.treeFrame.columnconfigure(3,weight=1)

        # self.tree = ttk.Treeview(self.treeFrame, selectmode='browse')
        # self.tree.grid(row=1, column=0, sticky=NSEW,in_=self.treeFrame, columnspan=3, rowspan=9)
        # self.tree.grid_propagate(False)
        # self.scbHDirSel =Scrollbar(self.treeFrame, orient=HORIZONTAL, command=self.tree.xview)
        # self.scbVDirSel =Scrollbar(self.treeFrame, orient=VERTICAL, command=self.tree.yview)
        # self.scbVDirSel.grid(row=1, column=50, rowspan=50, sticky=NS, in_=self.treeFrame)
        # self.scbHDirSel.grid(row=52, column=0, rowspan=2,columnspan=3, sticky=EW,in_=self.treeFrame)
        # self.tree.configure(yscrollcommand=self.scbVDirSel.set, xscrollcommand=self.scbHDirSel.set) 
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
class TabFrame(tk.Frame):
    def __init__(self, master, name, image=None, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.name = name
        self.master = master
        self.bind("<Visibility>", self.on_visibility)
        # self.bind("<ButtonPress-3>", self.on_right_click)


        self.tab_image = image
        self.tab_selected_before_this = 0
        self.recentlyAdded = None
        self.hiddenGraphsMenu = tk.Menu(master, tearoff=0)
        self.justLoadedFromMem = False
        self.rightClickMenu = tk.Menu(master, tearoff=0)

    def dostuff(self):
        i = 0

    # def on_right_click(self, event):
    #     print("WIPPPEEEE")

    def on_visibility(self, event):
        global canvasOffsetX
        global canvasOffsetY
        global current_tabs_dict
        global notebookFrame
        global canContainer
        global programmaticDeletionFlag
        global fig_dict

        print('in ONVISIBILITY')
        if programmaticDeletionFlag: return
        
        # if 'tabs' in fig_dict: return


        if notebookFrame.index(self) != 0:
            # hiding the previous view and creating the new view on notebook

            recentlyHiddenTabID = notebookFrame.tabs()[notebookFrame.index(self)]
            recentlyHiddenTabLabel = notebookFrame.tab(recentlyHiddenTabID, "text")
            # Do this every time we change tabs... update for when hiddentabsbutton is pressed
            hiddenGraphsTab = notebookFrame.tabs()[0]
            notebookFrame.nametowidget(hiddenGraphsTab).set_tab_selected_before_this(notebookFrame.index(self))


               # tab was deleted and not just now opened from disk                       # tab has been changed
            # if (notebookFrame.nametowidget(hiddenGraphsTab).tab_selected_before_this == notebookFrame.index(self)): return
            try:
                print notebookFrame.index(self) != notebookFrame.index(canContainer)
            except:
                pass 
                
            if self.justLoadedFromMem:
                self.justLoadedFromMem = False
                self.update()
                return

            if ('tabs' not in fig_dict and canContainer not in notebookFrame.tabs()) or notebookFrame.index(self) != notebookFrame.index(canContainer):
                # print notebookFrame.index(self), notebookFrame.index(canContainer)
                # print notebookFrame.nametowidget(canContainer) in notebookFrame.tabs()

                splitLabel1 = recentlyHiddenTabLabel.split('(')
                restoredOrigName = '('.join(splitLabel1[:-1])
                if recentlyHiddenTabLabel in current_tabs_dict or restoredOrigName in current_tabs_dict:
                    reopenGraph(recentlyHiddenTabLabel, recentlyHiddenTabID)
                    self.update()


        else:
            print(event.x, event.y, event.type)
            if self.tab_selected_before_this < len(notebookFrame.tabs()):
                print('force to stay on same tab')
                notebookFrame.select(self.tab_selected_before_this)
            self.hiddenGraphsMenu.tk_popup(app.winfo_x() + 76, app.winfo_y() + int(cancan.get_width_height()[1]) + canvasOffsetY - 19* len(notebookFrame.tabs()) + 19*7, 0)
        print('over ONVISIBILITY')

    def set_tab_selected_before_this(self, index):
        self.tab_selected_before_this = index

# TODO need to update graphTitle variable with rename, and to 
# update the crrent_tabs_dict, to remove the current tab, and 
# make a new entry for it.
def renameTab(label):
    global notebookFrame
    global current_tabs_dict
    global canContainer
    global graphTitle
    global fig_dict
    global fig
    print("in RENAME")
    if not fig or fig not in fig_dict: return

    if len(str(label.strip())) == 0:
        label = 'Untitled'

    context = None
    if 'lastSaved' not in fig_dict[fig]:
        context = 'first'

    currentTime = str(datetime.datetime.now())
    if label in current_tabs_dict:
        duplicates = len(current_tabs_dict[label])
        current_tabs_dict[label] += [currentTime]
        fig_dict[fig]['lastSaved'] = currentTime
        notebookFrame.tab(notebookFrame.select(), text = str(label) + "(" + str(duplicates) + ")")
        
        # graphTitle.set(str(graphTitle.get()) + "(" + str(duplicates) + ")")
        # fig.suptitle(graphTitle.get(), fontsize=18, fontweight='bold', fontname="Calibri")
    else:
        current_tabs_dict[label] = [currentTime]
        fig_dict[fig]['lastSaved'] = currentTime
        notebookFrame.tab(notebookFrame.select(), text = str(label))

    saveWorkspace(context)
    # if len(notebookFrame.tabs()) > 3:
    #     recentlyHiddenTabID = notebookFrame.tabs()[notebookFrame.index(canContainer) - 2]
    #     recentlyHiddenTabLabel = notebookFrame.tab(recentlyHiddenTabID, "text")
    #     hiddenGraphsTab = notebookFrame.tabs()[0]
    #     notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.add_command(label=recentlyHiddenTabLabel,  command = lambda: reopenGraph(recentlyHiddenTabLabel, recentlyHiddenTabID))
    #     notebookFrame.nametowidget(hiddenGraphsTab).recentlyAdded = recentlyHiddenTabID

        #     toHideTabLabel = notebookFrame.tab(tabID, "text")
        # notebookFrame.hide(tabID)
        # notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.add_command(label=toHideTabLabel,  command = lambda: reopenGraph(toHideTabLabel, tabID))
        # notebookFrame.add(notebookFrame.nametowidget(hiddenGraphsTab))
        # notebookFrame.nametowidget(hiddenGraphsTab).recentlyAdded = tabID
    print("over RENAME")

def hideExtraTabs(tabID = None):
    global notebookFrame
    global current_tabs_dict
    global canContainer
    global graphTitle
    global fig_dict
    global fig

    print("in HIDE EXTRA TABS")
    hiddenGraphsTab = notebookFrame.tabs()[0]
    hiddenGraphsTabShown = 'normal' == notebookFrame.tab(hiddenGraphsTab, 'state') 

    numGraphsInHiddenMenu = 0
    try:
        numGraphsInHiddenMenu = notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.index("end") + 1
    except:
        numGraphsInHiddenMenu = 0
        pass
    print(numGraphsInHiddenMenu)
    print(len(notebookFrame.tabs()))
    print('gothere',  len(notebookFrame.tabs()) - numGraphsInHiddenMenu)
    if len(notebookFrame.tabs()) > 1 and len(notebookFrame.tabs()) - numGraphsInHiddenMenu > 3:
        print('gothere2: reduce tabs')
        if not tabID:
            print('choosing a random visible tab')
            for i in range(0, len(notebookFrame.tabs())):
                thisID = notebookFrame.tabs()[i]
                if 'normal' == notebookFrame.tab(thisID, 'state') and str(thisID) != str(canContainer) and i != 0:
                    tabID = thisID
                    print('found a tab')
                    break
        print('hiding the tab to menu')
        toHideTabLabel = notebookFrame.tab(tabID, "text")
        notebookFrame.hide(tabID)
        notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.add_command(label=toHideTabLabel,  command = lambda: reopenGraph(toHideTabLabel, tabID, "menu"))
        notebookFrame.add(notebookFrame.nametowidget(hiddenGraphsTab))
        notebookFrame.nametowidget(hiddenGraphsTab).recentlyAdded = tabID
        numGraphsInHiddenMenu += 1
    elif  len(notebookFrame.tabs()) > 1 and numGraphsInHiddenMenu > 0 and len(notebookFrame.tabs()) - numGraphsInHiddenMenu < 3:
        print('gothere3: increase tabs')

        notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.delete(numGraphsInHiddenMenu - 1)
        numGraphsInHiddenMenu -= 1

        tabID = notebookFrame.nametowidget(hiddenGraphsTab).recentlyAdded # graph we just deleted from menu
        notebookFrame.add(tabID)

        if numGraphsInHiddenMenu - 1 >= 0: # there is at least 1 more element left in menu
            nextCandLabel = notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.entrycget(numGraphsInHiddenMenu - 1, "label")

            for i in range(0, len(notebookFrame.tabs())):
                thisID = notebookFrame.tabs()[i]
                if nextCandLabel == notebookFrame.tab(thisID, "text"):
                    notebookFrame.nametowidget(hiddenGraphsTab).recentlyAdded = thisID
                    break
            print("recently added was updated")


    if numGraphsInHiddenMenu == 0 and 'tabs' not in fig_dict:
        notebookFrame.nametowidget(hiddenGraphsTab).recentlyAdded = None
        notebookFrame.hide(notebookFrame.nametowidget(hiddenGraphsTab))
        print('gothere4')

    # if fig != None and fig in fig_dict:
    #     for figkey in dict(fig_dict):
    #         if figkey != fig:
    #             del fig_dict[figkey]
        #remove a tab from hiddenGraphsMenu
        #hide hiddenGraphsMenu
        #add the removed tab to Notebook

    print("over HIDE EXTRA TABS")

# reopens a graph specified by tabLabel and tabID.
#
# if this is one of multiple tabs, old tab is hidden 
# and this one shown.
# if this is the only tab, the canContainer
# is set and graph is opened.
# MODIFIED
def reopenGraph(tabLabel, tabID, context = None):
    global notebookFrame
    global current_tabs_dict
    global canContainer
    global graphTitle
    global fig_dict
    global fig
    print("in REOPEN")


    for i in range(0, len(notebookFrame.tabs())):
        print i
        thisID = notebookFrame.tabs()[i]
        if 'Blank Chart*' == notebookFrame.tab(thisID, "text"):
            notebookFrame.forget(thisID)
            hideExtraTabs()

    # if len(current_fig_dict.keys()) :

    saveWorkspace(context = 'final')
    # loaded_fig_dict = None
    # with open('savedWkspc1.pickle', 'rb') as handle:
    #     loaded_fig_dict = pl.load(handle)
    #     handle.close()
    print tabLabel
    lastSavedTimeExpected = None
    if tabLabel in current_tabs_dict:
        lastSavedTimeExpected = current_tabs_dict[tabLabel][0]
    else:
        splitLabel1 = tabLabel.split('(')
        splitLabel2 = splitLabel1[-1].split(')')
        if len(splitLabel2) != 2: return
        numToConvert = splitLabel2[0]
        if not numToConvert.isalnum(): return 
        index = int(numToConvert)
        restoredOrigName = '('.join(splitLabel1[:-1])

        if restoredOrigName in current_tabs_dict:
            lastSavedTimeExpected = current_tabs_dict[restoredOrigName][index]

    fig = None
    for figkey in fig_dict.keys():
        if fig_dict[figkey]['lastSaved'] == lastSavedTimeExpected:
            fig = figkey
            break
    if fig in fig_dict: print("fig was obtained :)")

    # print fig_dict[fig]

    #TODO INVESTIGATE
    if canContainer != None and fig in fig_dict:
        print("if this graph came from hidden menu, delete the entry in menu!!")
        oldCanContainer = canContainer
        canContainer = notebookFrame.nametowidget(tabID)
        openFig(fig)

        # TODO
        hiddenGraphsTab = notebookFrame.tabs()[0]
        menuIndex = -1

        try: 
            menuIndex = notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.index(tabLabel)
        except:
            menuIndex = -1
            pass

        if menuIndex >= 0:
            print('case from menu, tab will be removed from menu.')
            notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.delete(menuIndex)
            notebookFrame.add(canContainer)
            notebookFrame.select(notebookFrame.index(canContainer))
            hideExtraTabs(oldCanContainer)

        # hideExtraTabs(oldCanContainer) # if not from menu don't need to call hide
    else:
        print('graph was forced to open, open graph')
        canContainer = notebookFrame.nametowidget(tabID)
        openFig(fig)

    print("over REOPEN")

# saves the current figure.
# creates a new tab for the new figure.
# sets tab selected before property of the hiddenGraphsTab.
def addTab(name = 'Blank Chart*', selectedFromMenu = False):
    global notebookFrame
    global current_tabs_dict
    global canContainer
    global graphTitle
    print("in ADDTAB")
    
    #first want to save the previous figure...
        # replace the figure into the figdict...
        # saveWorkspace

    #by default, name will be Blank Chart*

    if str(name) == 'Blank Chart*': # a new chart is being created...
        saveWorkspace(context = 'final')

    canContainer = TabFrame(master =notebookFrame, name ="Chart", width=200, height=200)
    if str(name) != 'Blank Chart*':
        canContainer.justLoadedFromMem = True
    # canContainer.grid_propagate(False)
    notebookFrame.add(canContainer, text=name, compound=tk.BOTTOM) # since canContainer now equals the chart to appear on_visibility, reopen will not be called.
    canContainer.grid_rowconfigure(0, weight = 1)
    canContainer.grid_columnconfigure(0, weight = 1)
    canContainer = notebookFrame.nametowidget(canContainer)

    # Do this every time we change tabs... update for when hiddentabsbutton is pressed
    hiddenGraphsTab = notebookFrame.tabs()[0]
    notebookFrame.nametowidget(hiddenGraphsTab).set_tab_selected_before_this(notebookFrame.index(canContainer))
    print(notebookFrame.nametowidget(hiddenGraphsTab).tab_selected_before_this)
    notebookFrame.hide(notebookFrame.nametowidget(hiddenGraphsTab))

    notebookFrame.select(notebookFrame.index(canContainer)) #move focus to new tab << on_visibility is called... but name is not in current_dict yet...
    print("previous tab saved and new tab added successfully")
    # return canContainer
    # label = notebookFrame.tab(notebookFrame.select(), "text")
    # canvas = FancyFigureCanvas(fig, canContainer)
    # tab = TabFrame(notebookFrame, name)
    # notebookFrame.add(tab, text=name)
    # canContainer = notebookFrame.nametowidget(notebookFrame.select())

    # notebookFrame = notebookFrame.nametowidget(notebookFrame.select()).master
    # notebookFrame.tab(notebookFrame.select(), "text")
    # notebookFrame = ttk.Notebook(self, style='bottomtab.TNotebook')
    # canContainer = TabFrame(master=notebookFrame, name ="Chart", width=200, height=200)
    # notebookFrame.add(canContainer, text="Chart1", compound=tk.BOTTOM)
    # notebookFrame.select( notebookFrame.index(notebookFrame.select()))

    # canvas = FancyFigureCanvas(fig, canContainer)
    # tab = TabFrame(notebookFrame, name)

    # notebookFrame.add(tab, text=name)
    # notebookFrame.nametowidget(notebookFrame.select())
    # notebookFrame.tab(notebookFrame.select(), text = 'myNewText')
    
    # notebookFrame.tab(notebookFrame.select(), text=graphTitle.get())
    print("over ADDTAB")


def openFig(newFig = None):
    global axRight
    global axLeft
    global sRight
    global sLeft
    global a
    global fig
    global cursor
    global cursors
    global canContainer
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
    global statTableTxt
    global fillAxis
    global showTableOfStats
    global sliderCreatedOnce
    global sessionType
    global cursorState
    global sliderCIDs

    print("in OPEN")

    try: 
        cancan.get_tk_widget().destroy()
        cancan = None
    except:
        pass    

    if fig not in fig_dict or newFig not in fig_dict: return

    # fig_dict[fig]['loaded'] = True
    dataFile = fig_dict[fig]['csv_src']
    if len(fig_dict[fig]['slider_axes']) == 3:
        axLeft, axRight, fillBetFigure = fig_dict[fig]['slider_axes']
    elif len(fig_dict[fig]['slider_axes']) == 2:
        axLeft, axRight = fig_dict[fig]['slider_axes']

    sLeftVal, sRightVal = fig_dict[fig]['slider_values']

    fillAxis = fig_dict[fig]['fillAxis']
    statTableTxt =  fig_dict[fig]['statsTable']

    if statTableTxt.get_visible():
        showTableOfStats = True
    else:
        showTableOfStats = False

    sliderCreatedOnce = False
    sessionType = fig_dict[fig]['sessionType']
    if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
        topAxis = fig_dict[fig]['dictOfAxes'].keys()[0]
        globalMin = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mn']
        globalMu = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mu']
        globalMax = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mx']
        globalSigma = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['sigma']
        globalMultiplier = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['multiplier']
        fillAxis = topAxis
        topAxis.set_ylim(min(topAxis.get_ylim()), max(topAxis.get_ylim()))
        topAxis.set_xlim(min(topAxis.get_xlim()), max(topAxis.get_xlim()))

        for line in topAxis.get_lines():
            if '_' not in line.get_label():
                xAreaPoints = line.get_xdata()
                yAreaPoints = line.get_ydata()
                totalArea = trapz(yAreaPoints, xAreaPoints)
                break
        addAxesDict = fig_dict[fig]['dictOfAxes'][topAxis]['addAxes']
        for axkey in addAxesDict.keys():

            axkey.set_ylim(min(axkey.get_ylim()), max(axkey.get_ylim()))
            axkey.set_xlim(min(axkey.get_xlim()), max(axkey.get_xlim()))
            for artist in axkey.get_children():
                if artist.get_label() == 'histogram':
                    list_a, list_b = zip(*addAxesDict[axkey])
                    globalNPerBin = list(list_b)
                    globalBins = list(list_a)
                    break

    elif fig_dict[fig]['sessionType'] == 'RELA': # reload Rela

        dictOfAxes = fig_dict[fig]['dictOfAxes']
        for axkey in dictOfAxes.keys():

            if 'axesScales' in fig_dict[fig]['dictOfAxes'][axkey]:                        
                axkey.set_yscale(fig_dict[fig]['dictOfAxes'][axkey]['axesScales'][1], subplot = axkey)
                axkey.set_xscale(fig_dict[fig]['dictOfAxes'][axkey]['axesScales'][0]) 

            axkey.set_ylim(min(axkey.get_ylim()), max(axkey.get_ylim()))
            axkey.set_xlim(min(axkey.get_xlim()), max(axkey.get_xlim()))

            if axkey.get_label() == 'pdf':
                for line in axkey.get_lines():
                    if '_' not in line.get_label():

                        globalMin = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['mn']
                        globalMu = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['mu']
                        globalMax = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['mx']
                        globalSigma = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['sigma']
                        globalMultiplier = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['multiplier']

                        xAreaPoints = line.get_xdata()
                        yAreaPoints = line.get_ydata()
                        totalArea = trapz(yAreaPoints, xAreaPoints)
                        
    cancan = FancyFigureCanvas(fig, canContainer)
    fig.set_canvas(cancan)
    can = cancan.get_tk_widget()
    can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
    cancan._tkcanvas.grid(row=0, column=0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)
    connection_id = cancan.mpl_connect('button_press_event', on_press) #uncomment
    cancan.axpopup.entryconfig(1, state='normal')
    cancan.addable_menu.entryconfig(0, state = 'normal')

    # menuIndex = notebookFrame.nametowidget(hiddenGraphsTab).hiddenGraphsMenu.index(tabLabel)

    if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
        change_session('PDF')
        cursor = InformativeCursor(topAxis, useblit=True, color='red', linewidth=.5)


    elif fig_dict[fig]['sessionType'] == 'RELA': # reload Rela
        change_session('RELA')
        dictOfAxes = fig_dict[fig]['dictOfAxes']
        for axkey in dictOfAxes.keys():
            cursors += [InformativeCursor(axkey, useblit=True, color='red', linewidth=.5)]

        # cancan.addable_menu.entryconfig(cancan.addable_menu.index('Figure Title'), state = 'normal')


    if not cursorState.get():
        toggleCrossHairs()

    print(axLeft, axRight)
    with plt.style.context('classic'):
        sLeft = Slider2(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')
        sRight = Slider2(axRight, 'Time', 0, 1, valinit=0, color = axcolor)

    sliderCIDs[0] = sLeft.on_changed(update)
    sliderCIDs[1] = sRight.on_changed(update)
    cancan.toggle_slider_vis()
    cancan.toggle_slider_vis()

    cancan.toggle_table_of_stats()
    cancan.toggle_table_of_stats()

    axLState = axLeft.get_visible()
    axRState = axRight.get_visible()

    if not axLState:
        axLeft.set_visible(True)
        axRight.set_visible(True)

    updateClone(sLeftVal, sRightVal)
    axLeft.set_visible(axLState)
    axRight.set_visible(axRState)
    cancan.draw()
    print("over OPEN")
    
 # TODO: this function will open any kind of graph session. Will take in a clicked Axis.
def go_to_next_slide(newFig = None):
    global axRight
    global axLeft
    global sRight
    global sLeft
    global a
    global fig
    global cursor
    global cursors
    global canContainer
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
    global statTableTxt
    global fillAxis
    global showTableOfStats
    global sliderCreatedOnce
    global sessionType
    global cursorState
    global sliderCIDs
    global thisWkspcName
    global current_tabs_dict

    print("in OPEN")

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
    #cursor="wait")
    # #)

    if not newFig and thisWkspcName != None:
        loaded_fig_dict = None
        with open(thisWkspcName, 'rb') as handle:
            loaded_fig_dict = pl.load(handle)
            handle.close()
        # keys = sorted(fig_dict.keys())
        # fig = keys[0]
        fig_dict = dict(loaded_fig_dict)
        for f in fig_dict.keys():
            if str(f) != 'tabs':
                fig_dict[f]['loaded'] = True
            else:
                current_tabs_dict = dict(fig_dict[f])
        return
        # fig = fig_dict.keys()[0]
    else:
        fig = newFig


    try: 
        cancan.get_tk_widget().destroy()
        cancan = None
    except:
        pass    

    print(fig)
    
    dataFile = fig_dict[fig]['csv_src']
    if len(fig_dict[fig]['slider_axes']) == 3:
        axLeft, axRight, fillBetFigure = fig_dict[fig]['slider_axes']
    elif len(fig_dict[fig]['slider_axes']) == 2:
        axLeft, axRight = fig_dict[fig]['slider_axes']

    sLeftVal, sRightVal = fig_dict[fig]['slider_values']

    fillAxis = fig_dict[fig]['fillAxis']
    statTableTxt =  fig_dict[fig]['statsTable']

    if statTableTxt.get_visible():
        showTableOfStats = True
    else:
        showTableOfStats = False

    sliderCreatedOnce = False
    sessionType = fig_dict[fig]['sessionType']
    if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
        topAxis = fig_dict[fig]['dictOfAxes'].keys()[0]
        globalMin = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mn']
        globalMu = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mu']
        globalMax = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['mx']
        globalSigma = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['sigma']
        globalMultiplier = fig_dict[fig]['dictOfAxes'][topAxis]['specsTable']['multiplier']
        fillAxis = topAxis
        topAxis.set_ylim(min(topAxis.get_ylim()), max(topAxis.get_ylim()))
        topAxis.set_xlim(min(topAxis.get_xlim()), max(topAxis.get_xlim()))

        for line in topAxis.get_lines():
            if '_' not in line.get_label():
                xAreaPoints = line.get_xdata()
                yAreaPoints = line.get_ydata()
                totalArea = trapz(yAreaPoints, xAreaPoints)
                break
        addAxesDict = fig_dict[fig]['dictOfAxes'][topAxis]['addAxes']
        for axkey in addAxesDict.keys():

            axkey.set_ylim(min(axkey.get_ylim()), max(axkey.get_ylim()))
            axkey.set_xlim(min(axkey.get_xlim()), max(axkey.get_xlim()))
            for artist in axkey.get_children():
                if artist.get_label() == 'histogram':
                    list_a, list_b = zip(*addAxesDict[axkey])
                    globalNPerBin = list(list_b)
                    globalBins = list(list_a)
                    break

    elif fig_dict[fig]['sessionType'] == 'RELA': # reload Rela

        dictOfAxes = fig_dict[fig]['dictOfAxes']
        for axkey in dictOfAxes.keys():

            if 'axesScales' in fig_dict[fig]['dictOfAxes'][axkey]:                        
                axkey.set_yscale(fig_dict[fig]['dictOfAxes'][axkey]['axesScales'][1], subplot = axkey)
                axkey.set_xscale(fig_dict[fig]['dictOfAxes'][axkey]['axesScales'][0]) 

            axkey.set_ylim(min(axkey.get_ylim()), max(axkey.get_ylim()))
            axkey.set_xlim(min(axkey.get_xlim()), max(axkey.get_xlim()))

            if axkey.get_label() == 'pdf':
                for line in axkey.get_lines():
                    if '_' not in line.get_label():

                        globalMin = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['mn']
                        globalMu = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['mu']
                        globalMax = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['mx']
                        globalSigma = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['sigma']
                        globalMultiplier = fig_dict[fig]['dictOfAxes'][axkey]['specsTable']['multiplier']

                        xAreaPoints = line.get_xdata()
                        yAreaPoints = line.get_ydata()
                        totalArea = trapz(yAreaPoints, xAreaPoints)
                        
    cancan = FancyFigureCanvas(fig, canContainer)
    fig.set_canvas(cancan)
    can = cancan.get_tk_widget()
    can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
    cancan._tkcanvas.grid(row=0, column=0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)
    connection_id = cancan.mpl_connect('button_press_event', on_press) #uncomment
    cancan.axpopup.entryconfig(1, state='disabled')
    cancan.addable_menu.entryconfig(0, state = 'disabled')

    if fig_dict[fig]['numAxes'] == 1 and fig_dict[fig]['sessionType'] == 'PDF':
        change_session('PDF')
        cursor = InformativeCursor(topAxis, useblit=True, color='red', linewidth=.5)


    elif fig_dict[fig]['sessionType'] == 'RELA': # reload Rela
        change_session('RELA')
        dictOfAxes = fig_dict[fig]['dictOfAxes']
        for axkey in dictOfAxes.keys():
            cursors += [InformativeCursor(axkey, useblit=True, color='red', linewidth=.5)]

    if not cursorState.get():
        toggleCrossHairs()

    with plt.style.context('classic'):
        sLeft = Slider2(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')
        sRight = Slider2(axRight, 'Time', 0, 1, valinit=0, color = axcolor)

    sliderCIDs[0] = sLeft.on_changed(update)
    sliderCIDs[1] = sRight.on_changed(update)
    cancan.toggle_slider_vis()
    cancan.toggle_slider_vis()

    cancan.toggle_table_of_stats()
    cancan.toggle_table_of_stats()

    axLState = axLeft.get_visible()
    axRState = axRight.get_visible()

    if not axLState:
        axLeft.set_visible(True)
        axRight.set_visible(True)

    updateClone(sLeftVal, sRightVal)
    axLeft.set_visible(axLState)
    axRight.set_visible(axRState)
    cancan.draw()
    print("over OPEN")
    #cursor="")

#___________________________________________________________________________________________________            
class Slider2(Slider):

    def set_axes(self, ax):
        self.ax = ax
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
        #____for PDF Graphing___#
        self.popup_menu = tk.Menu(parent, tearoff=0)
        self.popup_menu.add_command(label="Show Slider", command=self.toggle_slider_vis)
        self.popup_menu.add_command(label = "Hide Table of Stats", command =self.toggle_table_of_stats)
        self.popup_menu.add_command(label="Hide Histogram", command= lambda: popupmsg('Not Supported'))
        self.popup_menu.add_command(label="Save as Image", command=saveImage)

        self.addable_menu = tk.Menu(parent, tearoff = 0)
        self.addable_menu.add_command(label = "Reference Line", command=self.ref_line_wrapper)
        self.addable_menu.add_command(label = "Chart Title", command= self.set_graph_title1)
        addable_menu = self.addable_menu
        self.popup_menu.add_cascade(label="Add", menu = self.addable_menu)
        # self.popup_menu.add_command(label = "")
        self.removable_menu = tk.Menu(parent, tearoff = 0)
        self.removable_menu.add_command(label = "Reference Lines", command=self.rem_ref_lines)
        self.removable_menu.add_command(label = "Secondary Axis Ticks", command= lambda: popupmsg('Not Supported'))
        removable_menu = self.removable_menu
        self.popup_menu.add_cascade(label="Remove", menu = self.removable_menu)
        popup_menu = self.popup_menu

        #____for Multiple Graphs in a page___#
        self.popup_multi = tk.Menu(parent, tearoff=0)
        self.popup_multi.add_command(label="Maximize", command= self.maximize_wrapper)
        self.popup_multi.add_cascade(label="Add", menu = self.addable_menu)
        self.popup_menu.add_cascade(label="Remove", menu = self.removable_menu)

        self.popup_multi.add_command(label="See All Stats", command = lambda: popupmsg('Not Supported'))

        self.view_menu = tk.Menu(parent, tearoff = 0)
        self.view_menu.add_command(label = "View with Linear Scale", command=self.toggle_axis_scale)

        popup_multi = self.popup_multi

        self.axpopup = tk.Menu(parent, tearoff=0)
        self.axpopup.add_command(label="Hide", command = self.toggle_slider_vis)
        self.axpopup.add_command(label="Set Cursor Values", command=self.set_slider_values)
        axpopup = self.axpopup


        self.gray_space_menu = tk.Menu(parent, tearoff=0)
        self.gray_space_menu.add_command(label="Show Slider", command=self.toggle_slider_vis)
        self.gray_space_menu.add_command(label = "Hide Table of Stats", command =self.toggle_table_of_stats)
        self.gray_space_menu.add_command(label="Save as Image", command=saveImage)

        gray_space_menu = self.gray_space_menu

    def toggle_axis_scale(self):
        global sessionType
        global fig_dict
        global fig
        axes = self.clickedAxes
        if 'axesScales' not in fig_dict[fig]['dictOfAxes'][axes]: 
            fig_dict[fig]['dictOfAxes'][axes]['axesScales'] = (str(axes.get_xscale()),  str(axes.get_yscale()))

        if axes.get_yscale() == fig_dict[fig]['dictOfAxes'][axes]['axesScales'][1] and axes.get_xscale() == fig_dict[fig]['dictOfAxes'][axes]['axesScales'][0]:
            self.clickedAxes.set_yscale('linear')
            self.clickedAxes.set_xscale('linear')
            self.view_menu.entryconfigure(0, label = 'View with Original Scale')               
                # print(cancan.popup_multi.index('Scale'))
            # self.filemenu2.delete("Stop")
            # cancan.addable_menu.entryconfigure(1, command = cancan.set_graph_title1)
        else:
            print(fig_dict[fig]['dictOfAxes'][axes]['axesScales'])
            self.clickedAxes.set_yscale(fig_dict[fig]['dictOfAxes'][axes]['axesScales'][1], subplot = axes)
            self.clickedAxes.set_xscale(fig_dict[fig]['dictOfAxes'][axes]['axesScales'][0]) 
            self.view_menu.entryconfigure(0, label = 'View with Linear Scale')               

        self.draw_idle()
        

    def toggle_slider_vis(self):
        global showTableOfStats
        global axRight
        global axLeft
        global fig
        global fig_dict
        if axRight != None and axLeft != None:
            axRight.set_visible(not axRight.get_visible())
            axLeft.set_visible(not axLeft.get_visible())
            # axRight = fig.add_axes()


            if not axRight.get_visible(): 
                if fig in fig_dict and len(fig_dict[fig]['dictOfAxes']) > 1: # multiple plots, then     
                    fig.subplots_adjust(wspace=.25, hspace=.35, left=0.12, right=0.88, top=0.88, bottom=0.12)
                    if not showTableOfStats:
                        fig.subplots_adjust(bottom = 0.12, right = .88, top = .88)
                    else:
                        fig.subplots_adjust(bottom = 0.12, right = .78, top = .88)
                else:
                    if not showTableOfStats:
                        fig.subplots_adjust(bottom = 0.18, right = .85, top = .85)
                    else:
                        fig.subplots_adjust(bottom = 0.18, right = .75, top = .85)

                # a2.set_xlim(min(x), (max(x)))#tocomment
                self.popup_menu.entryconfigure(0, label="Show Slider")
                self.gray_space_menu.entryconfigure(0, label="Show Slider")

            else:

                if fig in fig_dict and len(fig_dict[fig]['dictOfAxes']) > 1: # multiple plots, then     
                    fig.subplots_adjust(wspace=.25, hspace=.35, left=0.12, right=0.88, top=0.88, bottom=0.12)
                    if not showTableOfStats:
                        fig.subplots_adjust(bottom = 0.25, right = .88, top = .88)
                        slider_config_for_table_not_present_four_graphs()

                    else:
                        fig.subplots_adjust(bottom = 0.25, right = .78, top = .88)
                        slider_config_for_table_present_four_graphs()

                else:
                    if not showTableOfStats:
                        fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
                        slider_config_for_table_not_present_one_graph()

                    else:
                        fig.subplots_adjust(bottom = 0.25, right = .75, top = .85)
                        slider_config_for_table_present_one_graph()

                # fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
                self.popup_menu.entryconfigure(0, label="Hide Slider")
                self.gray_space_menu.entryconfigure(0, label="Hide Slider")

        self.draw()

    
    def toggle_table_of_stats(self):
        global statTableTxt
        global showTableOfStats
        global axRight
        global axLeft
        global sLeft
        global sRight
        global fillAxis
        global fig
        global fig_dict
        if axRight != None and axLeft != None:
            # clear canvas and redraw
            statTableTxt.set_visible(not statTableTxt.get_visible())
            showTableOfStats = statTableTxt.get_visible()
            if not statTableTxt.get_visible():
                if fig in fig_dict and len(fig_dict[fig]['dictOfAxes']) > 1: # multiple plots, then    
                    fig.subplots_adjust(wspace=.25, hspace=.35, left=0.12, right=0.88, top=0.88, bottom=0.12)
                    if not axRight.get_visible():
                        fig.subplots_adjust(bottom = 0.12, right = .88, top = .88)
                    else:
                        fig.subplots_adjust(bottom = 0.25, right = .88, top = .88)
                        # fig.subplots_adjust(bottom = 0.18, right = .75, top = .85)
                        slider_config_for_table_not_present_four_graphs()

                else:   
                    if not axRight.get_visible():
                        fig.subplots_adjust(bottom = 0.18, right = .85, top = .85)
                    else:
                        fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
                        # maximize slider and axes.
                        slider_config_for_table_not_present_one_graph()

                        # fig.subplots_adjust(bottom = 0.18, right = .75, top = .85)
                self.popup_menu.entryconfigure(1, label = "Show Table of Stats")
                self.gray_space_menu.entryconfigure(1, label = "Show Table of Stats")

            else:
                if fig in fig_dict and len(fig_dict[fig]['dictOfAxes']) > 1: # multiple plots, then    
                    fig.subplots_adjust(wspace=.25, hspace=.35, left=0.12, right=0.88, top=0.88, bottom=0.12)
                    if not axRight.get_visible():
                        fig.subplots_adjust(bottom = 0.12, right = .78, top = .88)
                    else:
                        fig.subplots_adjust(bottom = 0.25, right = .78, top = .88)
                        slider_config_for_table_present_four_graphs()

                else:
                    if not axRight.get_visible():
                        fig.subplots_adjust(bottom = 0.18, right = .75, top = .85)
                    else:
                        fig.subplots_adjust(bottom = 0.25, right = .75, top = .85)
                        slider_config_for_table_present_one_graph()

                self.popup_menu.entryconfigure(1, label="Hide Table of Stats")
                self.gray_space_menu.entryconfigure(1, label="Hide Table of Stats")

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
    global sessionType

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
            cancan.axpopup.tk_popup(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY + 82 + 10, 0)
        elif (cancan.clickedAxes != None and
                event.inaxes != axLeft and event.inaxes != axRight and
                sessionType in ['RELA']): #there need to be multiple graphs
            # cancan.addable_menu.add_command(label = "Figure Title", command = cancan.set_graph_title1)
            cancan.addable_menu.entryconfigure(1,command = cancan.set_graph_title2)
            print(cancan.clickedAxes.get_yscale())
            if fig in fig_dict:
                if cancan.clickedAxes.get_yscale() in ['mercator', 'normal', 'exponential', 'lognormal'] or 'axesScales' in fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]: # clicked on a scaled axis
                    try: 
                        i = cancan.popup_multi.index('Scale')
                    except:
                        cancan.popup_multi.add_cascade(label="Scale", menu = cancan.view_menu)

                elif 'axesScales' not in fig_dict[fig]['dictOfAxes'][cancan.clickedAxes] and cancan.clickedAxes.get_yscale() not in ['mercator', 'normal', 'exponential', 'lognormal']:
                    try:
                        cancan.popup_multi.delete("Scale")
                    except:
                        i = None

            cancan.popup_multi.tk_popup(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY + 82 + 10, 0)
            # print(cancan.popup_multi.yposition(2) )
            print()
            # print(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY)
        elif cancan.clickedAxes == None:
            print 'GPTHER'
            cancan.gray_space_menu.tk_popup(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY + 82 + 10, 0)
        elif cancan.clickedAxes.get_yscale() in ['mercator', 'normal']:
            print 'hi'
        else:
            cancan.addable_menu.entryconfigure(1, command = cancan.set_graph_title1)
            cancan.popup_menu.tk_popup(app.winfo_x() + int(event.x), app.winfo_y() + int(cancan.get_width_height()[1]) - int(event.y) + canvasOffsetY + 82 + 10, 0)
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
    global headerDropDownVar

    def validate():
        start = lValue.get()
        end = rValue.get()
        finished = False
        try:
            a = min(xAreaPoints)
            b = max(xAreaPoints)
            
            if stType.get():
                if (leftDeviations.get() == u"-1\u03c3"):
                    a = (globalMu - globalSigma) / globalMultiplier
                elif (leftDeviations.get() == u"-2\u03c3"):
                    a = (globalMu - 2*globalSigma) / globalMultiplier
                elif (leftDeviations.get() == u"\u03bc"):
                    a = (globalMu) / globalMultiplier
                elif (leftDeviations.get() == u"+1\u03c3"):
                    a = (globalMu + globalSigma) / globalMultiplier
                elif (leftDeviations.get() == u"+2\u03c3"):
                    a = (globalMu + 2*globalSigma) / globalMultiplier
                if a > max(xAreaPoints): a = max(xAreaPoints)
                if a < min(xAreaPoints): a = min(xAreaPoints)

                if (rightDeviations.get() == u"+1\u03c3"):
                    b = (globalMu + globalSigma) / globalMultiplier
                elif (rightDeviations.get() == u"+2\u03c3"):
                    b = (globalMu + 2*globalSigma) /globalMultiplier
                elif (rightDeviations.get() == u"\u03bc"):
                    b = (globalMu)/ globalMultiplier
                elif (rightDeviations.get() == u"-1\u03c3"):
                    b = (globalMu - globalSigma) / globalMultiplier
                elif (rightDeviations.get() == u"-2\u03c3"):
                    b = (globalMu - 2*globalSigma) / globalMultiplier
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
                tkMessageBox.showerror("Invalid Limit Values", "One or more limit values are invalid. Please check that you have entered a float value for the limits specified.\n")
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
        elif purpose == 'ANOVA1 Limit to N Observations':
            if not markLimit.get():
                limitToNEntry.grid_forget()
            else:
                limitToNEntry.grid(row=17, column=1, columnspan = 2, sticky="e")
            

    def addFigureTitle():
        print(cancan.clickedAxes)
        cancan.thisFigure.suptitle(graphTitle.get(), fontsize=18, fontweight='bold', fontname="Calibri")
        renameTab(graphTitle.get())
        cancan.draw_idle()
        popup.destroy()
        return

    def addChartTitle():
        print(cancan.clickedAxes)
        cancan.clickedAxes.set_title(graphTitle.get(), y =0.99, fontname="Arial")
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
                
                modTicks = []

                if toMarkX.get():
                    maxYTicks = max(cancan.clickedAxes.get_yticks())
                    for i in cancan.clickedAxes.get_yticks():
                        if i != maxYTicks:
                            modTicks += [i]
                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['refLines'] += \
                        [cancan.clickedAxes.axvline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]

                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['textBoxes'] += \
                        [cancan.clickedAxes.text(a, max(modTicks) , str(truncate(a, 3)), style='italic', rotation=270,
                            bbox={'lw':0.0 ,'boxstyle':'round', 'facecolor':'white', 'alpha':0.6, 'pad':0.15})]
                else:
                    maxXTicks = max(cancan.clickedAxes.get_xticks())
                    for i in cancan.clickedAxes.get_xticks():
                        if i != maxXTicks:
                            modTicks += [i]
                    # refLines += [cancan.clickedAxes.axhline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]
                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['refLines'] += \
                        [cancan.clickedAxes.axhline(a, 0, 1, color= '#000080', lw = .5, linestyle = '--')]
                    fig_dict[fig]['dictOfAxes'][cancan.clickedAxes]['textBoxes'] += \
                        [cancan.clickedAxes.text(max(modTicks), a, str(truncate(a, 3)), style='italic', rotation=0,
                            bbox={'lw':0.0 ,'boxstyle':'round', 'facecolor':'white', 'alpha':0.6, 'pad':0.15})]

                print(refLines)

            cancan.draw_idle()
            listOfRefLines = []
            popup.destroy()
        except ValueError, e:
            tkMessageBox.showerror("Invalid Limit Values", "One or more values are invalid. Please check that you have entered float values.\n")

    def moveToListBox(listBox1, listBox2):
        global headerDropDownVar
        # outdatalist = listbox1.selection_get()
        idxs = listBox1.curselection() 
        if not len(idxs): return
        if listBox2 == listbox2:
            for idx in idxs:
                currentValues = list(listBox2.get(0,'end'))
                if not listBox1.get(idx) in currentValues:
                    listBox2.insert('end', listBox1.get(idx))
        elif listBox2 == listbox1:
            for idx in idxs:
                listBox1.delete(idx)
        
        
    def process_anova_input(purpose):
        global dataFile
        if purpose not in ['ANOVA1', 'ANOVA2']: return
        
        if purpose == 'ANOVA1':
            limitToN = 0
            if markLimit.get():
                if str(limitToNVar.get()) == '--':
                    tkMessageBox.showwarning("Observations Limit Not Set", "You must provide a limit N on the number of observations.\n")
                    return     
                try:
                    a = int(limitToNVar.get())
                    b = 1/a
                    c = 1/(abs(a) + a) 
                except:
                    tkMessageBox.showerror("Invalid Observations Limit", "Please check that you have selected a positive integer for N.\n")
                    return
                limitToN = int(limitToNVar.get())
            if dataFile is None:
                tkMessageBox.showerror("No Data Chosen", "Please check that you have imported column data.\n")
                return

            if len(listbox2.get(0, 'end')) <= 1:
                tkMessageBox.showerror("Multiple Groups Required", "Please check that you have entered more than one group in Groups field.\n")
                return
            # if N not selected Select number of rows you would like to include

            if len(alphaVar.get()) <= 0:
                return
            
            try:
                a = float(alphaVar.get())
                b = 1/a
                c = 1/(abs(a) + a) 
            except:
                tkMessageBox.showerror("Invalid Alpha", "Please check that you have entered a positive float value for Alpha.\n")
                return

            alpha = float(alphaVar.get())

            groupHeaders = listbox2.get(0, 'end')
            groupData = []
            popData = []
            sumStats = {}
            for groupHeader in groupHeaders:
                dframe = pd.read_csv(dataFile)
                dframe = dframe.sort_values(groupHeader)
                l = dframe[groupHeader].dropna().values.tolist()
                stats = dframe[groupHeader].dropna().describe()
                sumStats[str(groupHeader)] = {'mu':  stats.iloc[1],
                    'variance': stats.iloc[2] ** 2,
                    'sigma': stats.iloc[2],
                    'mn': stats.iloc[3],
                    'mx': stats.iloc[7]
                }

                groupData += [l]
                popData += l
 
            if not limitToN:
                minColLength = len(popData)
                for group in groupData:
                    if len(group) < minColLength:
                        minColLength = len(group)
            else:
                minColLength = limitToN

            dfCol = len(groupHeaders) - 1
            dfErr = minColLength - len(groupHeaders)
            dfTot = minColLength - 1
      
            try:
                b = 1/dfErr
                a = 1/(abs(dfErr) + dfErr)
            except:
                tkMessageBox.showerror("Number of Groups Equal/Exceed Observations", "Please ensure number of observations are greater than the number of groups selected.\n")
                return


            popMean = sum(popData)/len(popData)
            
            sst = 0.0
            for dataPt in popData:
                sst += (dataPt - popMean)**2
            
            ssc = 0.0
            for group in groupData:
                groupMean = sum(group)/len(group)
                ssc += (groupMean - popMean)**2

            sse = 0.0
            for group in groupData:
                groupMean = sum(group)/len(group)
                for dataPt in group:
                    sse += (dataPt - groupMean)**2
                    

            msc = ssc/dfCol
            mse = sse/dfErr
            fStat = msc/mse

            fCritical = ss.f.ppf(q = 1-alpha, dfn = dfCol, dfd = dfErr)
            pValue = 1 - ss.f.cdf(fStat, dfn = dfCol, dfd = dfErr)


            print('     ss, df, MS, F, p-value, F-crit')
            print('b/w groups')
            print('within groups')
            print('Total')
            anovaStats = (msc, mse, fStat, fCritical, pValue, dfCol, dfErr, dfTot, minColLength, len(groupHeaders))

            plotAnova(groupData, anovaStats, tuple(), sumStats)
            # print groupData
                


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
        popup.resizable(1,1)

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

    elif purpose == 'Not Supported':
        titleLabel = ttk.Label(frame, text = "Sorry! This feature is not supported yet.", font = SMALL_FONT)
        titleLabel.grid(sticky = "nw", row=0, column= 1, pady = 8, padx = 8)

        B1 =  ttk.Button(popup, text="Okay")
        B1 = ttk.Button(popup, text="Okay", command = lambda: popup.destroy())
        B1.grid(row=15, column=3,  sticky="ew", pady=5, padx=5)

    elif purpose == 'ANOVA1':

        treeFrame = ttk.Frame(frame, width = 300, height = 400)
        treeFrame.grid(row=4, column=0, columnspan = 9, rowspan=9, padx=10, pady=3)
        # treeFrame.columnconfigure(0,weight=1)

        titleLabel = ttk.Label(treeFrame, text = "One-Way ANOVA", font = LARGE_FONT)
        titleLabel.grid(sticky = "nw", row=0, column= 1, pady = 8, padx = 8)

        importButton =  ttk.Button(treeFrame, text="Import Data", command = openFile)
        # importButton = ttk.Button(frame, text="Okay", command = prime_nxt_popup(purpose))
        importButton.grid(row=0, column=2, columnspan = 2, sticky="e", pady=5, padx=15)
        # importButton.config(command = lambda: prime_nxt_popup(purpose, hiddenWidgs, shownWidgs))

        groupTitle = ttk.Label(treeFrame, text = "Column Headers", font = MED_FONT)
        groupTitle.grid(sticky = "nw", row=3, column= 1, padx = 10)
        listbox1 = tk.Listbox(treeFrame, listvariable = headerDropDownVar, selectmode = "multiple")
        listbox1.grid(row=4, column = 1, sticky='ew', rowspan=9, padx=10, pady=5)        

        groupTitle2 = ttk.Label(treeFrame, text = "Groups", font = MED_FONT)
        groupTitle2.grid(sticky = "nw", row=3, column= 3, padx = 10)
        listbox2 = tk.Listbox(treeFrame, selectmode = "multiple")
        listbox2.grid(row=4, column = 3, sticky='ew', rowspan=9, padx=10, pady=5)

        addButton =  ttk.Button(treeFrame, text="Add >>", command = lambda: moveToListBox(listbox1, listbox2))
        # importButton = ttk.Button(frame, text="Okay", command = prime_nxt_popup(purpose))
        addButton.grid(row=5, column=2,  sticky="w", pady=5, padx=5)
        removeButton =  ttk.Button(treeFrame, text="<< Remove", command = lambda: moveToListBox(listbox2, listbox1))
        # importButton = ttk.Button(frame, text="Okay", command = prime_nxt_popup(purpose))
        removeButton.grid(row=6, column=2,  sticky="w", pady=5, padx=5)

        operationsFrame = ttk.Frame(frame, width = 300, height = 400)
        operationsFrame.grid(row=14, column=0, padx=10, pady=3)
        operationsFrame.columnconfigure(0,weight=1)

        myType = StringVar()
        typeLabel = ttk.Label(operationsFrame, text = "Data Type:", font = SMALL_FONT)
        typeLabel.grid(sticky = "w", row=14, column= 1, padx = 10, pady = 3)
        cmbBox2 = ttk.Combobox(operationsFrame, state="readonly",
            values=("Number", "Date (mm/dd/yyyy)", "Percent"), textvariable = myType)
        cmbBox2.grid(row=14, column=2, sticky = "ew")
        cmbBox2.current(0)

        alphaVar = StringVar()
        alphaVar.set(str(0.05))
        alphaLabel = ttk.Label(operationsFrame, text = "Alpha:", font = SMALL_FONT)
        alphaLabel.grid(sticky = "w", row=15, column= 1, padx = 10, pady = 3)
        locEntry = ttk.Entry(operationsFrame, textvariable = alphaVar)
        locEntry.grid(row=15, column=2, sticky="ew")

        markLimit = IntVar()
        markLimit.set(0)
        chkMarkLimit = ttk.Checkbutton(operationsFrame, text='Limit to N Observations', variable=markLimit, command = lambda: toggle_access(purpose + ' Limit to N Observations'))
        chkMarkLimit.grid( row=16, column=1, columnspan = 2, sticky="w", pady=3, padx=10)

        limitToNVar = StringVar()
        limitToNVar.set('--') 
        limitToNEntry = ttk.Entry(operationsFrame, textvariable = limitToNVar)
        limitToNEntry.grid(row=17, column=1, columnspan = 2, sticky="e")
        limitToNEntry.grid_forget()

        B1 =  ttk.Button(popup, text="Okay")
        B1 = ttk.Button(popup, text="Okay", command = lambda: process_anova_input(purpose))
        B1.grid(row=15, column=3,  sticky="ew", pady=5, padx=5)
        # B1.config(command = lambda: prime_nxt_popup(purpose, hiddenWidgs, shownWidgs))
        # B1.config(state = 'disabled')

        # tree2 = MultiColumnListbox(['                                          '], tuple(), treeFrame, mode = 'single_column', colnum = 1)

        #         container1 = self.parent
        # container = ttk.Frame(container1)
        # # create a treeview with dual scrollbars
        # B1 = ttk.Button(container, text="Okay", command=self.dostuff)
        # B1.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        # self.tree = ttk.Treeview(container1, columns=self.headers, show="headings")
        # vsb = ttk.Scrollbar(container1, orient="vertical", command=self.tree.yview)
        # hsb = ttk.Scrollbar(container1, orient="horizontal", command=self.tree.xview)
        # self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        # self.tree.grid(column=0, row=0, sticky='nsew', in_=container1)
        # vsb.grid(column=1, row=0, sticky='ns', in_=container1)
        # hsb.grid(column=0, row=1, sticky='ew', in_=container1)

        # container.grid_columnconfigure(0, weight=1)
        # container.grid_rowconfigure(0, weight=1)
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
        # tk.Tk.wm_title(self, "Graphing Program")
        tk.Tk.wm_title(self, "Histogram with PDF Fit  - Unsaved Workspace")

        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # self.resizable(False, False)
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
        modemenu.add_command(label = "Reliability Analysis", command = lambda: pre_plot_setup('RELA', None)) ### TODO weibull analyzis
        modemenu.add_separator()
        
        anova_menu = tk.Menu(modemenu, tearoff = 0)
        anova_menu.add_command(label = "One-Way ANOVA", command = lambda: self.anova1_wrapper())
        anova_menu.add_command(label = "Two-Way ANOVA", command = lambda: popupmsg('Not Supported'))
        modemenu.add_cascade(label = "Diff of Means", menu = anova_menu)
 
        menubar.add_cascade(label = "Analysis", menu = modemenu)


        graphmenu = tk.Menu(menubar, tearoff = 0)
        graphmenu.add_command(label = "Histogram with PDF Fit", command = lambda: pre_plot_setup('PDF', None)) ### TODO
        graphmenu.add_separator()
        menubar.add_cascade (label = "Graph", menu = graphmenu)

        wkspmenu = tk.Menu(menubar, tearoff = 0)
        wkspmenu.add_command(label = "Save Workspace", command = lambda: megaSaveWorkspace()) ### TODO weibull analyzis
        wkspmenu.add_separator()
        wkspmenu.add_command(label = "Open Workspace", command = lambda: openWorkspace())
        wkspmenu.add_separator()
        wkspmenu.add_command(label = "View Workspace Directory", command = lambda: popupmsg('Not Supported') )
        wkspmenu.add_separator()
        wkspmenu.add_command(label = "New Workspace", command = lambda: saveBeforeNew())
        menubar.add_cascade (label = "Workspace...", menu = wkspmenu)

        tk.Tk.config(self, menu = menubar)
        self.show_frame(PageThree)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def anova1_wrapper(self):
        pre_plot_setup('ANOVA1', None)
        popupmsg('ANOVA1')

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

# restores the current figure to savable
# state and saves the figure to disk
# saves the timestamp of the save operation in 
# current_tabs_dict to be accessed next time
# graph is opened.
def saveWorkspace(context = None):
    global fig_dict
    global fillBetFigure
    global maximizedAxis
    global maximizedGeometry
    global sessionType
    global fig_dict
    global fig
    global cancan
    global current_tabs_dict
    global canContainer
    global notebookFrame
    # axes = self.clickedAxes
    # if len(fig_dict[fig]['dictOfAxes'][axes]['axesScales']) == 0: 
    #     fig_dict[fig]['dictOfAxes'][axes]['axesScales'] = (axes.get_xscale(), axes.get_yscale())
    print("in SAVEWKSPC")
    #cursor="wait")
    #)

    if fig not in fig_dict: return
    print 'dictionary length', len(fig_dict)
    if maximizedGeometry != (1,1,1):
        maximize_axes(maximizedAxis, maximizedGeometry)
        
    if fig in fig_dict and fig_dict[fig]['sessionType'] in ['RELA', 'PDF']:
        
        fig_dict[fig]['slider_axes'] = [axLeft, axRight, fillBetFigure]
        fig_dict[fig]['slider_values'] = [sLeft.val, sRight.val]

        if context == 'final':
            sLeft.disconnect_events()
            sRight.disconnect_events()
        for axes in fig_dict[fig]['dictOfAxes'].keys():
            if 'axesScales' in fig_dict[fig]['dictOfAxes'][axes] and context != 'first':
                # this_data = fig_dict[fig]['dictOfAxes'][axes]
                axes.set_yscale('linear')
                axes.set_xscale('linear')            

    cancan.draw()
    currentTime = str(datetime.datetime.now())
    fig_dict[fig]['lastSaved'] = currentTime
    # fig_dict[fig]['loaded'] = True

    key = currentTime
    prevTabID = notebookFrame.tabs()[notebookFrame.index(canContainer)]
    prevTabLabel = notebookFrame.tab(prevTabID, "text")
    
    if prevTabLabel in current_tabs_dict:
        current_tabs_dict[prevTabLabel][0] = key
    else:
        splitLabel1 = prevTabLabel.split('(')
        splitLabel2 = splitLabel1[-1].split(')')
        if len(splitLabel2) != 2: return
        numToConvert = splitLabel2[0]
        if not numToConvert.isalnum(): return 
        index = int(numToConvert)
        restoredOrigName = '('.join(splitLabel1[:-1])

        if restoredOrigName in current_tabs_dict:
            current_tabs_dict[restoredOrigName][index] = key
    # loaded_fig_dict = None
    print("over SAVEWKSPC")
    #cursor="")

    return


def saveBeforeNew():
    global fig_dict
    global fillBetFigure
    global maximizedAxis
    global maximizedGeometry
    global sessionType
    global fig_dict
    global fig
    global cancan
    global current_tabs_dict
    global canContainer
    global notebookFrame
    global thisWkspcName
    global programmaticDeletionFlag
    global current_tabs_dict
    global openWorkspaceFlag

    if not thisWkspcName and not len(fig_dict) > 0: return
    
    if not len(fig_dict) > 0: 
        tkMessageBox.showerror("Save Error", "There is no" +
            " data to save. Changes to your workspace were not saved.")
        return

    megaSaveWorkspace()
    thisWkspcName = None
    canContainer = None
    # tk.Tk.wm_title(app, "Loading ...")
    titleWindow('Loading ...')
    # load tabs from newly set cur_tabs
    currentVisibleTabs = 0
    for tab in notebookFrame.tabs():
        print notebookFrame.index(tab)
        if notebookFrame.tab(tab, 'state') in ['normal', 'hidden'] and notebookFrame.index(tab) != 0:
            currentVisibleTabs += 1
    while currentVisibleTabs > 0:
        programmaticDeletionFlag = True
        # if currentVisibleTabs == 1:
        #     fig = None
        #     pre_plot_setup('PDF',None)
        #     fig_dict = {}
        # else:
        notebookFrame.forget(currentVisibleTabs)
        hideExtraTabs()
        currentVisibleTabs -= 1
    fig_dict = {}
    programmaticDeletionFlag = False
    pre_plot_setup('RELA',None)
    pre_plot_setup('PDF',None)
    hideExtraTabs()



# restores the current figure to savable
# state and saves the figure to disk
# saves the timestamp of the save operation in 
# current_tabs_dict to be accessed next time
# graph is opened.
def megaSaveWorkspace():
    global fig_dict
    global fillBetFigure
    global maximizedAxis
    global maximizedGeometry
    global sessionType
    global fig_dict
    global fig
    global cancan
    global current_tabs_dict
    global canContainer
    global notebookFrame
    global thisWkspcName
    global programmaticDeletionFlag
    global current_tabs_dict
    global openWorkspaceFlag
    # axes = self.clickedAxes
    # if len(fig_dict[fig]['dictOfAxes'][axes]['axesScales']) == 0: 
    #     fig_dict[fig]['dictOfAxes'][axes]['axesScales'] = (axes.get_xscale(), axes.get_yscale())
    print("in SAVEWKSPC")
    #ig(cursor="wait")
    #date()

    print(fig)
    print(fig in fig_dict) # the figure in ram is not the exact same as it is in disk. 
    if fig not in fig_dict:
        tkMessageBox.showerror("Save Failed", "Save failed. There is no plot session to be saved.")
        return

    if not thisWkspcName:
        try:
            fname = tkFileDialog.asksaveasfile(defaultextension = ".pickle", initialfile = '')
            if fname is None:
                return
            thisWkspcName = str(fname.name)
        except IOError, e:
            tkMessageBox.showerror("File In Use", "A file of the same name is currently in use in another program. Close this file and try again.")
            return


    if fig in fig_dict: 
        saveWorkspace(context = 'final')


    fig_dict['tabs'] = dict(current_tabs_dict)
    # print 'dictionary length', len(fig_dict)
    # if maximizedGeometry != (1,1,1):
    #     maximize_axes(maximizedAxis, maximizedGeometry)
    
    # TODO FOR OPEN
    # for fig in fig_dict.keys():
    #     fig_dict[fig]['loaded'] = True
                
    # cancan.draw()
    # output = open('savedWkspc1.pickle','rb')
    # loaded_fig_dict = pl.load(output)
    # output.close()

    loaded_fig_dict = {}

    # TODO FOR OPEN
    # arbitrary name... contains a blank dictionary always...
    # with open('savedWkspc1.pickle', 'rb') as handle:
    #     loaded_fig_dict = pl.load(handle)
    #     handle.close()

    # if fig_dict[fig]['loaded']:
    #     for figkey in loaded_fig_dict.keys():
    #         if loaded_fig_dict[figkey]['lastSaved'] == fig_dict[fig]['lastSaved']:
    #             del loaded_fig_dict[figkey]

    # loaded_fig_dict[fig] = dict(fig_dict[fig])
    # currentTime = str(datetime.datetime.now())
    # loaded_fig_dict[fig]['lastSaved'] = currentTime
    # loaded_fig_dict[fig]['loaded'] = True

    # fileHandle = currentTime + '.pickle'
    with open(thisWkspcName, 'wb') as handle:

        # with open('savedWkspc1.pickle', 'wb') as handle:
        pl.dump(fig_dict, handle, protocol=pl.HIGHEST_PROTOCOL)
        handle.close()

    del fig_dict['tabs']
    
    # pl.dump(loaded_fig_dict,file('savedWkspc1.pickle','wb'))
    # del fig_dict[fig]

    # Update the current_tabs_dict with the proper datetime reference
    # key = currentTime
    # prevTabID = notebookFrame.tabs()[notebookFrame.index(canContainer)]
    # prevTabLabel = notebookFrame.tab(prevTabID, "text")
    
    # if prevTabLabel in current_tabs_dict:
    #     current_tabs_dict[prevTabLabel][0] = key
    # else:
    #     splitLabel1 = prevTabLabel.split('(')
    #     splitLabel2 = splitLabel1[-1].split(')')
    #     if len(splitLabel2) != 2: return
    #     numToConvert = splitLabel2[0]
    #     if not numToConvert.isalnum(): return 
    #     index = int(numToConvert)
    #     restoredOrigName = '('.join(splitLabel1[:-1])

    #     if restoredOrigName in current_tabs_dict:
    #         current_tabs_dict[restoredOrigName][index] = key
    print("over SAVEWKSPC")
    #ig(cursor="")

    return


def openWorkspace():
    global axRight
    global axLeft
    global sRight
    global sLeft
    global a
    global a2
    global a3
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
    global canContainer
    global sliderCIDs
    global thisWkspcName
    global programmaticDeletionFlag
    global current_tabs_dict
    global openWorkspaceFlag

    print("in MEGA OPEN")

    # TODO popup save your work before continuing?

    try:
        fname = tkFileDialog.askopenfile(mode = 'rb', title = 'Choose a Workspace')
        if fname is None:
            return
    except IOError, e:
        tkMessageBox.showerror("File In Use", "A file of the same name is currently in use in another program. Close this file and try again.")
        return

    # print(type(fname))    # FOR DEBUGGNING
    print(fname.name)          # fname is type 'file'
    # print(str(fname))
    prevWkspcName = thisWkspcName
    thisWkspcName = fname.name

    if 'pickle' not in thisWkspcName.split('.'):
        thisWkspcName = prevWkspcName
        tkMessageBox.showerror("Open Error", "The workspace could not be opened. Check extension is '.pickle'")
        return

    try:
        go_to_next_slide()
    except:
        thisWkspcName = prevWkspcName
        tkMessageBox.showerror("Open Error", "The workspace could not be opened for an unknown reason. The contents may have been tinkered with.")
        return

    # tk.Tk.wm_title(app, "Loading ...")
    titleWindow('Loading ...')
    # load tabs from newly set cur_tabs
    currentVisibleTabs = 0
    for tab in notebookFrame.tabs():
        print notebookFrame.index(tab)
        if notebookFrame.tab(tab, 'state') in ['normal', 'hidden'] and notebookFrame.index(tab) != 0:
            currentVisibleTabs += 1
    while currentVisibleTabs > 0:
        programmaticDeletionFlag = True
        notebookFrame.forget(currentVisibleTabs)
        hideExtraTabs()
        currentVisibleTabs -= 1
    
    programmaticDeletionFlag = False
 

    for tabName in current_tabs_dict.keys():
        for i, listItem in enumerate(list(current_tabs_dict[tabName])):
            if listItem != None and i > 0:
                addTab(name = str(tabName) + '(' + str(i) + ')')
                hideExtraTabs()

            elif listItem != None and i == 0:
                addTab(name = str(tabName))
                hideExtraTabs()

        print('addingTab')
    hideExtraTabs()

    if 'tabs' in fig_dict:
        del fig_dict['tabs']
    
    # forces first graph to open
    hiddenTabsButton = notebookFrame.nametowidget(notebookFrame.tabs()[0])
    prevState = notebookFrame.tab(hiddenTabsButton, 'state')
    notebookFrame.select(hiddenTabsButton)
    hideExtraTabs()

    print('successful open')


def init_stats_table():
    global fig
    global fig_dict
    i = 0

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
        global headerDropDownVar
        global curHeader
        global dataType
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
        global buttContainer
        global relaWidgs
        global pdfWidgs
        global anovaWidgs
        global curWidgs
        global sessionType
        global notebookFrame
        global cursorState

        def toggle_this_frame_vis( container, expandButton):
            global fig
            if not toExpand.get():
                buttContainer.grid(row=0, column=3, rowspan=2, sticky="nsew", pady=5, padx=5)
                expandButton.configure(text='-')
            else:
                buttContainer.grid_forget()
                expandButton.configure(text='+')


       

        tk.Frame.__init__(self, parent)
        
        # styleNotebook = ttk.Style(parent)
        # styleNotebook.configure('TNotebook', )
        styleTabs = ttk.Style(parent)
        styleTabs.configure('bottomtab.TNotebook', tabposition='sw')
        styleTabs.configure('TNotebook.Tab', font=MED_FONT, padding=[5, 1], expand=[0,0,0,0])
        styleTabs.map("TNotebook.Tab", foreground=[("selected", "#8B0000")])
        print(styleTabs)


        # frame4 = ttk.Notebook(self, style='bottomtab.TNotebook')
        # frame4.grid(row=4, column=2, sticky=tk.E + tk.W + tk.N + tk.S, padx=30, pady=4)

        # tab1 = tk.Frame(frame4)
        # tab2 = tk.Frame(frame4)
        # tab3 = tk.Frame(frame4)

        # frame4.add(tab1, text="Tab One", compound=tk.BOTTOM)
        # frame4.add(tab2, text="Tab Two", compound=tk.BOTTOM)
        # frame4.add(tab3, text="Tab Three", compound=tk.BOTTOM)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=20000)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=200)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        curWidgs = []

        fig = Figure(dpi = 100)
        # fig.subplots_adjust(bottom = 0.0, right = .75, top = .85)
        # fig.subplots_adjust(wspace=.3, hspace=.35)
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

        # canContainer = tk.Frame(notebookFrame, width=200, height=200)

        notebookFrame = ttk.Notebook(self, style='bottomtab.TNotebook')
        notebookFrame.grid_propagate(False)

        newContainer = TabFrame(master=notebookFrame, name ="Chart", width=200, height=200)

        notebookFrame.add(newContainer, text=" < << ", compound=tk.BOTTOM)
        newContainer.grid_rowconfigure(0, weight = 1)
        newContainer.grid_columnconfigure(0, weight = 1)
        notebookFrame.hide(newContainer)
        print(newContainer)
        notebookFrame.bind('<Button-3>', self.on_tab_right_click)    

        canContainer = TabFrame(master=notebookFrame, name ="Chart", width=200, height=200)
        notebookFrame.add(canContainer, text="Blank Chart*", compound=tk.BOTTOM)
        notebookFrame.select(notebookFrame.index(canContainer)) #move focus to new tab

        canvas = FancyFigureCanvas(fig, canContainer)
        # connection_id = canvas.mpl_connect('button_press_event', on_press) #uncomment


        cancan = canvas
        cancan.axpopup.entryconfig(1, state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')



        if a.get_visible() and a2.get_visible():
            cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)

        # TODO: RESIZE CANVAS
        can = canvas.get_tk_widget()
        notebookFrame.grid(row=1, column=1, sticky = "nsew", ipadx = 5, ipady = 5)
        notebookFrame.grid_propagate(False)
        notebookFrame.grid_columnconfigure(0, weight=1)
        notebookFrame.grid_rowconfigure(0, weight=1)

        # canContainer.grid(row=0, column=0, sticky = "nsew", ipadx = 5, ipady = 5)
        toolbarContainer.grid(row=0, column=1, sticky = "nsew", pady = 5, padx = 5)
        expandButtonFrame.grid(row=0, column = 2, sticky = 'nsew')
        can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
        canvas._tkcanvas.grid(row=0, column=0, sticky = "nsew",ipadx = 5, ipady = 5)

        # label to show the position of the cursor
        self.cursorPosLabel = StringVar()
        cursorPosLabel = self.cursorPosLabel
        _cursorPosLabel= ttk.Label(self, text = "Inputs", textvariable = self.cursorPosLabel, font = SMALL_FONT, background = 'lightgoldenrodyellow', 
            borderwidth=1, relief = 'solid', padding = (5,5, 5,5))
        _cursorPosLabel.grid(sticky = "nw", row=1, column= 1, pady = 8, padx = 8)

        self.binning = IntVar()
        globalBinning = self.binning
        self.myHeader = StringVar()
        curHeader = self.myHeader
        self.myType = StringVar()
        dataType = self.myType
        label = ttk.Label(buttContainer, text = "Inputs", font = LARGE_FONT)
        label.grid(sticky = "ne", row=1+0, column= 1, pady = 8, padx = 8)

        crossHairsImg = tk.PhotoImage(file="crosHairs.gif")
        # create the image button, image is above (top) the optional text
        toggleCrossHairs()
        cursorState = IntVar()
        crosHairsButton = ttk.Checkbutton(toolbarContainer, image=crossHairsImg, command = lambda: toggleCrossHairs(), style = 'Toolbutton', variable=cursorState)
        crosHairsButton.grid(sticky = "w", row=0, column= 0)
        crosHairsButton.image = crossHairsImg

        tableImg = tk.PhotoImage(file="table.gif")
        # create the image button, image is above (top) the optional text
        tableButton = ttk.Button(toolbarContainer, image=tableImg, command = lambda: self.open_table_wrapper()) 
        tableButton.grid(sticky = "w", row=0, column= 1)
        tableButton.image = tableImg

        # TODO
        # prevGraphButton = ttk.Button(toolbarContainer, image=tableImg, command = lambda: go_to_next_slide()) 
        # prevGraphButton.grid(sticky = "w", row=0, column= 2)
        
        addToWkspcImg = tk.PhotoImage(file="addToWkspc.gif")
        addToWorkspaceButton = ttk.Button(toolbarContainer, image=addToWkspcImg, command = lambda: megaSaveWorkspace()) 
        addToWorkspaceButton.grid(sticky = "w", row=0, column= 2)
        addToWorkspaceButton.image = addToWkspcImg

        headerLabel = ttk.Label(toolbarContainer, text = ":", font = LARGE_FONT)

        headerDropDownVar = Variable()
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
            values=("Number", "Date (mm/dd/yyyy)", "Percent"), textvariable = self.myType)
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


        # button1 = ttk.Button(buttContainer, text = "Back to Home",
        #     command = lambda: controller.show_frame(StartPage))
        # button1.grid(row=1+13, column=2)

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
        self.sigmaVar.set(u"\u03c3 = " + str(globalSigma) + "\n" + u"\u03bc = \u1f4c4" + str(globalMu) + "\nmin = " + str(globalMin) + "\nmax = " + str(globalMax) )
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
           
        plotButton = ttk.Button(buttContainer, text = "Plot", command = lambda: plotDecider())#self.weibullPPF(canvas))#self.plotDecider(canvas))
        plotButton.config(state="disabled")
        plotButton.grid(row=1+12, column=2)
        plotButton = plotButton

        toExpand = IntVar()

        contractImg = tk.PhotoImage(file="contract.gif")
        chkExpand = ttk.Checkbutton(expandButtonFrame, image=contractImg, variable = toExpand, style = 'Toolbutton')
        chkExpand.configure(command = lambda: toggle_this_frame_vis(buttContainer, chkExpand))
        chkExpand.grid(sticky = "e", row=0, column= 0)
        chkExpand.image = contractImg
        chkExpand = chkExpand


        anovaStartButton = ttk.Button(buttContainer, text = "Make ANOVA", command = lambda: popupmsg('ANOVA1'))#self.weibullPPF(canvas))#self.plotDecider(canvas))
        anovaStartButton.grid(row=2, column=0, sticky = "nsew", pady = 8, padx = 10)
        anovaStartButton.grid_remove()

        anovaLabel = ttk.Label(buttContainer, text = "ANOVA", font = LARGE_FONT)
        anovaLabel.grid(sticky = "nw", row=1+0, column= 0, pady = 8, padx = 8)
        anovaLabel.grid_remove()
        # props = dict(boxstyle='round', facecolor='lightblue', lw = .25)
        # statTableTxt = fig.text(x = .85, y=.75, s = globalSigVar.get(), bbox = props, fontsize = 9)
        # showTableOfStats = False
        # ________RELIABILITY BAR_________#

        relaWidgs += [areaPCTLabel, sigLabel, statsLabel, label, headerLabel, headerDropDown, typeLabel, cmbBox2, distTypeLabel, pdfTypeCombobox, button2, plotButton]
        pdfWidgs = relaWidgs + [binningLabel, cmbBox3]

        anovaWidgs = [anovaStartButton, anovaLabel]
        sessionType = 'PDF'
        buttContainer.grid(row=0, column=3, rowspan = 2, sticky = "nsew", pady = 5, padx = 5)


        
        #MOVE TO PLOT
        # CREATE THE SLIDER, AND CONFIGURE.
        with plt.style.context('classic'):
            axLeft = fig.add_axes([0.12, 0.08, 0.67, 0.03], facecolor=axcolor)
            axRight = fig.add_axes([0.12, 0.05, 0.67, 0.03], facecolor='#8B0000')
            
            sLeft = Slider2(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')

            # sLeft = Slider2(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')
            sRight = Slider2(axRight, 'Time', 0, 1, valinit=0, color = axcolor)

            axLeft.clear()
            axRight.clear()
            axRight.grid(False)
            axLeft.set_xticks([])
            axLeft.set_yticks([])
            axRight.set_yticks([])

        # sLeft.on_changed(update)
        # sRight.on_changed(update)
        axLeft.set_visible(False)
        axRight.set_visible(False)

        # cancan.toggle_slider_vis()

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
        fig = None
        cancan.draw()

    def open_table_wrapper(self):
        popupmsg('Table')

    def on_tab_right_click(self, event):
        global notebookFrame
        print('widget:', event.widget)
        print('x:', event.x)
        print('y:', event.y)

        #selected = nb.identify(event.x, event.y)
        #print('selected:', selected) # it's not usefull

        clicked_tab_index = notebookFrame.tk.call(notebookFrame._w, "identify", "tab", event.x, event.y)
        print('clicked tab:', clicked_tab_index)
        
        if clicked_tab_index <= 0: return

        tabRightClickMenu = tk.Menu(notebookFrame, tearoff=0)
        tabRightClickMenu.add_command(label = "Delete Graph", command = lambda: deleteTab(clicked_tab_index))
        tabRightClickMenu.tk_popup(app.winfo_x() + event.x, app.winfo_y() + event.y, 0)

        # tabRightClickMenu.tk_popup(app.winfo_x() + 76, app.winfo_y() + int(cancan.get_width_height()[1]) + canvasOffsetY - 19* len(notebookFrame.tabs()) + 19*7, 0)

        # active_tab = notebookFrame.index(notebookFrame.select())
        # print(' active tab:', active_tab)

        # if clicked_tab == active_tab:
        #     notebookFrame.forget(clicked_tab)

# should just delete the tab clicked, and its timestamp in
# RAM. 
def deleteTab(tabIndex):
    global notebookFrame
    global canContainer
    global sessionType
    global fig
    global fig_dict

    print("in DELETE")
    #cursor="wait")
    #)

    if not fig or not tabIndex: return
    hiddenGraphsTab = notebookFrame.tabs()[0]

    if tabIndex < len(notebookFrame.tabs()):
        deleteGraph(notebookFrame.tabs()[tabIndex], str(notebookFrame.tab(notebookFrame.tabs()[tabIndex], "text")))
        notebookFrame.forget(tabIndex)
        hideExtraTabs()

        print(len(notebookFrame.tabs()))
        if len(notebookFrame.tabs()) == 1:
            oldSessionType = sessionType
            sessionType = None
            pre_plot_setup(oldSessionType, None)
            print("a blank plot is set up post delete all graphs")

    print("over DELETE")
    #cursor="")

    # notebookFrame.nametowidget(hiddenGraphsTab).set_tab_selected_before_this(notebookFrame.index(canContainer))
    # print(notebookFrame.nametowidget(hiddenGraphsTab).tab_selected_before_this)
    # notebookFrame.hide(notebookFrame.nametowidget(hiddenGraphsTab))

    # notebookFrame.select(notebookFrame.index(canContainer))

# to be used with tab ID or with tab Label
def deleteGraph(thisID = None, thisLabel = None):
    global notebookFrame
    global canContainer
    global sessionType
    global fig
    global fig_dict
    global current_tabs_dict
    global sLeft
    global sRight

    print("in DELETE GRAPH")

    if not thisID and not thisLabel: return
    print(canContainer)
    print(thisID)
    # loaded_fig_dict = None
    # with open('savedWkspc1.pickle', 'rb') as handle:
    #     loaded_fig_dict = pl.load(handle)
    #     handle.close()

        # find figure with the same name as clicked...
    if thisID: thisLabel = notebookFrame.tab(thisID, "text")

    timestamp = None
    if thisLabel != None:
        print("CASE 11")
        if thisLabel in current_tabs_dict:
            print("CASE 111")
            restoredOrigName = thisLabel
            timestamp = current_tabs_dict[restoredOrigName][0]

            if not thisID:

                for figkey in fig_dict.keys():
                    if fig_dict[figkey]['lastSaved'] == timestamp:
                        sLeft.disconnect_events()
                        sRight.disconnect_events()
                        del fig_dict[figkey]

            current_tabs_dict[restoredOrigName][0] = None

        else:
            print("CASE 1111")
            splitLabel1 = thisLabel.split('(')
            splitLabel2 = splitLabel1[-1].split(')')
            if len(splitLabel2) != 2: return
            numToConvert = splitLabel2[0]
            if not numToConvert.isalnum(): return 
            index = int(numToConvert)
            restoredOrigName = '('.join(splitLabel1[:-1])

            if restoredOrigName in current_tabs_dict:
                timestamp = current_tabs_dict[restoredOrigName][index]

                if not thisID:

                    for figkey in fig_dict.keys():
                        if fig_dict[figkey]['lastSaved'] == timestamp:
                            sLeft.disconnect_events()
                            sRight.disconnect_events()
                            del fig_dict[figkey]

                current_tabs_dict[restoredOrigName][index] = None


    if canContainer != None and str(canContainer) == str(thisID):
        print("CASE 1")
        # if fig in fig_dict and fig_dict[fig]['loaded']:
        #     for figkey in fig_dict.keys():
        #         if fig_dict[figkey]['lastSaved'] == fig_dict[fig]['lastSaved']:
        #             del fig_dict[figkey]
            
        if fig in fig_dict:
            sLeft.disconnect_events()
            sRight.disconnect_events()
            print("figure was deleted")
            del fig_dict[fig]
        canContainer = None

    elif canContainer != None and timestamp:
        # need to find the appropriate fig to delete!

        for figkey in fig_dict.keys():
            if fig_dict[figkey]['lastSaved'] == timestamp:
                del fig_dict[figkey]
                print("figure was deleted")

    print("over DELETE GRAPH")

    

def toggleCrossHairs():
    global cursor
    global cursors
    if len(cursors) > 0:
        for c in cursors:
            c.horizOn = not c.horizOn
            c.vertOn = not c.vertOn
    elif cursor is not None:
        cursor.horizOn = not cursor.horizOn
        cursor.vertOn = not cursor.vertOn

def plotAnova(data, anovaStats, tupleX, sumStats):
    global sessionType
    global graphTitle
    global fig
    global notebookFrame
    global anovaWidgs
    global a
    global globalSigVar
    global statTableTxt
    print('got here')

    # fig_dict[fig]['dictOfAxes'][axes]['refLines'] = []
    try:
        if sessionType == 'ANOVA1':
            if dataFile is not None:
                if fig != None:
                    addTab()
                set_up_new_figure('ANOVA1', sessionType)

                fig.subplots_adjust(wspace=.25, hspace=.35, left=0.12, right=0.78, top=0.88, bottom=0.12)
                
                for i, x in enumerate(data):
                    a = fig.add_subplot(211, label = 'group' + str(i))

                    for xElem in x:
                        y = y + [np.reciprocal(globalSigma * math.sqrt(2 * np.pi))
                            * np.reciprocal(np.exp(0.5 * ((xElem - globalMu) / (globalSigma)) ** 2))]
                    a.plot(x, y, label = 'normal distribution', lw = 1.0, color = '#8B0000')

                graphTitle.set('Box Plots')
                cancan.thisFigure.suptitle(' Reliability Plots for ' , fontsize=18, fontweight='bold', fontname="Calibri")

                globalSigVar.set(u"\u03c3 = " + str(truncate(globalSigma, 6)) + "\n" + u"\u03bc = " + str(truncate(globalMu, 6)) +"\nmin = " + str(truncate(globalMin, 3)) +  "\nmax = " + str(truncate(globalMax, 3)) )

                props = dict(boxstyle='round', facecolor='lightblue', lw = .25)
                statTableTxt = fig.text(x = .85, y=.75, s = globalSigVar.get(), bbox = props, fontsize = 9)

                slider_config_for_table_present_four_graphs()
                cancan.toggle_slider_vis()

                fig_dict[fig] = {}

                fig_dict[fig]['fig_next'] = None
                fig_dict[fig]['sessionType'] = 'ANOVA1'
                fig_dict[fig]['numAxes'] = 1
                fig_dict[fig]['csv_src'] = dataFile
                fig_dict[fig]['slider_axes'] = [axLeft, axRight]
                fig_dict[fig]['dictOfAxes'] = {}
                fig_dict[fig]['loaded'] = False
                fig_dict[fig]['table'] = None
                for axes in [a]:
                    init_fig_dict(axes)
                    # fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mn'] = globalMin
                    # fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mu'] = globalMu
                    # fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mx'] = globalMax 
                    # fig_dict[fig]['dictOfAxes'][axes]['specsTable']['sigma'] = globalSigma
                    # fig_dict[fig]['dictOfAxes'][axes]['specsTable']['corr_coeff'] = corrCoeff
                    # fig_dict[fig]['dictOfAxes'][axes]['specsTable']['multiplier'] = globalMultiplier
                    msc, mse, fStat, fCritical, pValue, dfCol, dfErr, dfTot, _N, _C = anovaStats
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['msc'] = msc
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mse'] = mse
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['fStat'] = fStat 
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['fCritical'] = fCritical
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['pValue'] = pValue
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['dfCol'] = dfCol

                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['dfErr'] = dfErr
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['dfTot'] = dfTot
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['N'] = _N 
                    fig_dict[fig]['dictOfAxes'][axes]['specsTable']['C'] = _C

                # fig_dict[fig]['dictOfAxes'][a]['axesScales'] = (str(ax2.get_xscale()),  str(ax2.get_yscale()))

                # for axes in [ax1, ax2, ax3, ax4]:
                #     init_fig_dict(axes)
                #     fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mn'] = globalMin
                #     fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mu'] = globalMu
                #     fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mx'] = globalMax 
                #     fig_dict[fig]['dictOfAxes'][axes]['specsTable']['sigma'] = globalSigma
                #     fig_dict[fig]['dictOfAxes'][axes]['specsTable']['corr_coeff'] = corrCoeff
                #     fig_dict[fig]['dictOfAxes'][axes]['specsTable']['multiplier'] = globalMultiplier

                #     if len(shapeSymbol):
                #         fig_dict[fig]['dictOfAxes'][axes]['specsTable']['shape'] = (shape, shapeSymbol)
                #     if len(locSymbol):
                #         fig_dict[fig]['dictOfAxes'][axes]['specsTable']['loc'] = (loc, locSymbol)
                #     if len(scaleSymbol):
                #         fig_dict[fig]['dictOfAxes'][axes]['specsTable']['scale'] = (scale, scaleSymbol)

                # if distType == 'Lognormal Distribution':
                #     ax2.set_yscale('lognormal', subplot = ax2)

                # fig_dict[fig]['fillAxis'] = fillAxis
                # fig_dict[fig]['statsTable'] = statTableTxt

                # fig_dict[fig]['dictOfAxes'][ax2]['axesScales'] = (str(ax2.get_xscale()),  str(ax2.get_yscale()))
                cancan.draw()

                renameTab(str(graphTitle.get()))
                hideExtraTabs()
                # if (dataType.get() == "Date (mm/dd/yyyy)"):
                #     allAxes = fig.get_axes()
                #     weibullPPF()
                # else:
                #     weibullPPF()
                # plotButton.config(text = "New Plot Session", command = lambda: plotWeibull())#

    except ValueError, e:
        tkMessageBox.showerror("Data NA Error", "Data at header " + str(gotten)
            + " in file " + str(dataFile) + " is missing or invalid.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except TypeError, e:
        tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
            gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except KeyError, e:
        tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
            gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except AttributeError, e:
        tkMessageBox.showerror("Error", "Graphs could not be created to the proper scale. Error:" +
            str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return


def plotWeibull():
    global sessionType
    global graphTitle
    global fig
    global notebookFrame
    print('got here')
    distType = pdfTypeCombobox.get()

    # fig_dict[fig]['dictOfAxes'][axes]['refLines'] = []
    try:
        if sessionType == 'RELA':
            gotten = curHeader.get()
            if dataFile is not None:
                if fig != None:
                    addTab()
                set_up_new_figure('RELA', sessionType)
                weibullPPF(distType)
                renameTab(str(graphTitle.get()))
                hideExtraTabs()

                # if (dataType.get() == "Date (mm/dd/yyyy)"):
                #     allAxes = fig.get_axes()
                #     weibullPPF()
                # else:
                #     weibullPPF()
                plotButton.config(text = "New Plot Session", command = lambda: plotWeibull())#

    except ValueError, e:
        tkMessageBox.showerror("Data NA Error", "Data at header " + str(gotten)
            + " in file " + str(dataFile) + " is missing or invalid.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except TypeError, e:
        tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
            gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except KeyError, e:
        tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
            gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except AttributeError, e:
        tkMessageBox.showerror("Error", "Graphs could not be created to the proper scale. Error:" +
            str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return


#____Calculate Stats______
def calc_corr_coeff(xIs, yIs):
    # report estimated correlation coefficient
    covar = 0.0
    xVarSum = 0.0
    yVarSum = 0.0
    corrCoef = 0.0
    avgY = sum(yIs)/len(yIs)
    avgX = sum(xIs)/len(xIs)
    for i, val in enumerate(yIs):
        xi = xIs[i]
        yi = val
        xVarSum += (xi - avgX)**2 
        yVarSum += (yi - avgY)**2 
        covar += (xi - avgX) * (yi - avgY)
    corrCoef = covar/(np.sqrt(xVarSum * yVarSum))
    return corrCoef

def excel_plottable_prob_plot(specs, xPoints, yPoints, plotType):
    yIs = []
    xIs = []
    if 'exponential probability plot' in plotType:
        yIs = [np.log(mr) for mr in yPoints]
        xIs = [t for t in xPoints]
    elif 'lognormal probability plot' in plotType:
        shape = specs['shape']
        loc = specs['loc']
        scale = specs['scale']
        yIs = ss.lognorm.ppf(yPoints, shape[0], loc[0], scale[0])# [np.log(1-mr) for mr in medianRanks]
        xIs = [t for t in xPoints]
    elif 'normal probability plot' in plotType:
        yIs = ss.norm.ppf(yPoints, globalMu, globalSigma)
        xIs = xPoints
    elif 'weibull probability plot' in plotType:
        yIs = [np.log(-1*np.log(1-mr)) for mr in yPoints]
        xIs = [np.log(t) for t in xPoints]
    xPoints, yPoints = (xIs, yIs)
    xPointsNew = [xPoint for i, xPoint in enumerate(xPoints[:]) if str(yPoints[i]) not in ['inf', '-inf', 'nan']]
    yPoints = [yPoints[i] for i, xPoint in enumerate(xPoints[:]) if str(yPoints[i]) not in ['inf', '-inf', 'nan']]
    xPoints = xPointsNew
    return (xPoints, yPoints)
        # yIs = [np.log(-1*np.log(1-mr)) for mr in medianRanks]
        # xIs = [np.log(t) for t in times]

#____Plotting____

def plotDecider():
    global sessionType
    global pdfTypeCombobox
    global fig
    global plotButton

    if fig != None:

        addTab()
    pdfType = pdfTypeCombobox.get()
    canvas = set_up_new_figure('PDF', sessionType)

    plot(canvas,pdfType)
    renameTab(str(graphTitle.get()))
    hideExtraTabs()
    plotButton.config(text = "New Plot Session", command = lambda: plotDecider())#

def pre_plot_setup(typeString, oldTypeString):
    global pdfTypeCombobox
    global plotButton
    global fig
    global notebookFrame
    global sessionType
    global cancan

    if sessionType == typeString:
        cancan.draw()
        return

    if fig != None:

        addTab()
        hideExtraTabs()
    if oldTypeString == None:
        set_up_new_figure(typeString, oldTypeString)

    if typeString == 'RELA':

        pdfTypeCombobox['values'] = ("Standard Weibull Distribution", "Normal Distribution", '2-Param Weibull Distribution',
                '3-Param Weibull Distribution', 'Standard Exponential Distribution', "Lognormal Distribution", "Loglogistic Distribution", "Logistic Distribution")
        plotButton.config(text = "Plot", command = lambda: plotWeibull())#self.weibullPPF(canvas))#self.plotDecider(canvas))

    elif typeString == 'PDF':
        pdfTypeCombobox['values'] = ("Weibull Distribution", "Normal Distribution", 'Lognormal Distribution', 'Loglogistic Distribution', 'Logistic Distribution')
        plotButton.config(text = "Plot", command = lambda: plotDecider())

    elif typeString == 'ANOVA1':
        i = 0
    #     popupmsg('ANOVA1')

    pdfTypeCombobox.current(0)
    set_up_new_figure(typeString, oldTypeString)

def change_session(typeString):
    global axRight
    global axLeft
    global sRight
    global sLeft
    global a
    global a2
    global fig
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

    global dataMultiplier
    global globalMultiplier
    global logBase
    global refLines
    global listOfRefLines
    global textBoxes
    global pdfTypeCombobox

    global canContainer
    global plotButton
    global sessionType
    global relaWidgs
    global pdfWidgs
    global anovaWidgs

    global buttContainer
    global cursors
    global cursor
    cursor = None
    cursors = []
    listOfRefLines = []
    refLines = []
    textBoxes = []
    if typeString == 'RELA':
        for child in buttContainer.winfo_children():
            child.grid_remove()
        for widg in relaWidgs:
            widg.grid()

        pdfTypeCombobox['values'] = ("Standard Weibull Distribution", "Normal Distribution", '2-Param Weibull Distribution',
            '3-Param Weibull Distribution', 'Standard Exponential Distribution', "Lognormal Distribution", "Loglogistic Distribution", "Logistic Distribution")
        plotButton.config(text = "New Plot Session", command = lambda: plotWeibull())#self.weibullPPF(canvas))#self.plotDecider(canvas))
        cancan.popup_multi.entryconfigure(0, label="Maximize")
        cancan.addable_menu.add_command(label = "Figure Title", command = cancan.set_graph_title1)
        cancan.axpopup.entryconfig(cancan.axpopup.index("Set Cursor Values"), state='normal')
        cancan.addable_menu.entryconfig(cancan.addable_menu.index("Reference Line"), state = 'normal')
        # cancan.axpopup.index("Set Cursor Values")

        # tk.Tk.wm_title(app, "Reliability Analysis")
        titleWindow("Reliability Analysis")

    elif typeString == 'PDF':
        for child in buttContainer.winfo_children():
            child.grid_remove()
        for widg in pdfWidgs:
            widg.grid()
        pdfTypeCombobox['values'] = ("Weibull Distribution", "Normal Distribution", 'Lognormal Distribution', 'Loglogistic Distribution', 'Logistic Distribution')
        plotButton.config(text = "New Plot Session", command = lambda: plotDecider())
        cancan.axpopup.entryconfig(cancan.axpopup.index("Set Cursor Values"), state='normal')
        cancan.addable_menu.entryconfig(cancan.addable_menu.index("Reference Line"), state = 'normal')

        # tk.Tk.wm_title(app, "Histogram with PDF Fit")
        titleWindow("Histogram with PDF Fit")

    pdfTypeCombobox.current(0)

def titleWindow(name):
    global thisWkspcName
    if not thisWkspcName:
        tk.Tk.wm_title(app, str(name) + '  - Unsaved Workspace')
    else:
        tk.Tk.wm_title(app, str(name) + '  -' + str(thisWkspcName))



def set_up_new_figure(typeString, oldTypeString):
    global axRight
    global axLeft
    global sRight
    global sLeft
    global a
    global a2
    global fig
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

    global dataMultiplier
    global globalMultiplier
    global logBase
    global refLines
    global listOfRefLines
    global textBoxes
    global pdfTypeCombobox

    global canContainer
    global plotButton
    global sessionType
    global relaWidgs
    global pdfWidgs
    global anovaWidgs
    global anovaButtonTxt1

    global buttContainer
    global cursors
    global cursor
    global sliderCIDs

    try: 
        cancan.get_tk_widget().destroy()
        cancan = None
    except:
        pass    

    sessionType = typeString

    if oldTypeString == None:
        fig = None
        auxfig = Figure(dpi = 100)

        auxfig.patch.set_facecolor('#E0E0E0')
        auxfig.patch.set_alpha(0.7)
        if typeString == 'RELA':
            ax1 = auxfig.add_subplot(221, label = 'pdf')
            ax2 = auxfig.add_subplot(222)
            ax3 = auxfig.add_subplot(223)
            ax4 = auxfig.add_subplot(224)
            for child in buttContainer.winfo_children():
                child.grid_remove()
            for widg in relaWidgs:
                widg.grid()
            # tk.Tk.wm_title(app, "Reliability Analysis")
            titleWindow("Reliability Analysis")

        elif typeString == 'PDF':
            a = auxfig.add_subplot(111)
            a2 = a.twinx()
            for child in buttContainer.winfo_children():
                child.grid_remove()
            for widg in pdfWidgs:
                widg.grid()
            # tk.Tk.wm_title(app, "Histogram with PDF Fit")
            titleWindow( "Histogram with PDF Fit")


        elif typeString == 'ANOVA1':
            a = auxfig.add_subplot(211)
            for child in buttContainer.winfo_children():
                child.grid_remove()
            for widg in anovaWidgs:
                widg.grid()
            # tk.Tk.wm_title(app, "One-Way ANOVA")
            titleWindow( "One-Way ANOVA")

        cancan = FancyFigureCanvas(auxfig, canContainer)
        auxfig.set_canvas(cancan)
        can = cancan.get_tk_widget()
        can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
        cancan._tkcanvas.grid(row=0, column=0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)
        return cancan

    # fig = None
    fig = Figure(dpi = 100)
    # fig.subplots_adjust(bottom = 0.25, right = .85, top = .85)
    # fig.subplots_adjust(bottom = 0.1, right = .85, top = .85)

    # fig.subplots_adjust(wspace=.25, hspace=.5, left=0.1, right=0.9, top=0.9, bottom=0.1)
    fig.patch.set_facecolor('#E0E0E0')
    fig.patch.set_alpha(0.7)
    if typeString == 'RELA':
        ax1 = fig.add_subplot(221, label = 'pdf')
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)
        for child in buttContainer.winfo_children():
            child.grid_remove()
        for widg in relaWidgs:
            widg.grid()
        # tk.Tk.wm_title(app, "Reliability Analysis")
        titleWindow("Reliability Analysis")
        plotButton.config(text = "New Plot Session", command = lambda: plotWeibull())#



        # pdfTypeCombobox['values'] = ("Standard Weibull Distribution", "Normal Distribution", '2-Param Weibull Distribution',
        #     '3-Param Weibull Distribution', 'Standard Exponential Distribution', "Lognormal Distribution", "Loglogistic Distribution", "Logistic Distribution")
        # pdfTypeCombobox.current(0)
        # plotButton.config(command = lambda: plotWeibull())
        
    elif typeString == 'PDF':
        a = fig.add_subplot(111)
        a2 = a.twinx()
        # tk.Tk.wm_title(app, "Histogram with PDF Fit")
        titleWindow("Histogram with PDF Fit")
        plotButton.config(text = "New Plot Session", command = lambda: plotDecider())#
        # for child in buttContainer.winfo_children():
        #     child.grid_remove()
        # for widg in pdfWidgs:
        #     widg.grid()

        # pdfTypeCombobox['values'] = ("Weibull Distribution", "Normal Distribution", 'Lognormal Distribution', 'Loglogistic Distribution', 'Logistic Distribution')
        # pdfTypeCombobox.current(0)
        # plotButton.config(command = lambda: plotDecider())
    elif typeString == 'ANOVA1':
        a = fig.add_subplot(211, label = 'boxplot')
        anovaButton, label = anovaWidgs
        anovaButton.config(text = "Make New ANOVA")


    globalMultiplier = 1.0
    logBase = 0
    for refLine in refLines:
        refLine.remove()
    # for entryBox in listOfRefLines:
    #     entryBox.destroy()
    # for txt in textBoxes:
    #     txt.remove()
    fillAxis = None
    fillBetFigure = None
    xAreaPoints = []
    yAreaPoints = []

    # showTableOfStats = True


    listOfRefLines = []
    refLines = []
    textBoxes = []

    # cursorChange_id = canvas.mpl_connect('axes_enter_event', on_graph_hover)
    # canContainer.bind('<Button-3>', on_press_area)
    # axes2.plot(data)
    cancan = FancyFigureCanvas(fig, canContainer)
    fig.set_canvas(cancan)
    can = cancan.get_tk_widget()
    can.grid(row=0, column=0, sticky = "nsew", pady = 5, padx = 5, ipadx = 5, ipady = 5)
    cancan._tkcanvas.grid(row=0, column=0, columnspan = 4, rowspan = 1, sticky = "nsew",ipadx = 5, ipady = 5)
    connection_id = cancan.mpl_connect('button_press_event', on_press) #uncomment
    cancan.axpopup.entryconfig(1, state='disabled')
    # cancan.addable_menu.entryconfig(0, state = 'disabled')

    # prevCursorVisibility = False
    # if len(cursors) > 0:
    #     if cursors[0].vertOn:
    #         prevCursorVisibility = True
    # if cursor != None:
    #     if cursor.vertOn and cursor.horizOn:
    #         prevCursorVisibility = True
    # print(prevCursorVisibility)

    cursor = None
    cursors = []
    if typeString == 'RELA':
        cancan.popup_multi.entryconfigure(0, label="Maximize")
        cancan.addable_menu.add_command(label = "Figure Title", command = cancan.set_graph_title1)
        cancan.axpopup.entryconfig(1,state='disabled')
        # cancan.addable_menu.entryconfig(0, state = 'disabled')

        cursors = [
            InformativeCursor(ax1, useblit=True, color='red', linewidth=.5),
            InformativeCursor(ax3, useblit=True, color='red', linewidth=.5),
            InformativeCursor(ax4, useblit=True, color='red', linewidth=.5),
            InformativeCursor(ax2, useblit=True, color='red', linewidth=.5)
        ]


    elif typeString == 'PDF':

        cancan.axpopup.entryconfig(1,state='disabled')
        # cancan.addable_menu.entryconfig(0, state = 'disabled')

        for axis in fig.get_axes():
            if axis != axRight and axis != axLeft:
                axis.clear()
                if axis is not a and axis is not a2:
                    axis.remove()
                else: 
                    axis.set_visible(True)
                    cursor = InformativeCursor(axis, useblit=True, color='red', linewidth=.5)
    
    # if not prevCursorVisibility:
    #     toggleCrossHairs()



    # if a.get_visible() and a2.get_visible():
    #     cursor = InformativeCursor(a2, useblit=True, color='red', linewidth=.5)

    # TODO figure out if to use separate sliders or to make new AxLeft, AxRight for each new figure created.
    with plt.style.context('classic'):
        axLeft = fig.add_axes([0.12, 0.08, 0.625, 0.03], facecolor=axcolor)
        axRight = fig.add_axes([0.12, 0.05, 0.625, 0.03], facecolor='#8B0000')
        sLeft = Slider2(axLeft, 'Time', 0, 1, valinit=1, color = '#00A3E0')
        sRight = Slider2(axRight, 'Time', 0, 1, valinit=0, color = axcolor)
        axLeft.clear()
        axRight.clear()
        axRight.grid(False)
        axLeft.set_xticks([])
        axLeft.set_yticks([])
        axRight.set_yticks([])
    sliderCIDs[0] = sLeft.on_changed(update)
    sliderCIDs[1] = sRight.on_changed(update)
    cancan.toggle_slider_vis()

    # if typeString == 'RELA':
    #     if len(cursors) > 0 : cancan.addable_menu.entryconfig(cancan.addable_menu.index('Figure Title'), state = 'disabled')
    return cancan


def binomialCoeff(n , k): 

    # Declaring an empty array 
    C = [0 for i in xrange(k+1)] 
    C[0] = 1 #since nC0 is 1 
  
    for i in range(1,n+1): 
  
        # Compute next row of pascal triangle using 
        # the previous row 
        j = min(i ,k) 
        while (j>0): 
            C[j] = C[j] + C[j-1] 
            j -= 1
  
    return C[k] 


# TODO FIX 
def weibullPPF(distType):
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
    global globalMultiplier
    global globalMu
    global globalSigma

    global xAreaPoints
    global yAreaPoints
    global a
    global a2
    global curHeader
    global dataType
    global graphTitle
    global axcolor
    global fillBetFigure
    global fillAxis
    global totalArea
    global globalSigVar
    global globalTitleVar
    global leftDeviations
    global rightDeviations
    global globalMultiplier
    global logBase
    global fig_dict
    global statTableTxt
    global showTableOfStats
    global sessionType
    global canContainer

    maximizedAxis = None
    maximizedGeometry = (1,1,1)
    showTableOfStats = True

    # fig2 = Figure(dpi = 100)
    # fig2.subplots_adjust(bottom = 0.0, right = .75, top = .85)
    # fig2.subplots_adjust(wspace=.3, hspace=.35)

    # fig2.add_axes(axRight)
    gotten = curHeader.get()
    dframe = pd.read_csv(dataFile)
    dframe = dframe.sort_values(gotten)
    x = (1037,1429,680,291,1577,90,1090,142,1297,1113,1153,150,837,890,269,468,1476,827,519,1100,1307,1360,919,373,563,978,650,362,383,272)


    if (dataType.get() == "Date (mm/dd/yyyy)"):
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
        x = dateDiffList
    else:
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

        globalMax = mx
        globalMin = mn
        globalSigma = sigma
        globalMu = mu

        mx /= globalMultiplier
        mn /= globalMultiplier
        sigma /= globalMultiplier
        mu /= globalMultiplier

        x = dframe[gotten].dropna()

    logScaling = ''
    if logBase > 0:
        logScaling += 'e+' + str(logBase) 

    globalSigVar.set(u"\u03c3 = " + str(truncate(sigma, 6)) + logScaling + "\n" + u"\u03bc = " + str(truncate(mu, 6))  + logScaling  +"\nmin = " + str(truncate(mn, 3))  + logScaling  +  "\nmax = " + str(truncate(mx, 3)) + logScaling )
    props = dict(boxstyle='round', facecolor='lightblue', lw = .25)
    
    statTableTxt = fig.text(x = .85, y=.75, s = globalSigVar.get(), bbox = props, fontsize = 9)


    # # fig_dict[fig]['dictOfAxes'][a3] = {}
    # # fig_dict[fig]['dictOfAxes'][a3]['refLines'] = []
    # fig_dict[fig]['dictOfAxes'][a3]['addAxes'] += [a]
    # # fig_dict[fig]['dictOfAxes'][a3]['specsTable'] = {}
    fig.subplots_adjust(wspace=.25, hspace=.35, left=0.12, right=0.78, top=0.88, bottom=0.12)

    ax1 = fig.add_subplot(221, label = 'pdf')
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)


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
    if not cursorState.get():
        toggleCrossHairs()

    # x=ss.weibull_min.rvs(c, size=nsample)
    # x = (5,16,16,17,28,30,39,39,43,45,51,53,58,61,66,68,68,72,72,77,78,80,81,90,96,100,109,110,131,153,165,180,186,188,207,219,265,285,285,308,334,340,342,370,397,445,482,515,545,583,596,630,670,675,733,841,852,915,941,979,995,1032,1141,1321,1386,1407,1571,1586,1799)
    # x = (0,1,4,7,10,6,14,18,5,12,23,10,3,3,7,3,26,1,2,25,29,29,29,28,2,3,12,32,34,36,29,37,9,16,41,3,6,3,9,18,49,35,17,3,59,2,5,2,1,1,5,9,10,13,3,1,18,17,2,17,22,25,25,25,6,6,2,26,38,22,4,24,41,41,1,44,2,45,2,46,49,50,4,54,38,59)
    # x = (69,64,38,63,65,49,69,68,43,70,81,63,63,52,48,61,42,35,63,56,55,67,63,65,46,53,69,68,43,55,42,64,65,65,55,66,60,67,53,62,67,72,48,68,67,61,60,62,38,50,63,64,43,34,66,62,52,47,63,68,45,41,66,62,60,66,38,53,37,54,60,48,52,70,50,62,65,58,62,64,63,58,64,52,35,63,70,51,40,69,36,71,62,60,44,54,66,49,72,68,62,71,70,61,71,59,67,60,69,57,39,62,50,43,70,66,61,81,58,63,60,62,42,69,63,45,68,39,66,63,49,64,65,64,67,65,37)
    # x = (16, 17, 16, 18, 19, 17, 34, 53, 75, 93, 120)
    sortedX = [xItem/globalMultiplier for xItem in sorted(x)]


    medianRanks = []
    for i,v in enumerate(sortedX):
        medianRanks += [(i + 1 - 0.3)/(len(x) + 0.4)]



    # if mn == 0:
    print(mx)
    xSpan_univ = np.linspace(0.0001, mx, 300 + 5 * int(math.sqrt(mx - mn)))
    xSpanDistribution = np.linspace(0.0001, mx, 300 + 5 * int(math.sqrt(mx - mn)))

    # nonzeros = min(sortedX[np.nonzero(sortedX)])
    corrCoeff = 0.0
    shape = 0.0
    loc = 0.0
    scale = 1.0

    shapeSymbol = ''
    locSymbol = ''
    scaleSymbol = ''

    if distType == 'Normal Distribution': # Can be one of "Weibull Distribution", "Normal Distribution", 'Lognormal Distribution', 'Loglogistic Distribution', 'Logistic Distribution'
        xSpan = np.linspace(mn, mx, 300 + 5 * int(math.sqrt(mx - mn)))
        xSpanDistribution = np.linspace(0.0001, 1.5*mx, 300 + 5 * int(math.sqrt(mx - mn)))
        print(globalMu, globalSigma)
        scaleSymbol = u"\u03c3"
        locSymbol = u"\u03bc" 

        loc = mu
        scale = sigma

        y = []
        for xElem in xSpanDistribution:
            y = y + [np.reciprocal(sigma * math.sqrt(2 * np.pi))
                * np.reciprocal(np.exp(0.5 * ((xElem - mu) / (sigma)) ** 2))]
        fillAxis = ax1
        xAreaPoints = xSpanDistribution
        yAreaPoints = y
        fillBetFigure = ax1.fill_between(xSpanDistribution, 0, y, facecolor = '#4B0082', alpha = 0)
        totalArea = trapz(yAreaPoints, xAreaPoints)

        ax1.plot(xSpanDistribution, y, 
            label = 'normal distribution', 
            lw = 1.0, 
            color = '#8B0000')
        ax1.set_ylim(0, 1.5 * (max(y)))
        ax1.set_title('Normal Distribution', y =0.99,  fontname="Arial")
        ax1.set_xlabel("Time (t)")
        ax1.set_ylabel("f(t)")

        y_cdf = ss.norm.cdf(xSpanDistribution, mu, sigma) # the normal cdf
        print y_cdf

        ax2.plot(sortedX, medianRanks, 'ob', markersize = 2.3, 
            label = 'normal probability plot scatter')

        ax2.plot(xSpanDistribution, y_cdf, lw = 1.0,  color = '#8B0000', label = 'normal probability plot')
        ax2.set_yscale('normal', subplot = ax2)
        ax2.set_axisbelow(True)
        ax2.grid(True, which = 'both')

        ax2.set_title('Normal Probability Plot', y =0.99,  fontname="Arial")
        ax2.set_xlabel("Time (t)")
        ax2.set_ylabel("Unreliability F(t)")
        ax2.yaxis.set_label_position('right')

        yIs = ss.norm.ppf(medianRanks, globalMu, globalSigma)
        xIs = sortedX
        corrCoeff = calc_corr_coeff(xIs, yIs)

        survival_y = []
        cdf_y = ss.norm.cdf(xSpanDistribution, mu, sigma) # the normal cdf
        pdf_y = ss.norm.pdf([xi for xi in xSpanDistribution], mu, sigma)
        hazardFnc_y = []
        hazardFnc_x = []
        for i, xElem in enumerate(xSpanDistribution):
            try:
                survival_y += [1-cdf_y[i]]
                if 1-cdf_y[i] != 0:
                    hazardFnc_y += [pdf_y[i]/(1-cdf_y[i])]
                    hazardFnc_x += [xElem] 
            except:
                continue
    
        ax3.plot(xSpanDistribution, survival_y , 
            label = 'normal reliability (survival) function', 
            color = '#8B0000', lw = 1.0)
        ax3.set_title('Survival Function', y =0.99, fontname="Arial", fontsize=12)
        ax3.set_xlabel("Time (t)")
        ax3.set_ylabel("Reliability 1-F(t)")
        ax3.set_ylim(0, max(ax3.get_ylim()))

        ax4.plot(hazardFnc_x, hazardFnc_y, 
            label = 'normal failure rate (hazard) function', 
            lw = 1.0, 
            color = '#8B0000')
        ax4.set_title('Hazard Function', y =0.99,  fontname="Arial", fontsize=12)
        ax4.set_xlabel("Time (t)")
        ax4.set_ylabel("Failure Rate (fr/time)")
        ax4.set_ylim(0, max(ax4.get_ylim()))
        ax4.yaxis.set_label_position('right')


    elif distType == 'Standard Weibull Distribution':
        #fit the gamma distribution
        # pars1 = ss.weibull_min.fit(sortedX)
        shapeSymbol = u'\u03b2'
        scaleSymbol = u'\u03b7'
        locSymbol = u'\u03b3'



        shape, loc, scale = ss.weibull_min.fit(sortedX, floc = 0, fscale = 1)
        #plot the result
        xSpan = np.linspace(0.0001, 1.5* mx, 300 + 5 * int(math.sqrt(mx - mn)))
        

        y = ss.weibull_min.pdf(xSpan, shape, loc, scale)
        ax1.plot(xSpan, y, 
            label = 'weibull distribution', 
            lw = 1.0, 
            color = '#8B0000')
        ax1.set_ylim(0, 1.5 * (max(y)))
        ax1.set_title('St Weibull Distribution', y =0.99,  fontname="Arial")
        ax1.set_xlabel("Time (t)")
        ax1.set_ylabel("f(t)")
        fillAxis = ax1

        xAreaPoints = xSpan
        yAreaPoints = y
        fillBetFigure = ax1.fill_between(xSpan, 0, y, facecolor = '#4B0082', alpha = 0)
        totalArea = trapz(yAreaPoints, xAreaPoints)

        unrelValuesFullNew = ss.weibull_min.cdf(xSpan, shape, loc, scale)
        ax2.plot(sortedX, medianRanks, 'ob', 
            markersize = 2.3, 
            label = 'weibull probability plot scatter')
        print(shape, loc, scale)
        ax2.plot(xSpan, ss.weibull_min.cdf(xSpan, shape, loc, scale), 'g-', label = 'weibull probability plot')

        ax2.set_ylabel("Unreliability F(t)")
        ax2.set_xscale('log')  
        ax2.set_yscale('mercator', subplot = ax2)
        ax2.set_axisbelow(True)
        ax2.grid(True, which = 'both')
        ax2.set_title('St Weibull Probability Plot', y =0.99,  fontname="Arial", fontsize=12)
        ax2.set_xlabel("Time (t)")
        ax2.yaxis.set_label_position('right')

        if max(unrelValuesFullNew) < 0.99:
            ax2.set_ylim(min(medianRanks), max(unrelValuesFullNew))
        else:
            ax2.set_ylim(min(medianRanks), 0.99)

        ax3.plot(xSpan, [np.exp(-1*((xi/scale)**shape)) for xi in xSpan], 
            label = 'weibull reliability (survival) function', 
            color = '#8B0000', lw = 1.0)
        ax3.set_title('Survival Function', y =0.99, fontname="Arial", fontsize=12)
        ax3.set_xlabel("Time (t)")
        ax3.set_ylabel("Reliability 1-F(t)")
        ax3.set_ylim(0, max(ax3.get_ylim()))

        ax4.plot(xSpan, [(shape/scale)*(xi/scale)**(shape - 1) for xi in xSpan], 
            label = 'weibull failure rate (hazard) function', 
            lw = 1.0, 
            color = '#8B0000')
        ax4.set_title('Hazard Function', y =0.99,  fontname="Arial", fontsize=12)
        ax4.set_xlabel("Time (t)")
        ax4.set_ylabel("Failure Rate (fr/time)")
        ax4.set_ylim(0, max(ax4.get_ylim()))
        ax4.yaxis.set_label_position('right')


        yIs = [np.log(-1*np.log(1-mr)) for mr in medianRanks]
        xIs = [np.log(t) for t in sortedX]
        
        corrCoeff = calc_corr_coeff(xIs, yIs)
        print('succeeded plot')
    elif distType == 'Lognormal Distribution':
        
        shapeSymbol = u"\u03c3" + "T'"
        scaleSymbol = u"\u03bc" + "'"
        locSymbol = 'loc'

        shape, loc, scale = ss.lognorm.fit([i for i in sortedX if i > 0.0])
        print(ax2)

        #plot the result
        xSpan = np.linspace(.0001, 1.5* mx, 300 + 5 * int(math.sqrt(mx - mn)))
        y = ss.lognorm.pdf(xSpan, shape, loc, scale)

        ax1.plot(xSpan, y, 
            label = 'lognormal distribution', 
            lw = 1.0, 
            color = '#8B0000')
        ax1.set_ylim(0, 1.5 * (max(y)))
        ax1.set_title('Lognormal Distribution', y =0.99,  fontname="Arial")
        ax1.set_xlabel("Time (t)")
        ax1.set_ylabel("f(t)")
        fillAxis = ax1

        xAreaPoints = xSpan
        yAreaPoints = y
        fillBetFigure = ax1.fill_between(xSpan, 0, y, facecolor = '#4B0082', alpha = 0)
        totalArea = trapz(yAreaPoints, xAreaPoints)

        ax2.plot(sortedX, medianRanks, 'ob', 
            markersize = 2.3, 
            label = 'lognormal probability plot scatter')
        cdf_y = ss.lognorm.cdf(xSpan, shape, loc, scale)
        ax2.plot(xSpan, cdf_y, 'g-', label = 'lognormal probability plot')
        print (shape, loc, scale)
        ax2.set_ylabel("Unreliability F(t)")
        ax2.set_xscale('linear')  
        if max(cdf_y) < 0.99:
            ax2.set_ylim(min(medianRanks), max(cdf_y))
        else:
            ax2.set_ylim(min(medianRanks), 0.99)

        ax2.set_axisbelow(True)
        ax2.grid(True, which = 'both')
        ax2.set_title('Lognormal Probability Plot', y =0.99,  fontname="Arial", fontsize=12)
        ax2.set_xlabel("Time (t)")
        ax2.yaxis.set_label_position('right')


        survival_y = []
        pdf_y = ss.lognorm.pdf(xSpan, shape, loc, scale)
        hazardFnc_y = []
        hazardFnc_x = []
        for i, xElem in enumerate(xSpan):
            try:
                survival_y += [1-cdf_y[i]]
                if 1-cdf_y[i] != 0:
                    hazardFnc_y += [pdf_y[i]/(1-cdf_y[i])]
                    hazardFnc_x += [xElem]       
            except:
                print 'ESXXX'
                continue
    
        ax3.plot(xSpan, survival_y , 
            label = 'normal reliability (survival) function', 
            color = '#8B0000', lw = 1.0)
        ax3.set_title('Survival Function', y =0.99, fontname="Arial", fontsize=12)
        ax3.set_xlabel("Time (t)")
        ax3.set_ylabel("Reliability 1-F(t)")
        # ax3.set_ylim(0, max(ax3.get_ylim()))

        ax4.plot(hazardFnc_x, hazardFnc_y, 
            label = 'normal failure rate (hazard) function', 
            lw = 1.0, 
            color = '#8B0000')
        ax4.set_title('Hazard Function', y =0.99,  fontname="Arial", fontsize=12)
        ax4.set_xlabel("Time (t)")
        ax4.set_ylabel("Failure Rate (fr/time)")
        ax4.yaxis.set_label_position('right')

        # ax4.set_ylim(0, max(ax4.get_ylim()))

        yIs = ss.lognorm.ppf(medianRanks, shape, loc, scale)# [np.log(1-mr) for mr in medianRanks]
        xIs = [np.log(t) for t in sortedX]
        corrCoeff = calc_corr_coeff(xIs, yIs)

    elif distType == 'Loglogistic Distribution':
        i = 0
    elif distType == 'Standard Exponential Distribution':
        p0, p1 = ss.expon.fit(sortedX) #loc and scale
        #plot the result
        xSpan = np.linspace(.0001, 1.5*mx, 300 + 5 * int(math.sqrt(mx - mn)))

        scaleSymbol = "1/" + u"\u03bb"
        locSymbol = u'\u03b3'

        loc = p0
        scale = p1

        rel_estimates = [1 - mr for mr in medianRanks]
        y = ss.expon.pdf(xSpan, p0, p1)

        ax1.plot(xSpan, y, 
            label = 'exponential distribution', 
            lw = 1.0, 
            color = '#8B0000')
        ax1.set_ylim(0, 1.5 * (max(y)))
        ax1.set_title('Exponential Distribution', y =0.99,  fontname="Arial")
        ax1.set_xlabel("Time (t)")
        ax1.set_ylabel("f(t)")
        fillAxis = ax1

        xAreaPoints = xSpan
        yAreaPoints = y
        fillBetFigure = ax1.fill_between(xSpan, 0, y, facecolor = '#4B0082', alpha = 0)
        totalArea = trapz(yAreaPoints, xAreaPoints)

        ax2.plot(sortedX, rel_estimates, 'ob', 
            markersize = 2.3, 
            label = 'exponential probability plot scatter')
        cdf_y = [1- val for val in ss.expon.cdf(xSpan, p0, p1)] # actually is the reliability function
        ax2.plot(xSpan, cdf_y, 'g-', label = 'exponential probability plot')

        ax2.set_ylabel("Reliability 1-F(t)")
        ax2.set_xscale('linear')  
        ax2.set_yscale('exponential', subplot = ax2)
        ax2.set_axisbelow(True)
        ax2.grid(True, which = 'both')
        ax2.set_title('St Exponential Probability Plot', y =0.99,  fontname="Arial", fontsize=12)
        ax2.set_xlabel("Time (t)")
        ax2.yaxis.set_label_position('right')
        if max(cdf_y) < 0.99:
            ax2.set_ylim(min(rel_estimates), max(cdf_y))
        else:
            ax2.set_ylim(min(rel_estimates), 0.99)

        print p0, p1
        ax3.plot(xSpan, [val for val in cdf_y], 
            label = 'exponential reliability (survival) function', 
            color = '#8B0000', lw = 1.0)
        ax3.set_title('Survival Function', y =0.99, fontname="Arial", fontsize=12)
        ax3.set_xlabel("Time (t)")
        ax3.set_ylabel("Reliability 1-F(t)")
        # ax3.set_ylim(0, max(ax3.get_ylim()))

        ax4.plot(xSpan, [p1 for xi in xSpan], 
            label = 'exponential failure rate (hazard) function', 
            lw = 1.0, 
            color = '#8B0000')
        ax4.set_title('Hazard Function', y =0.99,  fontname="Arial", fontsize=12)
        ax4.set_xlabel("Time (t)")
        ax4.set_ylabel("Failure Rate (fr/time)")
        ax4.yaxis.set_label_position('right')

        # ax4.set_ylim(0, max(ax4.get_ylim()))

        yIs = [np.log(1-mr) for mr in medianRanks]
        xIs = [t for t in sortedX]
        corrCoeff = calc_corr_coeff(xIs, yIs)

    elif distType == '3-Param Weibull Distribution':

        shapeSymbol = u'\u03b2'
        scaleSymbol = u'\u03b7'
        locSymbol = u'\u03b3'
        p0, p1, p2 = ss.weibull_min.fit(sortedX)
        shape, loc, scale = (p0, p1, p2)
        # TODO add all labels to each graph
        print(p0, p1, p2)
        mn = min(sortedX)
        mx = max(sortedX)
        xSpan = np.linspace(0.0001, 1.5*mx, 300 + 5 * int(math.sqrt(mx - mn)))
        xSpanDistribution = np.linspace(0.0001, 1.5*mx, 300 + 5 * int(math.sqrt(mx - mn)))

        y = ss.weibull_min.pdf(xSpanDistribution, p0, p1, p2)

        ax1.plot(xSpanDistribution, y, 
            label = 'weibull distribution', 
            lw = 1.0, 
            color = '#8B0000')
        ax1.set_ylim(0, 1.5 * (max(y)))
        ax1.set_title('Weibull Distribution', y =0.99,  fontname="Arial")
        ax1.set_xlabel("Time (t)")
        ax1.set_ylabel("f(t)")
        fillAxis = ax1

        xAreaPoints = xSpanDistribution
        yAreaPoints = y
        fillBetFigure = ax1.fill_between(xSpanDistribution, 0, y, facecolor = '#4B0082', alpha = 0)
        totalArea = trapz(yAreaPoints, xAreaPoints)

        xAxis_shiftedByLoc = [sortedXi - p1 for sortedXi in sortedX]
        xAxis_shiftedByLoc_Max = max(xAxis_shiftedByLoc)
        xAxis_shiftedByLoc_Min = min(xAxis_shiftedByLoc)


        xSpanNew = np.linspace(xAxis_shiftedByLoc_Min, 1.5*xAxis_shiftedByLoc_Max, 300 + 5 * int(math.sqrt(mx - mn)))
        unrelValuesFullNew = [1-np.exp(-1*(((xi)/p2)**p0)) for xi in xSpanNew]
        unrelValuesFullData = [1-np.exp(-1*(((xi)/p2)**p0)) for xi in xAxis_shiftedByLoc]

        ax2.plot(xAxis_shiftedByLoc, medianRanks,'ob', 
            markersize = 2.3, 
            label = 'weibull probability plot scatter')
        ax2.plot(xSpanNew, unrelValuesFullNew, color = '#8B0000', lw = 1.0, label = 'weibull probability plot')

        ax2.set_xscale('log')  
        ax2.set_yscale('mercator', subplot = ax2)
        ax2.set_axisbelow(True)
        ax2.grid(True, which = 'both')
        ax2.set_title('Weibull Probability Plot', y =0.99,  fontname="Arial", fontsize=12)
        ax2.set_xlabel("Time (t)")
        ax2.set_ylabel("Unreliability F(t)")
        ax2.yaxis.set_label_position('right')

        if max(unrelValuesFullNew) < 0.99:
            ax2.set_ylim(min(unrelValuesFullNew), max(unrelValuesFullNew))
        else:
            ax2.set_ylim(min(unrelValuesFullNew), 0.99)

        yIs = [np.log(-1*np.log(1-mr)) for mr in medianRanks]
        xIs = [np.log(t) for t in xAxis_shiftedByLoc]
        corrCoeff = calc_corr_coeff(xIs, yIs)

        ax3.plot(xSpan, [np.exp(-1*((xi/p2)**p0)) for xi in xSpanNew], 
            label = 'weibull reliability (survival) function', 
            color = '#8B0000', lw = 1.0)
        ax3.set_title('Survival Function', y =0.99, fontname="Arial", fontsize=12)
        ax3.set_xlabel("Time (t)")
        ax3.set_ylabel("Reliability 1-F(t)")
        ax3.set_ylim(0, max(ax3.get_ylim()))

        ax4.plot(xSpan, [(p0/p2)*(xi - p1/p2)**(p0 - 1) for xi in xSpan], 
            label = 'weibull failure rate (hazard) function', 
            lw = 1.0, 
            color = '#8B0000')
        ax4.set_title('Hazard Function', y =0.99,  fontname="Arial", fontsize=12)
        ax4.set_xlabel("Time (t)")
        ax4.set_ylabel("Failure Rate (fr/time)")
        ax4.set_ylim(0, max(ax4.get_ylim()))
        ax4.yaxis.set_label_position('right')

    elif distType == '2-Param Weibull Distribution':
        shapeSymbol = u'\u03b2'
        scaleSymbol = u'\u03b7'
        locSymbol = u'\u03b3'
        p0, p1, p2 = ss.weibull_min.fit(x, floc = 0)
        shape, loc, scale = (p0, p1, p2)

        mn = min(sortedX)
        mx = max(sortedX)
        xSpan = np.linspace(0.0001, mx*1.5, 300 + 5 * int(math.sqrt(mx - mn)))
        xSpanDistribution = np.linspace(0.0001, mx*1.5, 300 + 5 * int(math.sqrt(mx - mn)))

        y = ss.weibull_min.pdf(xSpanDistribution, p0, p1, p2)

        ax1.plot(xSpanDistribution, y, 
            label = 'weibull distribution', 
            lw = 1.0, 
            color = '#8B0000')
        ax1.set_ylim(0, 1.5 * (max(y)))
        ax1.set_title('Weibull Distribution', y =0.99,  fontname="Arial", fontsize=12)
        ax1.set_xlabel("Time (t)")
        ax1.set_ylabel("f(t)")
        fillAxis = ax1

        xAreaPoints = xSpanDistribution
        yAreaPoints = y
        fillBetFigure = ax1.fill_between(xSpanDistribution, 0, y, facecolor = '#4B0082', alpha = 0)
        totalArea = trapz(yAreaPoints, xAreaPoints)

        print (p0,p1,p2)

        xSpan2 = np.linspace(.0000001, 1.5* mx, 300 + 5 * int(math.sqrt(mx - mn)))

        unrelValuesFull = [1-np.exp(-1*((xi/p2)**p0)) for xi in xSpan2]
        unrelValues= [1-np.exp(-1*((xi/p2)**p0)) for xi in sortedX]

        ax2.plot(sortedX, medianRanks,'ob', 
            markersize = 2.3, 
            label = 'weibull probability plot scatter')
        ax2.plot(xSpan2, unrelValuesFull, color = '#8B0000', lw = 1.0, label = 'weibull probability plot')
        ax2.set_xscale('log')  
        ax2.set_yscale('mercator', subplot = ax2)
        ax2.set_axisbelow(True)
        ax2.grid(True, which = 'both')
        ax2.set_title('Weibull Probability Plot', y =0.99,  fontname="Arial", fontsize=12)
        ax2.set_xlabel("Time (t)")
        ax2.set_ylabel("Unreliability F(t)")
        ax2.yaxis.set_label_position('right')
        if max(unrelValuesFull) < 0.99:
            ax2.set_ylim(min(medianRanks), max(unrelValuesFull))
        else:
            ax2.set_ylim(min(medianRanks), 0.99)

        # report estimated correlation coefficient
        covar = 0.0
        xVarSum = 0.0
        yVarSum = 0.0
        corrCoef = 0.0

        yIs = [np.log(-1*np.log(1-mr)) for mr in medianRanks]
        xIs = [np.log(t) for t in sortedX]

        xIsForAvg = [np.log(t) for t in sortedX if t != 0]
        yIsForAvg = [np.log(-1*np.log(1-mr)) for i,mr in enumerate(medianRanks) if sortedX[i] != 0]
        avgY = sum(yIs)/len(yIs)
        avgX = sum(xIsForAvg)/len(xIsForAvg)
        # avgX = sum(medianRanks)/len(medianRanks)
        # avgY = sum(unrelValuesFullData) / len(sortedX)
        for i, val in enumerate(yIs):
            xi = xIs[i]
            yi = val
            if (str(xi) == '-inf' or str(xi) =='inf' or str(yi) == 'inf' or str(yi) == '-inf'): continue
            # if str(testSum) == : continue
            xVarSum += (xi - avgX)**2 
            yVarSum += (yi - avgY)**2 
            covar += (xi - avgX) * (yi - avgY)
        corrCoeff = covar/(np.sqrt(xVarSum * yVarSum))
        # if corrCoef < 0: corrCoef *= -1.0
        print 'CorrCoff ' + str(corrCoef)
        print 'min is ' + str(mn)


        ax3.plot(xSpan, [np.exp(-1*((xi/p2)**p0)) for xi in xSpan], 
            label = 'weibull reliability (survival) function', 
            color = '#8B0000', lw = 1.0)
        ax3.set_title('Survival Function', y =0.99, fontname="Arial", fontsize=12)
        ax3.set_xlabel("Time (t)")
        ax3.set_ylabel("Reliability 1-F(t)")
        ax3.set_ylim(0, max(ax3.get_ylim()))

        ax4.plot(xSpan, [(p0/p2)*(xi/p2)**(p0 - 1) for xi in xSpan], 
            label = 'weibull failure rate (hazard) function', 
            lw = 1.0, 
            color = '#8B0000')
        ax4.set_title('Hazard Function', y =0.99,  fontname="Arial", fontsize=12)
        ax4.set_xlabel("Time (t)")
        ax4.set_ylabel("Failure Rate (fr/time)")
        ax4.set_ylim(0, max(ax4.get_ylim()))
        ax4.yaxis.set_label_position('right')

    if (globalMultiplier > 1.0):
        ax1.set_xlabel(str(ax1.get_xlabel())+" (1e+%d)" % (logBase))
        ax2.set_xlabel(str(ax2.get_xlabel())+" (1e+%d)" % (logBase))
        ax3.set_xlabel(str(ax3.get_xlabel())+" (1e+%d)" % (logBase))
        ax4.set_xlabel(str(ax4.get_xlabel())+" (1e+%d)" % (logBase))

        # # report estimated correlation coefficient
        # covar = 0.0
        # xVarSum = 0.0
        # yVarSum = 0.0
        # corrCoef = 0.0
        # avgX = sum(medianRanks)/len(medianRanks)
        # avgY = sum(unrelValues) / len(sortedX)
        # for i, val in enumerate(unrelValues):
        #     xi = medianRanks[i]
        #     yi = val

        #     print (xi, yi)
        #     xVarSum += (xi - avgX)**2 
        #     yVarSum += (yi - avgY)**2 
        #     covar += (xi - avgX) * (yi - avgY)
        # corrCoef = covar/(np.sqrt(xVarSum * yVarSum))

        # # if corrCoef < 0: corrCoef *= -1.0

        # print 'CorrCoff ' + str(corrCoef)
        # print 'min is ' + str(mn)
    print('yes 1')
    slider_config_for_table_present_four_graphs()
    print('yes 2')
    # TODO TODO TODO
    fig_dict[fig] = {}
    fig_dict[fig]['fig_next'] = None
    fig_dict[fig]['sessionType'] = 'RELA'
    fig_dict[fig]['numAxes'] = 4
    fig_dict[fig]['csv_src'] = dataFile
    fig_dict[fig]['slider_axes'] = [axLeft, axRight]
    fig_dict[fig]['dictOfAxes'] = {}
    fig_dict[fig]['loaded'] = False

    for axes in [ax1, ax2, ax3, ax4]:
        init_fig_dict(axes)
        fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mn'] = globalMin
        fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mu'] = globalMu
        fig_dict[fig]['dictOfAxes'][axes]['specsTable']['mx'] = globalMax 
        fig_dict[fig]['dictOfAxes'][axes]['specsTable']['sigma'] = globalSigma
        fig_dict[fig]['dictOfAxes'][axes]['specsTable']['corr_coeff'] = corrCoeff
        fig_dict[fig]['dictOfAxes'][axes]['specsTable']['multiplier'] = globalMultiplier

        if len(shapeSymbol):
            fig_dict[fig]['dictOfAxes'][axes]['specsTable']['shape'] = (shape, shapeSymbol)
        if len(locSymbol):
            fig_dict[fig]['dictOfAxes'][axes]['specsTable']['loc'] = (loc, locSymbol)
        if len(scaleSymbol):
            fig_dict[fig]['dictOfAxes'][axes]['specsTable']['scale'] = (scale, scaleSymbol)

    if distType == 'Lognormal Distribution':
        ax2.set_yscale('lognormal', subplot = ax2)

    fig_dict[fig]['fillAxis'] = fillAxis
    fig_dict[fig]['statsTable'] = statTableTxt

    fig_dict[fig]['dictOfAxes'][ax2]['axesScales'] = (str(ax2.get_xscale()),  str(ax2.get_yscale()))

    cancan.toggle_slider_vis()

    # ax2.set_xlim(min(sortedX), max(sortedX))
    cancan.axpopup.entryconfig(1, state='normal')


    splitTypeName = distType.split(' ')
    truncatedName = ' '.join(splitTypeName[:-1])
    graphTitle.set(truncatedName + ' Reliability Plots for ' + str(gotten))

    cancan.thisFigure.suptitle(truncatedName + ' Reliability Plots for ' + str(gotten), fontsize=18, fontweight='bold', fontname="Calibri")
    cancan.draw()


    # notebookFrame = notebookFrame.nametowidget(notebookFrame.select()).master
    # notebookFrame.tab(notebookFrame.select(), "text")
    # notebookFrame = ttk.Notebook(self, style='bottomtab.TNotebook')
    # canContainer = TabFrame(master=notebookFrame, name ="Chart", width=200, height=200)
    # notebookFrame.add(canContainer, text="Chart1", compound=tk.BOTTOM)
    # notebookFrame.select( notebookFrame.index(notebookFrame.select()))

    # canvas = FancyFigureCanvas(fig, canContainer)
    # tab = TabFrame(notebookFrame, name)

    # notebookFrame.add(tab, text=name)
    # notebookFrame.nametowidget(notebookFrame.select())
    # notebookFrame.tab(notebookFrame.select(), text = 'myNewText')

    # notebookFrame.tab(notebookFrame.select(), text=graphTitle.get())





def plot(canvas,graphType):
    global writeCsv_lock
    global xAreaPoints
    global yAreaPoints
    global globalBins
    global globalNPerBin
    global dataFile
    global a
    global a2
    global curHeader
    global globalBinning
    global dataType
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
    global cursors
    global globalMultiplier
    global logBase
    global fig_dict
    global statTableTxt
    global sessionType
    global cursorState
    global showTableOfStats

    
    err_message = None

    
    try:
        numBins = globalBinning.get()
        gotten = curHeader.get()
        if dataFile is not None:
            dframe = pd.read_csv(dataFile)
            dframe = dframe.sort_values(gotten)
            a3 = None
            if (dataType.get() == "Date (mm/dd/yyyy)"):
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
                globalSigVar.set(u"\u03c3 = " + str(truncate(sigma, 6)) + "\n" + u"\u03bc = " + str(truncate(mu, 6)) +"\nmin = " + str(truncate(mn, 6)) +  "\nmax = " + str(truncate(mx, 6)) )
                props = dict(boxstyle='round', facecolor='lightblue', lw = .25)
                statTableTxt = fig.text(x = .85, y=.75, s = globalSigVar.get(), bbox = props, fontsize = 9)
                
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
                    graphTitle.set('Weibull PDF Fit to ' + str(gotten))

                elif graphType == 'Normal Distribution':
                    for xElem in x:
                        y = y + [np.reciprocal(stats.iloc[2][gotten] * math.sqrt(2 * np.pi))
                            * np.reciprocal(np.exp(0.5 * ((xElem - stats.iloc[1][gotten]) / (stats.iloc[2][gotten])) ** 2))]

                    graphTitle.set('Normal PDF Fit to ' + str(gotten))
                    a3.plot(x, y, label = 'normal distribution', lw = 1.0, color = '#8B0000')

                elif graphType == 'Lognormal Distribution':
                    s, p1, p2 = ss.lognorm.fit([i for i in datesDF[gotten].dropna().tolist() if i > 0.0], floc = 0)
                    print(s, p1, p2)
                    print(globalSigma, globalMu)
                    y = ss.lognorm.pdf(x, s, p1, p2)
                    print('gothere')
                    a3.plot(x, y, color = '#8B0000', lw=1.0, label='lognormal distribution')
                    graphTitle.set('Lognormal PDF Fit to ' + str(gotten))

                elif graphType == 'Loglogistic Distribution':
                    c, p1, p2 = ss.fisk.fit([i for i in datesDF[gotten].dropna().tolist() if i > 0.0], floc = 0)
                    print(c,p1, p2)
                    print(globalSigma, globalMu)
                    y = ss.fisk.pdf(x, c, p1, globalMu)
                    a3.plot(x, y, color = '#8B0000', lw=1.0, label='loglogistic distribution')                       
                    graphTitle.set('Loglogistic PDF Fit to ' + str(gotten))

                elif graphType == 'Logistic Distribution':
                    p0, p1 =ss.logistic.fit(datesDF[gotten].dropna().tolist(), floc=globalMu)
                    print(p0, p1)
                    y = ss.logistic.pdf(x, p0, p1)
                    a3.plot(x, y, label = 'logistic distribution', lw = 1.0, color = '#8B0000')
                    graphTitle.set('Logistic PDF Fit to ' + str(gotten))
                

                showTableOfStats = True


                a.set_ylim(0, 1.5 * (max(n)))
                globalBins = dates.num2date(bins)
                globalNPerBin = n


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

                # a.legend(bbox_to_anchor=(0, 1.08, 1, .102), loc=3,
                #         ncol=1, borderaxespad=0)

                totalArea = trapz(y, x)

                cancan.thisFigure.suptitle(graphTitle.get(), fontsize=18, fontweight='bold',  fontname="Calibri")
                slider_config_for_table_present_one_graph()


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

                fig_dict[fig]['dictOfAxes'][a3]['addAxes'][a] = zip(globalBins, globalNPerBin)
                fig_dict[fig]['fillAxis'] = fillAxis
                fig_dict[fig]['statsTable'] = statTableTxt
                cancan.draw()
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
                globalSigVar.set(u"\u03c3 = " + str(truncate(sigma, 6)) + "\n" + u"\u03bc = " + str(truncate(mu, 6)) +"\nmin = " + str(truncate(mn, 6)) +  "\nmax = " + str(truncate(mx, 6)) )
                props = dict(boxstyle='round', facecolor='lightblue', lw = .25)
                statTableTxt = fig.text(x = .85, y=.75, s = globalSigVar.get(), bbox = props, fontsize = 9)

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
                    graphTitle.set('Weibull PDF Fit to ' + str(gotten))

                elif graphType == 'Normal Distribution':
                    for xElem in x:
                        y = y + [np.reciprocal(globalSigma * math.sqrt(2 * np.pi))
                            * np.reciprocal(np.exp(0.5 * ((xElem - globalMu) / (globalSigma)) ** 2))]
                    a2.plot(x, y, label = 'normal distribution', lw = 1.0, color = '#8B0000')
                    graphTitle.set('Normal PDF Fit to ' + str(gotten))

                elif graphType == 'Lognormal Distribution':
                    s, p1, p2 = ss.lognorm.fit([i for i in xdata if i > 0.0], floc = 0)
                    print(s, p1, p2)
                    print(globalSigma, globalMu)
                    y = ss.lognorm.pdf(x, s, p1, p2)
                    print('gothere')
                    a2.plot(x, y, color = '#8B0000', lw=1.0, label='lognormal distribution')
                    graphTitle.set('Lognormal PDF Fit to ' + str(gotten))
                elif graphType == 'Loglogistic Distribution':
                    c, p1, p2 = ss.fisk.fit([i for i in xdata if i > 0.0], floc = 0)
                    print(c,p1, p2)
                    print(globalSigma, globalMu)
                    y = ss.fisk.pdf(x, c, p1, globalMu)
                    a2.plot(x, y, color = '#8B0000', lw=1.0, label='loglogistic distribution')
                    graphTitle.set('Loglogistic PDF Fit to ' + str(gotten))
                elif graphType == 'Logistic Distribution':
                    p0, p1 =ss.logistic.fit(xdata, floc=globalMu)
                    print(p0, p1)
                    y = ss.logistic.pdf(x, p0, p1)
                    a2.plot(x, y, label = 'logistic distribution', lw = 1.0, color = '#8B0000')
                    graphTitle.set('Logistic PDF Fit to ' + str(gotten))
                
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
                totalArea = trapz(y, x)

                a2.set_label('Normal PDF')
                a2.grid(False)

                try:
                    a2.set_ylim(0, 1.5 * (max(y)))
                except ValueError, e:
                    tkMessageBox.showerror("Zero Variation Error", "Data at header " + str(gotten)
                        + " in file " + str(dataFile) + " has no variation. Failed to draw " + str(graphType) +  " curve.\n\n" + " Error:" + str(e))
                    # set_up_new_figure('PDF', sessionType).draw()
                    # cancan.axpopup.entryconfig(1,state='disabled')
                    # cancan.addable_menu.entryconfig(0, state = 'disabled')

                    cancan.draw()
                    cancan.axpopup.entryconfig(1,state='disabled')
                    cancan.addable_menu.entryconfig(0, state = 'disabled')

                    tabIndex = notebookFrame.index(canContainer)
                    deleteTab(tabIndex)
                    hideExtraTabs()

                    wasPlotted = False
                    return

                apxBinDif = (max(xAreaPoints)-min(xAreaPoints))/numBins
                a.set_xlim(min(xAreaPoints)-apxBinDif ,max(xAreaPoints) + apxBinDif)

                # a2.set_xlim(min(x), (max(x))) #ToCOMMENT

                a2.tick_params(axis = 'y', labelcolor = '#8B0000')
                a2.set_ylabel("Distribution Values")
                # a.set_xlabel("Numeric Divisions")

                if (globalMultiplier > 1.0):
                    a.set_xlabel(str(gotten)+" (1e+%d)" % (logBase))
                else:
                    a.set_xlabel(str(gotten))

                a.set_ylabel("Frequency")
                a2.yaxis.tick_right()

                # a.legend(bbox_to_anchor=(0, 1.08, 1, .102), loc=3,
                #         ncol=1, borderaxespad=0)
                # graphTitle.set('Normal PDF Fit to ' + str(gotten))
                cancan.thisFigure.suptitle(graphTitle.get(), fontsize=18, fontweight='bold',  fontname="Calibri")

                showTableOfStats = True
                slider_config_for_table_present_one_graph()

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
                fig_dict[fig]['fillAxis'] = fillAxis
                fig_dict[fig]['statsTable'] = statTableTxt

                globalBins = bins
                globalNPerBin = n
                fig_dict[fig]['dictOfAxes'][a2]['addAxes'][a] = zip(globalBins, globalNPerBin)
                cancan.draw()

            if not cursorState.get():
                toggleCrossHairs()
            cancan.toggle_slider_vis()
            cancan.axpopup.entryconfig(1,state='normal')

            cancan.addable_menu.entryconfig(0, state = 'normal')
            wasPlotted = True
    except ValueError, e:
        tkMessageBox.showerror("Data NA Error", "Data at header " + str(gotten)
            + " in file " + str(dataFile) + " is missing or invalid.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except TypeError, e:
        tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
            gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return
    except KeyError, e:
        tkMessageBox.showerror("Parsing Error", "Data not valid at header " +
            gotten + ". Check that you have selected the right data type.\n\n" + " Error:" + str(e))
        cancan.draw()
        cancan.axpopup.entryconfig(1,state='disabled')
        cancan.addable_menu.entryconfig(0, state = 'disabled')

        tabIndex = notebookFrame.index(canContainer)
        deleteTab(tabIndex)
        hideExtraTabs()

        wasPlotted = False
        return


def on_app_close():

    if tkMessageBox.askokcancel("Quit", "Would you like to save your work to a workspace before quitting?"):
        app.destroy()


app = SeaofBTCapp()
app.protocol("WM_DELETE_WINDOW", on_app_close)
app.geometry("900x700")
app.mainloop() # tkinter functionality


# TODO update side inputs bar on change to reliability analysis
