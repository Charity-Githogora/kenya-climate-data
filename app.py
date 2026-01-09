#!/usr/bin/env python3
"""
app.py
Split cleaned station CSVs into county folders.

Assumptions:
- cleaned CSVs are stored under: cleaned_weather_data/
- output top folder will be: Counties/
- files are named like: 63612_Lodwar_cleaned.csv or 63612_Lodwar.csv
- The station->county mapping below should be extended if you add more stations.
"""

import os
import shutil
from pathlib import Path

# Config
CLEANED_DIR = Path("cleaned_weather_data")
OUTPUT_DIR = Path("Counties")

# 47 Kenyan counties list (default order — you can change order if you want specific numbering)
COUNTY_LIST = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita-Taveta", "Garissa", "Wajir",
    "Mandera", "Marsabit", "Isiolo", "Meru", "Tharaka-Nithi", "Embu", "Kitui", "Machakos",
    "Makueni", "Nyandarua", "Nyeri", "Kirinyaga", "Murang'a", "Kiambu", "Turkana",
    "West Pokot", "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo-Marakwet", "Nandi",
    "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado", "Kericho", "Bomet", "Kakamega",
    "Vihiga", "Bungoma", "Busia", "Siaya", "Kisumu", "Homa Bay", "Migori", "Kisii",
    "Nyamira", "Nairobi"
]

# Mapping from station names (as they appear in filenames) -> county (use the mapping you provided)
# Keys here are simplified station name substrings, lowercase.
station_to_county = {
    "lodwar": "Turkana",
    "moyale": "Marsabit",
    "mandera": "Mandera",
    "marsabit": "Marsabit",
    "kitale": "Trans Nzoia",
    "wajir": "Wajir",
    "eldoret_airstrip": "Uasin Gishu",
    "eldoret": "Uasin Gishu",
    "kakamega": "Kakamega",
    "nanyuki": "Laikipia",
    "meru_mulika": "Meru",
    "meru": "Meru",
    "kisumu": "Kisumu",
    "kisii": "Kisii",
    "kericho": "Kericho",
    "nakuru": "Nakuru",
    "nyeri": "Nyeri",
    "embu": "Embu",
    "garissa": "Garissa",
    "narok": "Narok",
    "nairobi_acc_fic_rcc_met_com": "Nairobi",
    "nairobi_acc": "Nairobi",
    "nairobi_ - _dagoretti": "Nairobi",
    "nairobi_dagoretti": "Nairobi",
    "nairobi_ - _wilson": "Nairobi",
    "nairobi_wilson": "Nairobi",
    "nairobi_ - _doonholm": "Nairobi",
    "nairobi_doonholm": "Nairobi",
    "makindu": "Makueni",
    "lamu": "Lamu",
    "voi": "Taita-Taveta",
    "taita": "Taita-Taveta",
    "malindi": "Kilifi",
    "mombasa": "Mombasa",
    "mara_serena_lodge_airstrip": "Narok",
    "masai_mara": "Narok",
    # add more mappings as you add stations
}

# Helper functions
def normalize_name(s: str) -> str:
    """Lowercase, replace spaces and punctuation with underscores for reliable matching."""
    if not s:
        return ""
    s = s.lower().strip()
    replacements = ["-", " ", "/", "\\", ".", ",", "(", ")", "__"]
    for r in replacements:
        s = s.replace(r, "_")
    # collapse multiple underscores
    while "__" in s:
        s = s.replace("__", "_")
    return s

def create_county_folders(base_dir: Path, county_list):
    base_dir.mkdir(exist_ok=True)
    created = []
    for i, county in enumerate(county_list, start=1):
        code = f"{i:02d}"
        safe_name = county.replace(" ", "_").replace("/", "_")
        folder_name = f"{code}_{safe_name}"
        folder = base_dir / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        created.append(folder)
    # Unknown folder
    unknown = base_dir / "99_Unknown"
    unknown.mkdir(exist_ok=True)
    created.append(unknown)
    return created

def find_county_for_filename(filename: str):
    """Try to identify county from filename using mapping and substring matching."""
    key = normalize_name(filename)
    # direct mapping keys check (exact or contains)
    for k, county in station_to_county.items():
        if k in key:
            return county
    # try matching by county name contained in filename
    for county in COUNTY_LIST:
        if normalize_name(county) in key:
            return county
    # try splitting filename parts
    parts = key.split("_")
    for part in parts[::-1]:
        if part in station_to_county:
            return station_to_county[part]
    return None

def main():
    if not CLEANED_DIR.exists():
        print(f"ERROR: cleaned directory not found: {CLEANED_DIR}")
        return

    print(f"Creating county folders under: {OUTPUT_DIR}")
    create_county_folders(OUTPUT_DIR, COUNTY_LIST)

    files = sorted([f for f in CLEANED_DIR.iterdir() if f.is_file() and f.suffix.lower() in (".csv", ".txt")])
    total = len(files)
    print(f"Found {total} files in {CLEANED_DIR}")

    moved = 0
    skipped = 0
    for f in files:
        fname = f.name
        county = find_county_for_filename(fname)
        if county is None:
            dest_folder = OUTPUT_DIR / "99_Unknown"
            reason = "no mapping"
        else:
            # find folder with matching county name in created folders
            # we find the folder by checking name contains normalized county
            normalized_county = normalize_name(county)
            dest_folder = None
            for child in OUTPUT_DIR.iterdir():
                if normalized_county in normalize_name(child.name):
                    dest_folder = child
                    break
            if dest_folder is None:
                dest_folder = OUTPUT_DIR / "99_Unknown"
                reason = "folder not found"
            else:
                reason = "mapped"

        dest_path = dest_folder / fname
        # Copy file (do not remove source), use copy2 to preserve metadata
        shutil.copy2(f, dest_path)
        print(f"Copied: {fname} -> {dest_folder.name} ({reason})")
        moved += 1

    print("\nSummary:")
    print(f"Total files processed: {total}")
    print(f"Total files copied: {moved}")
    print(f"Unknown / unmapped files placed in: {OUTPUT_DIR / '99_Unknown'}")
    print("Done.")

if __name__ == "__main__":
    main()
