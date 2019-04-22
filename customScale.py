import numpy as np
from numpy import ma
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import Formatter, FixedLocator
from matplotlib import rcParams
import scipy.stats as ss
from matplotlib.figure import Figure

# BUG: this example fails with any other setting of axisbelow
# rcParams['axes.axisbelow'] = True


globalBeta = 0.0
globalEta = 0.0
globalMu = 0.0
globalSigma = 0.0

class MercatorLatitudeScale(mscale.ScaleBase):
    """
    Scales data in range -pi/2 to pi/2 (-90 to 90 degrees) using
    the system used to scale latitudes in a Mercator projection.

    The scale function:
      ln(tan(y) + sec(y))

    The inverse scale function:
      atan(sinh(y))

    Since the Mercator scale tends to infinity at +/- 90 degrees,
    there is user-defined threshold, above and below which nothing
    will be plotted.  This defaults to +/- 85 degrees.

    source:
    http://en.wikipedia.org/wiki/Mercator_projection
    """

    # The scale class must have a member ``name`` that defines the
    # string used to select the scale.  For example,
    # ``gca().set_yscale("mercator")`` would be used to select this
    # scale.
    name = 'mercator'

    # def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
    def __init__(self, axis, thresh=1, *args, **kwargs):

        """
        Any keyword arguments passed to ``set_xscale`` and
        ``set_yscale`` will be passed along to the scale's
        constructor.

        thresh: The degree above which to crop the data.
        """
        mscale.ScaleBase.__init__(self)
        if thresh > 1:
            raise ValueError("thresh must be less than pi/2")
        self.thresh = thresh

    def get_transform(self):
        """
        Override this method to return a new instance that does the
        actual transformation of the data.

        The MercatorLatitudeTransform class is defined below as a
        nested class of this one.
        """
        return self.MercatorLatitudeTransform(self.thresh)

    def set_default_locators_and_formatters(self, axis):
        """
        Override to set up the locators and formatters to use with the
        scale.  This is only required if the scale requires custom
        locators and formatters.  Writing custom locators and
        formatters is rather outside the scope of this example, but
        there are many helpful examples in ``ticker.py``.

        In our case, the Mercator example uses a fixed locator from
        -90 to 90 degrees and a custom formatter class to put convert
        the radians to degrees and put a degree symbol after the
        value::
        """
        class DegreeFormatter(Formatter):
            def __call__(self, x, pos=None):
                return "%g" % (x * 100)

        # axis.set_major_locator(FixedLocator(
        #     np.radians(np.arange(-90, 90, 10))))

        axis.set_major_locator(FixedLocator(
            np.array(list(np.arange(.01, .10, .01)) + list(np.arange(.10, .99, .10)) + [.99]) ))
        axis.set_major_formatter(DegreeFormatter())
        axis.set_minor_formatter(DegreeFormatter())

    def limit_range_for_scale(self, vmin, vmax, minpos):
        """
        Override to limit the bounds of the axis to the domain of the
        transform.  In the case of Mercator, the bounds should be
        limited to the threshold that was passed in.  Unlike the
        autoscaling provided by the tick locators, this range limiting
        will always be adhered to, whether the axis range is set
        manually, determined automatically or changed through panning
        and zooming.
        """
        print('run')
        print(vmin)
        print(vmax)
        return max(vmin, -self.thresh), min(vmax, self.thresh)

    class MercatorLatitudeTransform(mtransforms.Transform):
        # There are two value members that must be defined.
        # ``input_dims`` and ``output_dims`` specify number of input
        # dimensions and output dimensions to the transformation.
        # These are used by the transformation framework to do some
        # error checking and prevent incompatible transformations from
        # being connected together.  When defining transforms for a
        # scale, which are, by definition, separable and have only one
        # dimension, these members should always be set to 1.
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True

        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh

        def transform_non_affine(self, a):
            global globalMu
            global globalSigma
            """
            This transform takes an Nx1 ``numpy`` array and returns a
            transformed copy.  Since the range of the Mercator scale
            is limited by the user-specified threshold, the input
            array must be masked to contain only valid values.
            ``matplotlib`` will handle masked arrays and remove the
            out-of-range data from the plot.  Importantly, the
            ``transform`` method *must* return an array that is the
            same shape as the input array, since these values need to
            remain synchronized with values in the other dimension.
            """
            x = np.linspace(-5, 5, 5000)
            stdev = 1
            mean = 0
            print(a)
            masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
            if masked.mask.any():
                # return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
                print('masked')
                # return np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in masked])
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                return ss.norm.ppf(masked, globalMu, globalSigma)
            else:   
                # return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))
                # return  np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in a])
                print('masked1')
                # return np.array([np.log(np.log(1/(1- xi))) for xi in masked])
                return ss.norm.ppf(a, globalMu, globalSigma)

        def inverted(self):
            """
            Override this method so matplotlib knows how to get the
            inverse transform for this transform.
            """
            return MercatorLatitudeScale.InvertedMercatorLatitudeTransform(
                self.thresh)

    class InvertedMercatorLatitudeTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True
        has_inverse = True


        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh

        def transform_non_affine(self, a):

            global globalMu
            global globalSigma
            # return np.array([1 + (-1*(np.exp(np.exp( (1-np.exp(-1*((xi/p2)**p0))) )))**(-1) ) for xi in a])
            # return np.arctan(np.sinh(a))
            # return np.array([1 + (-1*(np.exp(np.exp(xi)))**(-1) ) for xi in a])
            return ss.norm.cdf(a, globalMu, globalSigma)

        def inverted(self):
            return MercatorLatitudeScale.MercatorLatitudeTransform(self.thresh)

