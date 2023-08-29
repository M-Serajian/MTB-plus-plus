#!/usr/bin/env python
import sys
import time
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
import numpy as np
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.metrics import f1_score, roc_auc_score, recall_score, accuracy_score
import numpy as np
import pickle




def get_non_nan_indices(array):
    non_nan_indices = []
    for i in range(len(array)):
        if not np.isnan(array[i]):
            non_nan_indices.append(i)
    return non_nan_indices


# Argument 1: drug name
# 
# Loading Targets
drug_name_group=sys.argv[1]
Top_kmers_address=sys.argv[2]
Results_address=sys.argv[3]
Cross_Validation=sys.argv[4]
train_index_address=sys.argv[5]
test_index_address=sys.argv[6]
model_address=sys.argv[7]
alpha_lasso_parameter=sys.argv[8]
RF_trees=sys.argv[9]


train_index=np.load(train_index_address)
test_index=np.load(test_index_address)

df=pd.read_csv("6224_Targets_NA_3_letters.csv")

print("Columns in the CSV file are:",flush=True)
print(df.columns,flush=True)

drug_names=['ERR', 'ID', 'ERS',"Amikacin",\
            "Bedaquiline", "Clofazimine",\
            "Delamanid","Ethambutol", "Ethionamide",\
            "Isoniazid", "Kanamycin","Levofloxacin",\
            "Linezolid","Moxifloxacin", "Rifampicin",\
            "Rifabutin","RIA","AMG","FQS"]




try:
  CSV_index = drug_names.index(drug_name_group)
