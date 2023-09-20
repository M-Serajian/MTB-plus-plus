import argparse
import os
import subprocess
import numpy as np
import os
from src.resistance_predictor import resistance_predictor
import random
import string
import subprocess
import csv
# Global varible, drug names:

# Drug_number, orders 
drug_names=["Amikacin",\
            "Bedaquiline",\
            "Clofazimine",\
            "Delamanid",\
            "Ethambutol",\
            "Ethionamide",\
            "Isoniazid",\
            "Kanamycin",\
            "Levofloxacin",\
            "Linezolid",\
            "Moxifloxacin",\
            "Rifampicin",\
            "Rifabutin",\
            "RIA",\
            "AMG",\
            "FQS"]


def main():
    header= [" "]+drug_names
    LR_report=["Logistic Regression"]
    RF_report=["Random Forest"]
    parser = argparse.ArgumentParser(description="Mtb++ (Mycobacterium tuberculosis antimicrobial resistance detector)",usage="-f FASTAfile is required. The output is optional\n\
    By default, the output file is with the same name of input file in a .csv format unless specified!")
    
    parser.add_argument("-f", help="Input MTB assembled sequence or FASTA file (mandatory)", type=str)

    parser.add_argument("-o", help="The output file which will be .CSV (optional, default: input_file_name.csv)", type=str, default=None)
    
    args = parser.parse_args()
    
    # Ensure that input_file is provided
    if not args.f:
        parser.error("The input FASTA file is required!")
    
    # If output_file is not provided, set it to input_file + '.csv'
    if args.o is None:
        args.o = args.f + '.csv'
    
    input_file_address=args.f
    output_file_address=args.o
    # Define the characters that can be used in the random string
    characters = string.ascii_letters + string.digits
    # Generate a random 20-character string to be used as the name for temporary files during the processing
    prefix_temporary_files = ''.join(random.choice(characters) for _ in range(20))

    current_directory = os.getcwd()

    #Calculating the color matrix and parsing 
    #the Ascii code and doing the classification 
    #at the same time

    drug_number=0
    for drug in drug_names:
        address_to_kmer_counters_executable= "."+ os.path.join('/src',"SBWT-kmer-counters","counters") 
        SBWT_index="/home/m.serajian/projects/MTB-plus-plus/data/SBWT_indexes/{}.sbwt".format(drug)
        temporary_file="temp/"+prefix_temporary_files+"_"+drug+".txt"
        command= address_to_kmer_counters_executable+ " "+ SBWT_index + " " + input_file_address+">"+temporary_file
        subprocess.run(command, check=False, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        prediction=resistance_predictor.AMR_predictor(temporary_file,drug_number)
        LR_report.append(prediction[0])
        RF_report.append(prediction[1])
        os.remove(temporary_file)
    

        # Create and open the CSV file in write mode
    with open(output_file_address, mode='w', newline='') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)
        
        # Write the header row if needed (optional)
        # csv_writer.writerow(['Column1', 'Column2', 'Column3'])
        
        # Write each list as a row in the CSV file
        for row_data in zip(header, LR_report, RF_report):
            csv_writer.writerow(row_data)
    

    



if __name__ == "__main__":
    main()
