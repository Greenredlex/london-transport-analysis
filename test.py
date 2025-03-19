import pandas as pd

def get_metro_yearly_data():
    """
    Process and return Metro station usage data from 2019-2023
    """
    years = ['2019', '2020', '2021', '2022', '2023']
    total_inout = []
    
    # Load data from each year
    for year in years:
        file_path = f'data/raw/Metro/AC{year}_AnnualisedEntryExit.xlsx'
        df = pd.read_excel(file_path, engine='openpyxl')
        df = df[pd.to_numeric(df.iloc[:, -1], errors='coerce').notna()]
        total_inout.append(df.iloc[:, -1].sum())


    df_2023 = pd.read_excel(f'data/raw/Metro/AC2023_AnnualisedEntryExit.xlsx', engine='openpyxl')
    df_2023 = df_2023[pd.to_numeric(df_2023.iloc[:, -1].replace('---', ''), errors='coerce').notna()]
    df_2023.fillna(0, inplace=True)
    top_stations = df_2023.iloc[:, -1].sort_values(ascending=False).head(10)
    top_stations_dict = {station: value for station, value in zip(df_2023['Station'].iloc[top_stations.index], top_stations)}

        

    
    return {
        'years': years,
        'total_inout': total_inout,
        'top_stations': top_stations_dict
    }
print(get_metro_yearly_data())