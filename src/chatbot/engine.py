"""
Moteur principal du chatbot de support client.

Ce module implémente la logique centrale du chatbot, orchestrant
les différents composants NLP pour fournir des réponses intelligentes.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import structlog
from pydantic import BaseModel

from ..nlp.preprocessor import TextPreprocessor
from .intent_classifier import IntentClassifier
from .response_generator import ResponseGenerator

# Configuration du logging structuré
logger = structlog.get_logger(__name__)


class ConversationContext(BaseModel):
    """
    Modèle pour le contexte de conversation.
    
    Maintient l'état de la conversation pour personnaliser
    les réponses et assurer la cohérence.
    """
    
    session_id: str
    user_id: Optional[str] = None
    conversation_history: List[Dict] = []
    current_intent: Optional[str] = None
    entities: Dict = {}
    sentiment: Optional[str] = None
    confidence_threshold: float = 0.7
    created_at: float
    last_activity: float
    
    class Config:
        # Permettre la sérialisation des objets complexes
        arbitrary_types_allowed = True


class ChatbotResponse(BaseModel):
    """
    Modèle pour les réponses du chatbot.
    
    Structure standardisée pour toutes les réponses
    incluant métadonnées et informations de debug.
    """
    
    message: str
    intent: Optional[str] = None
    confidence: float = 0.0
    entities: Dict = {}
    suggestions: List[str] = []
    requires_human: bool = False
    session_id: str
    response_time_ms: float
    
    # Métadonnées pour le monitoring
    model_version: str = "1.0.0"
    timestamp: float


class ChatbotEngine:
    """
    Moteur principal du chatbot de support client.
    
    Orchestre tous les composants NLP et gère le flux de conversation
    pour fournir des réponses contextuelles et pertinentes.
    """
    
    def __init__(
        self,
        intent_classifier: Optional[IntentClassifier] = None,
        response_generator: Optional[ResponseGenerator] = None,
        confidence_threshold: float = 0.7,
        max_conversation_length: int = 50,
    ):
        """
        Initialise le moteur du chatbot.
        
        Args:
            intent_classifier: Classificateur d'intentions
            response_generator: Générateur de réponses
            confidence_threshold: Seuil de confiance minimum
            max_conversation_length: Longueur max de l'historique
        """
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.response_generator = response_generator or ResponseGenerator()
        self.text_preprocessor = TextPreprocessor()
        
        self.confidence_threshold = confidence_threshold
        self.max_conversation_length = max_conversation_length
        
        # Stockage en mémoire des contextes de conversation
        # En production, utiliser Redis ou une base de données
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        
        logger.info(
            "Chatbot engine initialized",
            confidence_threshold=confidence_threshold,
            max_conversation_length=max_conversation_length,
        )
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Crée une nouvelle session de conversation.
        
        Args:
            user_id: Identifiant optionnel de l'utilisateur
            
        Returns:
            str: ID de session unique
        """
        session_id = str(uuid4())
        current_time = time.time()
        
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            created_at=current_time,
            last_activity=current_time,
        )
        
        self.conversation_contexts[session_id] = context
        
        logger.info(
            "New conversation session created",
            session_id=session_id,
            user_id=user_id,
        )
        
        return session_id
    
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """
        Récupère le contexte d'une session.
        
        Args:
            session_id: ID de la session
            
        Returns:
            ConversationContext ou None si non trouvé
        """
        return self.conversation_contexts.get(session_id)
    
    def update_context(
        self, 
        session_id: str, 
        user_message: str, 
        bot_response: str,
        intent: Optional[str] = None,
        entities: Optional[Dict] = None,
    ) -> None:
        """
        Met à jour le contexte de conversation.
        
        Args:
            session_id: ID de la session
            user_message: Message de l'utilisateur
            bot_response: Réponse du bot
            intent: Intention détectée
            entities: Entités extraites
        """
        context = self.conversation_contexts.get(session_id)
        if not context:
            return
        
        # Ajouter l'échange à l'historique
        exchange = {
            "timestamp": time.time(),
            "user_message": user_message,
            "bot_response": bot_response,
            "intent": intent,
            "entities": entities or {},
        }
        
        context.conversation_history.append(exchange)
        context.current_intent = intent
        context.entities.update(entities or {})
        context.last_activity = time.time()
        
        # Limiter la taille de l'historique
        if len(context.conversation_history) > self.max_conversation_length:
            context.conversation_history = context.conversation_history[
                -self.max_conversation_length:
            ]
    
    def process_message(
        self, 
        message: str, 
        session_id: str,
        user_id: Optional[str] = None,
    ) -> ChatbotResponse:
        """
        Traite un message utilisateur et génère une réponse.
        
        Args:
            message: Message de l'utilisateur
            session_id: ID de session
            user_id: ID utilisateur optionnel
            
        Returns:
            ChatbotResponse: Réponse structurée du chatbot
        """
        start_time = time.time()
        
        try:
            # Récupérer ou créer le contexte
            context = self.get_context(session_id)
            if not context:
                session_id = self.create_session(user_id)
                context = self.get_context(session_id)
            
            logger.info(
                "Processing user message",
                session_id=session_id,
                message_length=len(message),
                user_id=user_id,
            )
            
            # 1. Préprocessing du texte
            processed_message = self.text_preprocessor.preprocess(message)
            
            # 2. Classification d'intention
            intent_result = self.intent_classifier.classify(
                processed_message, 
                context=context
            )
            
            intent = intent_result.get("intent")
            confidence = intent_result.get("confidence", 0.0)
            entities = intent_result.get("entities", {})
            
            # 3. Vérifier le seuil de confiance
            requires_human = confidence < self.confidence_threshold
            
            # 4. Génération de réponse
            if requires_human:
                response_text = self._get_fallback_response(context)
                suggestions = self._get_suggestions(processed_message)
            else:
                response_text = self.response_generator.generate_response(
                    intent=intent,
                    entities=entities,
                    context=context,
                    user_message=processed_message,
                )
                suggestions = self._get_intent_suggestions(intent)
            
            # 5. Mettre à jour le contexte
            self.update_context(
                session_id=session_id,
                user_message=message,
                bot_response=response_text,
                intent=intent,
                entities=entities,
            )
            
            # 6. Créer la réponse
            response_time = (time.time() - start_time) * 1000
            
            response = ChatbotResponse(
                message=response_text,
                intent=intent,
                confidence=confidence,
                entities=entities,
                suggestions=suggestions,
                requires_human=requires_human,
                session_id=session_id,
                response_time_ms=response_time,
                timestamp=time.time(),
            )
            
            logger.info(
                "Message processed successfully",
                session_id=session_id,
                intent=intent,
                confidence=confidence,
                response_time_ms=response_time,
                requires_human=requires_human,
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Error processing message",
                session_id=session_id,
                error=str(e),
                exc_info=True,
            )
            
            # Réponse d'erreur gracieuse
            return ChatbotResponse(
                message="Je suis désolé, j'ai rencontré un problème technique. "
                       "Un agent va vous aider sous peu.",
                requires_human=True,
                session_id=session_id,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=time.time(),
            )
    
    def _get_fallback_response(self, context: ConversationContext) -> str:
        """
        Génère une réponse de fallback quand la confiance est faible.
        
        Args:
            context: Contexte de conversation
            
        Returns:
            str: Message de fallback
        """
        fallback_messages = [
            "Je ne suis pas sûr de comprendre votre demande. "
            "Pouvez-vous reformuler ou être plus précis ?",
            
            "Je vais transférer votre demande à un agent humain "
            "qui pourra mieux vous aider.",
            
            "Votre demande semble complexe. Un conseiller va "
            "prendre le relais pour vous assister.",
        ]
        
        # Sélectionner un message basé sur l'historique
        history_length = len(context.conversation_history)
        message_index = min(history_length, len(fallback_messages) - 1)
        
        return fallback_messages[message_index]
    
    def _get_suggestions(self, message: str) -> List[str]:
        """
        Génère des suggestions basées sur le message.
        
        Args:
            message: Message utilisateur
            
        Returns:
            List[str]: Liste de suggestions
        """
        # Suggestions génériques basées sur des mots-clés
        suggestions = []
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["commande", "order", "achat"]):
            suggestions.extend([
                "Vérifier le statut de ma commande",
                "Modifier ma commande",
                "Annuler ma commande",
            ])
        
        if any(word in message_lower for word in ["remboursement", "retour"]):
            suggestions.extend([
                "Demander un remboursement",
                "Retourner un produit",
                "Politique de retour",
            ])
        
        if any(word in message_lower for word in ["compte", "connexion", "mot de passe"]):
            suggestions.extend([
                "Réinitialiser mon mot de passe",
                "Problème de connexion",
                "Modifier mes informations",
            ])
        
        return suggestions[:3]  # Limiter à 3 suggestions
    
    def _get_intent_suggestions(self, intent: str) -> List[str]:
        """
        Génère des suggestions basées sur l'intention détectée.
        
        Args:
            intent: Intention détectée
            
        Returns:
            List[str]: Suggestions contextuelles
        """
        intent_suggestions = {
            "order_status": [
                "Suivre ma commande",
                "Modifier l'adresse de livraison",
                "Accélérer la livraison",
            ],
            "refund_request": [
                "Politique de remboursement",
                "Retourner un produit",
                "Délai de remboursement",
            ],
            "technical_support": [
                "Guide d'utilisation",
                "Contacter le support technique",
                "Signaler un bug",
            ],
            "account_help": [
                "Réinitialiser mot de passe",
                "Modifier mes informations",
                "Supprimer mon compte",
            ],
        }
        
        return intent_suggestions.get(intent, [])
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Récupère l'historique de conversation.
        
        Args:
            session_id: ID de session
            
        Returns:
            List[Dict]: Historique des échanges
        """
        context = self.get_context(session_id)
        return context.conversation_history if context else []
    
    def clear_session(self, session_id: str) -> bool:
        """
        Supprime une session de conversation.
        
        Args:
            session_id: ID de session
            
        Returns:
            bool: True si supprimé avec succès
        """
        if session_id in self.conversation_contexts:
            del self.conversation_contexts[session_id]
            logger.info("Session cleared", session_id=session_id)
            return True
        return False
    
    def get_active_sessions_count(self) -> int:
        """
        Retourne le nombre de sessions actives.
        
        Returns:
            int: Nombre de sessions
        """
        return len(self.conversation_contexts)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Nettoie les sessions anciennes.
        
        Args:
            max_age_hours: Âge maximum en heures
            
        Returns:
            int: Nombre de sessions supprimées
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        old_sessions = [
            session_id for session_id, context in self.conversation_contexts.items()
            if current_time - context.last_activity > max_age_seconds
        ]
        
        for session_id in old_sessions:
            del self.conversation_contexts[session_id]
        
        if old_sessions:
            logger.info(
                "Cleaned up old sessions",
                count=len(old_sessions),
                max_age_hours=max_age_hours,
            )
        
        return len(old_sessions)