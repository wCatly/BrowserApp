import pandas as pd
import re
from src.config import DATASET_PATH

def load_and_clean_data():
    """Load and clean the movie dataset."""
    # Load the dataset
    df = pd.read_csv(DATASET_PATH)
    
    # Basic data cleaning
    df = df.fillna('')
    
    # Convert 'Runtime' to numeric (assuming format like "142 min")
    df['Runtime'] = df['Runtime'].apply(
        lambda x: int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 0
    )
    
    # Convert Released_Year to numeric
    df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
    
    # Prepare text for embedding
    df['text_for_embedding'] = df.apply(
        lambda row: f"{row['Series_Title']} {row['Overview']} {row['Genre']} "
                   f"{row['Director']} {row['Star1']} {row['Star2']} {row['Star3']} {row['Star4']}",
        axis=1
    )
    
    return df 