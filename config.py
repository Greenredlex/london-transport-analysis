from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    
    # Database configuration (if needed)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other configuration variables
    SECRET_KEY = 'your_secret_key_here'
    DEBUG = True  # Set to False in production

    # API keys or other sensitive information can be added here
    # WEATHER_API_KEY = 'your_weather_api_key_here'