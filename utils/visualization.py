from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd

def plot_correlation_matrix(dataframe):
    plt.figure(figsize=(10, 8))
    correlation_matrix = dataframe.corr()
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', square=True)
    plt.title('Correlation Matrix')
    plt.show()

def plot_time_series(dataframe, x_col, y_col, title):
    plt.figure(figsize=(12, 6))
    plt.plot(dataframe[x_col], dataframe[y_col], marker='o')
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid()
    plt.show()

def plot_bike_sharing_trends(dataframe):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=dataframe, x='date', y='count', hue='weather_condition', marker='o')
    plt.title('Bike Sharing Trends by Weather Condition')
    plt.xlabel('Date')
    plt.ylabel('Number of Rides')
    plt.xticks(rotation=45)
    plt.legend(title='Weather Condition')
    plt.tight_layout()
    plt.show()

def plot_underground_usage(dataframe):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=dataframe, x='station', y='ridership', palette='viridis')
    plt.title('Underground Station Ridership')
    plt.xlabel('Station')
    plt.ylabel('Number of Riders')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()