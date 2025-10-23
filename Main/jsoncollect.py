import json
import csv
import os


# config
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json", "r") as f:
    config = json.load(f)
vector = { 
    "city": config["City_Details"]["city"],
    "area": config["City_Details"]["area"],
    "latitude": config["City_Details"]["latitude"],
    "longitude": config["City_Details"]["longitude"],
    "pincode": config["City_Details"]["pincode"]
}

# AQI data
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\AQI\AQI_data.json", "r") as f:
    aqi_data = json.load(f)
tempvector = {
    "aqi": aqi_data["data"]["aqi"]
}
vector.update(tempvector)

# Water Quality
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Water Quality\WQI_Info.json", "r") as f:
    wqiInfo= json.load(f)
tempvector = {
    "wqi": wqiInfo["WQI"],
    "wqi_category": wqiInfo["WQI_Category"]
}
vector.update(tempvector) #Merge


# City Congestion
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Congestion\city_congestion_index.json", "r") as f:
    congestion= json.load(f)
tempvector = {
    "congestion": congestion["city_congestion_index"]
}
vector.update(tempvector) #Merge

# Local Congestion
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Congestion Local\local_congestion_index.json", "r") as f:
    loc_congestion= json.load(f)
tempvector = {
    "local_congestion": loc_congestion["city_congestion_index"]
}
vector.update(tempvector) #Merge



# Human Developement Index
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\HDI\City_HDI.json", "r") as f:
    HDI= json.load(f)
tempvector = {
    "hdi_rank": HDI["HDI_Rank"],
}
vector.update(tempvector) #Merge

# Housing Price
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Housing\avg_price.json", "r") as f:
    house= json.load(f)
tempvector = {
    "sqft_price": house["avg_price_per_sqft"],
}
vector.update(tempvector) #Merge


# Area Amenity Insights
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Place Type Counts\area_insights.json", "r") as f:
    amenities= json.load(f)
tempvector = {
    "supermarket": amenities["amenities"]["supermarket"],
    "store": amenities["amenities"]["store"],
    "park": amenities["amenities"]["park"],
    "playground": amenities["amenities"]["playground"],
    "hospital": amenities["amenities"]["hospital"],
    "school": amenities["amenities"]["school"],
    "library": amenities["amenities"]["library"],
    "police": amenities["amenities"]["police"],
}
vector.update(tempvector) #Merge



# Voter turnout %age
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Voter Turnout\VoterTurnout.json", "r") as f:
    voter= json.load(f)
tempvector = {
    "voter_turnout": voter["VoterTurnout"],
}
vector.update(tempvector) #Merge

with open("feature.json", "w") as f:
    json.dump(vector, f, indent = 4)

print("Data written")


# CSV file path
csv_file = r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\features.csv"

# Check if the file exists to determine if we need headers
file_exists = os.path.isfile(csv_file)

# Write vector to CSV
with open(csv_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=vector.keys())
    
    # Write headers only if file didn’t exist before
    if not file_exists:
        writer.writeheader()
    
    # Write the vector as a row
    writer.writerow(vector)

print(f" Vector saved to {csv_file}")
