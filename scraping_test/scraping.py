import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gbif_data_converter as dc

# reminder to comment this code as it gets better and use black for formatting

service = Service(executable_path="scraping_test/chromedriver-mac-arm64/chromedriver")
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # to keep the webpage from showing
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://gainesville.craigslist.org/search/ccc#search=1~list~0~0")

# we have to wait for the webpage to load
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cl-app-anchor.text-only.posting-title"))
    )
except:
    print("no listings or page loaded slowly")

titles = driver.find_elements(By.CSS_SELECTOR, "a.cl-app-anchor.text-only.posting-title")

names = dc.clean_data("gbif_backbone/VernacularName.tsv", "common_names")
animals = ["owl", "dog", "puppy", "puppies", "horse", "hound", "cat", "kitten", "rat", "pony", "dragon", "donkey", "pig", "bird", "pug", "pomeranian"]
names.extend(animals)

matched_listings = []

item_number = 1
if titles:
    for title in titles:
        title = title.text.lower()
        if any(name in title for name in names):
            print(f"{item_number}: {title}")
            matched_listings.append([title])
            item_number+=1
else:
    print("no listings")

driver.quit()

# make this file pathing windows compatible later
if not os.path.isdir("scraping_test/data"):
    os.makedirs("scraping_test/data")
csv_filename = "scraping_test/data/filtered_listings.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Matched Listings"])
    writer.writerow([])
    writer.writerows(matched_listings)
