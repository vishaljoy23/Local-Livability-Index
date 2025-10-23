#this reads lat long from config and retrieves waqi score
# 
# 
import pandas as pd
import json
from math import radians, cos, sin, sqrt, atan2

# ---------------- Load CSV ----------------
df = pd.read_csv("groundwater_wqi.csv")

# ---------------- Helper function to compute distance (Haversine) ----------------
def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 
    r = 6371 # Radius of earth in km
    return c * r

# ---------------- Function to search by latitude & longitude ----------------
def search_wqi(lat, lon):
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        return {"error": "Latitude/Longitude columns not found"}
    
    # Compute distance to each point
    df['distance'] = df.apply(lambda row: haversine(lat, lon, row['Latitude'], row['Longitude']), axis=1)
    
    # Find the closest point
    closest = df.loc[df['distance'].idxmin()]
    
    result = {
        "State": closest['State'],
        "District": closest['District'],
        "Location": closest['Location'],
        "WQI": closest['WQI'],
        "WQI_Category": closest['WQI_Category']
    }
    return result

# ---------------- Example usage ----------------
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

latitude_input = config["City_Details"]["latitude"]
longitude_input = config["City_Details"]["longitude"]

result_json = search_wqi(latitude_input, longitude_input)

output_file = "WQI_Info.json"
with open("WQI_Info.json", "w") as f:
    json.dump(result_json, f, indent = 4)

print("Results saved to WQI_Info.json")

