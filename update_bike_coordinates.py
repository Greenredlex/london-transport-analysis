"""
Update bike coordinates using a geocoding API.

This script provides a complete workflow to:
1. Run the bike preprocessing to generate initial data and station list
2. Geocode all bike station names using a geocoding API 
3. Regenerate all bike data with the accurate coordinates

Usage:
    python update_bike_coordinates.py
"""

import os
import time
import sys
from pathlib import Path

# Directory paths
PROCESSED_DIR = Path('data/processed/bike')

def clear_processed_data():
    """
    Clear all processed bike data files to start fresh
    """
    print("Clearing existing processed bike data...")
    
    if PROCESSED_DIR.exists():
        # Delete all JSON files except the geocoded_stations.json file
        deleted_count = 0
        for file_path in PROCESSED_DIR.glob('*.json'):
            if file_path.name != 'geocoded_stations.json':
                print(f"  Deleting {file_path.name}")
                os.remove(file_path)
                deleted_count += 1
        
        print(f"Deleted {deleted_count} processed files")
    else:
        # Create the directory if it doesn't exist
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        print("Created processed bike data directory")

def run_initial_preprocessing():
    """
    Run the initial preprocessing to generate the station list
    """
    print("\nRunning initial preprocessing to generate station list...")
    
    try:
        from utils.bike_preprocessing import preprocess_bike_data
        preprocess_bike_data()
        return True
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")
        return False

def run_geocoding():
    """
    Run the geocoding script to geocode all station names
    """
    print("\nGeocode bike stations using the geocoding API...")
    
    try:
        # Import and run the geocoding script
        sys.path.append('.')  # Make sure we can import from the current directory
        from geocode_bike_stations import geocode_all_stations
        geocoded_data = geocode_all_stations()
        return bool(geocoded_data)
    except Exception as e:
        print(f"Error during geocoding: {str(e)}")
        return False

def regenerate_with_geocoded_coordinates():
    """
    Regenerate all bike data using the geocoded coordinates
    """
    print("\nRegenerating bike data with geocoded coordinates...")
    
    try:
        # Clear processed data except the geocoded_stations.json file
        for file_path in PROCESSED_DIR.glob('*.json'):
            if file_path.name not in ['geocoded_stations.json']:
                os.remove(file_path)
        
        # Run preprocessing again
        from utils.bike_preprocessing import preprocess_bike_data
        preprocess_bike_data()
        return True
    except Exception as e:
        print(f"Error during regeneration: {str(e)}")
        return False

def main():
    """
    Main workflow function
    """
    start_time = time.time()
    print("Starting the bike coordinates update workflow...")
    
    # Step 1: Clear processed data
    clear_processed_data()
    
    # Step 2: Run initial preprocessing to get station list
    if not run_initial_preprocessing():
        print("Initial preprocessing failed. Aborting.")
        return
    
    # Step 3: Run geocoding to get accurate coordinates
    if not run_geocoding():
        print("Geocoding failed. Aborting.")
        return
    
    # Step 4: Regenerate all data with the accurate geocoded coordinates
    if not regenerate_with_geocoded_coordinates():
        print("Regeneration failed. Aborting.")
        return
    
    elapsed_time = time.time() - start_time
    print(f"\nSuccess! All bike data has been updated with accurate coordinates.")
    print(f"Total processing time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main() 