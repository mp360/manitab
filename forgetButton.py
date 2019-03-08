from Tkinter import *

def hide_me(event):
    event.widget.pack_forget()

root = Tk()
btn=Button(root, text="Click")
btn.bind('<Button-1>', hide_me)
btn.pack()
btn2=Button(root, text="Click too")
btn2.bind('<Button-1>', hide_me)
print(btn2["state"])
btn2.config(state=DISABLED)
btn2.pack()
root.mainloop()


# import sys
# import Tkinter as tk

# def toggle():
#     if mylabel.visible:
#         btnToggle["text"] = "Show Example"
#         print "Now you don't"
#         mylabel.place_forget()
#     else:
#         mylabel.place(mylabel.pi)
#         print "Now you see it"
#         btnToggle["text"] = "Hide Example"
#     mylabel.visible = not mylabel.visible

# root = tk.Tk()

# print "TkVersion", tk.TkVersion
# print "TclVersion", tk.TclVersion
# print "Python version", sys.version_info

# mylabel = tk.Label(text="Example")
# mylabel.visible = True
# mylabel.place(x=20, y=50)
# mylabel.pi = mylabel.place_info()

# btnToggle = tk.Button(text="Hide Example", command=toggle)
# btnToggle.place(x=70, y=150)

# root.mainloop()