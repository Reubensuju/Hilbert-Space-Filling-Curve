'''Implementing quicksort algorithm which aims to sort some set of multi-dimensional points based on some coordinate while
   simultaneously maintain one-to-one correspondance between the dataset and 2 other given arrays'''


import sys
sys.setrecursionlimit(1500)

def swap(array, i1, i2):
    x = array[i1]
    array[i1] = array[i2]
    array[i2] = x

def quicksort(arr,arr2,arr3, i, j,k):

  if i < j:
    pos = partition(arr,arr2,arr3, i, j,k)
    quicksort(arr,arr2,arr3, i, pos - 1,k)
    quicksort(arr,arr2,arr3, pos + 1, j,k) 


def partition(arr,arr2,arr3, i, j,coord):
  pivot = arr[j][coord]
  small = i - 1
  for k in range(i, j):
    if arr[k][coord] <= pivot:
      small += 1
      swap(arr, k, small)
      swap(arr2, k, small)
      swap(arr3, k, small)

  swap(arr, j, small + 1)
  swap(arr2, j, small + 1)
  swap(arr3, j, small + 1)
  return small + 1
