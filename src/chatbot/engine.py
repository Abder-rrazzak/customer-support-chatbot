from .intent_classifier import IntentClassifier
from .entity_extractor import EntityExtractor
from .response_generator import ResponseGenerator
from ..nlp.preprocessor import TextPreprocessor

class ChatbotEngine:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.response_generator = ResponseGenerator()
    
    def process_message(self, message: str, session_id: str = None):
        # Preprocess
        clean_text = self.preprocessor.clean(message)
        
        # Classify intent
        intent_result = self.intent_classifier.classify(clean_text)
        
        # Extract entities
        entities = self.entity_extractor.extract(clean_text)
        
        # Generate response
        response = self.response_generator.generate(
            intent_result["intent"], entities
        )
        
        return {
            "message": response,
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "entities": entities,
            "requires_human": intent_result["confidence"] < 0.7
        }