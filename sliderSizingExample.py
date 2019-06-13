import os
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

import glob
import h5py
#Define the xy size of the mapped array
xsize=3
ysize=3

lengthh5=9
readlist=[]
for i in range (0,lengthh5):
    npraw=np.random.rand(200,50,50)
    readlist.append (npraw)

fig=plt.figure()
# ls = []
# for k in range (0,lengthh5):
#     ax=fig.add_subplot(xsize,ysize,k)        
#     frame = 10
#     l = ax.imshow(readlist[k][frame,:,:]) 
#     ls.append(l)
#     plt.axis('off')

sframe = Slider(fig.add_subplot(1,1,50), 'Frame', 
                0, len(readlist[0])-1, valinit=0)

# def update(val):
#     frame = np.around(sframe.val)
#     for k, l in enumerate(ls):
#         l.set_data(readlist[k][frame,:,:])

# sframe.on_changed(update)
plt.show()