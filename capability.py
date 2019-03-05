import projImports



def popupmsg(param, canvas):
    popup = tk.Tk()

    def leavemini():
        popup.destroy()

    popup.wm_title("!")
    # label = ttk.Label(popup, text = param, font = SMALL_FONT)
    # label.pack(sticky = "n", fill = "x", pady = 10)

    B1 = ttk.Button(popup, text = "Okay", command = leavemini)
    B1.grid(row=0, column=1)

    # B1.pack()
    # e2 = ttk.Entry(popup)

    # e2.pack()

    # e1 = Entry(param)
    # e2 = Entry(popup)

    # e1.grid(row=0, column=1)


    popup.mainloop()


    print(param)


myfunc("Hello", )