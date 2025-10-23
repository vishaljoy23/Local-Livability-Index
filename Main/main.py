import subprocess
import sys
import os

def run_scripts(scripts):
    for script in scripts:
        if not os.path.isfile(script):
            print(f" File not found: {script}")
            continue

        script_dir = os.path.dirname(os.path.abspath(script)) or "."
        script_name = os.path.basename(script)

        print(f"\nRunning {script_name} in {script_dir}...")

        result = subprocess.run(
            [sys.executable, script],
            cwd=script_dir,              #  run script from its own folder
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f" {script_name} finished successfully")
            if result.stdout:
                print("--- Output ---")
                print(result.stdout)
        else:
            print(f" {script_name} failed with return code {result.returncode}")
            if result.stderr:
                print("--- Error ---")
                print(result.stderr)

if __name__ == "__main__":
    # List of Python scripts to run in sequence
    scripts_to_run = [
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\AQI\WAQI_lat_long_API_call.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Congestion\CongestionMeasureFinal.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Water quality\latlon_to_water.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\HDI\cityNameToHDIRank.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Housing\driver.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Place Type Counts\CountPlacesTypeInRadius_StoreinJson.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Voter Turnout\latlonToVotrTurnout.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Water quality\latlon_to_water.py",
        r"C:\Users\visha\OneDrive\Desktop\IIIT-H Research\Final CodePieces\Congestion Local\CongestionMeasureLocal.py",
        r"C:\Users\visha\OneDrive\Desktop\Main\jsoncollect.py"
        # add more as needed
    ]   

    run_scripts(scripts_to_run)
