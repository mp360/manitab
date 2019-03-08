#! /usr/bin/env python NO USE

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use("ggplot")

import numpy as np
import time

def newfig(l):
    fig, ax = plt.subplots(figsize=(10,8))
    fig.show()
    fig.tight_layout()

    #obj, = ax.plot(np.random.rand(l))  # normal line plot
    obj = ax.vlines(np.arange(l), [0], np.ones(l), alpha=0.5, linewidths=400./l)   # vlines return line collection

    obj.remove() # if using restore from bg method, bg should not contain lines; comment this line if use canvas.draw() method
    fig.canvas.draw()
    bg = fig.canvas.copy_from_bbox(ax.bbox)

    return fig, ax, obj, bg


class LiveFig:

    def __init__(self, l):
        self.fig, self.ax, self.obj, self.bg = newfig(l)

    def update(self, h):
        ## update data
        #self.obj.set_ydata(h)  # for normal line plot

        segs = np.zeros((len(h), 2, 2)) # for vlines
        segs[:, :, 0] = np.arange(len(h))[:, np.newaxis]
        segs[:, 1, 1] = h
        self.obj.set_paths(segs)

        ############################################################
        ## way1: update canvas by default, if use this then should not do obj.remove() above

        #  self.fig.canvas.draw()
        ############################################################

        ############################################################
        ## way2: update canvas partially, faster but fig cannot be resized, if use this
        ## then should do obj.remove() above before saving background

        self.fig.canvas.restore_region(self.bg)
        self.ax.draw_artist(self.obj)
        self.fig.canvas.update()
        ############################################################


        self.fig.canvas.flush_events()  # entering Qt event loop, both methods require this


if __name__ == "__main__":
    l1 = 300
    fig1 = LiveFig(l1)

    l2 = 400
    fig2 = LiveFig(l2)

    tstart = time.time()
    numfrm = 0
    tdelta = 10
    while time.time() - tstart < tdelta:
        h1 = np.random.rand(l1)
        fig1.update(h1)

        h2 = np.random.rand(l2)
        fig2.update(h2)

        numfrm += 1

    print "fps: ", numfrm / tdelta
    raw_input("Press any key to exit.")