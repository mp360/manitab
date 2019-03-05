import numpy as np
import matplotlib.pyplot as plt
import pickle as pl
import matplotlib
matplotlib.use("TkAgg")

# Plot simple sinus function
fig_handle = plt.figure()
x = np.linspace(0,2*np.pi)
y = np.sin(x)
plt.plot(x,y)

# Save figure handle to disk
pl.dump(fig_handle,file('sinus.pickle','wb'))
plt.show()
plt.close()


def openFile():
    global dataFile
    global plotButton
    file1 = tkFileDialog.askopenfile(mode = 'rb', title = 'Choose a file')
    if file1 is None:
        return
    else:
        try:
            pd.read_csv(file1.name)
            data = pd.read_csv(file1.name, nrows = 1)
            vals = tuple(data)
            headerDropDown['values'] = vals
            headerDropDown.current(0)
            plotButton.config(state="normal")
        except Exception, e:
            tkMessageBox.showerror("Unknown File", "The file you provided is either not of type .csv. or is empty.")
            return
    dataFile = file1.name