# Now that the Scale class has been defined, it must be registered so
# that ``matplotlib`` can find it.
mscale.register_scale(MercatorLatitudeScale)


if __name__ == '__main__':
    global globalBeta
    global globalEta
    global globalMu
    global globalSigma

    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # FOR WEIBILL
    x = (1037,1429,680,291,1577,90,1090,142,1297,1113,1153,150,837,890,269,468,1476,827,519,1100,1307,1360,919,373,563,978,650,362,383,272)
    x = (0,1,4,7,10,6,14,18,5,12,23,10,3,3,7,3,26,1,2,25,29,29,29,28,2,3,12,32,34,36,29,37,9,16,41,3,6,3,9,18,49,35,17,3,59,2,5,2,1,1,5,9,10,13,3,1,18,17,2,17,22,25,25,25,6,6,2,26,38,22,4,24,41,41,1,44,2,45,2,46,49,50,4,54,38,59)
    # x = (5,16,16,17,28,30,39,39,43,45,51,53,58,61,66,68,68,72,72,77,78,80,81,90,96,100,109,110,131,153,165,180,186,188,207,219,265,285,285,308,334,340,342,370,397,445,482,515,545,583,596,630,670,675,733,841,852,915,941,979,995,1032,1141,1321,1386,1407,1571,1586,1799)

    # sortedX = sorted(x)
    # p0, p1, p2 = ss.weibull_min.fit(x, floc=0)

    # medianRanks = []
    # print('medranks')
    # for i,v in enumerate(sortedX):
    #     print(i)
    #     medianRanks += [(i + 1 - 0.3)/(len(x) + 0.4)]
    # print(medianRanks)

    # ax.grid(True, which = 'both')
    # ax.plot(sortedX, medianRanks, 'ob')
    # ax.plot(sortedX, [1-np.exp(-1*((xi /p2)**p0)) for xi in sortedX], color = '#8B0000', lw = 1.0)

    # ax.set_yscale('mercator')
    # ax.set_xscale('log')
    # ax.set_axisbelow(True)

    # x = np.linspace(-5, 5, 5000)
    sortedX = sorted(x)
    mu, sigma = ss.norm.fit(x)
    globalMu = mu
    globalSigma = sigma
    medianRanks = []

    print('medranks')
    for i,v in enumerate(sortedX):
        print(i)
        medianRanks += [(i + 1 - 0.3)/(len(x) + 0.4)]
    print(medianRanks)
    y_cdf = ss.norm.cdf(sortedX, mu, sigma) # the normal cdf
    print y_cdf

    ax.grid(True, which = 'both')
    ax.plot(sortedX, medianRanks, 'ob')

    ax.plot(sortedX, y_cdf, label='cdf', lw = 1.0)
    ax.set_yscale('mercator')
    ax.set_axisbelow(True)

    plt.show()


####################_____________________#####################___________________###################
# class MercatorLatitudeScale(mscale.ScaleBase):
#     """
#     Scales data in range -pi/2 to pi/2 (-90 to 90 degrees) using
#     the system used to scale latitudes in a Mercator projection.

#     The scale function:
#       ln(tan(y) + sec(y))

#     The inverse scale function:
#       atan(sinh(y))

#     Since the Mercator scale tends to infinity at +/- 90 degrees,
#     there is user-defined threshold, above and below which nothing
#     will be plotted.  This defaults to +/- 85 degrees.

#     source:
#     http://en.wikipedia.org/wiki/Mercator_projection
#     """

#     # The scale class must have a member ``name`` that defines the
#     # string used to select the scale.  For example,
#     # ``gca().set_yscale("mercator")`` would be used to select this
#     # scale.
#     name = 'mercator'

