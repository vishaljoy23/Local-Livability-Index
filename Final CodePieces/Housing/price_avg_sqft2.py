import json
import re
import logging
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def scrape_sqft_prices(slug, city="bangalore", max_listings=30, output_file="avg_price.json"):
    """
    Scrape avg. price per sqft for a given area slug from housing.com.

    Args:
        slug (str): area slug from area_slug.json
        city (str): city name for URL construction
        max_listings (int): max listings to consider
        output_file (str): JSON file to save results

    Returns:
        dict: { "area": area_name, "avg_price_per_sqft": avg_price }
    """
    safe_city = city.lower().replace(" ", "-")
    url = f"https://housing.com/in/buy/{safe_city}/{slug}"

    # Extract area name from slug
    area_name = slug if slug else "unknown_area"

    # Selenium setup
    options = Options()
    # options.add_argument("--headless=new")  # enable headless after debugging
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    logging.info(f"Opening browser to scrape {url}")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        # Wait for first "Avg. Price" block
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Avg. Price')]"))
        )

        # Scroll a few times to load more listings
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(text(),'Avg. Price')]"))
                )
            except:
                pass

        html = driver.page_source

    finally:
        driver.quit()
        logging.info("Browser closed")

    # Parse prices
    soup = BeautifulSoup(html, "html.parser")
    results = []
    price_tags = soup.find_all("div", string=lambda t: t and "Avg. Price" in t)

    for tag in price_tags[:max_listings]:
        text = tag.get_text(" ", strip=True)
        match = re.search(r"₹([\d.]+)\s*K/sq\.ft", text)
        if match:
            results.append(float(match.group(1)))

    avg_price = round(sum(results) / len(results), 2) if results else None

    data = {
        "area": area_name,
        "avg_price_per_sqft": avg_price
    }

    # Save JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logging.info(f"Saved avg price data to {output_file}")
    return data, output_file


# ---------------- Example usage ----------------
if __name__ == "__main__":
    try:
        with open("area_slug.json", "r") as f:
            data = json.load(f)
        slug = data.get("slug")
        result, filename = scrape_sqft_prices(slug)
        logging.info(f"Scraped result: {result}")
    except Exception as e:
        logging.error(f"Error scraping avg price: {e}")
