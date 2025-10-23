import json

# Example JSON string
with open("bigConfig.json", "r") as f:
    all = json.load(f)

# Load JSON into Python object
data = all["locations"]
# If it's a list
if isinstance(data, list):
    count = len(data)

# If it's a dictionary
elif isinstance(data, dict):
    count = len(data.keys())

print("Number of entries:", count)
