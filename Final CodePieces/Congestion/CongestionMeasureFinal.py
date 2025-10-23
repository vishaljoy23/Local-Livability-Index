import os
import time
import csv
import json
from datetime import datetime
from geopy.distance import distance
from geopy.geocoders import Nominatim
import requests
import pandas as pd
from datetime import datetime, timedelta


# ------------------ CONFIG ------------------
API_KEY = "AIzaSyACLPG3K3RKxk3VuE0BRzoIS0Kkpn_Koi4"
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

#CITY = config["City_Details"]["city"]
CITY = config["City_Details"]["city"] + ", India"
BEARINGS = [0, 45, 90, 135, 180, 225, 270, 315]
RADII_KM = [5, 10, 20]

OUTPUT_FILE = "city_congestion.csv"
# Example weights for city-wide index
WEIGHTS = {5: 234, 10: 472, 20: 942}  

#TIME IS SET LATER

# TIMES = {
#     "freeflow": datetime(2025, 9, 23, 0, 0),
#     "peak": datetime(2025, 9, 23, 9, 0)
# }

# ------------------ HELPER FUNCTIONS ------------------
def next_weekday(start=None):
    """Return the nearest future weekday (Mon-Fri)."""
    if start is None:
        start = datetime.now()
    date = start + timedelta(days=1)  # start from tomorrow
    while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        date += timedelta(days=1)
    return date

def get_city_center(city):
    geolocator = Nominatim(user_agent="city_center_locator")
    location = geolocator.geocode(city)
    return location.latitude, location.longitude


def get_point(center, radius_km, bearing):
    point = distance(kilometers=radius_km).destination(center, bearing)
    return (point.latitude, point.longitude, bearing)


def gmaps_directions(origin, destination, departure_time):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin[0]},{origin[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "departure_time": int(departure_time.timestamp()),
        "traffic_model": "best_guess",
        "key": API_KEY
    }
    for _ in range(3):  # Retry up to 3 times
        r = requests.get(url, params=params)
        if r.status_code == 200:
            data = r.json()
            if data["status"] == "OK":
                leg = data["routes"][0]["legs"][0]
                return (
                    leg["duration"]["value"],  # normal duration
                    leg.get("duration_in_traffic", {}).get("value", None)  # traffic duration
                )
        time.sleep(1)
    return None, None


def measure_city(city):
    center = get_city_center(city)
    results = []

    for radius in RADII_KM:
        for bearing in BEARINGS:
            point_a = get_point(center, radius, bearing)
            point_b = get_point(center, radius, (bearing + 180) % 360)

            for label, dep_time in TIMES.items():
                normal, traffic = gmaps_directions((point_a[0], point_a[1]),
                                                   (point_b[0], point_b[1]),
                                                   dep_time)
                if normal is not None and traffic is not None:
                    ratio = traffic / normal if normal > 0 else None
                    results.append({
                        "city": city,
                        "radius_km": radius,
                        "bearing_deg": bearing,
                        "time_label": label,
                        "origin_lat": point_a[0],
                        "origin_lon": point_a[1],
                        "dest_lat": point_b[0],
                        "dest_lon": point_b[1],
                        "normal_duration_sec": normal,
                        "traffic_duration_sec": traffic,
                        "congestion_ratio": ratio
                    })
                time.sleep(0.2)  # Avoid hitting QPS limits
    return results


def save_results(results, filename):
    if not results:
        print("No data to save.")
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


# ------------------ CONFIG ------------------
#TIME

# Get nearest future weekday
future_date = next_weekday()


TIMES = {
    "freeflow": future_date.replace(hour=0, minute=0, second=0, microsecond=0),
    "peak": future_date.replace(hour=18, minute=0, second=0, microsecond=0),
}
# ------------------ ANALYSIS ------------------
def compute_city_congestion_index(csv_file):
    df = pd.read_csv(csv_file)

    freeflow = df[df["time_label"] == "freeflow"].copy()
    peak = df[df["time_label"] == "peak"].copy()

    merged = pd.merge(
        peak,
        freeflow,
        on=["city", "radius_km", "bearing_deg"],
        suffixes=("_peak", "_freeflow")
    )

    merged["traffic_ratio_peak_vs_freeflow"] = (
        merged["traffic_duration_sec_peak"] / merged["traffic_duration_sec_freeflow"]
    )

    avg_by_radius = (
        merged.groupby("radius_km")["traffic_ratio_peak_vs_freeflow"]
        .mean()
        .reset_index()
    )

    avg_pivot = avg_by_radius.pivot_table(
        index=[], columns="radius_km", values="traffic_ratio_peak_vs_freeflow"
    ).rename(columns={5: "c5", 10: "c10", 20: "c20"})

    if {"c5", "c10", "c20"}.issubset(avg_pivot.columns):
        avg_pivot["city_congestion_index"] = (
            WEIGHTS[5] * avg_pivot["c5"] + WEIGHTS[10] * avg_pivot["c10"] + WEIGHTS[20] * avg_pivot["c20"]
        ) / sum(WEIGHTS.values())



    return avg_pivot


# ------------------ MAIN ------------------
if __name__ == "__main__":
    all_data = measure_city(CITY)
    save_results(all_data, OUTPUT_FILE)
    print(f"Raw traffic data saved to {OUTPUT_FILE}")

    congestion_index = compute_city_congestion_index(OUTPUT_FILE)
    print("City-wide congestion index:", CITY)
    print(congestion_index)

    # Prepare JSON data with only city name and city-wide index
    city_index_data = {
    "city": CITY,
    "city_congestion_index": float(congestion_index["city_congestion_index"].iloc[0])
    }

    # Write to JSON file
    
    with open("city_congestion_index.json", "w") as f:
        json.dump(city_index_data, f, indent=4)

