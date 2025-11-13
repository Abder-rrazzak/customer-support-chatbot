import pytest
from src.chatbot.intent_classifier import IntentClassifier
from src.nlp.preprocessor import TextPreprocessor

def test_intent_classifier():
    classifier = IntentClassifier()
    result = classifier.classify("I need help with my order")
    assert "intent" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)

def test_text_preprocessor():
    preprocessor = TextPreprocessor()
    cleaned = preprocessor.clean("Hello @user! Check this link: http://example.com")
    assert "@user" not in cleaned
    assert "http://example.com" not in cleaned