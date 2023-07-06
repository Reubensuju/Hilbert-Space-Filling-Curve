''' This file Deals with Transforming an D-dimensional dataset into a M-dimensional dataset where M <= D '''

import math
from random import*
from Hilbert_Mapping import*
import time
import numpy as np
from Sorting import quicksort
from copy import*
import decimal as decimal
import pandas as pd
from sklearn import decomposition
from sklearn.decomposition import PCA


'''This function computes the euclidean distance between 2 points'''
def euclid_dist(elem_1, elem_2):
    sqrsum = 0
    for i in range(len(elem_1)):        
        sqrsum += pow(elem_1[i] - elem_2[i], 2)
        
    return decimal.Decimal(sqrsum).sqrt()

def euclid_dist_2(elem_1, elem_2):
    sqrsum = 0
    for i in range(len(elem_1)):        
        sqrsum += pow(elem_1[i] - elem_2[i], 2)
        
    return decimal.Decimal(sqrsum)


'''This function swaps 2 given columns of the dataset
 This function does not alter the point given
--------------------------------------------------
 Input: point -> The dataset
         i -> first column
         j -> column according to the permutation (i to be swapped with j)'''
def swap(point, i, j):
    y = deepcopy(point)
    for d in range(len(y)):
        a = y[d][i]
        y[d][i] = y[d][j]
        y[d][j] = a
    return y[:,i]
    
    
'''For m different permutations of columns of dataset, this function along with swap() swaps the columns
 This function does not alter the point given'''
def toggle(data_swap, perm):
    # get NxD matrix for each permutation
    d = []
    d = np.zeros([len(data_swap),len(data_swap[0])],dtype=int)
    for a in range(len(data_swap[0])):
        d[:,a] = swap(data_swap,a,perm[a])
    return d
    
              
'''This function plots a given 2D dataset in a figure of a given name
 Note: Must use plt.show() after this function to view the plot
---------------------------------------------------------------
 Input: data -> the dataset to be plotted
        figure -> the name of the figure where the dataset will be plotted

 Output: None'''
def graph(data, figure,target):

    plt.figure(figure)

    length = len(data)

    data_x = [data[i][0] for i in range(length)]
    data_y = [data[i][1] for i in range(length)]

    xmax = float(max(data_x))
    xmin = float(min(data_x))
    ymax = float(max(data_y))
    ymin = float(min(data_y))

    axis = [min([xmin,ymin]), max([xmax, ymax])]
    plt.scatter(data_x, data_y,c=target)


'''Compute nth root of x'''
def root(x, n):
    if type(x) != decimal.Decimal:
        return pow(x,1.0/n)
    else:
        return pow(x,decimal.Decimal(1.0/n))


'''Compute natural logarithm'''
def ln(x):

    return math.log(x, math.exp(1))


'''Finds the minimum number by which a given number has to be multiplied
 to make it an integer
---------------------------------------------------------------------
 Input: x -> the number for which a factor is to be computed
 Output: the factor by which x has to be multiplied to obtain an integer'''
def find_fac(x):

    if type(x) is int or type(x) is long:
        return 1       

    string = str(x)
    #Convert the number to decimal notation if it's given in
    #scientific notation
    n = string.find("e")

    if n != -1:
        string = format(x,'f')

    length = len(string)

    index = string.find(".")

    #If all digits to the right of the decimal are Os, return 1
    flag = False
    for i in range(index + 1, length):
        if string[i] != "0":
            flag = True

    if flag == False:
        return 1

    return pow(10,length - index - 1)


'''This function Removes all duplicates from a given array
 Note: This function modifies the given array'''
def remove_duplicates(array):

    for elem in array:
        while array.count(elem) > 1:
            array.remove(elem)


'''This function scales given dataset by a given factor
 Note: This function modifies the given array
--------------------------------------------------
 Input: factor -> the factor that the dataset will be scaled
                  Note: if factor is None, the dataset will be scaled by 1000
        array -> the dataset to be scaled
        n -> dimension of the data

 Output: None'''
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


'''This function shifts a given datset towards the origin as much as possible

 Note: This function Modifies the given dataset
 --------------------------------------------------------------------------------
 Input: array -> dataset to be shifted
        n -> dimension of the given dataset

 Output: None'''
def ShifttoZero(array,n):

    length = len(array)
    if n == 1:
        minimum = array[0][0]
        for i in range(1,len(array)):
            if array[i][0] < minimum:
                minimum = array[i][0]
        for i in range(length):
            array[i][0] -= minimum
        return

    else:

        array2 = [[0 for i in range(length)]for j in range(n)] #2-D array that stores all the values of each coordinate
        mins = [0] * n #minimum  of each coordinate
        
        for i in range(length):
            for j in range(n):
                array2[j][i] = array[i][j]

        for i in range(n):
            mins[i] = min(array2[i])

    #Perform shifting according to the computed minima
    for i in range(len(mins)):
        if mins[i] == True:
            mins[i] = 1
        elif mins[i] == False:
            mins[i] = 0
    for i in range(length):
        for j in range(n):
            array[i][j] -= mins[j]


'''Find the minimal order of the Hilbert Curve to cover a given dataset
--------------------------------------------------------------------
 Input: data -> the dataset for which a Hilbert order is to be found
        n -> the dimension of the given data

 Output: The order of the Hilbert curve that covers the given dataset'''
def find_Hilbert_order(data,n):

    length = len(data)

    #Find the minimum area that covers the given data

    array2 = [[0 for i in range(length)]for j in range(n)] #2-D array that stores all the values of each coordinate

    maxs = [0] * n #maximum  of each coordinate

    for i in range(length):
        for j in range(n):
            array2[j][i] = data[i][j]

    for i in range(n):
        maxs[i] = max(array2[i])

    maximum  = max(maxs)
    Area = maximum ** n # Area / Volume to be covered by the Hilbert curve

    #Find the minimum order of Hilbert curve that covers the computed area
    return int(math.ceil((ln(root(Area, n) + 1)) / ln(2)))


