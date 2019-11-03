#!/usr/bin/env python3

"""
BFV2 Theme 05 - Genomics - Sequencing Project

This script will connect to your SQL database and will fill it with the data from the annovar file

This script is meant to be run in the terminal

Deliverable 9
-------------

Usage:
    python3 deliverable9.py [-s sql_file] username password hostname database_name annovar_file

"""

# METADATA VARIABLES
__author__ = "Micha Beens, Nadia Choudhury"
__status__ = "Finished"
__version__ = "2019.d9.v5"

# IMPORTS
import sys
import argparse
import os.path
import re
from operator import itemgetter
import mysql.connector


# FUNCTIONS
def check_file_exists(file):
    """
    Checks if the given file exists

    Args:
        file (String): The filename of the file
    Return:
        exists (Bool): The value that says if the file exists
    """
    return os.path.exists(file)


def check_file_tab_separated(file):
    """
    Checks if the given file is tab separated

    Args:
        file (String): The filename of the file
    Return:
        tab_separated (Bool): The value that says if the file is tab separated
    """
    with open(file) as file_data:
        for line in file_data:
            line = line.split('\t')
            return len(line) > 1


class AnnovarDatabaseFiller:
    """
    With this object you can write your annovar file to a database
    """

    def __init__(self, user, password, host, database):
        self.dbcon = None
        self.cursor = None

        self.connect_to_database(user, password, host, database)

        self.tables = ["chromosomes", "genes", "variants"]
        self.columns = {}
        for table in self.tables:
            self.cursor.execute("desc %s" % table)

            tdescription = self.cursor.fetchall()
            # Get the actual columns from the table
            self.columns[table] = [column[0] for column in tdescription][1:]

    def connect_to_database(self, user, password, host, database):
        """
        Connect to the mysql database using the given credentials

        Args:
            user (String): The username for the database
            password (String): The Password of the user for the database
            host (String): The host adres of de database
            database (string): The name of the database
        Return:
            dbcon (Connection): A connection to the given database
        """
        try:
            self.dbcon = mysql.connector.connect(user=user,
                                                 password=password,
                                                 host=host,
                                                 database=database)

            self.cursor = self.dbcon.cursor()

            test_query = "SELECT 1"
            self.cursor.execute(test_query)
            if self.cursor.fetchall():
                print("Database connection is opened")
            else:
                print("Connection with database failed")
        except:
            print("Connection with database failed")

    def reset_tables(self, sql_file):
        """
        Resets the tables in the connected database

        Args:
            sql_file (String): The filepath to the sql file.

        Return:
            None
        """
        with open(sql_file) as sql_data:
            data = sql_data.read()
            commands = data.strip().split(";")

            # Execute every command from the input file
            for command in commands:
                self.cursor.execute(command)

        self.dbcon.commit()
        print("Tables are reset")

    def parse_annovar(self, file):
        """
        Parse the ANNOVAR file

        Args:
            file (String): The path to the ANNOVAR file

        Return:
            None
        """
        header = []

        # Open file
        with open(file) as data:

            # Read file contents
            for i, variant in enumerate(data):

                # Get header if we're processing the first line
                if i == 0:
                    header = self.process_annovar_line(variant, header=False)
                    continue

                # Process the data and add to a list
                row = self.process_annovar_line(variant, header)

                # Insert the data in the database
                self.insert_chromosomes(row)

                self.insert_genes(row)

                self.insert_variants(row)

    @staticmethod
    def process_annovar_line(variant, header):
        """
        Given a list of column indices, parse the header and all data lines

        Args:
            variant (String): A single row of a annovar file
            header (List): A list of the headers in a annovar file

        Return:
            (Dictionary): A Dictionary with the the correct values to each header.
        """
        # Define the columns of interest
        columns = [*range(0, 4), *range(9, 11), *range(15, 17), 27, *range(30, 36), 53]

        data = variant.split("\t")

        # Extract values for selected columns
        annotation_values = itemgetter(*columns)(data)

        # Return list of values if header is requested
        if not header:
            return [annotation.lower() for annotation in annotation_values]

        # Return all data as a dictionary with column: value
        return dict(
                    zip(
                        [field.strip() for field in header],
                        [field.strip() for field in annotation_values]
                    )
        )

    def insert_chromosomes(self, row):
        """
        Get Chromosome information: chromosome

        Args:
            row (Dictionary): a row of the annovar file

        Return:
            None
        """
        columns = self.columns[self.tables[0]]
        # The items that need to go in the db
        items = self.get_item(row, columns)

        # Check if chrom is in the table
        chrom_in_db_query = "SELECT * FROM {0} WHERE {1} = {2}".format(self.tables[0],
                                                                       columns[0],
                                                                       items[columns[0]][0])

        # Execute the query
        self.cursor.execute(chrom_in_db_query)
        # if the length of the query is more than nothing
        if not self.cursor.fetchall():
            # insert Chromosome information into the Chromosome table
            self.insert_row(self.tables[0], items)

    def insert_genes(self, row):
        """
        Get gene_information (Script 7): chrom_id, refseq_gene

        Args:
            row (Dictionary): a row of the annovar file

        Return:
            None
        """
        # Get the chrom columns
        chrom_columns = self.columns[self.tables[0]]

        # Get the gene columns
        gene_columns = self.columns[self.tables[1]]

        # Get Chrom_id
        chrom = "'{}'".format(row[chrom_columns[0]])
        row[gene_columns[0]] = "(SELECT {0} FROM {1} WHERE {2} = {3})".format(gene_columns[0],
                                                                              self.tables[0],
                                                                              chrom_columns[0],
                                                                              chrom)

        # Get refseq_gene
        row[gene_columns[1]] = self.get_gene_name(row[gene_columns[1]])

        # Get the items that need to be put in the database
        items = self.get_item(row, gene_columns)

        # Check if gene is in the table
        gene_in_db_query = "SELECT * FROM {0} WHERE {1} = {2}".format(self.tables[1],
                                                                      gene_columns[1],
                                                                      items[gene_columns[1]][0])
        self.cursor.execute(gene_in_db_query)

        # Check if the query returns empty
        if not self.cursor.fetchall():
            # insert Gene information into the Gene table
            self.insert_row(self.tables[1], items)

    def insert_variants(self, row):
        """
        get variant information: gene_id, refseq_func, dbsnp138, EUR, LJB2_SIFT,
        LJB2_PolyPhen2_HDIV, clinvar, begin position and reference.

        Args:
            row (Dictionary): a row of the annovar file

        Return:
            None
        """
        gene_columns = self.columns[self.tables[1]]
        variant_columns = self.columns[self.tables[2]]

        # Get gene_id
        ref_gene = "'{}'".format(self.get_gene_name(row[gene_columns[1]]))
        gene_id = "(SELECT {0} FROM {1} WHERE {2} = {3})".format(variant_columns[0],
                                                                 self.tables[1],
                                                                 gene_columns[1],
                                                                 ref_gene)
        row[variant_columns[0]] = gene_id

        items = self.get_item(row, variant_columns)

        # insert variant information into Variant table
        self.insert_row(self.tables[2], items)

    @staticmethod
    def get_item(row, db_keys):
        """
        Creates a dictionary where the keys are the db columns, with the correct value

        Args:
            row (Dict): a row of the annovar file
            db_keys (List): A list with the names of the db columns

        Returns:
            value (Dict): A dictionary where the keys are db columns with the corresponding values.
        """
        # A container dict where the keys are db columns
        value = {}

        for key in db_keys:
            # If current value is empty
            if row[key] == "":
                value[key] = ["null"]
            # If current value is a Int/Float or if the current value is a subquery
            elif row[key].isnumeric() or row[key].startswith("("):
                value[key] = [row[key]]
            # otherwise put the value in quotes
            else:
                value[key] = ["'{}'".format(row[key])]
        return value

    def insert_row(self, table, variablen):
        """
        Inserts a row into a given table in the given database

        Args:
            table (String): Name of the table you want to insert a row into
            variablen (Dictionary): Contains the data you want to put in the table, the keys should
                                    match the columns in the table.

        Return:
            None
        """
        # Get the keys
        keys = list(variablen.keys())

        # Go tru all variables
        for index in enumerate(variablen[keys[0]]):

            # Create the list where all variables wil be collected in
            var_lijst = []

            # Get all variables
            for key in keys:
                var_lijst.append("{}".format(variablen[key][index[0]]))

            # Create the SQL Insert statement
            insert = "INSERT INTO {}({}) VALUES({}) ".format(table,
                                                             ", ".join(keys),
                                                             ", ".join(var_lijst))

            # Execute the insert statement
            self.cursor.execute(insert)

    @staticmethod
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
        match = [match.group(2) for match in match_tuple
                 if match.group(2) != "" and match.group(2) is not None]

        if match:
            gene = "/".join(match)
        else:
            gene = "-"
        return gene

    def print_database_status(self):
        """
        Prints the number of rows in the tables used in this script
        """

        # Get nuber of row for each table
        for table in self.tables:
            query = "SELECT * FROM {}".format(table)
            self.cursor.execute(query)
            rows = len(self.cursor.fetchall())
            print("The table {} contains {} rows".format(table, rows))

    def close_conection_to_database(self):
        """
        Closes the connection to and the curser of the the database.
        """
        # Commit all db changes
        self.dbcon.commit()

        # Close the cursor
        self.cursor.close()

        # Close the db connection
        self.dbcon.close()
        print("Database connection is closed")


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Read a ANNOVAR file and puts the columns needed \
    for the experiment in a database.')

    parser.add_argument('user', type=str, help='Name of database user')

    parser.add_argument('password', type=str, help='user password for database')

    parser.add_argument('host', type=str, help='database host')

    parser.add_argument('database', type=str, help='Name of database')

    parser.add_argument('file', type=str, help='ANNOVAR annotation file')

    parser.add_argument("-s", "--sql_file", type=str, help='if given this file will be executed. \
                        This should only contain the data to reset the tables used in this script.')

    args = parser.parse_args()

    connection = AnnovarDatabaseFiller(args.user, args.password, args.host, args.database)

    if args.sql_file is not None and check_file_exists(args.sql_file):
        connection.reset_tables(args.sql_file)

    if check_file_exists(args.file) and check_file_tab_separated(args.file):
        connection.parse_annovar(args.file)

    connection.print_database_status()

    connection.close_conection_to_database()


if __name__ == "__main__":
    sys.exit(main())
