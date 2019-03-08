# from Tkinter import *

# # a subclass of Canvas for dealing with resizing of windows
# class ResizingCanvas(Canvas):
#     def __init__(self,parent,**kwargs):
#         Canvas.__init__(self,parent,**kwargs)
#         self.bind("<Configure>", self.on_resize)
#         self.height = self.winfo_reqheight()
#         self.width = self.winfo_reqwidth()

#     def on_resize(self,event):
#         # determine the ratio of old width/height to new width/height
#         wscale = float(event.width)/self.width
#         hscale = float(event.height)/self.height
#         self.width = event.width
#         self.height = event.height
#         # resize the canvas
#         self.config(width=self.width, height=self.height)
#         # rescale all the objects tagged with the "all" tag
#         self.scale("all",0,0,wscale,hscale)

# def main():
#     root = Tk()
#     myframe = Frame(root)
#     myframe.pack(fill=BOTH, expand=YES)
#     mycanvas = ResizingCanvas(myframe,width=850, height=400, bg="red", highlightthickness=0)
#     mycanvas.pack(fill=BOTH, expand=YES)

#     # add some widgets to the canvas
#     mycanvas.create_line(0, 0, 200, 100)
#     mycanvas.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
#     mycanvas.create_rectangle(50, 25, 150, 75, fill="blue")

#     # tag all of the drawn widgets
#     mycanvas.addtag_all("all")
#     root.mainloop()

# if __name__ == "__main__":
#     main()

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

def inputExplorer(f, sliders_properties, wait_for_validation = False):
    """ A light GUI to manually explore and tune the outputs of
        a function.
        slider_properties is a list of dicts (arguments for Slider )
        whose keys are in ( label, valmin, valmax, valinit=0.5,
        valfmt='%1.2f', closedmin=True, closedmax=True, slidermin=None,
        slidermax=None, dragging=True)

        def volume(x,y,z):
            return x*y*z

        intervals = [ { 'label' :  'width',  'valmin': 1 , 'valmax': 5 },
                  { 'label' :  'height',  'valmin': 1 , 'valmax': 5 },
                  { 'label' :  'depth',  'valmin': 1 , 'valmax': 5 } ]
        inputExplorer(volume,intervals)
    """

    nVars = len(sliders_properties)
    slider_width = 1.0/nVars
    print slider_width

    # CREATE THE CANVAS

    figure,ax = plt.subplots(1)
    figure.canvas.set_window_title( "Inputs for '%s'"%(f.func_name) )

    # choose an appropriate height

    width,height = figure.get_size_inches()
    height = min(0.5*nVars,8)
    figure.set_size_inches(width,height,forward = True)


    # hide the axis
    ax.set_frame_on(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)


    # CREATE THE SLIDERS

    sliders = []

    for i, properties in enumerate(sliders_properties):

        ax = plt.axes([0.1 , 0.95-0.9*(i+1)*slider_width,
                       0.8 , 0.8* slider_width])
        sliders.append( Slider(ax=ax, **properties) )


    # CREATE THE CALLBACK FUNCTIONS

    def on_changed(event) :

        res = f(*(s.val for s in sliders))

        if res is not None:

            print res

    def on_key_press(event):

        if event.key is 'enter':

            on_changed(event)

    # figure.canvas.mpl_connect('key_press_event', on_key_press)

    # AUTOMATIC UPDATE ?

    if not wait_for_validation:

        for s in sliders :

            s.on_changed(on_changed)


    # DISPLAY THE SLIDERS
    plt.show()

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint

def model(state,t, a,b,c,d):
    x,y = state
    return [ x*(a-b*y) , -y*(c - d*x) ]

ts = np.linspace(0,10,500)

fig,ax = plt.subplots(1)

def plotDynamics(x0,y0,a,b,c,d):
    ax.clear()
    ax.plot(ts, odeint(model, [x0,y0], ts, args = (a,b,c,d)) )

    fig.canvas.draw()

sliders = [ { 'label' :  label,  'valmin': 1 , 'valmax': 5 }
         for label in [ 'x0','y0','a','b','c','d' ] ]

inputExplorer(plotDynamics,sliders)

