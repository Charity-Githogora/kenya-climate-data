from datetime import datetime
from meteostat import Stations, Daily
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Define time range (10 years)
start = datetime(2015, 1, 1)
end = datetime(2025, 10, 29)

# Create a folder to store CSVs
os.makedirs("weather_data", exist_ok=True)

# Fetch all weather stations in Kenya
stations = Stations().region('KE').fetch()

print(f"Found {len(stations)} weather stations in Kenya\n")

def fetch_station_data(station_id, station_name):
    """Fetch data for a single station"""
    data = Daily(station_id, start, end).fetch()
    return data

# Get list of already downloaded files
existing_files = set(os.listdir("weather_data"))

# Loop through each station
skipped_count = 0
for idx, station_id in enumerate(stations.index, 1):
    try:
        station_name = stations.loc[station_id, 'name'] if 'name' in stations.columns else str(station_id)
        file_name = f"{station_id}_{station_name.replace(' ', '_').replace('/', '-')}.csv"
        
        # Check if file already exists
        if file_name in existing_files:
            skipped_count += 1
            print(f"[{idx}/{len(stations)}] ⏭️ Already exists: {station_name} ({station_id})")
            continue
        
        print(f"[{idx}/{len(stations)}] Fetching: {station_name} ({station_id})")
        
        # Use ThreadPoolExecutor with timeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fetch_station_data, station_id, station_name)
            try:
                data = future.result(timeout=30)  # 30 second timeout
                
                if not data.empty:
                    full_path = f"weather_data/{file_name}"
                    data.to_csv(full_path)
                    print(f"✅ Saved ({len(data)} records)\n")
                else:
                    print(f"⚠️ No data\n")
            except TimeoutError:
                print(f"⏱️ TIMEOUT - Skipping\n")
                
    except Exception as e:
        print(f"❌ Error: {e}\n")

print(f"\n✅ All done! (Skipped {skipped_count} already downloaded)")