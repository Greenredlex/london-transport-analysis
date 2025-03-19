"""
Run the bike data preprocessing to create summarized files.
This script should be run once to generate preprocessed data.
After running, the API will use these preprocessed files for faster performance.
"""

import utils.bike_preprocessing as bp

if __name__ == "__main__":
    print("Starting bike data preprocessing...")
    bp.preprocess_bike_data()
    print("Preprocessing complete! The API will now use preprocessed data for faster performance.") 