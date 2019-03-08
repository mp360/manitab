import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.figure import Figure
prevPlotf = 0
prevPlota = 0
fillBetFigure = None
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.25)
t = np.arange(0.0, 1.0, 0.001)
a0 = 5
f0 = 3
s = a0*np.sin(2*np.pi*f0*t)
l, = plt.plot(t, s, lw=2, color='red')
plt.axis([0, 1, -10, 10])

axcolor = 'lightgoldenrodyellow'
axfreq = plt.axes([0.35, 0.15, 0.65, 0.03], facecolor=axcolor)
axamp = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor='r')

sfreq = Slider(axfreq, 'Freq', 0, 1.0, valinit=0.1)
samp = Slider(axamp, 'Amp', 0, 1.0, valinit=0.1, color = axcolor)


def update(val):
    global prevPlotf
    global prevPlota
    global fillBetFigure
    # sfreq.valinit = 0
    # sfreq.vline = axfreq.axvline(sfreq.val, 0, 1, color= 'r', lw = 1)
    # axfreq.axvspan(0, 3)
    # axfreq.axvline(sfreq.val, 0, 1, color= 'r', lw = 1)
    axfreq.clear()
    axamp.clear()

    sfreq.valmax = 1
    sfreq.valmin = 0
    # axfreq.set_yticks([])

    print(sfreq.valinit)
    print(sfreq.val)
    # axfreq.axvline(samp.val, 0, 1, color= 'r', lw = 2)
    # axamp.axvline(sfreq.val, 0, 1, color= 'b', lw = 2)
    # axamp.axvline(sfreq.val, 0, 1, color= 'b', lw = 1)
    if (sfreq.val > samp.val and sfreq.val != prevPlotf):
        axfreq.axvspan(0, samp.val, 0, 1)
        sfreq.val = samp.val
        axfreq.axvline(samp.val, 0, 1, color= 'r', lw = 2)
        axamp.axvspan(0, samp.val, 0, 1, facecolor=axcolor)

    elif (sfreq.val > samp.val and samp.val != prevPlota):
        axamp.axvspan(0, sfreq.val, 0, 1, facecolor=axcolor)
        samp.val = sfreq.val
        axamp.axvline(sfreq.val, 0, 1, color= 'b', lw = 2)
        axfreq.axvspan(0, sfreq.val, 0, 1)
    else:
        axfreq.axvspan(0, sfreq.val, 0, 1)
        axamp.axvspan(0, samp.val, 0, 1, facecolor=axcolor)
        axfreq.axvline(samp.val, 0, 1, color= 'r', lw = 2)
        axamp.axvline(sfreq.val, 0, 1, color= 'b', lw = 2)
    axfreq.margins(x = 0)
    axamp.margins(x = 0)
    axfreq.set_xlim(0, 1)
    axamp.set_xlim(0, 1)
    prevPlota = samp.val
    prevPlotf = sfreq.val
    amp = samp.val
    freq = sfreq.val
    l.set_ydata(amp*np.sin(2*np.pi*freq*t))
    if fillBetFigure is not None:
        fillBetFigure.remove()
    newT = np.arange(prevPlotf, prevPlota, 0.001)
    fillBetFigure = ax.fill_between(newT, 0, amp*np.sin(2*np.pi*freq*newT), facecolor = '#4B0082', alpha = 0.4)
    fig.canvas.draw_idle()

sfreq.on_changed(update)
samp.on_changed(update)

resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')


def reset(event):
    sfreq.reset()
    samp.reset()

button.on_clicked(reset)

rax = plt.axes([0.025, 0.5, 0.15, 0.15], facecolor=axcolor)
radio = RadioButtons(rax, ('red', 'blue', 'green'), active=0)


def colorfunc(label):
    l.set_color(label)
    fig.canvas.draw_idle()

radio.on_clicked(colorfunc)

plt.show()


# import matplotlib.pyplot as plt
# import matplotlib.widgets as mwidgets
# fig, ax = plt.subplots()
# ax.plot([1, 2, 3], [10, 50, 100])
# def onselect(vmin, vmax):
#     print(vmin, vmax)
# rectprops = dict(facecolor='blue', alpha=0.5)
# span = mwidgets.SpanSelector(ax, onselect, 'horizontal',
#     rectprops=rectprops)
# plt.show()

        # a.axhline(color = 'k')
        # a.axvline(color = 'k')
    # dataLink = 'https://btc-e.com/api/3/trades/btc_usd?limit=2000'
    # data = urllib.request.urlopen(dataLink)
    # data = data.readall().decode("utf-8")
    # data = json.loads(data)

    # data = data["btc_usd"]
    # data = pd.DataFrame(data)

    # buys = data[(data['type']=="bid")]
    # buys["datestamp"] = np.array(buys["timestamp"]).astype("datetime64[s]")
    # buyDates = (buys["datestamp"]).tolist()


    # sells = data[(data['type']=="ask")]
    # sells["datestamp"] = np.array(sells["timestamp"]).astype("datetime64[s]")
    # sellDates = (sells["datestamp"]).tolist()

    # a.clear()

    # a.plot_date(buyDates, buys["price"], "#00A3E0", label="buys")
    # a.plot_date(sellDates, sells["price"], "#183A54", label="sells")

    # a.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3,
    #          ncol=2, borderaxespad=0)

    # title = "BTC-e BTCUSD Prices\nLast Price: "+str(data["price"][1999])
    # a.set_title(title)