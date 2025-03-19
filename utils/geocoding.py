import os
import json
import math
import re
from pathlib import Path
import random

# Reference file with geocoded stations
GEOCODED_FILE = 'data/processed/bike/geocoded_stations.json'

# Cache file path for coordinates not in the reference data
CACHE_FILE = 'data/processed/bike/station_coordinates_cache.json'

# Coordinates for central London as a fallback
LONDON_CENTER = {
    'lat': 51.5074,
    'lon': -0.1278
}

# Define known regions in London with approximate coordinates
LONDON_REGIONS = {
    'angel': {'lat': 51.5320, 'lon': -0.1058},
    'baker street': {'lat': 51.5226, 'lon': -0.1571},
    'bank': {'lat': 51.5132, 'lon': -0.0891},
    'barbican': {'lat': 51.5201, 'lon': -0.0942},
    'battersea': {'lat': 51.4778, 'lon': -0.1477},
    'belgravia': {'lat': 51.4991, 'lon': -0.1526},
    'bermondsey': {'lat': 51.4991, 'lon': -0.0715},
    'bethnal green': {'lat': 51.5271, 'lon': -0.0632},
    'bloomsbury': {'lat': 51.5209, 'lon': -0.1277},
    'borough': {'lat': 51.5017, 'lon': -0.0944},
    'brixton': {'lat': 51.4629, 'lon': -0.1147},
    'camden': {'lat': 51.5390, 'lon': -0.1426},
    'canada water': {'lat': 51.4982, 'lon': -0.0502},
    'canary wharf': {'lat': 51.5054, 'lon': -0.0235},
    'chelsea': {'lat': 51.4878, 'lon': -0.1690},
    'city of london': {'lat': 51.5155, 'lon': -0.0922},
    'clerkenwell': {'lat': 51.5225, 'lon': -0.1055},
    'covent garden': {'lat': 51.5117, 'lon': -0.1240},
    'earls court': {'lat': 51.4915, 'lon': -0.1947},
    'elephant and castle': {'lat': 51.4943, 'lon': -0.1000},
    'euston': {'lat': 51.5282, 'lon': -0.1337},
    'farringdon': {'lat': 51.5204, 'lon': -0.1053},
    'hammersmith': {'lat': 51.4927, 'lon': -0.2224},
    'holborn': {'lat': 51.5174, 'lon': -0.1192},
    'islington': {'lat': 51.5362, 'lon': -0.1033},
    'kennington': {'lat': 51.4883, 'lon': -0.1063},
    'kensington': {'lat': 51.5009, 'lon': -0.1925},
    'kings cross': {'lat': 51.5308, 'lon': -0.1238},
    'knightsbridge': {'lat': 51.5016, 'lon': -0.1606},
    'lambeth': {'lat': 51.4916, 'lon': -0.1177},
    'maida vale': {'lat': 51.5304, 'lon': -0.1858},
    'marylebone': {'lat': 51.5225, 'lon': -0.1546},
    'mayfair': {'lat': 51.5117, 'lon': -0.1492},
    'notting hill': {'lat': 51.5156, 'lon': -0.1967},
    'old street': {'lat': 51.5258, 'lon': -0.0882},
    'paddington': {'lat': 51.5173, 'lon': -0.1746},
    'pimlico': {'lat': 51.4893, 'lon': -0.1334},
    'regents park': {'lat': 51.5313, 'lon': -0.1570},
    'shoreditch': {'lat': 51.5245, 'lon': -0.0786},
    'soho': {'lat': 51.5141, 'lon': -0.1350},
    'southwark': {'lat': 51.5046, 'lon': -0.1059},
    'st james': {'lat': 51.5065, 'lon': -0.1366},
    'st pauls': {'lat': 51.5148, 'lon': -0.0982},
    'strand': {'lat': 51.5117, 'lon': -0.1199},
    'tower bridge': {'lat': 51.5055, 'lon': -0.0754},
    'vauxhall': {'lat': 51.4861, 'lon': -0.1229},
    'victoria': {'lat': 51.4950, 'lon': -0.1436},
    'waterloo': {'lat': 51.5036, 'lon': -0.1143},
    'west end': {'lat': 51.5126, 'lon': -0.1387},
    'westminster': {'lat': 51.4995, 'lon': -0.1248},
    'whitechapel': {'lat': 51.5155, 'lon': -0.0681}
}

