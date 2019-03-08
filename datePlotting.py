datelist =  ['2014-05-06', '2014-05-07', '2014-05-08', '2014-05-09', '2014-05-10',    '2014-05-11', '2014-05-12', '2014-05-13']

import matplotlib
from matplotlib import pyplot
from matplotlib import dates
import datetime

converted_dates = map(datetime.datetime.strptime, datelist, len(datelist)*['%Y-%m-%d'])
x_axis = (converted_dates)
formatter = dates.DateFormatter('%Y-%m-%d')


y_axis = range(0,8)
pyplot.plot( x_axis, y_axis, '-' )
ax = pyplot.gcf().axes[0]
ax.xaxis.set_major_formatter(formatter)
pyplot.gcf().autofmt_xdate(rotation=25)
pyplot.show()