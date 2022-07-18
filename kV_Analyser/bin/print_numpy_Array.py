# Analyses Lynx images from the kV Obliques and Orthogonal X-Rays on the ProteusONE
# Required:
#           baseline.npy - baseline values stored in a numpy array file
#           opg files of the lynx images stored in the path specified below
#
# 29.03.2021 Jamil Lambert


import numpy as np
import sys

try:
    if len(sys.argv) != 2 :
        print('Invalid input arguments, example usage: python print_numpy_array.py fileName')
    numpyFile = sys.argv[1]  # Numpy array file to print 
    tempList = np.load(numpyFile)
    numpyList = tempList.tolist()
    for line in numpyList:
        print(line)
except:
    print('Failed to open file')