except Exception as error:
  raise ValueError("Could not find the drug name; \
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
# 'RIF', 'RFB', 'RIFBB'='RIA', 'Ami_Kan'='AMG','Fluoroquinolone'='FQS']

drug_names_abbreviations=['ERR', 'ID', 'ERS',"AMI",\
            "BDQ", "CFZ",\
            "DLM","EMB", "ETH",\
            "INH", "KAN","LEV",\
            "LZD","MXF", "RIF",\
            "RFB","RIA","AMG","FQS"]


group=CSV_index 
print("Column number on CSV is {}".format(group),flush=True)
drug_name=drug_names[group]
drug_names_abbreviation=drug_names_abbreviations[group]

print("The drug is : {}".format(drug_name),flush=True)
target=np.array(df)
print("The shape of the target is:",flush=True)
print(np.shape(target),flush=True)
phenotype=target[:,group]


# Loading data
data=np.load(Top_kmers_address+ drug_name+ "/Classifer_data_524288.npy")
data=data[:,0:65536-1]
print("The data is loaded",flush=True)
print("The shape of the used data is:{}".format(np.shape(data)))

# loading clade
"""
clade=np.load("/blue/boucher/share/Deep_TB_Ali/Extracted_kmer_true_targets/Clade_counts.npy")

data=np.hstack((data,np.reshape(clade,(np.size(clade),1))))

print("Clade is added!")
print("The shape of the data is : {}".format(np.shape(data)))
"""

print("train data size is: {}\n".format(np.shape(train_index)),flush=True)
print("test data size is: {}\n".format(np.shape(test_index)),flush=True)


y_train=phenotype[train_index]
non_ambiguous_indecies_y_train=get_non_nan_indices(y_train)
train_index=train_index[non_ambiguous_indecies_y_train]
phenotype=target[:,group]
y_train=phenotype[train_index]
y_train=y_train.astype('int')

print("Number of R in train set is after ambiguity removal: {}".format(np.sum(y_train)),flush=True)
y_test =phenotype[test_index]
non_ambiguous_indecies_y_test=get_non_nan_indices(y_test)
test_index=test_index[non_ambiguous_indecies_y_test]
y_test =phenotype[test_index]
y_test=y_test.astype('int')


print("Number of R in test set is: {}".format(np.sum(y_test)),flush=True)
X_train=data[train_index,:]
X_test=data[test_index,:]



plt.axis("square")
plt.xlabel("False Positive Rate",fontsize=16)
plt.ylabel("True Positive Rate",fontsize=16)
#plt.title(drug_names_abbreviation,fontsize=22)

header_csv=["Model", "Kmers used","AUC(%)","mean_f1(%)","std_f1(%)","mean_recall(%)","mean_accuracy","mean_sensitivity","mean_specificity"]

csv_file=[]
base=2 # 1 kmers, base kmers, base^2 kmers, base^3 kmers , ...
list_kmers=[1* pow(base,i) for i in range(math.ceil(math.log(((np.size(X_train,1))/1),base)))]
#list_kmers.append(np.size(X_train,1))





color_counter=0
#Logistic Regression

LR=1
if (LR==1):
  for i in list_kmers :

    if ( 1000<i):
      model=LogisticRegression(penalty='l1', solver='liblinear', max_iter=2000,C=1/alpha_lasso_parameter)
      model_name="LR Lasso"
    else: 
      model=LogisticRegression(max_iter=2000)
      model_name="LR"
    
    print("{} model with {} Kmers".format(model_name,i),flush=True) 

    X_train_selected= X_train[:,0:i]
    #X_test_selected=X_test[:,0:i]
    

    # Generate some example data (replace this with your own dataset)


    # Perform 5-fold cross-validation with probability estimates
    num_folds = 5

    # Initialize lists to store metric scores for each fold
    auc_scores = []
    f1_scores = []
    recall_scores = []
    accuracy_scores = []
    sensitivity_scores = []
    specificity_scores = []

    for fold in range(num_folds):
        y_scores = cross_val_predict(model, X_train_selected, y_train, cv=num_folds, method='predict_proba')
        y_pred = np.argmax(y_scores, axis=1)
        
        # Calculate confusion matrix
        true_positives = np.sum((y_train == 1) & (y_pred == 1))
        true_negatives = np.sum((y_train == 0) & (y_pred == 0))
        false_positives = np.sum((y_train == 0) & (y_pred == 1))
        false_negatives = np.sum((y_train == 1) & (y_pred == 0))
        
        # Calculate metrics
        auc_scores.append(roc_auc_score(y_train, y_scores[:, 1]))
        f1_scores.append(f1_score(y_train, y_pred))
        recall_scores.append(recall_score(y_train, y_pred))
        accuracy_scores.append(accuracy_score(y_train, y_pred))
        sensitivity_scores.append(true_positives / (true_positives + false_negatives))
        specificity_scores.append(true_negatives / (true_negatives + false_positives))

    # Calculate mean and standard deviation for each metric
    mean_auc = np.mean(auc_scores)
    std_auc = np.std(auc_scores)
    mean_f1 = np.mean(f1_scores)
    std_f1 = np.std(100*f1_scores)
    mean_recall = np.mean(recall_scores)
    std_recall = np.std(recall_scores)
    mean_accuracy = np.mean(accuracy_scores)
    std_accuracy = np.std(accuracy_scores)
    mean_sensitivity = np.mean(sensitivity_scores)
    std_sensitivity = np.std(sensitivity_scores)
    mean_specificity = np.mean(specificity_scores)
    std_specificity = np.std(specificity_scores)



    csv_file.append([model_name, i, round(100*mean_auc,2),\
                    round(100*mean_f1,2), round(std_f1,4),\
                    round(100*mean_recall,2), round(100*mean_accuracy,2),\
                    round(100*mean_sensitivity,2),round(100*mean_specificity,2)])





# Random forest (RF)
RF=1

if (RF==1):
   
  for i in list_kmers :
    model_name="RF"
    print("{} model with {} Kmers".format(model_name,i),flush=True) 
    model = RandomForestClassifier(max_depth=10, random_state=10,n_estimators=RF_trees)

    X_train_selected= X_train[:,0:i]
    X_test_selected=X_test[:,0:i]
    
    # Perform 5-fold cross-validation with probability estimates
    num_folds = 5

    # Initialize lists to store metric scores for each fold
    auc_scores = []
    f1_scores = []
    recall_scores = []
    accuracy_scores = []
    sensitivity_scores = []
    specificity_scores = []

    for fold in range(num_folds):
        y_scores = cross_val_predict(model, X_train_selected, y_train, cv=num_folds, method='predict_proba')
        y_pred = np.argmax(y_scores, axis=1)
        
        # Calculate confusion matrix
        true_positives = np.sum((y_train == 1) & (y_pred == 1))
        true_negatives = np.sum((y_train == 0) & (y_pred == 0))
        false_positives = np.sum((y_train == 0) & (y_pred == 1))
        false_negatives = np.sum((y_train == 1) & (y_pred == 0))
        
        # Calculate metrics
        auc_scores.append(roc_auc_score(y_train, y_scores[:, 1]))
        f1_scores.append(f1_score(y_train, y_pred))
        recall_scores.append(recall_score(y_train, y_pred))
        accuracy_scores.append(accuracy_score(y_train, y_pred))
        sensitivity_scores.append(true_positives / (true_positives + false_negatives))
        specificity_scores.append(true_negatives / (true_negatives + false_positives))

    # Calculate mean and standard deviation for each metric
    mean_auc = np.mean(auc_scores)
    std_auc = np.std(auc_scores)
    mean_f1 = np.mean(f1_scores)
    std_f1 = np.std(100*f1_scores)
    mean_recall = np.mean(recall_scores)
    std_recall = np.std(recall_scores)
    mean_accuracy = np.mean(accuracy_scores)
    std_accuracy = np.std(accuracy_scores)
    mean_sensitivity = np.mean(sensitivity_scores)
    std_sensitivity = np.std(sensitivity_scores)
    mean_specificity = np.mean(specificity_scores)
    std_specificity = np.std(specificity_scores)



    csv_file.append([model_name, i, round(100*mean_auc,2),\
                round(100*mean_f1,2), round(std_f1,4),\
                round(100*mean_recall,2), round(100*mean_accuracy,2),\
                round(100*mean_sensitivity,2),round(100*mean_specificity,2)])




pd.DataFrame(csv_file).to_csv(Results_address+drug_names_abbreviation+\
                              '_CV{}.csv'.format(Cross_Validation), index_label = "MLs",\
                              header= header_csv)






   