# from scipy.stats import exponweib
# import matplotlib.pyplot as plt
# import numpy as np

# fig, ax = plt.subplots(1, 1)

# a, c = 2.89, 1.95
# mean, var, skew, kurt = exponweib.stats(a, c, moments='mvsk')


# x = np.linspace(exponweib.ppf(0.01, a, c),
#             exponweib.ppf(0.99, a, c), 100)
# ax.plot(x, exponweib.pdf(x, a, c),
#     'r-', lw=5, alpha=0.6, label='exponweib pdf')


# rv = exponweib(a, c)
# ax.plot(x, rv.pdf(x), 'k-', lw=2, label='frozen pdf')

# vals = exponweib.ppf([0.001, 0.5, 0.999], a, c)
# np.allclose([0.001, 0.5, 0.999], exponweib.cdf(vals, a, c))

# r = exponweib.rvs(a, c, size=1000)

# ax.hist(r, density=True, histtype='stepfilled', alpha=0.2)
# ax.legend(loc='best', frameon=False)
# plt.show()


# import scipy.stats as ss
# import matplotlib.pyplot as plt
# import numpy as np

# N=30
# counts, bins = np.histogram(x, bins=N)
# bin_width = bins[1]-bins[0]
# total_count = float(sum(counts))

# f, ax = plt.subplots(1, 1)
# f.suptitle(query_uri)

# ax.bar(bins[:-1]+bin_width/2., counts, align='center', width=.85*bin_width)
# ax.grid('on')
# def fit_pdf(x, name='lognorm', color='r'):
#     dist = getattr(ss, name)  # params = shape, loc, scale
#     # dist = ss.gamma  # 3 params

#     params = dist.fit(x, loc=0)  # 1-day lag minimum for shipping
#     y = dist.pdf(bins, *params)*total_count*bin_width
#     sqerror_sum = np.log(sum(ci*(yi - ci)**2. for (ci, yi) in zip(counts, y)))
#     ax.plot(bins, y, color, lw=3, alpha=0.6, label='%s   err=%3.2f' % (name, sqerror_sum))
#     return y

# colors = ['r-', 'g-', 'r:', 'g:']

# for name, color in zip(['exponweib', 't', 'gamma'], colors): # 'lognorm', 'erlang', 'chi2', 'weibull_min', 
#     y = fit_pdf(x, name=name, color=color)

# ax.legend(loc='best', frameon=False)
# plt.show()


import itertools
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

xdata=np.array([1e-8,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,3,3,4,4,4,5,4,4,5,5,6,6,6,6,7,7,8,8,8,9,9,10,11,12,13,13,14,14,13,17,14,15,17,18,18,19,22,23,22,23,24,26,28,32,33,32,31,33,34,37,36,40,40,41,44,41,44,45,47,52,53,51,52,52,53,55,56,59,61,62,65,63,68,69,80,71,71,72,71,69,70,70,71,72,73,75,74,74,75,76,74,79,77,77,77,84,92,88,79,81,81,83,84,88,87,84,84,85,85,85,94,95,91,89,90,87,89,89,90,93,92,93,96,95,98,99,100,99,100,98,94,89,87,86,85,85,84,85,83,83,84,83,81,85,83,83,81,84,93,91,78,79,80,80,80,80,80,78,79,78,79,80,78,78,78,78,79,77,77,77,78,80,82,83,82,80,82,82,83,87,82,82,80,80,79,77,77,77,77,75,75,73,71,73,73,70,72,69,70,70,78,81,69,68,68,68,65,64,66,65,64,62,62,62,62,67,65,61,61,59,58,59,59,59,59,59,59,59,59,59,59,59,58,56,55,52,50,50,48,48,47,46,46,45,44,44,43,43,43,41,41,41,46,47,40,39,39,38,37,37,38,36,35,35,35,35,36,35,33,33,32,31,31,31,29,29,28,28,28,28,30,30,30,28,27,26,25,23,22,23,22,21,20,19,19,18,18,18,17,17,17,14,14,13,13,14,13,12,12,11,11,10,10,9,9,9,8,8,8,8,7,7,7,7,7,7,6,6,6,6,6,6,6,6,6,6,5,5,5,5,5,5,5,5,5,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2])

