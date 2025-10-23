import json
import time
import subprocess

# Load all locations
with open(r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\bigConfig.json", "r") as f:
    locations = json.load(f)["locations"]

# Path to your config file used by the other program
config_file = r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\config.json"  # or "cong.json"

# Command to run your other program
command = ["python", "main.py"]  # adjust as needed

for loc in locations:
    # Load current config
    with open(config_file, "r") as f:
        config = json.load(f)
    
    # Update the City_Details
    config["City_Details"] = loc
    
    # Save back to the config file
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    
    print(f"Updated config for area: {loc['area']}")
    
    # Run the other program
    subprocess.run(command)
    
    # Optional: wait a little if needed
    time.sleep(0.5)
