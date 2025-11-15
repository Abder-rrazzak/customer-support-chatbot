#!/usr/bin/env python3
import json
import joblib
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
from pathlib import Path

def evaluate_model():
    """Evaluate trained model."""
    
    # Check if model exists
    model_path = Path("models/intent_classifier.joblib")
    vectorizer_path = Path("models/vectorizer.joblib")
    
    if not model_path.exists() or not vectorizer_path.exists():
        print("❌ Model or vectorizer not found. Run 'make train-intent' first.")
        return False
    
    # Load model and vectorizer
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    
    # Load or create test data
    test_data_path = Path("data/processed/test_data.csv")
    if not test_data_path.exists():
        # Create sample test data
        test_data = {
            'text_features': [
                'check my order status please',
                'need to return item',
                'technical issue with app',
                'store hours information'
            ],
            'intent': [
                'order_status',
                'return_request', 
                'technical_support',
                'general_inquiry'
            ]
        }
        df = pd.DataFrame(test_data)
        test_data_path.parent.mkdir(exist_ok=True)
        df.to_csv(test_data_path, index=False)
    else:
        df = pd.read_csv(test_data_path)
    
    # Transform text features
    X_test = vectorizer.transform(df["text_features"])
    y_test = df["intent"]
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    # Save metrics
    metrics = {
        "accuracy": accuracy,
        "classification_report": report
    }
    
    Path("metrics").mkdir(exist_ok=True)
    with open("metrics/evaluation_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Model evaluation completed. Accuracy: {accuracy:.4f}")
    return True

if __name__ == "__main__":
    evaluate_model()