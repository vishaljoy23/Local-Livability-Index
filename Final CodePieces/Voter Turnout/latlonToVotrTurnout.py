import pandas as pd
import json
import math

# ---------------- Haversine distance ----------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ---------------- Read config ----------------
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json", "r", encoding="utf-8") as f:
    config = json.load(f)



target_lat = config["City_Details"]["latitude"]
target_lon = config["City_Details"]["longitude"]

# ---------------- Read CSV ----------------
df = pd.read_csv("StateAreaPercentageLatLon.csv")

# ---------------- Find closest ----------------
min_dist = float("inf")
closest_total = None

for _, row in df.iterrows():
    if pd.notnull(row["Latitude"]) and pd.notnull(row["Longitude"]):
        dist = haversine(target_lat, target_lon, row["Latitude"], row["Longitude"])
        if dist < min_dist:
            min_dist = dist
            closest_total = row["Total"]

# ---------------- Save result ----------------
output = {"VoterTurnout": closest_total}

with open("VoterTurnout.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4)

print("Saved closest turnout to VoterTurnout.json")
