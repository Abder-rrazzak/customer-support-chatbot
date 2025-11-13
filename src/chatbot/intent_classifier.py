"""
Classificateur d'intentions pour le chatbot de support client.

Ce module implémente un classificateur ML pour identifier les intentions
des utilisateurs dans leurs messages, utilisant des techniques NLP avancées.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from ..nlp.entity_extractor import EntityExtractor

# Configuration du logging
logger = structlog.get_logger(__name__)


class IntentClassifier:
    """
    Classificateur d'intentions utilisant des embeddings et Random Forest.
    
    Combine des embeddings de phrases pré-entraînés avec un classificateur
    ML traditionnel pour une classification robuste et rapide.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        confidence_threshold: float = 0.7,
    ):
        """
        Initialise le classificateur d'intentions.
        
        Args:
            model_path: Chemin vers le modèle sauvegardé
            embedding_model: Nom du modèle d'embeddings
            confidence_threshold: Seuil de confiance minimum
        """
        self.embedding_model_name = embedding_model
        self.confidence_threshold = confidence_threshold
        self.model_path = Path(model_path) if model_path else None
        
        # Composants du modèle
        self.sentence_transformer = None
        self.classifier = None
        self.label_encoder = None
        self.entity_extractor = EntityExtractor()
        
        # Métadonnées du modèle
        self.is_trained = False
        self.intent_examples = {}
        self.model_version = "1.0.0"
        
        # Charger le modèle si disponible
        if self.model_path and self.model_path.exists():
            self.load_model()
        else:
            self._initialize_components()
    
    def _initialize_components(self) -> None:
        """Initialise les composants du modèle."""
        try:
            logger.info(
                "Initializing intent classifier components",
                embedding_model=self.embedding_model_name,
            )
            
            # Charger le modèle d'embeddings
            self.sentence_transformer = SentenceTransformer(
                self.embedding_model_name
            )
            
            # Initialiser le classificateur
            self.classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5,
                class_weight="balanced",  # Gérer les classes déséquilibrées
            )
            
            # Initialiser l'encodeur de labels
            self.label_encoder = LabelEncoder()
            
            logger.info("Components initialized successfully")
            
        except Exception as e:
            logger.error(
                "Failed to initialize components",
                error=str(e),
                exc_info=True,
            )
            raise
    
    def train(
        self,
        training_data: List[Dict],
        validation_split: float = 0.2,
        save_model: bool = True,
    ) -> Dict:
        """
        Entraîne le classificateur d'intentions.
        
        Args:
            training_data: Données d'entraînement
                Format: [{"text": "message", "intent": "intention"}, ...]
            validation_split: Proportion pour la validation
            save_model: Sauvegarder le modèle après entraînement
            
        Returns:
            Dict: Métriques d'entraînement
        """
        logger.info(
            "Starting intent classifier training",
            training_samples=len(training_data),
            validation_split=validation_split,
        )
        
        try:
            # Préparer les données
            texts = [item["text"] for item in training_data]
            intents = [item["intent"] for item in training_data]
            
            # Créer les embeddings
            logger.info("Generating embeddings for training data")
            embeddings = self.sentence_transformer.encode(
                texts, 
                show_progress_bar=True,
                batch_size=32,
            )
            
            # Encoder les labels
            encoded_intents = self.label_encoder.fit_transform(intents)
            
            # Division train/validation
            X_train, X_val, y_train, y_val = train_test_split(
                embeddings,
                encoded_intents,
                test_size=validation_split,
                random_state=42,
                stratify=encoded_intents,
            )
            
            # Entraînement du classificateur
            logger.info("Training Random Forest classifier")
            self.classifier.fit(X_train, y_train)
            
            # Évaluation
            train_predictions = self.classifier.predict(X_train)
            val_predictions = self.classifier.predict(X_val)
            
            train_accuracy = accuracy_score(y_train, train_predictions)
            val_accuracy = accuracy_score(y_val, val_predictions)
            
            # Rapport détaillé
            val_report = classification_report(
                y_val,
                val_predictions,
                target_names=self.label_encoder.classes_,
                output_dict=True,
            )
            
            # Stocker les exemples pour référence
            self._store_intent_examples(training_data)
            
            self.is_trained = True
            
            # Métriques d'entraînement
            metrics = {
                "train_accuracy": train_accuracy,
                "val_accuracy": val_accuracy,
                "train_samples": len(X_train),
                "val_samples": len(X_val),
                "num_intents": len(self.label_encoder.classes_),
                "intents": list(self.label_encoder.classes_),
                "classification_report": val_report,
            }
            
            logger.info(
                "Training completed successfully",
                train_accuracy=train_accuracy,
                val_accuracy=val_accuracy,
                num_intents=len(self.label_encoder.classes_),
            )
            
            # Sauvegarder le modèle
            if save_model and self.model_path:
                self.save_model()
            
            return metrics
            
        except Exception as e:
            logger.error(
                "Training failed",
                error=str(e),
                exc_info=True,
            )
            raise
    
    def classify(
        self, 
        text: str, 
        context: Optional[Dict] = None,
    ) -> Dict:
        """
        Classifie l'intention d'un message.
        
        Args:
            text: Texte à classifier
            context: Contexte de conversation optionnel
            
        Returns:
            Dict: Résultat de classification avec intention, confiance, entités
        """
        if not self.is_trained:
            logger.warning("Classifier not trained, using fallback")
            return self._fallback_classification(text)
        
        try:
            # Générer l'embedding
            embedding = self.sentence_transformer.encode([text])
            
            # Prédiction avec probabilités
            probabilities = self.classifier.predict_proba(embedding)[0]
            predicted_class = self.classifier.predict(embedding)[0]
            
            # Décoder l'intention
            intent = self.label_encoder.inverse_transform([predicted_class])[0]
            confidence = float(np.max(probabilities))
            
            # Extraire les entités
            entities = self.entity_extractor.extract(text, intent)
            
            # Ajuster la confiance avec le contexte
            if context:
                confidence = self._adjust_confidence_with_context(
                    intent, confidence, context
                )
            
            result = {
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "all_probabilities": {
                    self.label_encoder.inverse_transform([i])[0]: float(prob)
                    for i, prob in enumerate(probabilities)
                },
            }
            
            logger.debug(
                "Intent classified",
                intent=intent,
                confidence=confidence,
                text_length=len(text),
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Classification failed",
                text=text[:100],
                error=str(e),
                exc_info=True,
            )
            return self._fallback_classification(text)
    
    def _fallback_classification(self, text: str) -> Dict:
        """
        Classification de fallback basée sur des règles simples.
        
        Args:
            text: Texte à classifier
            
        Returns:
            Dict: Classification basique
        """
        text_lower = text.lower()
        
        # Règles simples basées sur des mots-clés
        if any(word in text_lower for word in ["commande", "order", "livraison"]):
            intent = "order_status"
            confidence = 0.6
        elif any(word in text_lower for word in ["remboursement", "retour", "rembourser"]):
            intent = "refund_request"
            confidence = 0.6
        elif any(word in text_lower for word in ["compte", "connexion", "mot de passe"]):
            intent = "account_help"
            confidence = 0.6
        elif any(word in text_lower for word in ["problème", "bug", "erreur", "marche pas"]):
            intent = "technical_support"
            confidence = 0.6
        else:
            intent = "general_inquiry"
            confidence = 0.3
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": {},
            "fallback": True,
        }
    
    def _adjust_confidence_with_context(
        self, 
        intent: str, 
        confidence: float, 
        context: Dict,
    ) -> float:
        """
        Ajuste la confiance basée sur le contexte de conversation.
        
        Args:
            intent: Intention prédite
            confidence: Confiance initiale
            context: Contexte de conversation
            
        Returns:
            float: Confiance ajustée
        """
        # Bonus si l'intention est cohérente avec l'historique
        if hasattr(context, 'current_intent') and context.current_intent:
            if intent == context.current_intent:
                confidence = min(1.0, confidence + 0.1)
            elif self._are_related_intents(intent, context.current_intent):
                confidence = min(1.0, confidence + 0.05)
        
        # Bonus si des entités pertinentes sont présentes
        if hasattr(context, 'entities') and context.entities:
            relevant_entities = self._get_relevant_entities(intent)
            if any(entity in context.entities for entity in relevant_entities):
                confidence = min(1.0, confidence + 0.05)
        
        return confidence
    
    def _are_related_intents(self, intent1: str, intent2: str) -> bool:
        """
        Vérifie si deux intentions sont liées.
        
        Args:
            intent1: Première intention
            intent2: Deuxième intention
            
        Returns:
            bool: True si les intentions sont liées
        """
        related_groups = [
            {"order_status", "shipping_info", "delivery_update"},
            {"refund_request", "return_product", "exchange_product"},
            {"account_help", "login_issue", "password_reset"},
            {"technical_support", "bug_report", "feature_request"},
        ]
        
        for group in related_groups:
            if intent1 in group and intent2 in group:
                return True
        
        return False
    
    def _get_relevant_entities(self, intent: str) -> List[str]:
        """
        Retourne les entités pertinentes pour une intention.
        
        Args:
            intent: Intention
            
        Returns:
            List[str]: Liste des entités pertinentes
        """
        entity_mapping = {
            "order_status": ["order_number", "product_name", "date"],
            "refund_request": ["order_number", "product_name", "amount"],
            "account_help": ["email", "username", "phone"],
            "technical_support": ["product_name", "error_code", "device"],
        }
        
        return entity_mapping.get(intent, [])
    
    def _store_intent_examples(self, training_data: List[Dict]) -> None:
        """
        Stocke des exemples pour chaque intention.
        
        Args:
            training_data: Données d'entraînement
        """
        self.intent_examples = {}
        
        for item in training_data:
            intent = item["intent"]
            text = item["text"]
            
            if intent not in self.intent_examples:
                self.intent_examples[intent] = []
            
            if len(self.intent_examples[intent]) < 5:  # Garder 5 exemples max
                self.intent_examples[intent].append(text)
    
    def get_intent_examples(self, intent: str, limit: int = 3) -> List[str]:
        """
        Retourne des exemples pour une intention.
        
        Args:
            intent: Intention
            limit: Nombre maximum d'exemples
            
        Returns:
            List[str]: Exemples de messages
        """
        return self.intent_examples.get(intent, [])[:limit]
    
    def save_model(self) -> None:
        """Sauvegarde le modèle entraîné."""
        if not self.model_path:
            raise ValueError("No model path specified")
        
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                "classifier": self.classifier,
                "label_encoder": self.label_encoder,
                "embedding_model_name": self.embedding_model_name,
                "intent_examples": self.intent_examples,
                "model_version": self.model_version,
                "is_trained": self.is_trained,
            }
            
            with open(self.model_path, "wb") as f:
                pickle.dump(model_data, f)
            
            logger.info(
                "Model saved successfully",
                model_path=str(self.model_path),
            )
            
        except Exception as e:
            logger.error(
                "Failed to save model",
                model_path=str(self.model_path),
                error=str(e),
                exc_info=True,
            )
            raise
    
    def load_model(self) -> None:
        """Charge un modèle sauvegardé."""
        if not self.model_path or not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        try:
            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)
            
            self.classifier = model_data["classifier"]
            self.label_encoder = model_data["label_encoder"]
            self.embedding_model_name = model_data["embedding_model_name"]
            self.intent_examples = model_data.get("intent_examples", {})
            self.model_version = model_data.get("model_version", "1.0.0")
            self.is_trained = model_data.get("is_trained", True)
            
            # Recharger le modèle d'embeddings
            self.sentence_transformer = SentenceTransformer(
                self.embedding_model_name
            )
            
            logger.info(
                "Model loaded successfully",
                model_path=str(self.model_path),
                model_version=self.model_version,
                num_intents=len(self.label_encoder.classes_),
            )
            
        except Exception as e:
            logger.error(
                "Failed to load model",
                model_path=str(self.model_path),
                error=str(e),
                exc_info=True,
            )
            raise
    
    def get_supported_intents(self) -> List[str]:
        """
        Retourne la liste des intentions supportées.
        
        Returns:
            List[str]: Liste des intentions
        """
        if self.label_encoder and self.is_trained:
            return list(self.label_encoder.classes_)
        return []
    
    def get_model_info(self) -> Dict:
        """
        Retourne les informations sur le modèle.
        
        Returns:
            Dict: Informations du modèle
        """
        return {
            "model_version": self.model_version,
            "embedding_model": self.embedding_model_name,
            "is_trained": self.is_trained,
            "supported_intents": self.get_supported_intents(),
            "num_intents": len(self.get_supported_intents()),
            "confidence_threshold": self.confidence_threshold,
        }