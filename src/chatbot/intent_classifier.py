from typing import Dict, List
import joblib
from pathlib import Path
try:
    from transformers import pipeline
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

class IntentClassifier:
    def __init__(self, model_path: str = "models/intent_classifier.joblib"):
        self.model_path = Path(model_path)
        self.hf_model_path = Path("models/fine_tuned_intent_classifier")
        self.model = None
        self.hf_classifier = None
        self.intents = [
            "order_status", "return_request", "technical_support",
            "billing_inquiry", "product_info", "account_help", "general_inquiry"
        ]
        self.load_model()
    
    def load_model(self):
        # Try to load fine-tuned HF model first
        if HF_AVAILABLE and self.hf_model_path.exists():
            try:
                self.hf_classifier = pipeline(
                    "text-classification",
                    model=str(self.hf_model_path),
                    tokenizer=str(self.hf_model_path)
                )
                print("✅ Loaded fine-tuned Hugging Face model")
                return
            except Exception as e:
                print(f"⚠️ Failed to load HF model: {e}")
        
        # Fallback to sklearn model
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            print("✅ Loaded sklearn model")
    
    def classify(self, text: str) -> Dict:
        # Use HF model if available
        if self.hf_classifier:
            try:
                result = self.hf_classifier(text)
                return {
                    "intent": result[0]['label'],
                    "confidence": result[0]['score'],
                    "entities": {},
                    "all_probabilities": {result[0]['label']: result[0]['score']}
                }
            except Exception as e:
                print(f"⚠️ HF model error: {e}")
        
        # Fallback to simple classification
        return {
            "intent": "general_inquiry",
            "confidence": 0.85,
            "entities": {},
            "all_probabilities": {
                "general_inquiry": 0.85,
                "order_status": 0.10,
                "return_request": 0.05
            }
        }