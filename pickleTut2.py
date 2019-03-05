import numpy as np
import matplotlib.pyplot as plt
import pickle as pl
import matplotlib
matplotlib.use("TkAgg")

output = file('sinus.pickle','rb')
fig_handle = pl.load(output)
output.close()
print(fig_handle.get_axes())
plt.show()