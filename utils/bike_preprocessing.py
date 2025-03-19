import pandas as pd
import numpy as np
import json
import os
import glob
from datetime import datetime
import time
from pathlib import Path
from utils.geocoding import get_coordinates  # Import our new geocoding module

def preprocess_bike_data():
    """
    Process all bike data files and create preprocessed monthly summary files
    for faster API access.
    """
    start_time = time.time()
    print("Starting bike data preprocessing...")
    
    # Create output directory if it doesn't exist
    output_dir = Path('data/processed/bike')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get list of all bike data files
    bike_files = sorted(glob.glob('data/raw/Bike/*.csv'))
    
    # Track all unique months found in the data
    all_months = set()
    
    # Process each file and group by month
    monthly_data = {}
    
    # Keep track of all unique station names
    all_station_names = set()
    
    for i, file_path in enumerate(bike_files):
        print(f"Processing file {i+1}/{len(bike_files)}: {os.path.basename(file_path)}")
        
        try:
            # Read CSV file with optimizations - handle UK date format 
            df = pd.read_csv(
                file_path, 
                parse_dates=['Start date', 'End date'],
                dayfirst=True,  # Handle UK date format (DD/MM/YYYY)
                low_memory=False
            )
            
            # Create month identifier (YYYY-MM format)
            df['month'] = df['Start date'].dt.strftime('%Y-%m')
            
            # Add the months to our tracking set
            months_in_file = df['month'].unique()
            all_months.update(months_in_file)
            
            # Collect unique station names
            start_stations = df['Start station'].unique()
            end_stations = df['End station'].unique()
            all_station_names.update(start_stations)
            all_station_names.update(end_stations)
            
            # Process each month in this file
            for month in months_in_file:
                month_df = df[df['month'] == month]
                
                # Create a new monthly dataframe with only the data we need
                if month not in monthly_data:
                    # Initialize for this month
                    monthly_data[month] = {
                        'summary': {
                            'total_rides': 0,
                            'total_duration_ms': 0,
                            'bike_models': {}
                        },
                        'station_stats': {},
                        'daily_counts': {},
                    }
                
                # Update summary statistics
                monthly_data[month]['summary']['total_rides'] += len(month_df)
                monthly_data[month]['summary']['total_duration_ms'] += month_df['Total duration (ms)'].sum()
                
                # Update bike model counts
                bike_models = month_df['Bike model'].value_counts().to_dict()
                for model, count in bike_models.items():
                    if model in monthly_data[month]['summary']['bike_models']:
                        monthly_data[month]['summary']['bike_models'][model] += count
                    else:
                        monthly_data[month]['summary']['bike_models'][model] = count
                
                # Process station statistics
                for _, row in month_df.iterrows():
                    # Get station names
                    start_station_name = str(row.get('Start station', 'N/A'))
                    end_station_name = str(row.get('End station', 'N/A'))
                    
                    # Get coordinates from our geocoding module
                    start_coords = get_coordinates(start_station_name)
                    end_coords = get_coordinates(end_station_name)
                    
                    # Update start station stats
                    if start_station_name not in monthly_data[month]['station_stats']:
                        monthly_data[month]['station_stats'][start_station_name] = {
                            'pickups': 0,
                            'returns': 0,
                            'lat': start_coords['lat'],
                            'lon': start_coords['lon']
                        }
                    monthly_data[month]['station_stats'][start_station_name]['pickups'] += 1
                    
                    # Update end station stats
                    if end_station_name not in monthly_data[month]['station_stats']:
                        monthly_data[month]['station_stats'][end_station_name] = {
                            'pickups': 0,
                            'returns': 0,
                            'lat': end_coords['lat'],
                            'lon': end_coords['lon']
                        }
                    monthly_data[month]['station_stats'][end_station_name]['returns'] += 1
                    
                    # Update daily counts
                    ride_date = row['Start date'].strftime('%Y-%m-%d')
                    if ride_date not in monthly_data[month]['daily_counts']:
                        monthly_data[month]['daily_counts'][ride_date] = 0
                    monthly_data[month]['daily_counts'][ride_date] += 1
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            continue
    
    # Save each month's data to a separate file
    print(f"Saving {len(monthly_data)} monthly summary files...")
    
    # Create a months index file for easy lookup
    months_index = sorted(list(all_months))
    
    with open(f'{output_dir}/months_index.json', 'w') as f:
        json.dump({'months': months_index}, f)
    
    # Save each month's data
    for month, data in monthly_data.items():
        print(f"Saving month: {month}")
        
        # Calculate derived statistics
        total_rides = data['summary']['total_rides']
        total_duration = data['summary']['total_duration_ms']
        avg_duration = total_duration / total_rides if total_rides > 0 else 0
        
        # Format the top stations lists
        top_pickup_stations = sorted(
            [{
                'name': name,
                'count': stats['pickups'],
                'coordinates': {
                    'lat': stats['lat'],
                    'lon': stats['lon']
                }
            } for name, stats in data['station_stats'].items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        top_return_stations = sorted(
            [{
                'name': name,
                'count': stats['returns'],
                'coordinates': {
                    'lat': stats['lat'],
                    'lon': stats['lon']
                }
            } for name, stats in data['station_stats'].items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        # Prepare final output data structure
        output_data = {
            'month': month,
            'summary': {
                'total_rides': total_rides,
                'avg_duration_ms': int(avg_duration),
                'avg_duration_formatted': format_duration(avg_duration),
                'bike_models': data['summary']['bike_models']
            },
            'top_stations': {
                'pickups': top_pickup_stations,
                'returns': top_return_stations
            },
            'daily_counts': data['daily_counts'],
            'station_stats': data['station_stats']
        }
        
        # Save to JSON file
        with open(f'{output_dir}/{month}.json', 'w') as f:
            json.dump(output_data, f)
    
    # Create a sample journeys file for the frontend
    print("Creating sample journeys file...")
    create_sample_journeys()
    
    # Create yearly summary file
    print("Creating yearly summary file...")
    create_yearly_summary(monthly_data)
    
    # Save the list of all stations (useful for reference)
    print(f"Saving list of {len(all_station_names)} unique station names...")
    with open(f'{output_dir}/all_stations.json', 'w') as f:
        station_list = sorted([s for s in all_station_names if s and str(s).lower() != 'nan'])
        json.dump({'stations': station_list}, f)
    
    elapsed_time = time.time() - start_time
    print(f"Preprocessing complete! Took {elapsed_time:.2f} seconds")

def create_sample_journeys():
    """
    Create a sample of journeys for visualization purposes
    """
    output_dir = Path('data/processed/bike')
    
    # Get a random sampling of bike files
    bike_files = sorted(glob.glob('data/raw/Bike/*.csv'))
    sample_file = np.random.choice(bike_files)
    
    try:
        # Read sample file with UK date format
        df = pd.read_csv(
            sample_file,
            parse_dates=['Start date', 'End date'],
            dayfirst=True  # Handle UK date format (DD/MM/YYYY)
        )
        
        # Take a sample of journeys (limit to 1000 for performance)
        if len(df) > 1000:
            sample_df = df.sample(1000)
        else:
            sample_df = df
        
        # Process the sample
        journeys = []
        
        for _, row in sample_df.iterrows():
            # Get station names
            start_station_name = str(row.get('Start station', 'N/A'))
            end_station_name = str(row.get('End station', 'N/A'))
            
            # Get coordinates from our geocoder
            start_coords = get_coordinates(start_station_name)
            end_coords = get_coordinates(end_station_name)
            
            journey = {
                'id': str(row.get('Number', 'N/A')),
                'start_time': str(row.get('Start date', 'N/A')),
                'start_station': {
                    'id': str(row.get('Start station number', 'N/A')),
                    'name': start_station_name,
                    'coordinates': start_coords
                },
                'end_time': str(row.get('End date', 'N/A')),
                'end_station': {
                    'id': str(row.get('End station number', 'N/A')),
                    'name': end_station_name,
                    'coordinates': end_coords
                },
                'bike': {
                    'number': str(row.get('Bike number', 'N/A')),
                    'model': str(row.get('Bike model', 'CLASSIC'))
                },
                'duration': str(row.get('Total duration', 'N/A')),
                'duration_ms': int(row.get('Total duration (ms)', 0))
            }
            
            journeys.append(journey)
        
        # Save sample journeys
        with open(f'{output_dir}/sample_journeys.json', 'w') as f:
            json.dump({'journeys': journeys}, f)
            
    except Exception as e:
        print(f"Error creating sample journeys: {str(e)}")

def create_yearly_summary(monthly_data):
    """
    Create yearly summary statistics based on the monthly data
    """
    output_dir = Path('data/processed/bike')
    
    # Group months by year
    yearly_data = {}
    
    for month, data in monthly_data.items():
        year = month.split('-')[0]
        
        if year not in yearly_data:
            yearly_data[year] = {
                'total_rides': 0,
                'total_duration_ms': 0,
                'bike_models': {},
                'station_stats': {}
            }
        
        # Add to yearly totals
        yearly_data[year]['total_rides'] += data['summary']['total_rides']
        yearly_data[year]['total_duration_ms'] += data['summary']['total_duration_ms']
        
        # Combine bike models
        for model, count in data['summary']['bike_models'].items():
            if model in yearly_data[year]['bike_models']:
                yearly_data[year]['bike_models'][model] += count
            else:
                yearly_data[year]['bike_models'][model] = count
        
        # Combine station stats
        for station, stats in data['station_stats'].items():
            if station not in yearly_data[year]['station_stats']:
                yearly_data[year]['station_stats'][station] = {
                    'pickups': 0,
                    'returns': 0,
                    'lat': stats['lat'],
                    'lon': stats['lon']
                }
            yearly_data[year]['station_stats'][station]['pickups'] += stats['pickups']
            yearly_data[year]['station_stats'][station]['returns'] += stats['returns']
    
    # Format each year's top stations
    years_summary = {}
    
    for year, data in yearly_data.items():
        avg_duration = data['total_duration_ms'] / data['total_rides'] if data['total_rides'] > 0 else 0
        
        # Get top stations for this year
        top_pickup_stations = sorted(
            [{
                'name': name,
                'count': stats['pickups'],
                'coordinates': {
                    'lat': stats['lat'],
                    'lon': stats['lon']
                }
            } for name, stats in data['station_stats'].items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        top_return_stations = sorted(
            [{
                'name': name,
                'count': stats['returns'],
                'coordinates': {
                    'lat': stats['lat'],
                    'lon': stats['lon']
                }
            } for name, stats in data['station_stats'].items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]
        
        years_summary[year] = {
            'summary': {
                'total_rides': data['total_rides'],
                'avg_duration_ms': int(avg_duration),
                'avg_duration_formatted': format_duration(avg_duration),
                'bike_models': data['bike_models']
            },
            'top_stations': {
                'pickups': top_pickup_stations,
                'returns': top_return_stations
            }
        }
    
    # Save yearly summary
    with open(f'{output_dir}/yearly_summary.json', 'w') as f:
        json.dump({
            'years': sorted(list(yearly_data.keys())),
            'data': years_summary
        }, f)

def format_duration(duration_ms):
    """
    Format duration in milliseconds to a human-readable format (e.g., "5m 30s")
    """
    total_seconds = int(duration_ms / 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}m {seconds}s"

if __name__ == "__main__":
    preprocess_bike_data() 