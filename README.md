# MTB++
This is the software developed to predict antimicrobial resistance in MTB bacteria using machine learning for 13 groups of antibiotics including Amikacin, Bedaquiline, Clofazimine, Delamanid, Ethambutol, Ethionamide, Isoniazid, Kanamycin, Levofloxacin, Linezolid, Moxifloxacin, Rifampicin, Rifabutin; and 3 antibiotic families including Rifampin, Aminoglycosides, Fluoroquinolone.

This README contains instructions on how to run the trained classifier or to rebuild the classifier from raw data.  Rebuilding is an advanced use-case.  We expect most users to only run the trained classifier.   This software is maintained by Ali Serajian (ma.serajian@gmail.com).  Please post an Issue onto GitHub if there are any issues with these instructions.

## Installation ##

### Autimatic Installation ###

#### Dependencies ####

* python 3.0+ (3.6+ recommended)
    - sk-learn (Version 1.1.2) 
    - joblib
* [Cmake](https://cmake.org/)
*  GCC (9.3.3 recommended)

#### Installation Instructions ####

To simplify the installation process, the provided `setup.sh` script automates the setup by utilizing the "module load" environment. The script loads essential modules such as GCC and CMake (they need to be installed), compiles SBWT, and verifies the version of Scikit-learn. To use the script, follow these steps:

```bash
git clone https://github.com/M-Serajian/MTB-plus-plus.git
cd MTB-plus-plus
sh setup.sh
```

### Manual Installation ###

If the setup script is not applicable to your system (for example, if your system does not support the "module load" environment), follow these manual installation steps:

1. **Install Dependencies:**
    * CMake
    * Python 3+
        - sk-learn (Version 1.1.2) 
        - joblib
    * GCC (9.3.3 recommended)

```bash
git clone https://github.com/M-Serajian/MTB-plus-plus.git
cd MTB-plus-plus
```
2. **Compiling and Installing SBWT_Kmer_Counters:**
    Compile [SBWT_Kmer_Counters](https://github.com/M-Serajian/SBWT-kmer-counters) as follows:

```bash
git clone https://github.com/M-Serajian/MTB-plus-plus.git
cd MTB-plus-plus/src
git clone https://github.com/M-Serajian/SBWT-kmer-counters.git
cd SBWT-kmer-counters
git submodule update --init --recursive
cd SBWT/build
cmake ..
make -j
```

3. **Install Scikit-learn version 1.1.2:**
   ```bash
   pip3 install scikit-learn==1.1.2
   ```



# Usage
Mtb++.py can be located at the MTB-plus-plus directory (the root on the cloned directory).
 
```bash
python Mtb++.py -f FASTAfile -o Output.csv
```

# Example 
```bash
python Mtb++.py -f data/sample_genomes/ERR8665561.fasta -o ERR8665561.csv
```

### Citation ###
This software is under GNU license.  If you use the software please cite the following paper:   



## Classifying Data using MTB++ ##
Below are the instructions to use the classifier. Here, we assume that the data to be classified is available as a set of paired-end sequence reads.  In our example, we will have `reads1.fq` and `reads2.fq`

### Dependencies for training classifiers from scratch ###
* python 3.0+ (3.6+ recommended)
    ** sk-learn (Version 1.1.2) 
    ** joblib
* [Cmake](https://cmake.org/)
*  GCC (9.3.3 recommended)
* [SBWT_Kmer_counters](https://github.com/M-Serajian/SBWT-kmer-counters)
* [SPAdes](https://github.com/ablab/spades)
* [enaBrowserTools](https://github.com/M-Serajian/enaBrowserTools/blob/c9ed1a39510bb976079177f2726f0a0ec9cf1275/Projects.txt)

### Assemble the data into contigs ###
Use SPAdes to assemble the data
```bash
spades.py -r1 reads1.fastq -r2 reads2.fastq -o contigs.fa
```
### Classify the data using the models ###
Take the `contigs.fa` file to make a prediction using the models
```bash
run.py -i contigs.fa -o prediction.txt 
```


## Building the Classifier ##
Below are the instructions in order to rebuild the classifier and reproduce our results. If you would like to just use the trained classifier, see above.


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
These commands are also available in a script. The output should be `.npy` files that we will use in the next step.  See [ascii_to_feature.sh](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Ascii_to_Feature_Matrix).


### Feature selection. ### 

Create five folds of the data to be further used for Chi-squared test and classification.
```bash
./mypython.py somthing.npy > output
```

Next, we perform Chi-squared test to rank the features based on their significance [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Chi-Square-Kmer-Ranking).
 ```bash
./mypython.py somthing.npy > output
```
Lastly, we select the top features for each resistance class for training the classifiers [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Kmer_Select).
```bash
./mypython.py somthing.npy > output
```
### Train the Classifiers ### 
The last step is to train classifiers, both the Logistic Regression and Random Forest classifiers. [here](https://github.com/M-Serajian/MTB-plus-plus/tree/main/src/Classifier).
```bash
./mypython.py somthing.npy > output
```