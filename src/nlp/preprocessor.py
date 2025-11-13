import re
from typing import str

class TextPreprocessor:
    def __init__(self):
        self.patterns = [
            (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ''),
            (r'@[A-Za-z0-9]+', ''),
            (r'#[A-Za-z0-9]+', ''),
        ]
    
    def clean(self, text: str) -> str:
        text = text.lower().strip()
        for pattern, replacement in self.patterns:
            text = re.sub(pattern, replacement, text)
        return text