import numpy as np
import matplotlib.pyplot as plt

def f(t):
    return np.exp(-t)*np.cos(2*np.pi*t)+(t/10)**2.

t1=np.arange(0.0,5.0,0.1)
t2=np.arange(0.0,5.0,0.02)

def plot(ax, i):
    ax.set_title('Jon Snow')
    kraft_plot,=ax.plot(t1,np.sin(t1),color='purple')
    tyrion=ax.axvline(2,color='darkgreen',ls='dashed')
    ax.set_ylabel('Kraft [N]',color='purple',fontweight='bold')
    ax.set_xlabel('Zeit [s]',fontweight='bold')
    ax2=ax.twinx()
    strecke_plot,=ax2.plot(t2,t2/5,color='grey',label='Verlauf der Strecke')
    ax2.set_ylabel('Strecke [mm]',color='grey',fontweight='bold')
    ax.legend((kraft_plot,tyrion,strecke_plot),('Jonny','Dwarf','andalltherest'),loc=2)

figures=[]

for i in range(2):
    fig= plt.figure(i)
    ax1=fig.add_subplot(111)
    plot(ax1, i)
    figures.append(fig)

# create third figure
fig, (ax1,ax2) = plt.subplots(nrows=2)
plot(ax1, 0)
plot(ax2, 1)
figures.append(fig)

from matplotlib.backends.backend_pdf import PdfPages
with PdfPages('multipage_pdf.pdf') as pdf:
    for fig in figures:
        pdf.savefig(fig)


plt.show()