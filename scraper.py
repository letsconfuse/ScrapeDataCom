# scraper.py

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from fake_useragent import UserAgent
from datetime import datetime  
import os  # Import os module to get the current working directory

def scrape_yellowpages(search_term, location):
    """
    Scrapes business information from YellowPages for a given search term and location.
    """

    search_term = search_term.replace(" ", "+")
    location = location.replace(" ", "+")

    base_url = f"https://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page="

    options = Options()
    options.use_chromium = True
    options.add_argument("--disable-blink-features=AutomationControlled")

    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

    # Get the current working directory where the script is run
    current_directory = os.getcwd()

    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(current_directory, f"yellowpages_data_{timestamp}.csv")  # Save directly in the current directory

    page_num = 1
    business_listings = []

    try:
        while True:
            url = base_url + str(page_num)
            driver.get(url)
            time.sleep(random.uniform(3, 6))

            business_cards = driver.find_elements(By.CLASS_NAME, "result")
            if not business_cards:
                break

            for business in business_cards:
                try:
                    name = business.find_element(By.CLASS_NAME, "business-name").text.strip()
                    address = business.find_element(By.CLASS_NAME, "street-address").text.strip() if business.find_elements(By.CLASS_NAME, "street-address") else "-"
                    locality = business.find_element(By.CLASS_NAME, "locality").text.strip() if business.find_elements(By.CLASS_NAME, "locality") else "-"
                    phone = business.find_element(By.CLASS_NAME, "phones").text.strip() if business.find_elements(By.CLASS_NAME, "phones") else "-"
                    website = business.find_element(By.CLASS_NAME, "track-visit-website").get_attribute("href") if business.find_elements(By.CLASS_NAME, "track-visit-website") else "-"

                    business_listings.append({
                        "Business Name": name,
                        "Address": f"{address}, {locality}",
                        "Phone": phone,
                        "Website": website
                    })

                except Exception as e:
                    print(f"❌ Error extracting data for a business: {e}")
                    continue

            if business_listings:
                df = pd.DataFrame(business_listings)
                df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)
                print(f"✅ Data saved to {filename}")
                business_listings.clear()

            page_num += 1

    except Exception as e:
        print(f"❌ Error during scraping: {e}")

    finally:
        driver.quit()
        print("✅ Scraping finished.")
        return filename
