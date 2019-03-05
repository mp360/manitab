import os
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import Tkinter as tkinter# Tkinter -> tkinter in Python 3

class custom_plot(Figure):
    def __init__(self, *args, **kwargs):

        figtitle = kwargs.pop('figtitle', 'no title')
        super(custom_plot,self).__init__(*args, **kwargs)
        #Figure.__init__(self, *args, **kwargs)
        self.text(0.5, 0.95, figtitle, ha='center')
        self.popup_menu = tkinter.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Delete",
                                    command=self.delete_selected)
        self.popup_menu.add_command(label="Select All",
                                    command=self.select_all)
        self.bind("<Button-3>", self.popup) # Button-2 on Aqua

    def cplot(self,data):

        self.fig = plt
        fn = os.path.join(os.path.dirname(__file__), 'custom_plot.mplstyle')
        self.fig.style.use([fn])
        self.fig.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom='off',  # ticks along the bottom edge are off
            top='off',  # ticks along the top edge are off
            labelbottom='off')  # labels along the bottom edge are off
        self.fig.plot(data)
        
    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def delete_selected(self):
        # for i in self.curselection()[::-1]:
        #     self.delete(i)
        return

    def select_all(self):
        # self.selection_set(0, 'end')
        return
fig1 = plt.figure(FigureClass=custom_plot, figtitle='my title')
# fig1.cplot([1,2,3])
plt.show()