import Tkinter as tk
import ttk

root = tk.Tk()

mygray = "#555555"
mygreen = "#d2ffd2"
MED_FONT = ("Verdana", 10)

style = ttk.Style()


style.theme_create( "yummy", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
        "TNotebook.Tab": {
            "configure": {"padding": [5, 1], "background": mygray, "font": MED_FONT},
            "map":       {"background": [("selected", mygreen)],
                          "expand": [("selected", [0, 0, 0, 0])] } } } )

style.theme_use("yummy")

note = ttk.Notebook(root)
f1 = ttk.Frame(note, width=300, height=200)
note.add(f1, text = 'First')
f2 = ttk.Frame(note, width=300, height=200)
note.add(f2, text = 'Second')
note.pack(expand=1, fill='both', padx=5, pady=5)

tk.Button(root, text='yummy!').pack(fill='x')

root.mainloop()


# Style().configure("TNotebook", background=myTabBarColor)
# Style().map("TNotebook.Tab", background=[("selected", myActiveTabBackgroundColor)], foreground=[("selected", myActiveTabForegroundColor)])
# Style().configure("TNotebook.Tab", background=myTabBackgroundColor, foreground=myTabForegroundColor)