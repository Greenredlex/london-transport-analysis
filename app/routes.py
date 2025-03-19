from flask import render_template, request, Blueprint, jsonify
import pandas as pd
import numpy as np
import json
import os
import glob
from datetime import datetime
from utils.data_processing import load_data
from utils.correlation_utils import analyze_correlations
from functools import lru_cache

main = Blueprint('main', __name__)

underground_data, bike_sharing_data, weather_data = load_data()


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/weather')
def weather():
    return render_template('visualizations/weather.html')

@main.route('/metro_stations')
def metro_stations():
    return render_template('visualizations/metro_stations.html')

@main.route('/correlations')
def correlations():
    try:
        correlation_results = analyze_correlations(underground_data, bike_sharing_data, weather_data)
        
        # Format the correlations for the chart
        formatted_correlations = {
            'labels': [],
            'values': []
        }
        
        # Process correlation_results to extract labels and values
        for key, value in correlation_results.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    # Check if the value is JSON serializable
                    if callable(sub_value):
                        # Skip functions/methods or convert to string representation
                        continue
                    
                    # Convert numpy values to Python native types if needed
                    if hasattr(sub_value, 'item'):  # Handle numpy values
                        sub_value = sub_value.item()
                    
                    formatted_correlations['labels'].append(f"{key} - {sub_key}")
                    formatted_correlations['values'].append(sub_value)
        
        return render_template('visualizations/correlations.html', correlations=formatted_correlations)
    except Exception as e:
        # Debug information to help identify the error
        print(f"Error in correlations route: {str(e)}")
        return render_template('visualizations/correlations.html', 
                              correlations={'labels': [], 'values': []})

@main.route('/api/correlations')
def api_correlations():
    try:
        correlation_results = analyze_correlations(underground_data, bike_sharing_data, weather_data)
        
        # Format the correlations for the chart
        formatted_correlations = {
            'labels': [],
            'values': []
        }
        
        # Process correlation_results to extract labels and values
        for key, value in correlation_results.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    # Check if the value is JSON serializable
                    if callable(sub_value):
                        # Skip functions/methods or convert to string representation
                        continue
                    
                    # Convert numpy values to Python native types if needed
                    if hasattr(sub_value, 'item'):  # Handle numpy values
                        sub_value = sub_value.item()
                    
                    formatted_correlations['labels'].append(f"{key} - {sub_key}")
                    formatted_correlations['values'].append(sub_value)
        
        return formatted_correlations
    except Exception as e:
        # Debug information to help identify the error
        print(f"Error in correlations route: {str(e)}")
        return {'labels': [], 'values': []}

