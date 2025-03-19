"""
Reset and regenerate bike data using the improved geocoding approach.

This script:
1. Deletes all current processed bike data files
2. Calls the preprocessing function to regenerate all data with improved coordinates
"""

import os
import glob
import shutil
from pathlib import Path
from utils.bike_preprocessing import preprocess_bike_data

def reset_bike_data():
    """
    Reset and regenerate all bike data files with improved coordinates
    """
    print("Resetting bike coordinates and regenerating data...")
    
    # Path to processed bike data
    processed_dir = Path('data/processed/bike')
    
    # Delete all JSON files in the processed directory, but maintain directory structure
    if processed_dir.exists():
        print("Deleting existing processed bike data files...")
        for file_path in glob.glob(f'{processed_dir}/*.json'):
            print(f"  Deleting {os.path.basename(file_path)}")
            os.remove(file_path)
    else:
        # Create the directory if it doesn't exist
        processed_dir.mkdir(parents=True, exist_ok=True)
        print("Created processed bike data directory")
    
    # Call the preprocessing function to regenerate the data
    print("\nRegenerating bike data with improved coordinates...")
    preprocess_bike_data()
    
    print("\nBike data has been reset and regenerated with improved station coordinates!")
    print("The new coordinates are based on region matching and will be cached for consistency.")

if __name__ == "__main__":
    reset_bike_data() 