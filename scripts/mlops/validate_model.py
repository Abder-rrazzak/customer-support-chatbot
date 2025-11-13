#!/usr/bin/env python3
"""Model validation script."""

import joblib
from pathlib import Path
import numpy as np

def validate_model():
    """Validate trained model."""
    
    model_path = Path("models/intent_classifier.joblib")
    
    if not model_path.exists():
        print("❌ Model file not found")
        return False
    
    try:
        # Load model
        model = joblib.load(model_path)
        
        # Basic validation
        if not hasattr(model, 'predict'):
            print("❌ Model doesn't have predict method")
            return False
        
        print("✅ Model validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

if __name__ == "__main__":
    validate_model()