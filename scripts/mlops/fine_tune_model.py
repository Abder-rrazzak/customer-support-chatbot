#!/usr/bin/env python3
"""Fine-tune pre-trained model from Hugging Face."""

from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, pipeline
)
from datasets import Dataset
import pandas as pd
import numpy as np
from pathlib import Path
import torch

def fine_tune_intent_classifier():
    """Fine-tune BERT model for intent classification."""
    
    # Load data
    data_path = Path("data/processed/training_data.csv")
    if not data_path.exists():
        print("❌ Training data not found. Run 'python scripts/download_dataset.py' first.")
        return False
    
    df = pd.read_csv(data_path)
    
    # Prepare labels
    unique_intents = df['intent'].unique()
    label2id = {intent: i for i, intent in enumerate(unique_intents)}
    id2label = {i: intent for intent, i in label2id.items()}
    
    df['labels'] = df['intent'].map(label2id)
    
    # Load pre-trained model and tokenizer
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(unique_intents),
        id2label=id2label,
        label2id=label2id
    )
    
    # Tokenize data
    def tokenize_function(examples):
        return tokenizer(examples['text_features'], truncation=True, padding=True)
    
    # Create dataset
    dataset = Dataset.from_pandas(df[['text_features', 'labels']])
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Split dataset
    train_size = int(0.8 * len(tokenized_dataset))
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./models/fine_tuned_intent_classifier",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir="./logs",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )
    
    # Fine-tune
    print("🚀 Starting fine-tuning...")
    trainer.train()
    
    # Save model
    model_path = Path("models/fine_tuned_intent_classifier")
    trainer.save_model(model_path)
    tokenizer.save_pretrained(model_path)
    
    # Test the model
    classifier = pipeline(
        "text-classification",
        model=model_path,
        tokenizer=model_path
    )
    
    test_texts = [
        "I want to check my account balance",
        "How do I transfer money?",
        "My card is not working"
    ]
    
    print("\n🧪 Testing fine-tuned model:")
    for text in test_texts:
        result = classifier(text)
        print(f"Text: {text}")
        print(f"Intent: {result[0]['label']} (confidence: {result[0]['score']:.3f})")
        print()
    
    print("✅ Fine-tuning completed successfully!")
    return True

if __name__ == "__main__":
    fine_tune_intent_classifier()