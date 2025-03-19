"""
Update all bike station coordinates in processed files using the geocoded_stations.json file.

This script:
1. Loads the geocoded_stations.json file with accurate coordinates
2. Updates all coordinates in the monthly data files
3. Updates coordinates in sample_journeys.json
4. Reports the number of stations updated

Usage:
    python update_station_coordinates.py
"""

import json
import os
import glob
from pathlib import Path

# Directory paths 
PROCESSED_DIR = Path('data/processed/bike')
GEOCODED_FILE = PROCESSED_DIR / 'geocoded_stations.json'

def load_geocoded_coordinates():
    """
    Load the geocoded coordinates from the reference file
    """
    print(f"Loading geocoded coordinates from {GEOCODED_FILE}...")
    
    try:
        with open(GEOCODED_FILE, 'r') as f:
            geocoded_data = json.load(f)
            
        print(f"Loaded {len(geocoded_data)} geocoded stations")
        return geocoded_data
    except Exception as e:
        print(f"Error loading geocoded data: {str(e)}")
        return {}

def update_monthly_files(geocoded_data):
    """
    Update coordinates in all monthly data files
    """
    monthly_files = sorted(glob.glob(str(PROCESSED_DIR / '*.json')))
    
    # Filter out non-monthly files (those that don't follow YYYY-MM.json pattern)
    monthly_files = [f for f in monthly_files if os.path.basename(f).replace('.json', '').count('-') == 1]
    
    if not monthly_files:
        print("No monthly data files found.")
        return 0
    
    print(f"Found {len(monthly_files)} monthly data files to update")
    
    total_stations_updated = 0
    
    for file_path in monthly_files:
        file_name = os.path.basename(file_path)
        print(f"Updating {file_name}...")
        
        try:
            # Load the monthly data
            with open(file_path, 'r') as f:
                monthly_data = json.load(f)
            
            # Keep track of updated stations for this file
            updated_count = 0
            
            # Update station coordinates
            for station_name, stats in monthly_data.get('station_stats', {}).items():
                if station_name in geocoded_data:
                    # Update with coordinates from geocoded data
                    stats['lat'] = geocoded_data[station_name]['lat']
                    stats['lon'] = geocoded_data[station_name]['lon']
                    updated_count += 1
            
            # Save the updated file
            with open(file_path, 'w') as f:
                json.dump(monthly_data, f)
            
            print(f"  Updated {updated_count} stations in {file_name}")
            total_stations_updated += updated_count
            
        except Exception as e:
            print(f"Error updating {file_name}: {str(e)}")
    
    return total_stations_updated

def update_sample_journeys(geocoded_data):
    """
    Update coordinates in the sample_journeys.json file
    """
    sample_file = PROCESSED_DIR / 'sample_journeys.json'
    
    if not sample_file.exists():
        print("Sample journeys file not found.")
        return 0
    
    print("Updating sample journeys file...")
    
    try:
        # Load the sample journeys
        with open(sample_file, 'r') as f:
            journeys_data = json.load(f)
        
        # Keep track of updated stations
        updated_count = 0
        
        # Update each journey's station coordinates
        for journey in journeys_data.get('journeys', []):
            # Update start station coordinates
            start_station_name = journey.get('start_station', {}).get('name')
            if start_station_name and start_station_name in geocoded_data:
                journey['start_station']['coordinates'] = {
                    'lat': geocoded_data[start_station_name]['lat'],
                    'lon': geocoded_data[start_station_name]['lon']
                }
                updated_count += 1
            
            # Update end station coordinates
            end_station_name = journey.get('end_station', {}).get('name')
            if end_station_name and end_station_name in geocoded_data:
                journey['end_station']['coordinates'] = {
                    'lat': geocoded_data[end_station_name]['lat'],
                    'lon': geocoded_data[end_station_name]['lon']
                }
                updated_count += 1
        
        # Save the updated file
        with open(sample_file, 'w') as f:
            json.dump(journeys_data, f)
        
        print(f"  Updated {updated_count} station references in sample journeys")
        return updated_count
    
    except Exception as e:
        print(f"Error updating sample journeys: {str(e)}")
        return 0

def main():
    """
    Main function to update all coordinates
    """
    print("Starting station coordinates update...")
    
    # Check if the geocoded file exists
    if not GEOCODED_FILE.exists():
        print(f"Error: Geocoded stations file not found at {GEOCODED_FILE}")
        print("Please run the geocode_bike_stations.py script first.")
        return
    
    # Load the geocoded coordinates
    geocoded_data = load_geocoded_coordinates()
    if not geocoded_data:
        print("No geocoded data found. Aborting.")
        return
    
    # Update monthly files
    monthly_updated = update_monthly_files(geocoded_data)
    
    # Update sample journeys
    sample_updated = update_sample_journeys(geocoded_data)
    
    # Print summary
    print("\nUpdate complete!")
    print(f"Updated {monthly_updated} station entries in monthly files")
    print(f"Updated {sample_updated} station references in sample journeys")
    print(f"Total coordinates updated: {monthly_updated + sample_updated}")

if __name__ == "__main__":
    main() 