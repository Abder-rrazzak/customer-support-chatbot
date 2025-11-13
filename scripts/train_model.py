#!/usr/bin/env python3
"""Script to train the intent classification model."""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

def train_intent_classifier():
    """Train and save the intent classification model."""
    # Sample training data
    data = {
        'text': [
            'I need help with my order',
            'Where is my package',
            'I want to return an item',
            'How do I cancel my order',
            'What is your refund policy'
        ],
        'intent': [
            'order_help',
            'shipping_inquiry', 
            'return_request',
            'cancel_order',
            'refund_policy'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Vectorize text
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['text'])
    y = df['intent']
    
    # Train model
    model = MultinomialNB()
    model.fit(X, y)
    
    # Save model and vectorizer
    with open('models/intent_classifier.pkl', 'wb') as f:
        pickle.dump({'model': model, 'vectorizer': vectorizer}, f)
    
    print("Model trained and saved successfully!")

if __name__ == "__main__":
    train_intent_classifier()