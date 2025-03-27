"""
This program takes the tsv of the common and scientific names gbif data, and removes everything
that isn't just the name. This is so we can parse the data easier when checking for valid postings online.
"""
import csv
import sys
import os
import re

csv.field_size_limit(sys.maxsize) # this is so we don't have problems reading from columns with lots of data
    
def clean_data(input_filepath, output_filename, return_list=True):
    # opens the file at the given filepath, and then make a list of all the names from the list
    with open(input_filepath) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        next(rd)
        common_names = [[row[1]] for row in rd]
        # print(common_names)
    
    if not os.path.isdir("scraping_test/data"):
        os.makedirs("scraping_test/data")

    # saves the names in a folder called data
    output_filepath = "scraping_test/data/" + output_filename + ".csv"
    with open("scraping_test/data/common_names.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=" ")
        writer.writerow(["Common Names"])
        # writer.writerow([])
        writer.writerows(common_names)

    if return_list:
        # this turns each item in the list into a string pefore returning it
        return list(map(str, common_names))
    
    print("CSV at " + output_filepath + " is complete!")