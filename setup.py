import sys
from cx_Freeze import setup, Executable
additionals = ['numpy.core._methods', 'numpy.lib.format', 'scipy.sparse.csgraph._validation']
setup(name = 'MoneyTab',
    version = '0.1',
    description = 'MoneyTab',
    options = {'build_exe': {'includes': additionals}},
    executables = [Executable("NormHistoGrapher.py", base = "Win32GUI")])