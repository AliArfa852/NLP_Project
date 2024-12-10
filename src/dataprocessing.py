import pandas as pd
import os
import yaml
from sklearn.model_selection import train_test_split

def load_config(config_path='config/config.yaml'):
    """Load configuration settings from a YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def preprocess_data():
    """Process the XLSM file and split it into training and test datasets."""
    # Load configuration
    config = load_config()
    raw_data_path = config['data']['raw_data_path']
    processed_data_path = config['data']['processed_data_path']

    # Load the dataset from the XLSM file
    print("Loading dataset...")
    df = pd.read_excel(raw_data_path, sheet_name="Annotation Dataset")
    
    # Keep only the relevant columns: Tweets and Level 2 (Emotion)
    df = df[['Tweets', 'Level 2']]

    # Rename columns for better understanding
    df.columns = ['Tweet', 'Emotion']

    # Filter rows with required emotions
    valid_emotions = ['Anger', 'Happy', 'Neutral', 'Sad']
    df = df[df['Emotion'].isin(valid_emotions)]

    # Split the data into training (80%) and test (10%) sets
    print("Splitting data...")
    train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)

    # Save the processed datasets
    os.makedirs(processed_data_path, exist_ok=True)
    train_data.to_csv(os.path.join(processed_data_path, 'train.csv'), index=False)
    test_data.to_csv(os.path.join(processed_data_path, 'test.csv'), index=False)

    print(f"Data preprocessing complete. Processed data saved to {processed_data_path}.")

if __name__ == "__main__":
    preprocess_data()
