from typing import Dict

class ResponseGenerator:
    def __init__(self):
        self.templates = {
            "order_status": "I'll help you check your order status. Could you provide your order number?",
            "return_request": "I can help you with your return. What item would you like to return?",
            "technical_support": "I'm here to help with technical issues. What problem are you experiencing?",
            "billing_inquiry": "I can assist with billing questions. What would you like to know?",
            "product_info": "I'd be happy to provide product information. Which product interests you?",
            "account_help": "I can help with your account. What do you need assistance with?",
            "general_inquiry": "Hello! How can I help you today?"
        }
    
    def generate(self, intent: str, entities: Dict = None) -> str:
        return self.templates.get(intent, self.templates["general_inquiry"])