#     # def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
#     def __init__(self, axis, thresh=1, *args, **kwargs):

#         """
#         Any keyword arguments passed to ``set_xscale`` and
#         ``set_yscale`` will be passed along to the scale's
#         constructor.

#         thresh: The degree above which to crop the data.
#         """
#         mscale.ScaleBase.__init__(self)
#         if thresh > 1:
#             raise ValueError("thresh must be less than pi/2")
#         self.thresh = thresh

#     def get_transform(self):
#         """
#         Override this method to return a new instance that does the
#         actual transformation of the data.

#         The MercatorLatitudeTransform class is defined below as a
#         nested class of this one.
#         """
#         return self.MercatorLatitudeTransform(self.thresh)

#     def set_default_locators_and_formatters(self, axis):
#         """
#         Override to set up the locators and formatters to use with the
#         scale.  This is only required if the scale requires custom
#         locators and formatters.  Writing custom locators and
#         formatters is rather outside the scope of this example, but
#         there are many helpful examples in ``ticker.py``.

#         In our case, the Mercator example uses a fixed locator from
#         -90 to 90 degrees and a custom formatter class to put convert
#         the radians to degrees and put a degree symbol after the
#         value::
#         """
#         class DegreeFormatter(Formatter):
#             def __call__(self, x, pos=None):
#                 print(x)
#                 return "%g" % (x * 100)

#         # axis.set_major_locator(FixedLocator(
#         #     np.radians(np.arange(-90, 90, 10))))

#         axis.set_major_locator(FixedLocator(
#             np.array(list(np.arange(.01, .10, .01)) + list(np.arange(.10, .99, .10)) + [.99]) ))
#         axis.set_major_formatter(DegreeFormatter())
#         axis.set_minor_formatter(DegreeFormatter())

#     def limit_range_for_scale(self, vmin, vmax, minpos):
#         """
#         Override to limit the bounds of the axis to the domain of the
#         transform.  In the case of Mercator, the bounds should be
#         limited to the threshold that was passed in.  Unlike the
#         autoscaling provided by the tick locators, this range limiting
#         will always be adhered to, whether the axis range is set
#         manually, determined automatically or changed through panning
#         and zooming.
#         """
#         return max(vmin, -self.thresh), min(vmax, self.thresh)

#     class MercatorLatitudeTransform(mtransforms.Transform):
#         # There are two value members that must be defined.
#         # ``input_dims`` and ``output_dims`` specify number of input
#         # dimensions and output dimensions to the transformation.
#         # These are used by the transformation framework to do some
#         # error checking and prevent incompatible transformations from
#         # being connected together.  When defining transforms for a
#         # scale, which are, by definition, separable and have only one
#         # dimension, these members should always be set to 1.
#         input_dims = 1
#         output_dims = 1
#         is_separable = True
#         has_inverse = True

#         def __init__(self, thresh):
#             mtransforms.Transform.__init__(self)
#             self.thresh = thresh

#         def transform_non_affine(self, a):
#             global globalBeta
#             global globalEta

#             """
#             This transform takes an Nx1 ``numpy`` array and returns a
#             transformed copy.  Since the range of the Mercator scale
#             is limited by the user-specified threshold, the input
#             array must be masked to contain only valid values.
#             ``matplotlib`` will handle masked arrays and remove the
#             out-of-range data from the plot.  Importantly, the
#             ``transform`` method *must* return an array that is the
#             same shape as the input array, since these values need to
#             remain synchronized with values in the other dimension.
#             """
#             p0 = globalBeta
#             p2 = globalEta
#             print('__')
#             print(a)
#             print(globalBeta)
#             masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
#             if masked.mask.any():
#                 # return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
#                 print('masked')
#                 # return np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in masked])
#                 return np.array([np.log(np.log(1/(1- xi ))) for xi in masked])

#             else:
#                 # return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))
#                 # return  np.array([np.log(np.log(1/(1- (1-np.exp(-1*((xi/p2)**p0))) ))) for xi in a])
#                 return np.array([np.log(np.log(1/(1- xi ))) for xi in masked])

#         def inverted(self):
#             """
#             Override this method so matplotlib knows how to get the
#             inverse transform for this transform.
#             """
#             return MercatorLatitudeScale.InvertedMercatorLatitudeTransform(
#                 self.thresh)

#     class InvertedMercatorLatitudeTransform(mtransforms.Transform):
#         input_dims = 1
#         output_dims = 1
#         is_separable = True
#         has_inverse = True

#         def __init__(self, thresh):
#             mtransforms.Transform.__init__(self)
#             self.thresh = thresh