# xdata=np.array([1e-8,120,120,120,120,120,120,120,120,120,120,120,120,120,120,120,120,120,120,120,120,60,60,60,60,60,60,2,2,3,3,3,3,3,3,4,4,4,5,4,4,5,5,120,120,120,120,7,7,8,8,8,9,9,10,11,12,13,13,14,14,13,17,14,15,17,18,18,19,22,23,22,23,24,26,28,32,33,32,31,33,34,37,36,40,40,41,44,41,44,45,47,52,53,51,52,52,53,55,56,59,61,62,65,63,68,69,80,71,71,72,71,69,70,70,71,72,73,75,74,74,75,76,74,79,77,77,77,84,92,88,79,81,81,83,84,88,87,84,84,85,85,85,94,95,91,89,90,87,89,89,90,93,92,93,96,95,98,99,100,99,100,98,94,89,87,86,85,85,84,85,83,83,84,83,81,85,83,83,81,84,93,91,78,79,80,80,80,80,80,78,79,78,79,80,78,78,78,78,79,77,77,77,78,80,82,83,82,80,82,82,83,87,82,82,80,80,79,77,77,77,77,75,75,73,71,73,73,70,72,69,70,70,78,81,69,68,68,68,65,64,66,65,64,62,62,62,62,67,65,61,61,59,58,59,59,59,59,59,59,59,59,59,59,59,58,56,55,52,50,50,48,48,47,46,46,45,44,44,43,43,43,41,41,41,46,47,40,39,39,38,37,37,38,36,35,35,35,35,36,35,33,33,32,31,31,31,29,29,28,28,28,28,30,30,30,28,27,26,25,23,22,23,22,21,20,19,19,18,18,18,17,17,17,14,14,13,13,14,13,12,12,11,11,10,10,9,9,9,8,8,8,8,7,7,7,7,7,7,120,120,120,120,120,120,120,120,120,120,5,5,5,5,5,5,5,5,5,5,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,2,2,3,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,2,2,2])
# stats.exponweib.fit(xdata, floc=0, f0=1)
# stats.weibull_min.fit(xdata, floc=0)
p0, p1, p2=stats.weibull_min.fit(xdata, floc=0)
ydata=stats.weibull_min.pdf(np.linspace(0, 120, 100), p0, p1, p2)
plt.hist(xdata, 25, normed=True)
plt.plot(np.linspace(0, 120, 100), ydata, '-')

# x2data=list(itertools.chain(*[[i,]*int(val) for i, val in enumerate(xdata)]))
# p0, p1, p2=stats.weibull_min.fit(x2data, floc=0)

# print(p0)
# print(p1)



# y2data=stats.weibull_min.pdf(np.linspace(0, 500, 100), p0, p1, p2)
# plt.plot(np.linspace(0, 500, 100), y2data, '-')
# r1,r2,r3=plt.hist(x2data, bins=60, normed=True)

plt.show()
# import numpy as np
# import matplotlib.pyplot as plt

# np.random.seed(19680801)

# fig, ax = plt.subplots()
# x = 30*np.random.randn(10000)
# mu = x.mean()
# median = np.median(x)
# sigma = x.std()
# textstr = '\n'.join((
#     r'$\mu=%.2f$' % (mu, ),
#     r'$\mathrm{median}=%.2f$' % (median, ),
#     r'$\sigma=%.2f$' % (sigma, )))

# ax.hist(x, 50)
# # these are matplotlib.patch.Patch properties
# props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

# # place a text box in upper left in axes coords
# ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
#         verticalalignment='top', bbox=props)

# plt.show()