#!/usr/bin/env python3
import os
from sqlalchemy import create_engine
from src.database.models import Base

def init_database():
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/chatbot")
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print("Database initialized successfully")

if __name__ == "__main__":
    init_database()