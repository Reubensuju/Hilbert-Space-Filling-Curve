''' Projection of a given D-dimensional point into a Hilbert curve of
specific Dimension and order
'''
import matplotlib.pyplot as plt
from random import*
import numpy as np
from numpy import array
import matplotlib.patches as mpatches
import time
from bitstring import BitArray
from copy import deepcopy
import decimal as decimal
import math


#Computes the length the n-dimensional Hilbert curve of order p
#-------------------------------------------------------------
# Input: n -> the dimension of the Hilbert Curve
#        p -> the order of the Hilbert Curve
#
# Output: The length of the given Hilbert Curve
def scale(factor, array, n):

# scale each value by 1000
    if (factor == None):
        for i in range(len(array)):
            for j in range(n):
                array[i][j] = int(array[i][j]*1000)
    else:

        factor = 1
        
        for point in array:
            for elem in point:
                if type(elem) is float:
                    k = find_fac(str(elem)) # k: Factor needed to make elem an integer
                    if k > factor:
                        factor = k
        if n == 1:

            for i in range(len(array)):
                array[i] *= factor
                array[i] = int(array[i])

        else:
            for i in range(len(array)):
                for j in range(n):
                    array[i][j] *= factor
                    array[i][j] = int(array[i][j])

def HilbertLength(n, p):

    return pow(pow(2,n),p) - 1


#This function Converts a binary array to decimal
#------------------------------------------------
# Input: BitArray -> The binary representation (as an array of bits) of the number to be converted to decimal
#        Lookup -> Table of the powers of 2 created in "Hilbert_transform" function
#
# Output: The integer represented by the given binary sequence
def bin2dec(BitArray, Lookup):
    
    return np.sum(Lookup[[(len(BitArray) - 1) - np.array(np.where(BitArray == 1))]])

# This function converts the binnary array returned by the function "point2Hilbert" into an integer
#-----------------------------------------------------------------------------------------
# Input: X -> the array returned by the function "point2Hilbert"
#        Order -> the Order of the Hilbert curve to be used
#        Lookup -> lookup table of the powers of 2 created in "Hilbert_transform" function
#
# Output: The Hilbert index of the given array
def Convert2Index(X, Order, Lookup):

    D = len(X) # D: Dimension of the point
                                                                                 
    BitArray = np.zeros(D * Order, dtype=np.int8)

    k = 0

    range1 = range(Order - 1, -1, -1)
    range2 = range(0, D)
    
    for j in range1:
        for i in range2:

            BitArray[k] = (X[i] >> j) & 1
            k += 1
            
    return bin2dec(BitArray, Lookup)
                                                                                
# This function maps a given point into a hilbert index
#
#
# From : "programming the Hilbert Curve" by John Skilling
# -------------------------------------------------------
# Input: point -> The point to be mapped into a Hilbert index
#        Order -> The order of the Hilbert Curve to be used in the mapping
#        Lookup -> lookup table of the powers of 2 created in "Hilbert_transform" function,
#                  which can be found in the file "Hilbert_transform.py"
#
# Output: The Hilbert index for the given point
#
def point2Hilbert(point, Order, Lookup):

    X = point[:]
    D = len(X) # D: Dimension of the given point
    M = 1 << (Order - 1)
    P = 0
    Q = M
    t = 0
    
    while Q > 1:

        P = Q - 1

        for i in range(D):

            if X[i] & Q != 0:
                X[0] ^= P
            else:

                t = (X[0] ^ X[i]) & P
                X[0] ^= t
                X[i] ^= t

        Q >>= 1

    for i in range(1,D):
        X[i] ^= X[i-1]
        
    t = 0

    Q = M
    
    while Q > 1:

        if(X[D-1] & Q) != 0:
            t ^= Q - 1
            
        Q >>= 1

    for i in range(D):

        X[i] ^= t
        
    return Convert2Index(X,Order, Lookup)

def root(x, n):
    if type(x) != decimal.Decimal:
        return pow(x,1.0/n)
    else:
        return pow(x,decimal.Decimal(1.0/n))

def ln(x):

    return math.log(x, math.exp(1))
    
def find_Hilbert_order(data,n):
    length = len(data)
    array2 = [[0 for i in range(length)]for j in range(n)] #2-D array that stores all the values of each coordinate

    maxs = [0] * n #maximum  of each coordinate

    for i in range(length):
        for j in range(n):
            array2[j][i] = data[i][j]

    for i in range(n):
        maxs[i] = max(array2[i])

    maximum  = max(maxs)
    Area = maximum ** n
    return int(math.ceil((ln(root(Area, n) + 1)) / ln(2)))

#def Hilbert_map_plot(dataset,y,fig_name):
#
#    D = len(dataset[0]) #D : dimensions of the data given
#    scale(None,dataset,D)
#    order = find_Hilbert_order(dataset,D)
#    Lookup = 2 ** np.arange(D * order, dtype=decimal.Decimal)
#    for i in range(len(Lookup)):
#        assert(Lookup[i] == pow(2,i))
#
#    #Build Rank array
#    length = len(dataset)
#
#    Rank = [0] * length
#
#    for i in range(length):
#        
#        Rank[i] = point2Hilbert(dataset[i], order, Lookup)
