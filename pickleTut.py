import numpy as np
import matplotlib.pyplot as plt
import pickle as pl
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import Tkinter as tk, tkFileDialog
from Tkinter import Entry, StringVar, IntVar, DoubleVar, Toplevel
import tkMessageBox
import tkFont
# from Tkinter import *
import ttk     

matplotlib.use("TkAgg")
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
        self.popup_menu.add_command(label="Save as...", command=saveImage)

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
        showTableOfStats
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
        for refLine in refLines:
            refLine.remove()
        for entryBox in listOfRefLines:
            entryBox.destroy()
        for txt in textBoxes:
            txt.remove()
        listOfRefLines = []
        refLines = []
        textBoxes = []
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



# Plot simple sinus function
# fig_handle = plt.figure()

fig2 = Figure(dpi = 100)

fig2.subplots_adjust(bottom = 0.25, right = .85, top = .85)
fig2.subplots_adjust(wspace=.3, hspace=.35)
fig2.patch.set_facecolor('#E0E0E0')
fig2.patch.set_alpha(0.7)

axes2 = fig2.add_subplot(111)

x = np.linspace(0,2*np.pi)
y = np.sin(x)
axes2.plot(x,y)


dictPickle = {}
dictPickle[fig2] = y

# Save figure handle to disk
pl.dump(dictPickle,file('sinus.pickle','wb'))


