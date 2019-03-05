
# import csv
import pandas as pd
import Tkinter as tk, tkFileDialog
# import Tkinter as tk, tkFileDialog

# print range(1,101) # printing numbers from 1 to 100.
# outerMatrix = []

for i in range(4,101):
    innerMatrix = [0,0,0,0]
    rowCounter = 1
    for j in range(0,4):
        innerMatrix[j] = i * rowCounter - (i- j) 
        rowCounter += 1
    outerMatrix.append(innerMatrix)
print(outerMatrix)
print(i)

# def openFile():
#     file1 = tkFileDialog.askopenfile(mode = 'rb', title = 'Choose a file')
#     if file1 is None:
#         return
#     else:
#         try:
#             pd.read_csv(file1.name)
#             data = pd.read_csv(file1.name)
#             print data
#             vals = tuple(data)
#             print vals
#             # headerDropDown['values'] = vals
#             # headerDropDown.current(0)
#             # plotButton.config(state="normal")
#         except Exception, e:
#             tkMessageBox.showerror("Unknown File", "The file you provided is either not of type .csv. or is empty.")
#             return

# openFile()