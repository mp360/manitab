import scipy.stats as ss
import matplotlib.pyplot as plt

nsample=500
c = 1.79
#create list of random variables
x=ss.weibull_min.rvs(c, size=nsample)

weibull = ss.weibull_min(c)
# Calculate quantiles and least-square-fit curve
(quantiles, values), (slope, intercept, r) = ss.probplot(x, dist=weibull)
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.set_xscale("log", nonposx='clip')

#plot results

plt.plot(values, quantiles,'ob')
plt.plot(quantiles * slope + intercept, quantiles, 'r')

#define ticks
ticks_perc=[1, 5, 10, 20, 50, 80, 90, 95, 99, 99.9]

#transfrom them from precentile to cumulative density
ticks_quan=[ss.weibull_min.ppf(i/100., c) for i in ticks_perc]

#assign new ticks
plt.yticks(ticks_quan,ticks_perc)

#show plot
plt.grid(False)
plt.show()