#         def transform_non_affine(self, a):
#             global globalBeta
#             global globalEta
#             p0 = globalBeta
#             p2 = globalEta
#             # return np.array([1 + (-1*(np.exp(np.exp( (1-np.exp(-1*((xi/p2)**p0))) )))**(-1) ) for xi in a])
#             # return np.arctan(np.sinh(a))
#             return np.array([1 + (-1*(np.exp(np.exp( xi )))**(-1) ) for xi in a])

#         def inverted(self):
#             return MercatorLatitudeScale.MercatorLatitudeTransform(self.thresh)

# # Now that the Scale class has been defined, it must be registered so
# # that ``matplotlib`` can find it.
# mscale.register_scale(MercatorLatitudeScale)


# if __name__ == '__main__':
#     global globalBeta
#     global globalEta

#     import matplotlib.pyplot as plt

#     # t = np.arange(-180.0, 180.0, 0.1)
#     # s = np.radians(t)/2.
#     x = (1037,1429,680,291,1577,90,1090,142,1297,1113,1153,150,837,890,269,468,1476,827,519,1100,1307,1360,919,373,563,978,650,362,383,272)
#     x = (0,1,4,7,10,6,14,18,5,12,23,10,3,3,7,3,26,1,2,25,29,29,29,28,2,3,12,32,34,36,29,37,9,16,41,3,6,3,9,18,49,35,17,3,59,2,5,2,1,1,5,9,10,13,3,1,18,17,2,17,22,25,25,25,6,6,2,26,38,22,4,24,41,41,1,44,2,45,2,46,49,50,4,54,38,59)
#     x = (5,16,16,17,28,30,39,39,43,45,51,53,58,61,66,68,68,72,72,77,78,80,81,90,96,100,109,110,131,153,165,180,186,188,207,219,265,285,285,308,334,340,342,370,397,445,482,515,545,583,596,630,670,675,733,841,852,915,941,979,995,1032,1141,1321,1386,1407,1571,1586,1799)

#     sortedX = sorted(x)
#     p0, p1, p2 = ss.weibull_min.fit(x, floc=0)
    
#     globalBeta = p0
#     globalEta = p2

#     medianRanks = []
#     print('medranks')
#     for i,v in enumerate(sortedX):
#         print(i)
#         medianRanks += [(i + 1 - 0.3)/(len(x) + 0.4)]
#     print(medianRanks)

#     # plt.plot(t, s, '-', lw=2)
#     plt.grid(True, which = 'both')
#     plt.plot(sortedX, medianRanks, 'ob')
#     plt.plot(sortedX, [1-np.exp(-1*((xi /p2)**p0)) for xi in sortedX], color = '#8B0000', lw = 1.0)

#     plt.gca().set_yscale('mercator')
#     plt.gca().set_xscale('log')
#     plt.gca().set_axisbelow(True)

#     plt.xlabel('Longitude')
#     plt.ylabel('Latitude')
#     plt.title('Mercator: Projection of the Oppressor')

#     plt.show()

####################_____________________#####################___________________###################
# import numpy as np
# from numpy import ma
# from matplotlib import scale as mscale
# from matplotlib import transforms as mtransforms
# from matplotlib.ticker import Formatter, FixedLocator
# from matplotlib import rcParams


# # BUG: this example fails with any other setting of axisbelow
# rcParams['axes.axisbelow'] = False


# class MercatorLatitudeScale(mscale.ScaleBase):
#     """
#     Scales data in range -pi/2 to pi/2 (-90 to 90 degrees) using
#     the system used to scale latitudes in a Mercator projection.

#     The scale function:
#       ln(tan(y) + sec(y))

#     The inverse scale function:
#       atan(sinh(y))

#     Since the Mercator scale tends to infinity at +/- 90 degrees,
#     there is user-defined threshold, above and below which nothing
#     will be plotted.  This defaults to +/- 85 degrees.

#     source:
#     http://en.wikipedia.org/wiki/Mercator_projection
#     """

#     # The scale class must have a member ``name`` that defines the
#     # string used to select the scale.  For example,
#     # ``gca().set_yscale("mercator")`` would be used to select this
#     # scale.
#     name = 'mercator'

#     def __init__(self, axis, thresh=np.deg2rad(85), *args, **kwargs):
#         """
#         Any keyword arguments passed to ``set_xscale`` and
#         ``set_yscale`` will be passed along to the scale's
#         constructor.

#         thresh: The degree above which to crop the data.
#         """
#         mscale.ScaleBase.__init__(self)
#         if thresh >= np.pi / 2:
#             raise ValueError("thresh must be less than pi/2")
#         self.thresh = thresh

