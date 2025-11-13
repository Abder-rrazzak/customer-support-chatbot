#!/usr/bin/env python3
"""Data ingestion script."""

import pandas as pd
from pathlib import Path
import os

def ingest_data():
    """Ingest conversation data from various sources."""
    
    # Simulate data ingestion
    conversations = [
        {"message": "Hello, I need help", "intent": "general_inquiry", "entities": "{}"},
        {"message": "Track my order", "intent": "order_status", "entities": "{}"},
        {"message": "Return this item", "intent": "return_request", "entities": "{}"},
    ]
    
    df = pd.DataFrame(conversations)
    
    # Save to raw data
    output_path = Path("data/raw/conversations.csv")
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print("✅ Data ingestion completed")
    return True

if __name__ == "__main__":
    ingest_data()