#!/usr/bin/env python3
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import User, Conversation

def seed_database():
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/chatbot")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Sample data
    sample_user = User(user_id="demo_user_123")
    sample_conversation = Conversation(
        session_id="demo_session_123",
        user_message="Hello, I need help",
        bot_response="Hello! How can I help you today?",
        intent="general_inquiry",
        confidence=0.95
    )
    
    session.add(sample_user)
    session.add(sample_conversation)
    session.commit()
    session.close()
    print("Database seeded successfully")

if __name__ == "__main__":
    seed_database()