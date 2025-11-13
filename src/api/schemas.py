"""
Schémas Pydantic pour l'API du chatbot.

Ce module définit tous les modèles de données utilisés par l'API
pour la validation des entrées et la sérialisation des sorties.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ChatMessage(BaseModel):
    """
    Modèle pour un message de chat.
    
    Représente un message envoyé par l'utilisateur ou le bot
    avec toutes les métadonnées nécessaires.
    """
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Contenu du message",
        example="Bonjour, j'ai un problème avec ma commande"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="ID de session de conversation",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="ID de l'utilisateur",
        example="user_12345"
    )
    
    metadata: Optional[Dict] = Field(
        default_factory=dict,
        description="Métadonnées additionnelles"
    )
    
    @validator('message')
    def validate_message(cls, v):
        """Valide que le message n'est pas vide après nettoyage."""
        if not v.strip():
            raise ValueError('Le message ne peut pas être vide')
        return v.strip()


class ChatResponse(BaseModel):
    """
    Modèle pour la réponse du chatbot.
    
    Contient la réponse générée et toutes les métadonnées
    associées pour le monitoring et le debugging.
    """
    
    message: str = Field(
        ...,
        description="Réponse du chatbot"
    )
    
    session_id: str = Field(
        ...,
        description="ID de session"
    )
    
    intent: Optional[str] = Field(
        None,
        description="Intention détectée",
        example="order_status"
    )
    
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Niveau de confiance de la classification"
    )
    
    entities: Dict = Field(
        default_factory=dict,
        description="Entités extraites du message"
    )
    
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions de réponses rapides"
    )
    
    requires_human: bool = Field(
        False,
        description="Indique si un agent humain est nécessaire"
    )
    
    response_time_ms: float = Field(
        ...,
        description="Temps de traitement en millisecondes"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la réponse"
    )
    
    model_version: str = Field(
        "1.0.0",
        description="Version du modèle utilisé"
    )


class ConversationHistory(BaseModel):
    """
    Modèle pour l'historique de conversation.
    
    Représente l'historique complet d'une session
    avec tous les échanges utilisateur-bot.
    """
    
    session_id: str = Field(
        ...,
        description="ID de session"
    )
    
    user_id: Optional[str] = Field(
        None,
        description="ID de l'utilisateur"
    )
    
    messages: List[Dict] = Field(
        ...,
        description="Liste des échanges de la conversation"
    )
    
    created_at: datetime = Field(
        ...,
        description="Date de création de la session"
    )
    
    last_activity: datetime = Field(
        ...,
        description="Dernière activité"
    )
    
    total_messages: int = Field(
        ...,
        description="Nombre total de messages"
    )


class SessionCreate(BaseModel):
    """
    Modèle pour créer une nouvelle session.
    
    Utilisé pour initialiser une nouvelle conversation
    avec des paramètres optionnels.
    """
    
    user_id: Optional[str] = Field(
        None,
        description="ID de l'utilisateur"
    )
    
    metadata: Optional[Dict] = Field(
        default_factory=dict,
        description="Métadonnées de session"
    )


class SessionResponse(BaseModel):
    """
    Modèle pour la réponse de création de session.
    
    Retourne les informations de la session créée.
    """
    
    session_id: str = Field(
        ...,
        description="ID de la session créée"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date de création"
    )
    
    message: str = Field(
        "Session créée avec succès",
        description="Message de confirmation"
    )


class HealthResponse(BaseModel):
    """
    Modèle pour la réponse de santé de l'API.
    
    Utilisé par les endpoints de monitoring pour vérifier
    que tous les composants fonctionnent correctement.
    """
    
    status: str = Field(
        ...,
        description="Statut général de l'API",
        example="healthy"
    )
    
    version: str = Field(
        ...,
        description="Version de l'API",
        example="1.0.0"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la vérification"
    )
    
    components: Dict = Field(
        ...,
        description="Statut des composants individuels"
    )
    
    active_sessions: int = Field(
        ...,
        description="Nombre de sessions actives"
    )


class IntentClassificationRequest(BaseModel):
    """
    Modèle pour une requête de classification d'intention.
    
    Utilisé pour tester le classificateur d'intentions
    de manière isolée.
    """
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Texte à classifier"
    )
    
    context: Optional[Dict] = Field(
        None,
        description="Contexte optionnel pour améliorer la classification"
    )


