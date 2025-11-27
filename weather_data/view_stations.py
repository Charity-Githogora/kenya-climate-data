from meteostat import Stations
import pandas as pd

# Step 1: Search for weather stations in Kenya
stations = Stations().region('KE').fetch()

# Step 2: Check how many stations were found
print(f"\n✅ Found {len(stations)} weather stations in Kenya\n")

# Step 3: Display available columns
print("📋 Columns available:")
print(stations.columns.tolist())

# Step 4: Display station names and IDs
if 'name' in stations.columns:
    print("\n🛰️ Weather station names in Kenya:\n")
    print(stations[['name', 'latitude', 'longitude', 'elevation']])
else:
    print("\n⚠️ 'name' column not found. Here's what we have instead:\n")
    print(stations.head())

# Step 5 (optional): Save to CSV for later use
stations.to_csv('kenya_weather_stations.csv', index=False)
print("\n💾 Saved station list to 'kenya_weather_stations.csv'\n")
