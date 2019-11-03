#!/usr/bin/env python3

"""
BFV2 Theme 05 - Genomics - Sequencing Project

Template for filtering Gene names from the 'RefSeq_Gene' column given
in ANNOVAR output files.

Deliverable 7
-------------
Make changes to the 'get_gene_name' function

    usage:
        python3 deliverable7.py
"""

# METADATA VARIABLES
__author__ = "Micha Beens, Nadia Choudhury"
__status__ = "Finished"
__version__ = "2019.d7.v1"

# IMPORT
import sys
import re


def get_gene_name(gene_name):
    """
    This function returns the a filtered gene name from the given raw gene_name

    Args:
        gene_name (String): The raw gene name
    Returns:
        gene (String): The filtered gene name
    """
    # Regular Expression Link to explenation: https://regex101.com/r/UPDa0e/5
    reg_ex = r"((?=LOC)[A-Z0-9\-]+|(?=LIN)[A-Z0-9\-]+|NONE|\([^)]*\))?(?(1)|([A-Z0-9\-]+))"

    # Finding all matches with the regular expression
    match_tuple = re.finditer(reg_ex, gene_name, re.IGNORECASE)

    # Setting the values of group 2 in a list if the values are not empty string
    match = [match.group(2)
             for match in match_tuple
             if match.group(2) != "" and match.group(2) is not None]

    if match:
        gene = "/".join(match)
    else:
        gene = "-"
    return gene


######
# Do not change anything below this line
######

# MAIN
def main():
    """ Main function """

    # INPUT #
    refseq_genes = [
        'TNNI3(NM_000363:exon5:c.371+2T>A)',
        'TSHZ3(dist=65732),THEG5(dist=173173)',
        'ACTR3BP2(dist=138949),NONE(dist=NONE)',
        'BIN1(dist=32600),CYP27C1(dist=43909)',
        'LOC101927282(dist=1978702),LOC101927305(dist=14658)',
        'NBPF10,NBPF20',
        'ERBB4',
        'LOC100507291',
        'NONE'
    ]

    # OUTPUT #
    genes = [
        'TNNI3',
        'TSHZ3/THEG5',
        'ACTR3BP2',
        'BIN1/CYP27C1',
        '-',
        'NBPF10/NBPF20',
        'ERBB4',
        '-',
        '-'
    ]
    # Process the ANNOVAR-file
    fail = 0
    for i, refseq_gene in enumerate(refseq_genes):
        filtered_gene = get_gene_name(refseq_gene)
        print("Input RefSeq_Gene: '", refseq_gene, "', Filtered gene name: '",
              filtered_gene, "'", sep='')
        if filtered_gene != genes[i]:
            print("\tUnfortunately, '", filtered_gene,
                  "' (your output) is different from the expected output ('",
                  genes[i], "').\n", sep='')
            fail = 1
        else:
            print('\tWell done! The gene name is correct.')

    if fail == 1:
        print('\nNot all genes are filtered correctly, please review',
              'the list above and try again.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
