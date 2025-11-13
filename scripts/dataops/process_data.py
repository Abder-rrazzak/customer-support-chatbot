#!/usr/bin/env python3
"""Process raw data for training."""

import pandas as pd
from pathlib import Path

def process_data():
    """Process raw conversation data."""
    
    # Load raw data
    raw_path = Path("data/raw/sample_conversations.csv")
    processed_path = Path("data/processed/training_data.csv")
    
    if not raw_path.exists():
        print("❌ Raw data not found")
        return False
    
    df = pd.read_csv(raw_path)
    
    # Simple processing - clean text
    df['text_features'] = df['message'].str.lower().str.strip()
    
    # Save processed data
    processed_path.parent.mkdir(exist_ok=True)
    df[['text_features', 'intent']].to_csv(processed_path, index=False)
    
    print("✅ Data processing completed")
    return True

if __name__ == "__main__":
    process_data()