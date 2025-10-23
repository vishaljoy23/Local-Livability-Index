# driver.py
import logging
import json
from payload_capture import capture_housing_payload
from readPayload_GetSlug import get_housing_slug
from price_avg_sqft2 import scrape_sqft_prices

# ---------------- CONFIG ----------------

CONFIG_FILE = r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

PAYLOAD_FILE = "payload.json"
SLUG_FILE = "area_slug.json"
AVG_PRICE_FILE = "avg_price.json"
CITY = config["City_Details"]["city"] 

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    try:
        # Step 1: Capture payload from housing.com
        logging.info("Starting payload capture...")
        capture_housing_payload()  # writes to PAYLOAD_FILE
        logging.info(f"Payload saved to {PAYLOAD_FILE}")

        # Step 2: Extract area slug from payload
        logging.info("Extracting slug from payload...")
        slug = get_housing_slug(payload_file=PAYLOAD_FILE, slug_file=SLUG_FILE)
        if not slug:
            logging.error("Failed to get slug. Exiting pipeline.")
            return
        logging.info(f"Slug saved to {SLUG_FILE}: {slug}")

        # Step 3: Scrape average price per sqft
        logging.info("Calculating average price per sqft...")
        result, filename = scrape_sqft_prices(slug, city=CITY, output_file=AVG_PRICE_FILE)
        logging.info(f"Average price saved to {filename}: {result}")

        logging.info("Pipeline completed successfully!")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.info("Pipeline terminated with errors.")

if __name__ == "__main__":
    main()
