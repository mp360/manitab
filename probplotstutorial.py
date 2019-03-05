import warnings
warnings.simplefilter('ignore')

import numpy
from matplotlib import pyplot
import seaborn

import probscale
clear_bkgd = {'axes.facecolor':'none', 'figure.facecolor':'none'}
seaborn.set(style='ticks', context='talk', color_codes=True, rc=clear_bkgd)

# load up some example data from the seaborn package
tips = seaborn.load_dataset("tips")
iris = seaborn.load_dataset("iris")

position, bill = probscale.plot_pos(tips['total_bill'])
position *= 100
fig, ax = pyplot.subplots(figsize=(6, 3))
ax.plot(position, bill, marker='.', linestyle='none', label='Bill amount')
ax.set_xlabel('Percentile')
ax.set_ylabel('Total Bill (USD)')
ax.set_yscale('log')
ax.set_ylim(bottom=1, top=100)
seaborn.despine()