#!/usr/bin/env python3
"""Data validation script for CI/CD pipeline."""

import pandas as pd
from pathlib import Path
import sys

def validate_data():
    """Validate conversation data exists and has correct format."""
    
    # Check if raw data exists
    raw_data_path = Path("data/raw/sample_conversations.csv")
    if not raw_data_path.exists():
        print("❌ Raw conversation data not found")
        return False
    
    try:
        # Load and validate data
        df = pd.read_csv(raw_data_path)
        
        # Check required columns
        required_columns = ["message", "intent", "entities"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        # Check data quality
        if df.empty:
            print("❌ Data file is empty")
            return False
        
        if df["message"].isnull().any():
            print("❌ Found null messages")
            return False
        
        print("✅ Data validation passed")
        print(f"   - {len(df)} conversations found")
        print(f"   - {df['intent'].nunique()} unique intents")
        return True
        
    except Exception as e:
        print(f"❌ Data validation failed: {e}")
        return False

if __name__ == "__main__":
    success = validate_data()
    sys.exit(0 if success else 1)