# Load geocoded stations from reference file
def load_geocoded_stations():
    """Load the geocoded stations from the reference file"""
    if os.path.exists(GEOCODED_FILE):
        try:
            with open(GEOCODED_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading geocoded stations: {str(e)}")
    
    return {}

# Load the coordinates cache (creating it if it doesn't exist)
def load_coordinates_cache():
    """Load coordinates from cache file, create if doesn't exist"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading coordinates cache: {str(e)}")
    
    # Create the directory if needed
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    # Return empty cache
    return {}

# Save coordinates to cache
def save_coordinates_cache(cache):
    """Save coordinates cache to file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving coordinates cache: {str(e)}")

# Load geocoded stations and coordinates cache
GEOCODED_STATIONS = load_geocoded_stations()
COORDINATES_CACHE = load_coordinates_cache()

def get_coordinates(station_name):
    """
    Get coordinates for a bike station name
    
    First tries the geocoded reference file, then falls back to cache 
    and region-based positioning for unknown stations.
    
    Args:
        station_name: Name of the bike station
        
    Returns:
        Dictionary with 'lat' and 'lon' keys
    """
    # Handle null or empty values
    if not station_name or str(station_name).lower() == 'nan':
        return LONDON_CENTER.copy()
    
    # Try geocoded reference data first (highest priority)
    if station_name in GEOCODED_STATIONS:
        data = GEOCODED_STATIONS[station_name]
        return {
            'lat': data['lat'],
            'lon': data['lon']
        }
    
    # Check cache next
    if station_name in COORDINATES_CACHE:
        return COORDINATES_CACHE[station_name].copy()
    
    # Clean up station name
    clean_name = str(station_name).strip().lower()
    
    # Extract region from station name
    coordinates = extract_region_coordinates(clean_name)
    
    # Add some randomness based on name to distribute stations
    # Use hash for deterministic "randomness" based on name
    name_hash = hash(clean_name)
    random_offset = 0.002  # About 200 meters
    
    # Add slight randomness based on hash of name
    coordinates['lat'] += (name_hash % 1000) / 1000 * random_offset
    coordinates['lon'] += ((name_hash // 1000) % 1000) / 1000 * random_offset
    
    # Round to 6 decimal places (about 10cm precision)
    coordinates['lat'] = round(coordinates['lat'], 6)
    coordinates['lon'] = round(coordinates['lon'], 6)
    
    # Cache the result
    COORDINATES_CACHE[station_name] = coordinates.copy()
    save_coordinates_cache(COORDINATES_CACHE)
    
    return coordinates

def extract_region_coordinates(station_name):
    """
    Extract London region from station name and return its coordinates
    """
    # Common words that can be ignored in matching
    common_words = [
        'station', 'bike', 'docking', 'stand', 'dock', 'point', 
        'north', 'south', 'east', 'west', 'central', 'upper', 'lower',
        'street', 'road', 'avenue', 'lane', 'place', 'square', 'corner',
        'the', 'and', 'of', 'in', 'on', 'at'
    ]
    
    # Clean up station name - remove commas, etc.
    cleaned_name = re.sub(r'[^\w\s]', ' ', station_name).lower()
    
    # Check full name against regions first
    for region, coords in LONDON_REGIONS.items():
        if region in cleaned_name:
            return coords.copy()
    
    # Split into words and remove common words
    words = cleaned_name.split()
    meaningful_words = [word for word in words if word not in common_words]
    
    # Check if any of the words match a region
    for word in meaningful_words:
        for region, coords in LONDON_REGIONS.items():
            region_words = region.split()
            if word in region_words:
                return coords.copy()
    
    # If no region match, use hashing to create a point near central London
    # This ensures the same station name always gets the same coordinates
    name_hash = hash(station_name)
    
    # Create a deterministic point within central London
    # Use a spiral pattern to distribute points
    angle = (name_hash % 360) * (math.pi / 180)  # Convert to radians
    radius = 0.01 * (abs(name_hash) % 100) / 100  # 0 to 0.01 degrees (about 1km)
    
    # Create coordinates with spiral pattern
    lat = LONDON_CENTER['lat'] + radius * math.cos(angle)
    lon = LONDON_CENTER['lon'] + radius * math.sin(angle)
    
    return {'lat': lat, 'lon': lon} 