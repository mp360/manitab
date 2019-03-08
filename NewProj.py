#%matplotlib notebook

import xlwings as xw
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import style
from matplotlib.ticker import MaxNLocator
from collections import namedtuple
from matplotlib.widgets import Slider, Button, RadioButtons

def hello_xlwings():
    wb = xw.Book.caller()
    wb.sheets[0].range("A1").value = "Hello xlwings!"


@xw.func
def hello(name):
    return "hello {0}".format(name)

@xw.func
def create_figure():
    # N = 150
    # r = 2 * np.random.rand(N)
    # area = 200 * r**2
    # colors = theta
    # fig = plt.figure(figsize = (4.4)) #need obtain reference to figure object
    # ax = fig.add_subplot(111, projection = 'polar')
    # c = ax.scatter(theta, r, c = colors, s = area, cmap = 'hsv', alpha = 0.75)

    # # Make original signal graph
    # np.random.seed(0)

    # x, y = np.random.randn(2, 100)
    # fig = plt.figure()
    # ax1 = fig.add_subplot(211)
    # ax1.xcorr(x, y, usevlines=True, maxlags=50, normed=True, lw=2)
    # ax1.grid(True)
    # ax1.axhline(0, color='black', lw=2)

    # ax2 = fig.add_subplot(212, sharex=ax1)
    # ax2.acorr(x, usevlines=True, normed=True, maxlags=50, lw=2)
    # ax2.grid(True)
    # ax2.axhline(0, color='black', lw=2)

    # return fig


    # wb.sheets[1].range("A1").value = "Hello xlwings!"
    # #Get the constant from Excel
    # x = wb.sheets[1].range("A1").value
    # wb.sheets[1].range("B1").value = x
    wb = xw.Book.caller()
    xOnSheet2 = wb.sheets[1].range("B10:B10010").count
    yOnSheet2 = wb.sheets[1].range("C10:C10010").count
    x = []
    y = []
    for xLem in range(xOnSheet2):
        x = x + [wb.sheets[1].range("B" + str(10 + xLem)).value]
        y += [wb.sheets[1].range("C" + str(10 + xLem)).value]

    wb.sheets[1].range("D2").value = str(type(xOnSheet2))

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.scatter(x,y, label = 'skitscat', color = 'k')
    # ax1.xlabel('x')
    # ax1.ylabel('y')
    # ax1.title('Interesting Graph\nChekitout')
    ax1.legend()

    return fig


def polar_scatterplot():
    #Create a reference to the calling exel workbook
    wb = xw.Book.caller()

    # wb.sheets[0].range("A1").value = "Hello xlwings!"
    # #Get the constant from Excel
    # x = wb.sheets[0].range("A1").value
    # wb.sheets[0].range("B1").value = x

    sht = wb.sheets[0]
    #Get the figure and show it in Excel
    fig = create_figure()
    pic = sht.pictures.add(fig, name = 'Polar Plot', update = True)
