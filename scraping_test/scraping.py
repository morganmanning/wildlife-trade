import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


service = Service(executable_path="chromedriver-mac-arm64/chromedriver")
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
print("hi")
animals = ["owl", "dog", "puppy", "puppies", "horse", "hound", "cat", "kitten", "rat", "pony", "dragon", "donkey", "pig", "bird", "pug", "pomeranian"]
matched_listings = []

if titles:
    for i, title in enumerate(titles, start=1):
        title = title.text.lower()
        if any(animal in title for animal in animals):
            print(f"{i}: {title}")
            matched_listings.append([title])
else:
    print("no listings")

driver.quit()

# make this windows compatible later
if not os.path.isdir(r'./data/'):
    os.makedirs(r'./data/')

csv_filename = "data/filtered_listings.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Matched Listings"])
    writer.writerow([])
    writer.writerows(matched_listings) 

