import csv
import sys
import os

"""
This program takes the tsv of the common and scientific names gbif data, and removes everything
that isn't just the name. This is so we can parse the data easier when checking for valid postings online.
"""

csv.field_size_limit(sys.maxsize) # this is so we don't have problems reading from columns with lots of data
   
# made this a function so that it can be applied to other lists of names with extraneous information
def clean_data(input_filepath, output_filename, return_list=True):
    # opens the file at the given filepath, and then make a list of all the names from the list
    with open(input_filepath) as f:
        rd = csv.reader(f, delimiter="\t")
        next(rd) # skips the title row
        common_names = [[row[1]] for row in rd]
    
    if not os.path.isdir("scraping_test/data"):
        os.makedirs("scraping_test/data")

    # saves the common names in a folder called "data"
    output_filepath = "scraping_test/data/" + output_filename + ".csv"
    with open("scraping_test/data/common_names.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=" ")
        writer.writerow(["Common Names"])
        writer.writerows(common_names)
    
    print("CSV at " + output_filepath + " is complete!")

    if return_list:
        # this ensures each item in the list is a string before returning it
        return list(map(str, common_names))
