from playwright.sync_api import sync_playwright, TimeoutError
import json
import time

# === CONFIG ===
CONFIG_FILE = r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json"
TARGET_API = "apiName=TYPE_AHEAD_API"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

CITY = config["City_Details"]["city"]
if (CITY == "Bengaluru"):
    CITY = "Bangalore"
    
area = config["City_Details"]["area"]

safe_city = CITY.lower().replace(" ", "-")
SEARCH_URL = f"https://housing.com/in/buy/real-estate-{safe_city}"
SEARCH_SELECTOR = 'div[data-q="search"] input'
SEARCH_QUERY = area


def capture_housing_payload():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()

        print(f"Navigating to {SEARCH_URL}...")
        page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60000)

        # ✅ Wait for the search box
        try:
            page.wait_for_selector(SEARCH_SELECTOR, timeout=20000)
        except TimeoutError:
            print("[ERROR] Search box not found.")
            browser.close()
            return

     
        # #OLD
        # # Type search query slowly
        # page.click(SEARCH_SELECTOR)
        # page.type(SEARCH_SELECTOR, SEARCH_QUERY, delay=100)

        # Wait and ensure input exists
        #page.wait_for_selector(SEARCH_SELECTOR, state="visible")

        # Clear and fill input in one go
        # Using fill because .type() was not working as well
        # page.click(SEARCH_SELECTOR)
        # page.fill(SEARCH_SELECTOR, SEARCH_QUERY)

        page.wait_for_selector(SEARCH_SELECTOR, state="visible", timeout=30000)
        page.wait_for_timeout(1000)  # Give React time to attach handlers
        page.fill(SEARCH_SELECTOR, SEARCH_QUERY)

        # Optional: wait briefly before capturing network request
        #page.wait_for_timeout(1000)




        # ✅ Wait specifically for the GraphQL request
        try:
            request = page.wait_for_event(
                "request",
                lambda r: TARGET_API in r.url,
                timeout=20000  # wait up to 20 sec
            )
        except TimeoutError:
            print("[ERROR] No matching request found.")
            browser.close()
            return

        print(f"[MATCH] URL: {request.url}")
        post_data = request.post_data
        payload = None

        if post_data:
            try:
                payload = json.loads(post_data)
                # Fix variables if stringified JSON
                if isinstance(payload.get("variables"), str):
                    try:
                        payload["variables"] = json.loads(payload["variables"])
                    except json.JSONDecodeError:
                        pass
            except json.JSONDecodeError:
                payload = post_data

        if payload:
            save_path = r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Housing\payload.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"[SAVED] {save_path}")
            print(json.dumps(payload, indent=2))
        else:
            print("[ERROR] Could not extract payload.")

        browser.close()


if __name__ == "__main__":
    capture_housing_payload()
