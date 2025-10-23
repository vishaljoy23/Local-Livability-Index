import requests
import json

# ===== CONFIG =====
#API_URL = "https://api.waqi.info/feed/geo:12.908135;77.560839/?token=0a702b09cfffc0e623d5dccf98d656b044b832d2"  # Replace with the API endpoint
# ===== CONFIG =====
CONFIG_FILE = r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json"
OUTPUT_FILE = "AQI_data.json"
API_TOKEN = "0a702b09cfffc0e623d5dccf98d656b044b832d2"  # Replace with your actual token

def fetch_and_save():
    try:
        # Read config file
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        lat = config["City_Details"]["latitude"]
        lon = config["City_Details"]["longitude"]

        # Build API URL
        api_url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={API_TOKEN}"

        # Send GET request
        response = requests.get(api_url)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        # Convert response to Python dictionary
        data = response.json()

        # Save JSON data to file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Data saved to {OUTPUT_FILE}")

    except (requests.exceptions.RequestException, KeyError, FileNotFoundError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_and_save()
