# # -*- noplot -*-

# """
# This example shows how to use matplotlib to provide a data cursor.  It
# uses matplotlib to draw the cursor and may be a slow since this
# requires redrawing the figure with every mouse move.

# Faster cursoring is possible using native GUI drawing, as in
# wxcursor_demo.py.

# The mpldatacursor and mplcursors third-party packages can be used to achieve a
# similar effect.  See
#     https://github.com/joferkington/mpldatacursor
#     https://github.com/anntzer/mplcursors
# """
# from __future__ import print_function
# import matplotlib.pyplot as plt
# import numpy as np


# class Cursor(object):
#     def __init__(self, ax):
#         self.ax = ax
#         self.lx = ax.axhline(color='k')  # the horiz line
#         self.ly = ax.axvline(color='k')  # the vert line

#         # text location in axes coords
#         self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

#     def mouse_move(self, event):
#         if not event.inaxes:
#             return

#         x, y = event.xdata, event.ydata
#         # update the line positions
#         self.lx.set_ydata(y)
#         self.ly.set_xdata(x)

#         self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
#         plt.draw()


# class SnaptoCursor(object):
#     """
#     Like Cursor but the crosshair snaps to the nearest x,y point
#     For simplicity, I'm assuming x is sorted
#     """

#     def __init__(self, ax, x, y):
#         self.ax = ax
#         self.lx = ax.axhline(color='k')  # the horiz line
#         self.ly = ax.axvline(color='k')  # the vert line
#         self.x = x
#         self.y = y
#         # text location in axes coords
#         self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

#     def mouse_move(self, event):

#         if not event.inaxes:
#             return

#         x, y = event.xdata, event.ydata

#         indx = np.searchsorted(self.x, [x])[0]
#         x = self.x[indx]
#         y = self.y[indx]
#         # update the line positions
#         self.lx.set_ydata(y)
#         self.ly.set_xdata(x)

#         self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
#         print('x=%1.2f, y=%1.2f' % (x, y))
#         plt.draw()

# t = np.arange(0.0, 1.0, 0.01)
# s = np.sin(2*2*np.pi*t)
# fig, ax = plt.subplots()

# #cursor = Cursor(ax)
# cursor = SnaptoCursor(ax, t, s)
# plt.connect('motion_notify_event', cursor.mouse_move)

# ax.plot(t, s, 'o')
# plt.axis([0, 1, -1, 1])
# plt.show()
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import numpy as np

import wx


class CanvasFrame(wx.Frame):
    def __init__(self, ):
        wx.Frame.__init__(self, None, -1, 'CanvasFrame', size=(550, 350))

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)

        self.axes.plot(t, s)
        self.axes.set_xlabel('t')
        self.axes.set_ylabel('sin(t)')
        self.figure_canvas = FigureCanvas(self, -1, self.figure)

        # Note that event is a MplEvent
        self.figure_canvas.mpl_connect(
            'motion_notify_event', self.UpdateStatusBar)
        self.figure_canvas.Bind(wx.EVT_ENTER_WINDOW, self.ChangeCursor)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.figure_canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

        self.statusBar = wx.StatusBar(self, -1)
        self.SetStatusBar(self.statusBar)

        self.toolbar = NavigationToolbar2Wx(self.figure_canvas)
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.toolbar.Show()

    def ChangeCursor(self, event):
        self.figure_canvas.SetCursor(wx.Cursor(wx.CURSOR_CROSS))

    def UpdateStatusBar(self, event):
        if event.inaxes:
            self.statusBar.SetStatusText(
                "x={}  y={}".format(event.xdata, event.ydata))


class App(wx.App):
    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame()
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

if __name__ == '__main__':
    app = App(0)
    app.MainLoop()