from pandas import read_csv, DataFrame

def load_data():
    underground_path = 'data/raw/underground_data.csv'
    bike_sharing_path = 'data/raw/bike_sharing.csv'
    weather_path = 'data/raw/london_weather.csv'
    
    underground_data = read_csv(underground_path)
    bike_sharing_data = read_csv(bike_sharing_path)
    weather_data = read_csv(weather_path)
    return underground_data, bike_sharing_data, weather_data

def clean_data(df):
    df.dropna(inplace=True)
    # Additional cleaning steps can be added here
    return df

def preprocess_data(underground_data, bike_sharing_data, weather_data):
    underground_data = clean_data(underground_data)
    bike_sharing_data = clean_data(bike_sharing_data)
    weather_data = clean_data(weather_data)

    # Example of merging datasets
    combined_data = underground_data.merge(bike_sharing_data, on='date', how='inner')
    combined_data = combined_data.merge(weather_data, on='date', how='inner')

    return combined_data

def save_processed_data(combined_data, output_path):
    combined_data.to_csv(output_path, index=False)

