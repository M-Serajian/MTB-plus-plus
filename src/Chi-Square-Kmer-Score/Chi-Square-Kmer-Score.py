#!/usr/bin/env python
import time
import numpy as np
from scipy.stats import chi2_contingency
import pandas as pd
import sys
import copy



import argparse
parser = argparse.ArgumentParser(description="Process arguments")
parser.add_argument('-1', dest='arg1', type=str, required=True, help="file_number")
parser.add_argument('-2', dest='arg2', type=str, required=True, help="Drug name")
parser.add_argument('-3', dest='arg3', type=str, required=True, help="Number of samples (fasta files)")
parser.add_argument('-4', dest='arg4', type=str, required=True, help="Address to the Kmers stored")
parser.add_argument('-5', dest='arg5', type=str, required=True, help="Desierd directory for the outputs")
parser.add_argument('-6', dest='arg6', type=str, required=True, help="Address to the index of cross-validation")
parser.add_argument('-7', dest='arg7', type=str, required=True, help="The address to the phenotypes")
parser.add_argument('-8', dest='arg8', type=str, required=True, help="Number of cross-validation folds (5 in our study!)")
parser.add_argument('-9', dest='arg9', type=str, required=True, help="Which fold of cross-validation (which fold to be validation and the rest are training) (from zero to 4 for 5 fold cross-validation)")
args = parser.parse_args()


i=str(args.arg1) #file number, we considered 12 files
drug_name_group=args.arg2
Number_of_samples=int(args.arg3)
Kmers_address=args.arg4
Chi_score_addresses_for_each_drug=args.arg5
Cross_validation_indexes_address=args.arg6
The_address_to_phenotypes=args.arg7
Cross_validation_folds=args.arg8
Cross_validation_index=args.arg9

df=pd.read_csv(The_address_to_phenotypes)
# Separating test and train data
# Chi-Score should only be performed on the train data

def get_non_nan_indices(array):
    non_nan_indices = []
    for i in range(len(array)):
        if not np.isnan(array[i]):
            non_nan_indices.append(i)
    return non_nan_indices


#--------------------------------------------------#
list_indexes=[]
#Loading the index of each fold into the list_indexes list
for i in range (Cross_validation_folds):
   list_indexes.append(np.load(\
      Cross_validation_indexes_address+\
      "indexes_of_fold_{}.npy".format(i)))

#Choosing the Cross_validation_index in the list_indexes as validation or test set
test_index =list_indexes[Cross_validation_index]

list_indexes.pop[Cross_validation_index]

#considering the rest of folds in index_list as training set
train_index= np.concatenate(list_indexes)


# Loading Targets
print("Columns in the CSV file are:")
print(df.columns,flush=True)


# Which drug? See below
drug_names=['ERR', 'ID', 'ERS',"Amikacin", "Bedaquiline", \
            "Clofazimine","Delamanid","Ethambutol", "Ethionamide",\
            "Isoniazid","Kanamycin","Levofloxacin","Linezolid",\
            "Moxifloxacin", "Rifampicin","Rifabutin",\
            "RIA","AMG","FQS"]




try:
  CSV_index = drug_names.index(drug_name_group)
except Exception as error:
  raise ValueError("Could not find the drug name; \n \
                   The drug names are: \n \
                   Amikacin ,\n \
                   Bedaquiline ,\n \
                   Clofazimine,\n \
                   Delamanid ,\n \
                   Ethambutol ,\n \
                   Ethionamide ,\n \
                   Isoniazid ,\n \
                   Kanamycin ,\n \
                   Levofloxacin ,\n \
                   Linezolid ,\n \
                   Moxifloxacin ,\n \
                   Rifampicin ,\n \
                   Rifabutin ,\n \
                   RIA ,\n \
                   AMG ,\n \
                   FQS ")

print("Drug Found!",flush=True)

# Columns of the target file are: 
#IDX:0      1     2      3      4      5      6
# ['ERR', 'ID', 'ERS', 'AMI', 'BDQ', 'CFZ', 'DLM',
# 'EMB', 'ETH', 'INH','KAN', 'LEV', 'LZD', 'MXF',
# 'RIF', 'RFB', 'RIFBB', 'Ami_Kan','Fluoroquinolone']
   

group=CSV_index 
print("Column on CSV is {}".format(group),flush=True)
drug_name=drug_names[group]
target=np.array(df)

phenotype=target[:,group]
phenotype=phenotype[train_index] # Separating the train set

non_ambiguous_indecies=get_non_nan_indices(phenotype)


non_ambiguous_train_indecies=train_index[non_ambiguous_indecies]

phenotype=target[:,group] # recreating the phynotype to just use the non_ambiguous_train_indecies on them
phenotype=phenotype[non_ambiguous_train_indecies]
phenotype=phenotype.astype('int')


print("The shape of Targets (after removing ambiguous phenotypes) used in Chi_Square is:",flush=True)
print(np.shape(phenotype),flush=True)




# Base address for the data (all the Kmers generated by SBWT)
base_address=Kmers_address



file_name="counts_file"+i+".npy"


print(drug_name+" is being checked",flush=True)

print("---------------------------- file {} ---------------------------------------".format(i),flush=True)

data=np.load(base_address+file_name)
print("The total data shape is {}".format(np.shape(data)),flush=True)
#important Kmers are the rows and samples are the columns


print("Train data size with ambiguous phenotypes is: {}\n".format(np.shape(train_index)),flush=True)


print("Train data size without ambiguous phenotypes is: {}\n".format(np.shape(non_ambiguous_train_indecies)),flush=True)



train_data=data[:,non_ambiguous_train_indecies] # The color matrix generated by SBWT (rows are kmers and columns are strands)

counter=0
chi_score=[] #list of chi score

# Chi-square test
for j in range (np.size(train_data,0)): # Kmers are in the rows
    row=train_data[j,:]  
    contigency_pct = pd.crosstab(row,phenotype)
    chi, _, _, _ = chi2_contingency((contigency_pct))
    chi_score.append(chi)

chi_score=np.array(chi_score)

np.save(Chi_score_addresses_for_each_drug +drug_name+\
        "/chi_score_file"+i+"_fold_number_{}.npy".format(Cross_validation_index),chi_score)

print("The output chi square array's size is : {}".\
      format(np.shape(chi_score)))

print("----------------------------  Finished  ----------------------------")
