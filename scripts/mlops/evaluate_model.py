#!/usr/bin/env python3
import json
import joblib
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
from pathlib import Path

def evaluate_model():
    # Load test data
    test_data = pd.read_csv("data/processed/test_data.csv")
    X_test = test_data["text_features"]
    y_test = test_data["intent"]
    
    # Load model
    model = joblib.load("models/intent_classifier.joblib")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # Save metrics
    metrics = {
        "accuracy": accuracy,
        "classification_report": report
    }
    
    Path("metrics").mkdir(exist_ok=True)
    with open("metrics/evaluation_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Model evaluation completed. Accuracy: {accuracy:.4f}")

if __name__ == "__main__":
    evaluate_model()