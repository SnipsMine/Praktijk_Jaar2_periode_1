#!/usr/bin/env python3

"""
BFV2 Theme 05 - Genomics - Sequencing Project

Script for a program performing the following steps:
----------------------------------------------------------
* Load the BED file containing the information (names, chromosome and
  coordinates of the exons) of all cardiopanel genes
* Load the pileup file containing the mapping data
* For each exon found in the BED file:
    * read the start- and end-coordinate
    * find all entries in the pileup file for this chromosome and within
      these coordinates
    * for each pileup-entry:
        * store the coverage (data from column 4)
* Given the found coverage for each position in all exons:
    * Calculate the average coverage per gene
    * Count the number of positions with a coverage < 30
* Write a report on all findings (output to Excel-like file)

Deliverable 4
-------------
    usage:
        python3 deliverable4.py [bed-file.bed] [pileup-file.pileup]
"""

# METADATA VARIABLES
__author__ = "Micha Beens, Nadia Choudhury"
__status__ = "Finished"
__version__ = "2019.d4.v1"

# IMPORT
import sys
import csv


# FUNCTIONS
def read_data(filename):
    """ This function reads in data and returns a list containing one
        line per element. """

    # Open the file given the filename stored in 'filename'
    with open(filename) as file_data:
        data = [line.strip() for line in file_data]
    # Return a list where each line is a list element
    return data


def parse_bed_data(bed_data):
    """ Function that parses BED data and stores its contents
    in a dictionary
    """
    # Create empty dictionary to hold the data
    bed_dict = {}

    # Iterate over all lines in the 'bed_data' list and fill the
    # `bed_dict` dictionary with the `chromosome` as key. The other fields
    # are added as a tuple using the correct types.
    # Check the `expected_bed_dict` output example in the `main` function below.
    for line in bed_data:
        line = line.split()
        chrome = line[0]
        start = int(line[1])
        stop = int(line[2])
        nuc = line[3]

        if chrome in bed_dict:
            bed_dict[chrome].append((start, stop, nuc))
        else:
            bed_dict[chrome] = [(start, stop, nuc)]

        # Return the bed_dict one all lines are done
    return bed_dict


def parse_pileup_data(pileup_data, bed_dict):
    """ Function that parses pileup data and collects the per-base coverage
    of all exons contained in the BED data.

    Iterate over all pileup lines and for each line:
        - check if the position falls within an exon (from `bed_dict`)
            - if so; add the coverage to the `coverage_dict` for the correct gene
    """

    # Create empty dictionary to hold the data
    coverage_dict = {}

    counter = 0
    comp_list = [int(len(pileup_data)/50*i) for i in range(50)]
    print("Progress")

    # Iterate over all the lines contained in the pileup_data
    for line in pileup_data:
        if counter in comp_list:
            print("-", end="")

        counter += 1

        line = line.split('\t')
        # Extract the 'chromosome' field and remove the 'chr' text
        chrom = line[0].replace('chr', '')
        pos = line[1]
        cov = line[3]
        # Check if the chromosome is contained in the bed_dict
        if chrom in bed_dict:
            # If yes; extract the coordinate from the pileup and compare to all
            #         exons for that chromosome in the `bed_dict`
            #         If the position falls within an exon, add the coverage
            #         value to the list for the gene in the `coverage_dict`
            for tup in bed_dict[chrom]:
                gen = tup[2]
                start = tup[0]
                end = tup[1]
                if start <= int(pos) < end:
                    if gen in coverage_dict.keys():
                        coverage_dict[gen].append(int(cov))
                    else:
                        coverage_dict[gen] = [int(cov)]

    # Return coverage dictionary
    print()
    return coverage_dict


def mean(values):
    """
    Calculates the mean value of the given values
    :param values: A list with ints/floats
    :return: the average value of values
    """
    average = sum(values)/len(values)
    return average


