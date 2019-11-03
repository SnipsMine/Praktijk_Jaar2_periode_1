#!/usr/bin/env python3

"""
BFV2 Theme 05 - Genomics - Sequencing Project

Script for parsing and filtering VCF data given a certain variant
allele frequency value.

Deliverable 5
-------------
Make changes to the `parse_vcf_data` function AND the `main` function,
following the instructions preceded with double '##' symbols.

    usage:
        python3 deliverable5.py vcf_file.vcf frequency out_file.vcf

    arguments:
        vcf_file.vcf: the input VCF file, output from the varscan tool
                      frequency: a number (integer) to use as filtering value
        out_file.vcf: name of the output VCF file

    output:
        a VCF file containing the complete header (comment lines) and
        only the remaining variant positions after filtering.
"""

# METADATA VARIABLES
__author__ = "Micha Beens, Nadia Choudhury"
__status__ = "Finished"
__version__ = "2019.d5.v1"

# IMPORT
import sys
import argparse


def parse_vcf_data(vcf_input_file, frequency, vcf_output_file):
    """ This function reads the input VCF file line by line, skipping the first
    n-header lines. The remaining lines are parsed to filter out variant allele
    frequencies > frequency.
    """

    # Open the INTPUT VCF file, read the contents line-by-line
    with open(vcf_input_file) as vcf_data:

        # Open the Output VCF file, add the good lines in the file
        with open(vcf_output_file, "w") as output:
            for line in vcf_data:
                # Write the first ... comment-lines (header) directly to the output file
                if line.startswith("#"):
                    output.write(line)

                # Compare the 'FREQ' field with the `frequency` value and write the line
                else:
                    line = line.split("\t")
                    formats = line[8].split(":")
                    index_freq = 0
                    for index, form in enumerate(formats):
                        if form == "FREQ":
                            index_freq = index
                    freq = line[9].split(":")[index_freq]
                    # to the output file if FREQ > frequency
                    if float(freq.replace("%", "")) > frequency:
                        output.write("\t".join(line))


# MAIN
def main(args):
    """ Main function """
    # Create argument parser. Use default values when no arguments are given
    parser = argparse.ArgumentParser(
        description='Creates a vcf file that contains all variants where the '
                    'frequency is above the given frequency value from the given vcf file')
    parser.add_argument('vcf_file', nargs='?', default='data/example.vcf',
                        type=str, help='name of the vcf input file')
    parser.add_argument('frequency', nargs='?', type=int, default=30,
                        help='give a number to use as filtering value')
    parser.add_argument('out_vcf', nargs='?', default='data/d5_output.vcf',
                        type=str, help='give name for your output file')

    # Give warning when the default values of the arguments are used
    if len(args) == 1:
        print('Warning, no arguments given, using default values (testing only)...')

    # Create variables for each argument
    args = parser.parse_args()
    vcf_file = args.vcf_file
    frequency = args.frequency
    out_vcf = args.out_vcf

    # Process the VCF-file
    parse_vcf_data(vcf_file, frequency, out_vcf)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
