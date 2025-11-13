#!/usr/bin/env python3
"""MLOps training pipeline with experiment tracking."""

import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import joblib
from pathlib import Path

def train_intent_classifier():
    """Train intent classification model with MLflow tracking."""
    
    # Start MLflow run
    with mlflow.start_run():
        # Load data
        data = pd.read_csv('data/processed/training_data.csv')
        X = data['text_features']
        y = data['intent']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_param("n_estimators", 100)
        
        # Save model
        model_path = Path("models/intent_classifier.joblib")
        model_path.parent.mkdir(exist_ok=True)
        joblib.dump(model, model_path)
        
        # Log model
        mlflow.sklearn.log_model(model, "intent_classifier")
        
        print(f"Model trained with accuracy: {accuracy:.4f}")
        return model

if __name__ == "__main__":
    train_intent_classifier()