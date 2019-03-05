
import numpy as np
from scipy.stats import norm, lognorm, uniform
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons
from matplotlib.patches import Polygon


#####Mean and standard deviation#####

mu_a1 = 1
mu_b1 = 10
mu_c1 = -13
sigma_a1 =  0.14
sigma_b1 =  1.16
sigma_c1 =  2.87
mu_x01 = -11
sigma_x01 =  1.9

#####_____#####



#####Generating random data#####

a1 = 0.75*mu_a1 + (1.25 - 0.75)*sigma_a1*np.random.sample(10000)
b1 = 8*mu_b1 + (12 - 8)*sigma_b1*np.random.sample(10000)
c1 = -12*mu_c1 + 2*sigma_c1*np.random.sample(10000)
x01 = (-b1 - np.sqrt(b1**2 - (4*a1*c1)))/(2*a1)

#####_____#####



#####Creating Subplots#####

fig = plt.figure()
plt.subplots_adjust(left=0.13,right=0.99,bottom=0.05)

ax1 = fig.add_subplot(331)                                                  #Subplot 1
ax1.set_xlabel('a' , fontsize = 14)
ax1.grid(True)

ax2 = fig.add_subplot(334)                                                  #Subplot 2
ax2.set_xlabel('b', fontsize = 14)
ax2.grid(True)

ax3 = fig.add_subplot(337)                                                  #Subplot 3
ax3.set_xlabel('c', fontsize = 14)
ax3.grid(True)

ax4 = fig.add_subplot(132)                                                  #Subplot 4
ax4.set_xlabel('x0', fontsize = 14)
ax4.set_ylabel('PDF', fontsize = 14)
ax4.grid(True)

ax5 = fig.add_subplot(133)                                                  #Subplot 5
ax5.set_xlabel('x0', fontsize = 14)
ax5.set_ylabel('CDF', fontsize = 14)
ax5.grid(True)

#####_____#####


#####Plotting Distributions#####

[n1,bins1,patches] = ax1.hist(a1, bins=50, color = 'red',alpha = 0.5, normed = True)
[n2,bins2,patches] = ax2.hist(b1, bins=50, color = 'red',alpha = 0.5, normed = True)
[n3,bins3,patches] = ax3.hist(c1, bins=50, color = 'red',alpha = 0.5, normed = True)
[n4,bins4,patches] = ax4.hist(x01, bins=50, color = 'red',alpha = 0.5, normed = True)
ax4.axvline(np.mean(x01), color = 'black', linestyle = 'dashed', lw = 2)
dx = bins4[1] - bins4[0]
CDF = np.cumsum(n4)*dx
ax5.plot(bins4[1:], CDF, color = 'red')

#####_____#####



#####Event handler for button_press_event#####

def enter_axes(event):
    print('enter_axes', event.inaxes)
    event.canvas.draw()

def leave_axes(event):
    print('leave_axes', event.inaxes)
    event.canvas.draw()

def onclick(event):
    '''
    Event handler for button_press_event
    @param event MouseEvent
    '''
    global ix
    ix = event.xdata

    for i, ax in enumerate([ax1, ax2, ax3, ax4, ax5]):
        # For infomation, print which axes the click was in
        if ax == event.inaxes:
            print "Click is in axes ax{}".format(i+1)

    # Check if the click was in ax4 or ax5
    if event.inaxes in [ax4, ax5]:
        if ix is not None:
            print 'x = %f' %(ix)

        ax4.clear()
        ax5.clear()
        ax4.grid(True)
        ax5.grid(True)
        [n4,bins4,patches] = ax4.hist(x01, bins=50, color = 'red',alpha = 0.5, normed = True)
        ax4.axvline(np.mean(x01), color = 'black', linestyle = 'dashed', lw = 2)
        xmin = ix
        xmax = ax4.get_xlim()[1]
        ax4.axvspan(xmin, xmax, facecolor='0.9', alpha=0.5)
        dx = bins4[1] - bins4[0]
        CDF = np.cumsum(n4)*dx
        ax5.plot(bins4[1:], CDF, color = 'red')
        ax5.axvspan(xmin, xmax, facecolor='0.9', alpha=0.5)
        plt.draw()
        return ix

    else:
        return
        
cid = fig.canvas.mpl_connect('button_press_event', onclick)
#fig.canvas.mpl_disconnect(cid)

plt.show()

#####_____#####