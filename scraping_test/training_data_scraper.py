import csv
import os
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gbif_data_converter as dc
import re
from tqdm import tqdm  # progress bar

def collect_training_data(num_samples = 100):
    """
    Collect a training dataset from Craigslist ads that contain keywords.
    Will randomly select 100 ads from those containing keywords.
    """
   ##### Define the keyword list for initial filtering
    # calls gbif_data_converter to turn the gbif backbone into a csv of common names
    # eventually this will check if the CSV already exists before remaking it (copied from August)
    if not os.path.isfile("scraping_test/data/common_names.csv"):
        names = dc.clean_data("gbif_backbone/VernacularName.tsv", "common_names")
    else: 
        with open("scraping_test/data/common_names.csv") as f:
            f = csv.reader(f)
            next(f)
            names = [str(name[0]).strip().lower() for name in f]

    # poorly written, but it adds a few names I thought of that could be useful. Ideally we would add these to 
    # the actual csv. This will be deleted eventually (copied from August)
    extra_names = [ "exotic", "rare", "wildlife", "wild", "endangered", "protected", 
                   "species", "bushmeat", "taxidermy", "mount", 
                   "pelt", "hide", "dog", "puppy", "puppies", "cat", "kitten", 
                   "kittens", "bird", "fish", "reptile", "snake", "lizard", "turtle", 
                   "tortoise", "frog", "toad", "salamander", "newt", "gecko", 
                   "iguana", "chameleon", "python", "boa", "parrot", "macaw", 
                   "cockatoo", "finch", "canary", "parakeet", "budgie", "cockatiel", 
                   "hamster", "gerbil", "guinea pig", "mouse", "rat", "ferret", 
                   "rabbit", "chinchilla", "hedgehog", "sugar glider", "tarantula",
                   "scorpion", "centipede", "millipede"]
    names.extend(extra_names)
    
    
    # list of Craigslist regions that cover the whole US (lots of overlap though)
    list_of_cities = [
        'https://provo.craigslist.org/search/hanna-ut/pet?lat=40.5603&lon=-111.0339&search_distance=960#search=1~gallery~0~0', # western US (pets category)
        'https://provo.craigslist.org/search/hanna-ut/sss?lat=40.5603&lon=-111.0339&search_distance=960#search=1~gallery~0~0', # western US (general for sale category)
        'https://ksu.craigslist.org/search/barnes-ks/pet?lat=39.7455&lon=-96.8471&search_distance=960#search=1~gallery~0~0', # central US (pets category)
        'https://ksu.craigslist.org/search/barnes-ks/sss?lat=39.7455&lon=-96.8471&search_distance=960#search=1~gallery~0~0', # central US (general for sale category)
        'https://athensohio.craigslist.org/search/union-furnace-oh/pet?lat=39.4295&lon=-82.4142&search_distance=960#search=1~gallery~0~0', # eastern US (pets category)
        'https://athensohio.craigslist.org/search/union-furnace-oh/sss?lat=39.4295&lon=-82.4142&search_distance=960#search=1~gallery~0~0', # eastern US (general for sale category)
        'https://fairbanks.craigslist.org/location/hughes-ak?lat=65.4189&lon=-153.3024&search_distance=570', # northern Alaska
        'https://kenai.craigslist.org/location/old-harbor-ak?lat=55.7271&lon=-149.6777&search_distance=570', # southern Alaska
        'https://honolulu.craigslist.org/location/waianae-hi?lat=21.2484&lon=-158.7524&search_distance=320' # Hawaii
    ]
    
    # boilerplate code for initalizing the webdriver and connecting the code to chrome (August)
    service = Service(executable_path="scraping_test/chromedriver-mac-arm64/chromedriver") 
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # keeps the webpage from showing
    driver = webdriver.Chrome(service = service, options = options)
    
    # store unique ad URLs to avoid duplicates
    seen_urls = set()

    # list to store ads that contain keywords
    filtered_ads = []
    
    # create directory for data if it doesn't exist
    if not os.path.isdir("training_data"):
        os.makedirs("training_data")
    
    print("Collecting ads :)")
    
    # collect all ads from each region that contain keywords
    for region_url in tqdm(list_of_cities, desc = "Scraping regions"):
        try:
            # load the page
            driver.get(region_url)
            
            # wait for listings to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.cl-app-anchor.text-only.posting-title"))
            )
            
            # scroll down to load more listings
            for _ in range(3):  # scroll a few times to load more ads
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)  # wait for new listings to load
            
            # get all listings on the page
            listings = driver.find_elements(By.CSS_SELECTOR, "a.cl-app-anchor.text-only.posting-title")
            
            # filter listings that contain keywords
            for listing in listings:
                title = listing.text.strip().lower()
                link = listing.get_attribute('href')
                
                # Skip if we've already seen this URL
                if link in seen_urls:
                    continue

                # check if title contains any keyword
                if any(re.search(r'\b' + re.escape(name) + r'\b', title) for name in names):
                    # add the URL to our seen set
                    seen_urls.add(link)

                    # keep original case
                    filtered_ads.append((listing.text.strip(), link)) 
            
        except Exception as e:
            print(f"Potential error loading {region_url}: {e}")
            continue
    
    print(f"Found {len(filtered_ads)} ads containing keywords across all regions")

    # shuffle filtered_ads to randomize
    random.shuffle(filtered_ads)
    
    # Take only the first num_samples ads (or all if fewer than num_samples)
    sample_ads = filtered_ads[:min(num_samples, len(filtered_ads))]
    
    print(f"Randomly selected {len(sample_ads)} ads for the training dataset :)")
    
    # create or overwrite the training data file
    with open("training_data/raw_ads.csv", "w", newline = "", encoding = "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Description", "Price", "Location", "URL", "IsAnimalTrade"])
    
    # process each selected ad
    for title, link in tqdm(sample_ads, desc = "Processing ads"):
        try:
            # visit the ad page to get full details
            driver.get(link)
            
            # wait for the post body to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section#postingbody"))
            )
            
            # get description
            description = driver.find_element(By.CSS_SELECTOR, "section#postingbody").text.strip()
            
            # get price if available
            try:
                price = driver.find_element(By.CSS_SELECTOR, "span.price").text.strip()
            except:
                price = "NA"
            
            # get location if available
            try:
                location = driver.find_element(By.CSS_SELECTOR, "div.mapaddress").text.strip()
            except:
                location = "NA"
            
            # save it
            with open("training_data/raw_ads.csv", "a", newline = "", encoding = "utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([title, description, price, location, link, ""])  # IsAnimalTrade left blank for manual labeling
            
            # add a delay between requests to avoid being blocked >:)
            time.sleep(random.uniform(0.5, 1.5)) # could increase this
            
        except Exception as e:
            print(f"Error processing ad at {link}: {e} :(")
            continue
    
    driver.quit()  # Close the webdriver
    print("Training dataset collection complete! Slay!:)")
    print(f"Successfully collected data for {len(sample_ads)} ads")
    print(f"Manually label the 'IsAnimalTrade' column in training_data/raw_ads.csv with 'yes' or 'no'")
    print("But make sure you're not overwriting the original data file!!!")

# create fresh training data file
if os.path.exists("training_data/raw_ads.csv"):
    os.remove("training_data/raw_ads.csv") # overwrite
    
collect_training_data(100)  # collect 100 random ads for training