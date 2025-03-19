# London Transport Analysis

This project aims to analyze and visualize the correlations between data from the London Underground, bike-sharing services, and weather conditions in London. By integrating these datasets, we can gain insights into how weather impacts transport usage and bike-sharing trends.

## Project Structure

- **app/**: Contains the Flask application code.
  - **__init__.py**: Initializes the Flask app and sets up configurations.
  - **routes.py**: Defines the routes for the application.
  - **models/**: Contains data models (if using an ORM).
  - **static/**: Contains static files such as CSS and JavaScript.
    - **css/**: Styles for the application.
    - **js/**: JavaScript for dynamic visualizations.
  - **templates/**: HTML templates for rendering web pages.
    - **base.html**: Base template for the application.
    - **index.html**: Landing page of the application.
    - **visualizations/**: Contains specific visualization pages.
      - **correlations.html**: Displays correlation analysis results.
      - **underground_analysis.html**: Analysis of London Underground data.
      - **bike_sharing.html**: Analysis of bike-sharing data.
      - **weather_impact.html**: Impact of weather on transport and bike-sharing.

- **data/**: Contains raw and processed datasets.
  - **raw/**: Raw data files.
    - **underground_data.csv**: London Underground ridership statistics.
    - **bike_sharing.csv**: Bike-sharing usage data.
    - **london_weather.csv**: Weather data for London.
  - **processed/**: Processed datasets for analysis.
    - **combined_dataset.csv**: Combined dataset for analysis.

- **notebooks/**: Jupyter notebooks for data exploration and analysis.
  - **data_exploration.ipynb**: Initial data exploration.
  - **correlation_analysis.ipynb**: Correlation analysis between datasets.
  - **visualization_development.ipynb**: Development of visualizations.

- **utils/**: Utility functions for data processing and visualization.
  - **__init__.py**: Initializes the utils module.
  - **data_processing.py**: Functions for data cleaning and transformation.
  - **correlation_utils.py**: Functions for correlation analysis.
  - **visualization.py**: Functions for creating visualizations.

- **config.py**: Configuration settings for the application.

- **requirements.txt**: Lists dependencies required for the project.

- **run.py**: Entry point for running the Flask application.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd london-transport-analysis
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

5. Open your web browser and go to `http://127.0.0.1:5000` to view the application.

## Usage

Explore the different analyses available through the landing page. You can view correlations between datasets, analyze the London Underground data, examine bike-sharing trends, and understand the impact of weather on transport usage.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.