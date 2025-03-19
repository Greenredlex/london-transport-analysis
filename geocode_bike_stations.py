"""
Geocode all bike stations using a geocoding API to get accurate coordinates.

This script:
1. Loads the list of all bike station names from all_stations.json
2. Geocodes each station name using the Nominatim (OpenStreetMap) geocoding API
3. Saves the geocoded coordinates to a reference file for use in preprocessing
"""

import json
import time
import requests
import os
from pathlib import Path
from urllib.parse import quote

# Directory paths
PROCESSED_DIR = Path('data/processed/bike')
REFERENCE_FILE = PROCESSED_DIR / 'geocoded_stations.json'

# Nominatim API settings (OpenStreetMap's free geocoding service)
NOMINATIM_API = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "London-Transport-Analysis/1.0"  # Required by Nominatim terms of use

def load_station_names():
    """Load all station names from the all_stations.json file"""
    try:
        all_stations_path = PROCESSED_DIR / 'all_stations.json'
        if all_stations_path.exists():
            with open(all_stations_path, 'r') as f:
                data = json.load(f)
                return data.get('stations', [])
        else:
            print(f"Station list file not found: {all_stations_path}")
            return []
    except Exception as e:
        print(f"Error loading station names: {str(e)}")
        return []

def load_existing_geocodes():
    """Load existing geocoded data if available"""
    if REFERENCE_FILE.exists():
        try:
            with open(REFERENCE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing geocoded data: {str(e)}")
    
    return {}

def save_geocoded_data(geocoded_data):
    """Save geocoded data to reference file"""
    try:
        # Ensure directory exists
        REFERENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(REFERENCE_FILE, 'w') as f:
            json.dump(geocoded_data, f, indent=2)
        print(f"Geocoded data saved to {REFERENCE_FILE}")
    except Exception as e:
        print(f"Error saving geocoded data: {str(e)}")

def geocode_station(station_name):
    """
    Geocode a single station name using Nominatim API
    
    Args:
        station_name: Name of the bike station
        
    Returns:
        Dictionary with lat and lon coordinates, or None if geocoding failed
    """
    try:
        # Add context to improve geocoding accuracy - specify London, UK
        search_term = f"{station_name}, London, UK"
        
        # URL encode the search term
        encoded_term = quote(search_term)
        
        # Build the API request URL
        url = f"{NOMINATIM_API}?q={encoded_term}&format=json&limit=1&addressdetails=0"
        
        # Set headers with user agent as required by Nominatim
        headers = {
            "User-Agent": USER_AGENT
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        
        # Respect rate limiting (1 request per second as per Nominatim guidelines)
        time.sleep(1)
        
        if response.status_code == 200:
            results = response.json()
            if results:
                # Return the first result's coordinates
                return {
                    'lat': float(results[0]['lat']),
                    'lon': float(results[0]['lon']),
                    'display_name': results[0].get('display_name', ''),
                    'source': 'nominatim'
                }
        
        return None
    
    except Exception as e:
        print(f"Error geocoding station '{station_name}': {str(e)}")
        return None

def geocode_all_stations():
    """
    Geocode all bike stations and save coordinates to reference file
    """
    # Load existing geocoded data if available
    geocoded_data = load_existing_geocodes()
    print(f"Loaded {len(geocoded_data)} previously geocoded stations")
    
    # Load list of all station names
    station_names = load_station_names()
    print(f"Loaded {len(station_names)} station names from all_stations.json")
    
    if not station_names:
        print("No station names found. Make sure to run bike preprocessing first.")
        return
    
    # Calculate stations that need geocoding
    stations_to_geocode = [name for name in station_names if name not in geocoded_data]
    print(f"Need to geocode {len(stations_to_geocode)} new stations")
    
    # Geocode each station that's not already in our data
    successful = 0
    failed = 0
    
    for i, station_name in enumerate(stations_to_geocode):
        print(f"Geocoding {i+1}/{len(stations_to_geocode)}: {station_name}")
        
        # Skip empty or NaN station names
        if not station_name or station_name.lower() == 'nan':
            continue
        
        # Geocode the station
        result = geocode_station(station_name)
        
        if result:
            geocoded_data[station_name] = result
            successful += 1
        else:
            failed += 1
            # Use a fallback for failed geocoding - Central London with slight offset
            # This ensures we have coordinates for all stations
            import random
            geocoded_data[station_name] = {
                'lat': 51.5074 + (random.random() - 0.5) * 0.02,
                'lon': -0.1278 + (random.random() - 0.5) * 0.02,
                'display_name': 'Not found - using fallback',
                'source': 'fallback'
            }
    
    # Save updated geocoded data
    save_geocoded_data(geocoded_data)
    
    # Print summary
    print(f"Geocoding complete!")
    print(f"Successfully geocoded: {successful} stations")
    print(f"Failed to geocode: {failed} stations")
    print(f"Total geocoded stations: {len(geocoded_data)}")
    
    # Return the data for use in preprocessing
    return geocoded_data

if __name__ == "__main__":
    geocode_all_stations() 