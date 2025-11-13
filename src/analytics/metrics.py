from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
REQUEST_COUNT = Counter('chatbot_requests_total', 'Total requests')
RESPONSE_TIME = Histogram('chatbot_response_time_seconds', 'Response time')
INTENT_ACCURACY = Gauge('chatbot_intent_accuracy', 'Intent classification accuracy')

class MetricsCollector:
    def __init__(self):
        self.start_time = None
    
    def start_request(self):
        self.start_time = time.time()
        REQUEST_COUNT.inc()
    
    def end_request(self):
        if self.start_time:
            duration = time.time() - self.start_time
            RESPONSE_TIME.observe(duration)
    
    def update_accuracy(self, accuracy: float):
        INTENT_ACCURACY.set(accuracy)