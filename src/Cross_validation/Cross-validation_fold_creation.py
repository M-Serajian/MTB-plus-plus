#!/usr/bin/env python
import numpy as np
import sys
import pandas as pd


import argparse
parser = argparse.ArgumentParser(description="Process arguments")
parser.add_argument('-1', dest='arg1', type=str, required=True, help="Number of samples")
parser.add_argument('-2', dest='arg2', type=str, required=True, help="Number of Flods")
parser.add_argument('-3', dest='arg3', type=str, required=True, help="The directory to save these indexes")
args = parser.parse_args()

number_of_samples= int(args.arg1)
number_of_folds=args.arg2
saving_address=args.arg3


def main():
    
    index= np.arange(number_of_samples) # each sample or isolate has a unique address
    np.random.shuffle(index)

    # Calculate the approximate size of each fold
    folds_size = len(index) // number_of_folds
    # Divide the array into subarrays

    folds=[] # list of the folds

    for i in range(number_of_folds - 1):
        subarray = index[i * folds_size : (i + 1) * folds_size]
        folds.append(subarray)
    
    # Add the remaining elements to the last subarray
    folds.append(index[(number_of_folds - 1) * folds_size:])
    
    for i in range (number_of_folds):
        np.save(saving_address+"indexes_of_fold_{}.npy".\
            format(i),folds[i])
    

if __name__ == "__main__":
    main()