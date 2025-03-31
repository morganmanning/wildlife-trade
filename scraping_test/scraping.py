import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gbif_data_converter as dc
import re

"""
TODO:
1. more efficnet name checking of description and title
2. add in scrolling the page
3. scrape the descriptions, images, and location data as well
4. add in more craigslist regions (i.e links), and eventually more websites
5. change to sets instead of lists for duplicate post prevention and faster operations, particualarly when scrolling
6. make the filepaths windows compatible
7. format with black
"""

# boilerplate code for initalizing the webdriver and connecting the code to chrome
service = Service(executable_path="scraping_test/chromedriver-mac-arm64/chromedriver")
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # keeps the webpage from showing
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://gainesville.craigslist.org/search/ccc#search=1~list~0~0")

# loads the webpage, and waits until either 10 seconds have passed or the posting titles have loaded
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cl-app-anchor.text-only.posting-title"))
    )
except:
    print("no listings or page loaded slowly")

titles = driver.find_elements(By.CSS_SELECTOR, "a.cl-app-anchor.text-only.posting-title")

# calls gbif_data_converter to turn the gbif backbone into a csv of common names
# eventually this will check if the CSV already exists before remaking it
if not os.path.isfile("scraping_test/data/common_names.csv"):
    names = dc.clean_data("gbif_backbone/VernacularName.tsv", "common_names")
else: 
    with open("scraping_test/data/common_names.csv") as f:
        f = csv.reader(f)
        next(f)
        names = [str(name[0]).strip().lower() for name in f]

# poorly written, but it adds a few names I thought of that could be useful. Ideally we would add these to 
# the actual csv. This will be deleted eventually
extra_names = ["bushmeat", "endangered", "owl", "dog", "puppy", "puppies", "horse", "hound", "cat", "kitten", "rat", "pony", "dragon", "donkey", "pig", "bird", "pug", "pomeranian"]
names.extend(extra_names)

matched_listings = [] # an empty list to save the titles of posts we want to
item_number = 1
# loops through the post titles we found and checks if they have any of our names in them
for title in titles:
    title_text = title.text.strip().lower()
    
    #the below is only comparing against extra_names because comparing against "names" in general is really 
    # slow right now if you'd like to try, change "extra_names" in the following line to just "names"
    if any(re.search(r'\b' + re.escape(name) + r'\b', title_text) for name in extra_names):  # this is a regular expressions (regex) pattern to ensure we only have whole names from
                                                                                             # the names list. this may have a problem with two word animal names
        print(f"{item_number}: {title_text}")
        matched_listings.append([title_text])
        item_number += 1

driver.quit() # closes the webdriver

# makes a folder to save the data (if it doesn't already exist) and then saves the listings we want row by row
if not os.path.isdir("scraping_test/data"):
    os.makedirs("scraping_test/data")
    
csv_filename = "scraping_test/data/filtered_listings.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Matched Listings"])
    writer.writerow([])
    writer.writerows(matched_listings)

