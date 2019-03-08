import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)
fig.canvas.set_window_title('Einfluss der Geschwindigkeitskonstanten')

a0 = 1
b0 = 0
plt.axis([0, 5, 0, 2])
plt.xticks([1, 4], ['A', 'B'])
plt.bar(1, a0, color = 'red')

#slider:
axcolor = 'lightblue'
axrs = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
srs = Slider(axrs, 'RS', 0, 20, valinit=0)

def slider_val_fkt(t):
    ya = []
    t = srs.val
    ya = [np.exp(-0.6 * t)]
    print(ya)
    plt.bar(5, ya, color = 'red')
    #plt.draw()
    #plt.show()
    fig.canvas.draw()

srs.on_changed(slider_val_fkt)

plt.show()

# import random
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates

# # generate some random data (approximately over 5 years)
# data = [float(random.randint(1271517521, 1429197513)) for _ in range(1000)]

# # convert the epoch format to matplotlib date format
# mpl_data = mdates.epoch2num(data)

# # plot it
# fig, ax = plt.subplots(1,1)
# ax.hist(mpl_data, bins=50, color='lightblue')
# ax.xaxis.set_major_locator(mdates.YearLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
# plt.show()