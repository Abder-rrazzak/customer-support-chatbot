from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import uvicorn
import os

from .schemas import ChatRequest, ChatResponse, SessionCreate, SessionResponse
from ..chatbot.engine import ChatbotEngine
from ..analytics.metrics import MetricsCollector

app = FastAPI(
    title="Customer Support Chatbot API",
    description="Enterprise-grade AI chatbot for customer support",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
chatbot = ChatbotEngine()
metrics = MetricsCollector()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-api"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    metrics.start_request()
    
    result = chatbot.process_message(request.message, request.session_id)
    
    metrics.end_request()
    
    return ChatResponse(**result)

@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        result = chatbot.process_message(data)
        await websocket.send_json(result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)