#!/usr/bin/env python3
"""Download real customer support dataset from Hugging Face."""

from datasets import load_dataset
import pandas as pd
from pathlib import Path

def download_customer_support_dataset():
    """Download and prepare customer support dataset."""
    
    try:
        # Load Banking77 dataset for intent classification
        print("📥 Downloading Banking77 dataset...")
        banking_dataset = load_dataset("banking77")
        
        # Prepare banking77 for intent classification
        train_data = banking_dataset['train']
        
        # Convert to pandas DataFrame
        df = pd.DataFrame({
            'text': train_data['text'],
            'intent': train_data['label']
        })
        
        # Map label numbers to intent names
        label_names = banking_dataset['train'].features['label'].names
        df['intent'] = df['intent'].map(lambda x: label_names[x])
        
        # Save to CSV
        data_path = Path("data/raw")
        data_path.mkdir(exist_ok=True)
        
        df.to_csv(data_path / "banking77_dataset.csv", index=False)
        
        # Create processed version
        processed_path = Path("data/processed")
        processed_path.mkdir(exist_ok=True)
        
        # Simple preprocessing
        df['text_features'] = df['text'].str.lower().str.strip()
        df[['text_features', 'intent']].to_csv(processed_path / "training_data.csv", index=False)
        
        print(f"✅ Downloaded {len(df)} samples from Banking77 dataset")
        print(f"📊 {df['intent'].nunique()} unique intents")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return False

if __name__ == "__main__":
    download_customer_support_dataset()