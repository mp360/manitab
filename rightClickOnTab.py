import Tkinter as tk
import ttk

# --- functions ---

def on_click(event):
    print('widget:', event.widget)
    print('x:', event.x)
    print('y:', event.y)

    #selected = nb.identify(event.x, event.y)
    #print('selected:', selected) # it's not usefull

    clicked_tab = nb.tk.call(nb._w, "identify", "tab", event.x, event.y)
    print('clicked tab:', clicked_tab)

    active_tab = nb.index(nb.select())
    print(' active tab:', active_tab)

    if clicked_tab == active_tab:
        nb.forget(clicked_tab)

# --- main ---

root = tk.Tk()

# create notebook
nb = ttk.Notebook(root)
nb.pack(fill='both')

# bind function to notebook
nb.bind('<Button-3>', on_click)    

# add some tabs
for char in "ABCDEF":
    if char != 'A':

        nb.add(tk.Label(nb, text=(char*15)), text=char*3)
    else:
        x = tk.Label(nb, text=(char*15))
        nb.add(x, text=char*3)
        nb.hide(x)


root.mainloop()