'''Normalizes a given dataset to be between 0 and 1 using the maximmum of all axes
 Note: This function modifies the given dataset
-------------------------------------------------
 Input: data -> the dataset to be normalized

 Output: None'''
def Normalize(data):

    length = len(data)
    dim = len(data[0])
    coord_max = [0 for i in range(dim)] # max of each coordinate

    for i in range(length):
        for j in range(dim):
            x = data[i][j]
            if x > coord_max[j]:
                coord_max[j] = x

    factor = max(coord_max)

    for i in range(length):
        for j in range(dim):

            if coord_max[j] != 0:
                if type(data[i][j]) != decimal.Decimal and type(factor) != decimal.Decimal:
                    data[i][j] = 1.0* data[i][j] / factor
                else:
                    data[i][j] = data[i][j] / factor


'''This function reduces the dimension of a given dataset into lower or equal dimension
 using the Hilbert Curve mapping technique
 Note: This function modifies the given dataset
-------------------------------------------------------------------------------------
 Input: data -> the dataset to be reduced,
        order -> the hilbert order,
        m -> the dimension that the given dataset is to be reduced to

 Output: [process_time, data_new,optimal order]
   process_time : time taken to find the Hilbert mapping for the entire dataset
   data_new: the reduced dataset'''
def reduce_dataset(data, order, m):

    #If a numpy array is given, convert it to a list
    if type(data) != list:
        data= data.tolist()

    length = len(data)
        
    D = len(data[0]) #D : dimensions of the data given
    Normalize(data) #Make data between 0 and 1
    scale(None,data,D) #Scale data into all integers
    ShifttoZero(data,D) #Shift the data as close to the origin as possible
    N = len(data) # N: number of data points in the dataset
    data_new = [[0 for j in range(m)] for i in range(N)]
    max_order = find_Hilbert_order(data,D)   #the optimal order for this dataset
    
    # Define a lookup table of powers of 2 of length D * Order where index i contains 2^i
    Lookup = 2 ** np.arange(D * order, dtype=decimal.Decimal)

    for i in range(len(Lookup)):
        assert(Lookup[i] == pow(2,i))

    start = time.time() # Timing to check for processing time
    
    #compute different permuations of NxD; return a dict with 'D!' keys and NxD values
    perm = []
    np.random.seed(0)
    f = math.factorial(len(data[0]))
    if int(m)<=f:
        while len(perm)<int(m):
            a = np.random.permutation(len(data[0]))
            if tuple(a.tolist()) not in perm:
                perm.append(tuple(a.tolist()))
    
    data_perm ={}
    data = np.array(data)
    j = 0
    for p in range(len(perm)):
        data_perm[j] = np.array(toggle(data,perm[p]))  #OUTPUT -> 0:[1st permutation dataset],1:[2nd permutation dataset],....
        j+=1

    for v in range(len(data_perm)):
        for i in range(len(data)):
            data_new[i][v] = point2Hilbert(data_perm[v][i],order,Lookup)

    end = time.time()
    
    process_time = end-start
    return [process_time, data_new, max_order]


'''Reduces the Dimensions of a given dataset into a m-dimensional dataset
 This function performs shrinking of the transform space's coordinates
 Note: This function modifies the given dataset
----------------------------------------------------------------------
 Input: data -> the dataset to be reduced,
        order -> order of the dataset,
        m -> the dimension that the given dataset is to be reduced to

 Output: The reduced dataset, optimal order'''
def Hilbert_data_transform(data, order, m):

    data_copy = deepcopy(data)
    data_copy2 = deepcopy(data)
    original_data = deepcopy(data_copy) #O(n)

    if type(original_data) != list:
        original_data = original_data.tolist()
    
    # use previously defined Hilbert transform to reduce dimension of the dataset
    t,data_copy,max_order = reduce_dataset(data_copy, order, m) #O(n)
    
    #shift the coordinate of each transformed point such that the distnace
    # on each transformed coordinate is equal to the euclidean distance
    # between the points in the original space

    Transform2Original = [i for i in range(len(original_data))]
    Original2Transform = [i for i in range(len(original_data))]


    for i in range(m):

        #sort points in data based on current coordinate
        quicksort(data_copy, original_data,Transform2Original,0, len(original_data) - 1, i )

        for j in range(1,len(data_copy)):

            original_dist = euclid_dist(original_data[j], original_data[j - 1])

            if data_copy[j][i] - data_copy[j - 1][i] > original_dist:

                data_copy[j][i] = data_copy[j-1][i] + original_dist

            elif data_copy[j][i] - data_copy[j - 1][i] < original_dist:
                if j != len(data_copy) - 1: #if not at the last element
                    max_dist = data_copy[j][i] - data_copy[j+1][i] - 1 #max distance that can be moved
                                                                                                   # while still maintaining order
                    if max_dist < (data_copy[j-1][i] + original_dist - data_copy[j][i]): #max dist not sufficient
                        data_copy[j][i] += max_dist

                    else:
                        data_copy[j][i] += data_copy[j - 1][i] + original_dist - data_copy[j][i]


    new_data = [[0 for i in range(m)] for j in range(len(data))]
    for i in range(len(data)):
        new_data[Transform2Original[i]] = data_copy[i]

    print ("Transformation done!!!")
    
    D = len(new_data[0])
    scale(None,new_data,D)
    
    return new_data,max_order

