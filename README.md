# MTB-plus-plus
This is the software developed to predict antimicrobial resistance (AMR) in MTB bacteria using machine learning for 13 groups of antibiotics including Amikacin, Bedaquiline, Clofazimine, Delamanid, Ethambutol, Ethionamide, Isoniazid, Kanamycin, Levofloxacin, Linezolid, Moxifloxacin, Rifampicin, Rifabutin; and 3 antibiotic families including Rifampin(RIA), Aminoglycosides(AMG), Fluoroquinolone(FQS).
### Build ###
#### Dependencies ####
* [SPAdes] (https://github.com/ablab/spades)
* [enaBrowserTools] ((https://github.com/M-Serajian/enaBrowserTools/blob/
c9ed1a39510bb976079177f2726f0a0ec9cf1275/Projects.txt))
* python 3.0+
* sk-learn


## Building the Classifier ##
Below are the instructions in order to rebuild the classifier and reproduce our results. If you would like to just use the trained classifier, see above.

### Install SBWT ### 
```bash
docker pull sbwt
```

### Download the raw data ###
The first step is to download the FASTQ data, using European Nucleotide Archive (ENA) Browser Tools.

### Assemble the data into contigs ###
Use spades to assemble the data
```bash
spades.py -r1 reads1.fastq -r2 reads2.fastq
```
### Extract and match phenotypic data ### 
Extract the phenotypes from the ENA data and match the identifier numbers [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Extract%20Phenotypes)

```bash
command line here
```

### Create feature matrix ### 
The first step is to extract the k-mers using the SBWT.  The `fasta_filenames.txt` is a list with all the names of the fasta files.  
```bash
./sbwt build --in-file fasta_filenames.txt -k 31 -o index.sbwt -t 8 -m 10 --temp-dir temp
./counters index.sbwt fasta_filenames.txt > index_file.txt
```

From the above command, you should have an index file outputted from SBWT (`index_file.txt`).  Next, we transform this index file to a feature matrix that can be used for training.
```bash
Npy_files_address="/blue/boucher/share/Deep_TB_Ali/Final_TB/NPY_Binary_Files_with_index/"
Number_of_Samples=6224
Number_of_kmers_in_file=30000000
min_filter_kmers_occurring_less_than=10 # Less than 10 times occurance, the kmer will be ignored
max_filter_kmers_occurring_more_than=3000

mkdir -p $Npy_files_address

python projects/MTB-plus-plus/src/Ascii_to_Feature_Matrix/Ascii_to_Matrix.py $file_number $Number_of_Samples \
          $Color_matrix_address $Npy_files_address\
          $Number_of_kmers_in_file \
          $min_filter_kmers_occurring_less_than\
          $max_filter_kmers_occurring_more_than
```
These commands are also available in a script. See [ascii_to_feature.sh](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Ascii_to_Feature_Matrix).


### Feature selection. ### 

Create five folds of the data to be further used for Chi-squared test and classification [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Cross_validation)

Next, we perform Chi-squared test to rank the features based on their significance [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Chi-Square-Kmer-Ranking).
 
Lastly, we select the top features for each resistance class for training the classifiers [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Kmer_Select).

### Train the Classifiers ### 

The last step is to train classifiers, both the Logistic Regression and Random Forest classifiers. [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Classifier).
