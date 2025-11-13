import pytest
from src.chatbot.engine import ChatbotEngine

def test_chatbot_initialization():
    engine = ChatbotEngine()
    assert engine is not None

def test_process_message():
    engine = ChatbotEngine()
    response = engine.process_message("Hello")
    assert response is not None
    assert isinstance(response, str)