import json
import pandas as pd

# Step 1: Load config.json
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

city_name = config["City_Details"]["city"]

# Step 2: Read the sorted HDI CSV
df = pd.read_csv("hdi_rank_sorted.csv")

# Step 3: Partial, case-insensitive match
matches = df[df["District"].str.lower().str.contains(city_name.lower())]

if not matches.empty:
    # Take the first match
    hdi_rank = int(matches.iloc[0]["Rank in HDI"])
    matched_name = matches.iloc[0]["District"]
    print(f"Found match: {matched_name} with HDI Rank {hdi_rank}")
else:
    matched_name = None
    hdi_rank = None
    print(f"No match found for {city_name} in the HDI dataset.")

# Step 4: Write result to JSON
output_data = {
    "City": city_name,
    "HDI_Rank": hdi_rank
}

with open("city_hdi.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=4)

print("Saved city HDI info to city_hdi.json")
