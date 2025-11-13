# Documentation

## API Endpoints

### POST /chat
Send a message to the chatbot.

**Request:**
```json
{
  "message": "I need help with my order",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "response": "I can help you with your order. What specific issue are you experiencing?",
  "intent": "order_help",
  "confidence": 0.85
}
```

## Configuration

The application uses `configs/config.yaml` for configuration settings.

## Database Schema

- **conversations**: Stores chat history with user messages and bot responses.