@main.route('/api/weather')
def api_weather():
    try:
        # Use cached data processing function
        return get_weather_data(
            request.args.get('start_date', '2019-01-01'),
            request.args.get('end_date', '2023-12-31')
        )
    except Exception as e:
        print(f"Error in weather API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@lru_cache(maxsize=1)  # Cache the most recent result
def get_weather_data(start_date, end_date):
    """Process and return weather data with caching for better performance."""
    # Load data from CSV file
    weather_data = pd.read_csv(r'data\raw\Weather\london_weather_data_1979_to_2023.csv')
    
    # Filter weather data by date range
    filtered_data = weather_data[(weather_data['DATE'] >= int(start_date.replace('-', ''))) & 
                                (weather_data['DATE'] <= int(end_date.replace('-', '')))]
    
    # Prepare daily data
    daily_data = []
    for _, row in filtered_data.iterrows():
        # Replace NaN values with 0 before converting to float
        daily_record = {
            'date': str(row['DATE']),
            'tx': float(row['TX'] if pd.notna(row['TX']) else 0),  # Max temperature
            'tn': float(row['TN'] if pd.notna(row['TN']) else 0),  # Min temperature
            'tg': float(row['TG'] if pd.notna(row['TG']) else 0),  # Ground temperature
            'rr': float(row['RR'] if pd.notna(row['RR']) else 0),  # Rainfall
            'ss': float(row['SS'] if pd.notna(row['SS']) else 0),  # Sunshine duration
            'hu': float(row['HU'] if pd.notna(row['HU']) else 0),  # Humidity
            'cc': float(row['CC'] if pd.notna(row['CC']) else 0)   # Cloud cover
        }
        daily_data.append(daily_record)
    
    # Calculate summary statistics
    avg_temp = np.mean(filtered_data[['TX', 'TN']].fillna(0).mean(axis=1)) / 10  # Convert to Celsius
    max_temp = np.max(filtered_data['TX'].fillna(0)) / 10  # Convert to Celsius
    min_temp = np.min(filtered_data['TN'].fillna(0)) / 10  # Convert to Celsius
    rainy_days = np.sum(filtered_data['RR'] > 0)
    
    # Prepare monthly averages
    # Extract month from DATE (YYYYMMDD format)
    filtered_data['MONTH'] = filtered_data['DATE'].astype(str).str[4:6].astype(int)
    
    monthly_data = []
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for month in range(1, 13):
        month_data = filtered_data[filtered_data['MONTH'] == month]
        if not month_data.empty:
            monthly_data.append({
                'month': month_names[month-1],
                'avg_temp': float(np.mean(month_data[['TX', 'TN']].fillna(0).mean(axis=1)) / 10),
                'avg_rainfall': float(np.mean(month_data['RR'].fillna(0)) / 10),
                'avg_sunshine': float(np.mean(month_data['SS'].fillna(0)) / 10)
            })
    
    # Prepare response
    response = {
        'summary': {
            'avg_temp': float(avg_temp),
            'max_temp': float(max_temp),
            'min_temp': float(min_temp),
            'rainy_days': int(rainy_days)
        },
        'daily': daily_data,
        'monthly': monthly_data
    }
    
    return jsonify(response)

@main.route('/api/metro/stations')
def api_metro_stations():
    try:
        # Load the stations.json file
        with open('data/raw/Metro/stations.json', 'r') as f:
            stations_data = json.load(f)
        
        # Add entry/exit data for each year to the stations
        years = ['2019', '2020', '2021', '2022', '2023']
        
        # Load usage data for each year
        station_usage = {}
        for y in years:
            file_path = f'data/raw/Metro/AC{y}_AnnualisedEntryExit.xlsx'
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Clean the data - handle '---' and convert to numeric
            df['Annual Entries & Exits'] = pd.to_numeric(df.iloc[:,-1].replace('---', 0), errors='coerce')
            df.fillna(0, inplace=True)
            
            # Create a dictionary with station names as keys and usage counts as values
            for _, row in df.iterrows():
                station_name = row['Station']
                usage_count = int(row['Annual Entries & Exits'])
                
                if station_name not in station_usage:
                    station_usage[station_name] = {}
                    
                station_usage[station_name][y] = usage_count
        
        # Add usage data to each station
        for key, station in stations_data['stations'].items():
            station_title = station['title']
            station['usage'] = {}
            
            for y in years:
                if station_title in station_usage and y in station_usage[station_title]:
                    station['usage'][y] = station_usage[station_title][y]
                else:
                    station['usage'][y] = 0
        return jsonify(stations_data)
    except Exception as e:
        print(f"Error in stations API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main.route('/api/metro/yearly_usage')
def api_metro_yearly_usage():
    try:
        # Get yearly data
        yearly_data = get_metro_yearly_data()
        return jsonify(yearly_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@lru_cache(maxsize=1)  # Cache the result
def get_metro_yearly_data():
    """
    Process and return Metro station usage data from 2019-2023
    with the top 10 busiest stations for each year
    """
    years = ['2019', '2020', '2021', '2022', '2023']
    total_inout = []
    top_stations_by_year = {}
    
    # Load data from each year
    for year in years:
        file_path = f'data/raw/Metro/AC{year}_AnnualisedEntryExit.xlsx'
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Clean the data - handle '---' and convert to numeric
        df['Annual Entries & Exits'] = pd.to_numeric(df.iloc[:,-1].replace('---', 0), errors='coerce')
        df.fillna(0, inplace=True)
        
        # Calculate total entries/exits for the year
        total_inout.append(df['Annual Entries & Exits'].sum())
        
        # Get top 10 stations for this year
        top_stations_df = df.nlargest(10, 'Annual Entries & Exits')
        
        # Create dictionary of top stations with names as keys and usage counts as values
        top_stations = {}
        for _, row in top_stations_df.iterrows():
            station_name = row['Station']
            usage_count = int(row['Annual Entries & Exits'])  # Convert to integer for cleaner JSON
            top_stations[station_name] = usage_count
        
        # Add to the by-year dictionary
        top_stations_by_year[year] = top_stations
    
    # Calculate the top 10 stations across all years (by total)
    all_years_df = pd.DataFrame()
    for year in years:
        file_path = f'data/raw/Metro/AC{year}_AnnualisedEntryExit.xlsx'
        df = pd.read_excel(file_path, engine='openpyxl')
        df['Annual Entries & Exits'] = pd.to_numeric(df.iloc[:,-1].replace('---', 0), errors='coerce')
        df.fillna(0, inplace=True)
        
        if all_years_df.empty:
            all_years_df = df[['Station', 'Annual Entries & Exits']].copy()
            all_years_df.rename(columns={'Annual Entries & Exits': 'Total'}, inplace=True)
        else:
            all_years_df['Total'] = all_years_df['Total'] + df['Annual Entries & Exits']
    
    # Get top 10 stations across all years
    top_all_years = all_years_df.nlargest(10, 'Total')
    top_total = {}
    for _, row in top_all_years.iterrows():
        station_name = row['Station']
        usage_count = int(row['Total'])  # Convert to integer for cleaner JSON
        top_total[station_name] = usage_count
    
    top_stations_by_year['total'] = top_total
    
    return {
        'years': years,
        'total_inout': [int(val) for val in total_inout],  # Convert to integers for cleaner JSON
        'top_stations_by_year': top_stations_by_year
    }

@main.route('/bike_sharing')
def bike_sharing():
    return render_template('visualizations/bike_sharing_visual.html')

@main.route('/api/bike_sharing')
def api_bike_sharing():
    try:
        # Get date parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Missing date parameters'}), 400
            
        # Convert dates to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Get the months we need to load
        months_needed = []
        current_dt = start_dt
        while current_dt <= end_dt:
            months_needed.append(current_dt.strftime('%Y-%m'))
            # Move to first day of next month
            if current_dt.month == 12:
                current_dt = current_dt.replace(year=current_dt.year + 1, month=1)
            else:
                current_dt = current_dt.replace(month=current_dt.month + 1)
        
        # Load and combine data from each month
        combined_data = {
            'summary': {
                'total_rides': 0,
                'total_duration_ms': 0,
                'bike_models': {}
            },
            'top_stations': {
                'pickups': [],
                'returns': []
            },
            'daily_counts': {},
            'station_stats': {}
        }
        
        for month in months_needed:
            try:
                with open(f'data/processed/bike/{month}.json', 'r') as f:
                    month_data = json.load(f)
                    
                    # Update summary
                    combined_data['summary']['total_rides'] += month_data['summary']['total_rides']
                    combined_data['summary']['total_duration_ms'] += month_data['summary']['avg_duration_ms'] * month_data['summary']['total_rides']
                    
                    # Update bike models
                    for model, count in month_data['summary']['bike_models'].items():
                        if model in combined_data['summary']['bike_models']:
                            combined_data['summary']['bike_models'][model] += count
                        else:
                            combined_data['summary']['bike_models'][model] = count
                    
                    # Update daily counts
                    combined_data['daily_counts'].update(month_data['daily_counts'])
                    
                    # Update station stats
                    for station, stats in month_data['station_stats'].items():
                        if station not in combined_data['station_stats']:
                            combined_data['station_stats'][station] = {
                                'pickups': 0,
                                'returns': 0,
                                'coordinates': {
                                    'lat': stats['lat'],
                                    'lon': stats['lon']
                                }
                            }
                        combined_data['station_stats'][station]['pickups'] += stats['pickups']
                        combined_data['station_stats'][station]['returns'] += stats['returns']
            except FileNotFoundError:
                print(f"Warning: No data found for month {month}")
                continue
        
        # Calculate average duration
        if combined_data['summary']['total_rides'] > 0:
            avg_duration = combined_data['summary']['total_duration_ms'] / combined_data['summary']['total_rides']
            combined_data['summary']['avg_duration_ms'] = int(avg_duration)
            combined_data['summary']['avg_duration_formatted'] = format_duration(avg_duration)
        else:
            combined_data['summary']['avg_duration_ms'] = 0
            combined_data['summary']['avg_duration_formatted'] = '0m 0s'
        
        # Get top stations
        stations_list = [{'name': name, **stats} for name, stats in combined_data['station_stats'].items()]
        combined_data['top_stations']['pickups'] = sorted(
            stations_list,
            key=lambda x: x['pickups'],
            reverse=True
        )[:10]
        combined_data['top_stations']['returns'] = sorted(
            stations_list,
            key=lambda x: x['returns'],
            reverse=True
        )[:10]
        
        # Filter daily counts to requested date range
        filtered_counts = {
            date: count for date, count in combined_data['daily_counts'].items()
            if start_date <= date <= end_date
        }
        combined_data['daily_counts'] = filtered_counts
        
        return jsonify(combined_data)
        
    except Exception as e:
        print(f"Error in api_bike_sharing: {str(e)}")
        return jsonify({'error': str(e)}), 500

def format_duration(duration_ms):
    """
    Format duration in milliseconds to a human-readable format (e.g., "5m 30s")
    """
    total_seconds = int(duration_ms / 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}m {seconds}s"

