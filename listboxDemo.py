
import Tkinter
from Tkinter import *
import ttk

class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        # self.dora = DoraExplorer()

        self.currentDict = {}
        self.lbox_list = []
        self.prevIndex =''
        self.pack()
        self.create_widgets()

    def populateTreeView(self,tabDict):
        header = tabDict['header']
        data = tabDict['data']
        self.tree["columns"] = header
        self.tree['show'] = 'headings'
        self.tree.delete(*self.tree.get_children())

        for head in header:
            self.tree.column(head, width=10, anchor='c')
            self.tree.heading(head, text=head)
        #print(data)
        for j in range(len(data)):
            row = list(data[j])
            self.tree.insert("",'end',text=str(j),values=row)

    def queryAction(self):
        #self.frame.delete('1.0',END)
        d = self.dbVar.get()
        t = self.tableVar
        cf = self.query.get()
        queryResults = self.dora.runQueries(cf,d,t)

        queryText = queryResults['text']
        label = queryText['label']
        title = queryText['title']


        self.populateTreeView(queryResults['table'])
    def create_widgets(self):

        self.query = StringVar()
        # self.createDBMenu()
        self.search_var = StringVar()
        # self.search_var.trace("w", self.update_list)
        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.lbox = Listbox(self, width=45, height=15,yscrollcommand=self.scrollbar.set)
        # self.lbox.bind('<<ListboxSelect>>',self.onselect)
        self.lbox.grid(row=4, column=1,rowspan=9, padx=10, pady=3)

        self.entry = Entry(self, textvariable=self.search_var, width=40)
        self.entry.grid(row=3, column=1, padx=10, pady=3)

        self.cRadio = Radiobutton(self,text='Count',variable=self.query,value ='countTop',indicatoron=0)
        self.cRadio.grid(row=13,column=1)

        self.fRadio = Radiobutton(self,text='Foreign',variable=self.query,value ='foreignKeys',indicatoron=0)
        self.fRadio.grid(row=14,column=1)

        self.queryButton = Button(self, text="Query", command=self.queryAction)
        self.queryButton.grid(row=9,column=2,padx=3,pady=.05)

        self.treeFrame = Frame(self,width = 300, height = 400)
        self.treeFrame.grid(row=4, column=3,columnspan=3,rowspan=9, padx=10, pady=3)
        self.treeFrame.columnconfigure(3,weight=1)

        self.tree = ttk.Treeview(self.treeFrame, selectmode='browse')
        self.tree.grid(row=1, column=0, sticky=NSEW,in_=self.treeFrame, columnspan=3, rowspan=9)
        self.tree.grid_propagate(False)
        self.scbHDirSel =Scrollbar(self.treeFrame, orient=HORIZONTAL, command=self.tree.xview)
        self.scbVDirSel =Scrollbar(self.treeFrame, orient=VERTICAL, command=self.tree.yview)
        self.scbVDirSel.grid(row=1, column=50, rowspan=50, sticky=NS, in_=self.treeFrame)
        self.scbHDirSel.grid(row=52, column=0, rowspan=2,columnspan=3, sticky=EW,in_=self.treeFrame)
        self.tree.configure(yscrollcommand=self.scbVDirSel.set, xscrollcommand=self.scbHDirSel.set) 


        # container1 = self.parent
        # container = ttk.Frame(container1)
        # # create a treeview with dual scrollbars
        # B1 = ttk.Button(container, text="Okay", command=self.dostuff)
        # B1.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        # self.tree = ttk.Treeview(container1, columns=self.headers, show="headings")
        # vsb = ttk.Scrollbar(container1, orient="vertical", command=self.tree.yview)
        # hsb = ttk.Scrollbar(container1, orient="horizontal", command=self.tree.xview)
        # self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        # self.tree.grid(column=0, row=0, sticky='nsew', in_=container1)
        # vsb.grid(column=1, row=0, sticky='ns', in_=container1)
        # hsb.grid(column=0, row=1, sticky='ew', in_=container1)
        
        # container.grid_columnconfigure(0, weight=1)
        # container.grid_rowconfigure(0, weight=1)
root = Tk()

root.title("Tk dropdown example")

app= Application(master=root)
app.mainloop()