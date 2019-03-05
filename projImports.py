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
from Tkinter import Entry, StringVar, IntVar, DoubleVar
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