#!/usr/bin/env python3

"""
script that parses the ANNOVAR data into a Dictionary object
"""

import sys
import json
from operator import itemgetter


def parse_annovar(filename):
    """
    Loops thru the annovar file and creates a dictionary from its contents
    :param filename: The file location of the annovar file
    :return: A list of dictionaries witch contain all the annovar data
    """
    header = []
    annovar_data = []

    with open(filename) as data:
        for i, variant in enumerate(data):

            # Get header if we're processing the first line
            if i == 0:
                header = process_annovar_line(variant, header=False)
                continue

            # Process the data and add to a list
            annovar_data.append(process_annovar_line(variant, header))

    return annovar_data


def process_annovar_line(variant, header):
    """ Given a list of column indices, parse the header and all data lines """
    # Define the columns of interest
    columns = [1, 3, *range(8, 11), *range(15, 16), *range(30, 36), 53]

    data = variant.split("\t")

    print(*columns)
    # Extract values for selected columns
    annotation_values = itemgetter(*columns)(data)

    # Return list of values if header is requested
    if not header:
        return annotation_values

    # Return all data as a dictionary with column: value
    return dict(
                zip(
                    [field.strip() for field in header],
                    [field.strip() for field in annotation_values]
                )
    )


def main():
    """ Main function for processing Annovar annotation data """

    # Pretty-print the dictionary as JSON object
    print(json.dumps(parse_annovar('data/Galaxy15-[_ANNOVAR_Annotated_variants_on_data_13].tabular')
                     , indent=4))

    return 0


if __name__ == "__main__":
    sys.exit(main())