#     def get_transform(self):
#         """
#         Override this method to return a new instance that does the
#         actual transformation of the data.

#         The MercatorLatitudeTransform class is defined below as a
#         nested class of this one.
#         """
#         return self.MercatorLatitudeTransform(self.thresh)

#     def set_default_locators_and_formatters(self, axis):
#         """
#         Override to set up the locators and formatters to use with the
#         scale.  This is only required if the scale requires custom
#         locators and formatters.  Writing custom locators and
#         formatters is rather outside the scope of this example, but
#         there are many helpful examples in ``ticker.py``.

#         In our case, the Mercator example uses a fixed locator from
#         -90 to 90 degrees and a custom formatter class to put convert
#         the radians to degrees and put a degree symbol after the
#         value::
#         """
#         class DegreeFormatter(Formatter):
#             def __call__(self, x, pos=None):
#                 print(x)
#                 print()
#                 return "%d\N{DEGREE SIGN}" % np.degrees(x)

#         axis.set_major_locator(FixedLocator(
#             np.radians(np.arange(-90, 90, 10))))
#         axis.set_major_formatter(DegreeFormatter())
#         axis.set_minor_formatter(DegreeFormatter())

#     def limit_range_for_scale(self, vmin, vmax, minpos):
#         """
#         Override to limit the bounds of the axis to the domain of the
#         transform.  In the case of Mercator, the bounds should be
#         limited to the threshold that was passed in.  Unlike the
#         autoscaling provided by the tick locators, this range limiting
#         will always be adhered to, whether the axis range is set
#         manually, determined automatically or changed through panning
#         and zooming.
#         """
#         return max(vmin, -self.thresh), min(vmax, self.thresh)

#     class MercatorLatitudeTransform(mtransforms.Transform):
#         # There are two value members that must be defined.
#         # ``input_dims`` and ``output_dims`` specify number of input
#         # dimensions and output dimensions to the transformation.
#         # These are used by the transformation framework to do some
#         # error checking and prevent incompatible transformations from
#         # being connected together.  When defining transforms for a
#         # scale, which are, by definition, separable and have only one
#         # dimension, these members should always be set to 1.
#         input_dims = 1
#         output_dims = 1
#         is_separable = True
#         has_inverse = True

#         def __init__(self, thresh):
#             mtransforms.Transform.__init__(self)
#             self.thresh = thresh

#         def transform_non_affine(self, a):
#             """
#             This transform takes an Nx1 ``numpy`` array and returns a
#             transformed copy.  Since the range of the Mercator scale
#             is limited by the user-specified threshold, the input
#             array must be masked to contain only valid values.
#             ``matplotlib`` will handle masked arrays and remove the
#             out-of-range data from the plot.  Importantly, the
#             ``transform`` method *must* return an array that is the
#             same shape as the input array, since these values need to
#             remain synchronized with values in the other dimension.
#             """
#             print('__')
#             print(a)
#             masked = ma.masked_where((a < -self.thresh) | (a > self.thresh), a)
#             if masked.mask.any():
#                 return ma.log(np.abs(ma.tan(masked) + 1.0 / ma.cos(masked)))
#             else:
#                 return np.log(np.abs(np.tan(a) + 1.0 / np.cos(a)))

#         def inverted(self):
#             """
#             Override this method so matplotlib knows how to get the
#             inverse transform for this transform.
#             """
#             return MercatorLatitudeScale.InvertedMercatorLatitudeTransform(
#                 self.thresh)

#     class InvertedMercatorLatitudeTransform(mtransforms.Transform):
#         input_dims = 1
#         output_dims = 1
#         is_separable = True
#         has_inverse = True

#         def __init__(self, thresh):
#             mtransforms.Transform.__init__(self)
#             self.thresh = thresh

#         def transform_non_affine(self, a):
#             return np.arctan(np.sinh(a))

#         def inverted(self):
#             return MercatorLatitudeScale.MercatorLatitudeTransform(self.thresh)

# # Now that the Scale class has been defined, it must be registered so
# # that ``matplotlib`` can find it.
# mscale.register_scale(MercatorLatitudeScale)


# if __name__ == '__main__':
#     import matplotlib.pyplot as plt

#     t = np.arange(-180.0, 180.0, 0.1)
#     s = np.radians(t)/2.

#     plt.plot(t, s, '-', lw=2)
#     plt.gca().set_yscale('mercator')

#     plt.xlabel('Longitude')
#     plt.ylabel('Latitude')
#     plt.title('Mercator: Projection of the Oppressor')
#     plt.grid(True)

#     plt.show()