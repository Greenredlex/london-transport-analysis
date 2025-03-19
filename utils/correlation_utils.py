from scipy.stats import pearsonr
import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path)

def calculate_correlation(data1, data2):
    # make data same length
    data1 = data1[:len(data2)]
    data2 = data2[:len(data1)]
    correlation, _ = pearsonr(data1, data2)
    return correlation

def analyze_correlations(underground_data, bike_sharing_data, weather_data):
    """
    Analyze correlations between different datasets
    """
    correlations = {
        'underground_weather': {},
        'bike_weather': {},
        'underground_bike': {}
    }
    
    # Example correlation calculations (replace with actual analysis)
    # These are placeholder values - your actual analysis will differ
    correlations['underground_weather']['temperature'] = 0.65
    correlations['underground_weather']['rainfall'] = -0.45
    correlations['bike_weather']['temperature'] = 0.78
    correlations['bike_weather']['rainfall'] = -0.62
    correlations['underground_bike']['usage'] = 0.35
    
    return correlations
