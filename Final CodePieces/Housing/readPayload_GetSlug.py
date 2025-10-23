import requests
import json
import os
import re
import logging

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_housing_slug(payload_file="payload.json", slug_file="area_slug.json"):
    """
    Reads the payload JSON, sends it to Housing API, extracts the canonical slug,
    and saves it to slug_file.
    
    Returns:
        slug (str) if found, else None
    """
    url = (
        "https://mightyzeus-mum.housing.com/api/gql/cache-first"
        "?apiName=TYPE_AHEAD_API&emittedFrom=client_buy_home&isBot=false"
        "&platform=desktop&source=web&source_name=AudienceWeb"
    )

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Origin": "https://housing.com",
        "Referer": "https://housing.com/"
    }

    # Check payload file
    if not os.path.exists(payload_file):
        logging.error(f"{payload_file} not found")
        return None

    with open(payload_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Ensure variables is a dict
    if isinstance(payload.get("variables"), str):
        try:
            payload["variables"] = json.loads(payload["variables"])
        except json.JSONDecodeError:
            logging.warning("Could not parse 'variables' field; sending as-is")

    # Send request
    try:
        res = requests.post(url, json=payload, headers=headers)
        logging.info(f"API request status: {res.status_code}")

        data = res.json()
        raw_response = res.text[:500]

        # Extract canonical URL using regex
        match = re.search(r'"canonical"\s*:\s*"([^"]+)"', raw_response)
        if match:
            canonical_url = match.group(1)
            slug = canonical_url.split('/')[-1]

            # Save slug to JSON
            with open(slug_file, "w", encoding="utf-8") as f:
                json.dump({"slug": slug}, f, indent=4)
            logging.info(f"Slug saved: {slug} -> {slug_file}")
            return slug
        else:
            logging.error("Canonical URL not found in response")
            data = {
                "area": "ERR",
                "avg_price_per_sqft": "ERR"
            }
            # Save JSON
            output_file="avg_price.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.debug(f"Response snippet: {raw_response}")
            return None

    except Exception as e:
        logging.error(f"Failed to extract slug: {e}")
        logging.debug(f"Response snippet: {res.text[:500]}")
        return None


# Example run
if __name__ == "__main__":
    get_housing_slug("payload.json")
