# Programs

This folder contains all scripts from this project. 
This folder also contains a folder with all the data 
files that are needed to run these scripts.

### Deliverable 1  
This deliverable parses a bed file and creates a 
dictionary that contains the bed file data.

Usage:
> python3 deliverable1.py

### Deliverable 2
This script parses and filters the pileup data form a pileup 
file and creates a coverage dictionary

Usage:
> python3 deliverable2.py

### Deliverable 3
This script reads a bed file, a pileup file and a 
coverage dictionary to calculate the coverage and writes 
this to a output file.

Usage:
> python3 deliverable3.py

### Deliverable 4
This script is the combination of deliverable 1, 2 and 3.  
When run this script parses a bed file and the pileup file,
creates a coverage dictionary and writes the coverage 
dictionary to an output file.

Usage:
> python3 deliverable4.py bed_file pileup_file

### Deliverable 5
This script reads a vcf file, checks each line if the 
frequency is above the threshold if this is true 
the line will be writen to the output vcf file.

Usage:
> python3 deliverable5.py vcf_file min_frequency vcf_output_file

### Deliverable 6
This script parses an ANNOVAR file and creates a list where 
each entery is a line of the ANNOVAR file as a dictionary.

Usage:
> python3 delivarable6.py

### Deliverable 7
This script reads the raw gene_names colomn from the ANNOVAR 
file and reformat's the name so only the gene name remains.

Usage:
> python3 deliverable7.py

### Deliverable 8
This file contains the code to create the database tables 
we need to fill in deliverable 9.  

This file creates three tables:
- chromosomes
- genes
- variants

Usage:  
> mysql -u user -h host -D database - p < deliverable8.sql  

or

>  mysqlsh -u user -h host -D database - p < deliverable8.sql

### Deliverable 9
This script will connect to your database and add the data 
from a ANNOVAR file to the database.

Usage:
> python3 deliverable9.py [-s sql_file] username password hostname database_name annovar_file