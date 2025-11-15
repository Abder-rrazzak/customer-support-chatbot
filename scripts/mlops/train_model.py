#!/usr/bin/env python3
"""Simple training pipeline for intent classifier."""

import pandas as pd
import joblib
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score

def train_intent_classifier():
    """Train intent classification model."""
    
    # Load data
    data_path = Path('data/processed/training_data.csv')
    if not data_path.exists():
        print("Training data not found. Creating sample data...")
        sample_data = {
            'text_features': [
                'hello help order', 'track my order', 'where is my package',
                'return product', 'refund request', 'want to return item',
                'app not working', 'technical issue', 'login problem',
                'store hours', 'contact info', 'general question',
                'billing question', 'payment issue', 'invoice problem',
                'account help', 'reset password', 'update profile'
            ],
            'intent': [
                'order_status', 'order_status', 'order_status',
                'return_request', 'return_request', 'return_request',
                'technical_support', 'technical_support', 'technical_support',
                'general_inquiry', 'general_inquiry', 'general_inquiry',
                'billing_inquiry', 'billing_inquiry', 'billing_inquiry',
                'account_help', 'account_help', 'account_help'
            ]
        }
        df = pd.DataFrame(sample_data)
        data_path.parent.mkdir(exist_ok=True)
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)
    
    # Prepare features
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df['text_features'])
    y = df['intent']
    
    # Handle small datasets
    if len(df) < 10:
        # Use all data for training and testing
        X_train, X_test = X, X
        y_train, y_test = y, y
    else:
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    
    # Train model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model and vectorizer
    models_path = Path("models")
    models_path.mkdir(exist_ok=True)
    joblib.dump(model, models_path / "intent_classifier.joblib")
    joblib.dump(vectorizer, models_path / "vectorizer.joblib")
    
    # Save metrics
    metrics_path = Path("metrics")
    metrics_path.mkdir(exist_ok=True)
    metrics = {"accuracy": accuracy, "n_estimators": 50}
    with open(metrics_path / "intent_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Model trained with accuracy: {accuracy:.4f}")
    return model

if __name__ == "__main__":
    train_intent_classifier()