def save_coverage_statistics(coverage_file, coverage_statistics):
    """ Writes coverage data to a tabular file using Python's
        csv library: https://docs.python.org/3/library/csv.html#csv.writer
    """

    # Write the coverage_statistics to a CSV file
    with open(coverage_file, 'w') as output:

        writer = csv.writer(output, delimiter="\t")
        for stat in coverage_statistics:
            writer.writerow(stat)


def calculate_mapping_coverage(coverage_dict):
    """ Function to calculate all coverage statistics on a per-gene basis
        and store this in a list.
        Note: this function is taken from deliverable 5 and slightly modified
    """

    # Create an empty list that will hold all data to save
    statistics = []

    # Iterate over all the genes in the coverage_dict getting the gene name
    # and list with coverage data for that gene
    for gene in coverage_dict:
        # Put the following elements in a single tuple and append to the
        # statistics list.
        #      * Gene name,
        #      * Total positions (gene length covered)
        #      * Average Coverage (use round with one position)
        #      * Number of low-coverage positions (coverage value < 30)
        name = gene
        total_pos = len(coverage_dict[gene])
        avg_cov = round(mean(coverage_dict[gene]), 1)
        num_of_low_cov = sum([coverage < 30 for coverage in coverage_dict[gene]])
        statistics.append((name, total_pos, avg_cov, num_of_low_cov))

    # Return the list of tuples holding the data
    return statistics


# MAIN
def main(args):
    """ Main function connecting all functions
        Note: the 'is None' checks that are done are only
        necessary for this program to run without error if
        not all functions are completed.
    """

    ### INPUT ###
    # Try to read input en output filenames from the commandline. Use defaults if
    # they are missing and warn if the extensions are 'wrong'.
    if len(args) > 1:
        bed_file = args[1]
        if not bed_file.lower().endswith('.bed'):
            print('Warning: given BED file does not have a ".bed" extension.')
        pileup_file = args[2]
        if not pileup_file.lower().endswith('.pileup'):
            print('Warning: given pileup file does not have a ".pileup" extension.')
        output_file = args[3]
    else:
        bed_file = 'data/example.bed'
        pileup_file = 'data/example.pileup'
        output_file = 'data/d4_output.csv'

    # STEP 1: Read BED data
    print('Reading BED data from', bed_file)
    bed_data = read_data(bed_file)
    if bed_data is None:
        print('No BED-data read...')
    else:
        print('\t> A total of', len(bed_data), 'lines have been read.\n')

    # STEP 2: Read Pileup data
    print('Reading pileup data from', pileup_file)
    pileup_data = read_data(pileup_file)
    if pileup_data is None:
        print('No Pileup-data read...')
    else:
        print('\t> A total of', len(pileup_data), 'lines have been read.\n')

    # STEP 3: Parsing BED data
    print('Parsing BED data...')
    bed_dict = parse_bed_data(bed_data)
    if bed_dict is None:
        print('BED-data not parsed!')
    else:
        print('\t> A total of', len(bed_dict.keys()), 'chromosomes have been stored.\n')

    # STEP 4: Parsing and filtering pileup data
    print('Parsing and filtering pileup-data...')
    coverage_dict = parse_pileup_data(pileup_data, bed_dict)
    if coverage_dict is None:
        print('Pileup data not parsed!')
    else:
        print('\t> Coverage of', len(coverage_dict.keys()), 'genes have been stored.\n')

    # STEP 5: Store calculated data
    print('Calculating coverage statistics...')
    coverage_statistics = calculate_mapping_coverage(coverage_dict)
    if coverage_statistics is None:
        print('No coverage statistics calculated!')
    else:
        print('\t> Statistics for', len(coverage_statistics), 'genes have been calculated.\n')

    # STEP 6: Write output data
    print('Writing the coverage statistics to', output_file)
    if coverage_statistics is None:
        print('Nothing to write, quitting...')
    else:
        save_coverage_statistics(output_file, coverage_statistics)
        from pathlib import Path
        csv_file_check = Path(output_file)
        if csv_file_check.is_file():
            print('\t> CSV file created, program finished.')
        else:
            print('\tCSV file', output_file, 'does not exist!')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
