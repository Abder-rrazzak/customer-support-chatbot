"""
Module principal du chatbot avec logique de conversation.

Ce module contient les composants core du chatbot :
- Moteur de conversation
- Gestion des intents
- Génération de réponses
- Contexte de conversation
"""

from .engine import ChatbotEngine
from .intent_classifier import IntentClassifier
from .response_generator import ResponseGenerator

__all__ = ["ChatbotEngine", "IntentClassifier", "ResponseGenerator"]