class IntentClassificationResponse(BaseModel):
    """
    Modèle pour la réponse de classification d'intention.
    
    Retourne l'intention détectée avec les métadonnées
    de classification.
    """
    
    intent: str = Field(
        ...,
        description="Intention détectée"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Niveau de confiance"
    )
    
    entities: Dict = Field(
        default_factory=dict,
        description="Entités extraites"
    )
    
    all_probabilities: Dict = Field(
        default_factory=dict,
        description="Probabilités pour toutes les intentions"
    )
    
    processing_time_ms: float = Field(
        ...,
        description="Temps de traitement"
    )


class TrainingDataItem(BaseModel):
    """
    Modèle pour un élément de données d'entraînement.
    
    Représente un exemple d'entraînement pour le
    classificateur d'intentions.
    """
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Texte d'exemple"
    )
    
    intent: str = Field(
        ...,
        description="Intention associée"
    )
    
    entities: Optional[Dict] = Field(
        None,
        description="Entités annotées (optionnel)"
    )


class TrainingRequest(BaseModel):
    """
    Modèle pour une requête d'entraînement.
    
    Contient les données et paramètres pour entraîner
    le classificateur d'intentions.
    """
    
    training_data: List[TrainingDataItem] = Field(
        ...,
        min_items=10,
        description="Données d'entraînement"
    )
    
    validation_split: float = Field(
        0.2,
        ge=0.1,
        le=0.5,
        description="Proportion pour la validation"
    )
    
    save_model: bool = Field(
        True,
        description="Sauvegarder le modèle après entraînement"
    )


class TrainingResponse(BaseModel):
    """
    Modèle pour la réponse d'entraînement.
    
    Retourne les métriques et résultats de l'entraînement
    du classificateur.
    """
    
    success: bool = Field(
        ...,
        description="Succès de l'entraînement"
    )
    
    metrics: Dict = Field(
        ...,
        description="Métriques d'entraînement"
    )
    
    training_time_seconds: float = Field(
        ...,
        description="Durée d'entraînement"
    )
    
    model_version: str = Field(
        ...,
        description="Version du modèle entraîné"
    )
    
    message: str = Field(
        ...,
        description="Message de statut"
    )


class ErrorResponse(BaseModel):
    """
    Modèle standardisé pour les réponses d'erreur.
    
    Fournit des informations détaillées sur les erreurs
    pour faciliter le debugging et le monitoring.
    """
    
    error: str = Field(
        ...,
        description="Message d'erreur principal"
    )
    
    error_code: str = Field(
        ...,
        description="Code d'erreur pour identification programmatique"
    )
    
    details: Optional[str] = Field(
        None,
        description="Détails supplémentaires sur l'erreur"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de l'erreur"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="ID de requête pour le tracing"
    )


class WebSocketMessage(BaseModel):
    """
    Modèle pour les messages WebSocket.
    
    Structure standardisée pour la communication
    en temps réel via WebSocket.
    """
    
    type: str = Field(
        ...,
        description="Type de message",
        example="chat_message"
    )
    
    data: Dict = Field(
        ...,
        description="Données du message"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="ID de session"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp du message"
    )


class AnalyticsRequest(BaseModel):
    """
    Modèle pour les requêtes d'analytics.
    
    Utilisé pour récupérer des statistiques et métriques
    sur l'utilisation du chatbot.
    """
    
    start_date: Optional[datetime] = Field(
        None,
        description="Date de début pour les statistiques"
    )
    
    end_date: Optional[datetime] = Field(
        None,
        description="Date de fin pour les statistiques"
    )
    
    metrics: List[str] = Field(
        default_factory=lambda: ["total_conversations", "avg_response_time"],
        description="Métriques à inclure"
    )
    
    group_by: Optional[str] = Field(
        None,
        description="Grouper par (day, hour, intent, etc.)"
    )


class AnalyticsResponse(BaseModel):
    """
    Modèle pour les réponses d'analytics.
    
    Retourne les statistiques et métriques demandées
    sur l'utilisation du chatbot.
    """
    
    period: Dict = Field(
        ...,
        description="Période analysée"
    )
    
    metrics: Dict = Field(
        ...,
        description="Métriques calculées"
    )
    
    trends: Optional[Dict] = Field(
        None,
        description="Tendances identifiées"
    )
    
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date de génération du rapport"
    )