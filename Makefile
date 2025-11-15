.PHONY: help setup dev-install download-models db-init db-migrate db-seed train-intent evaluate-model api docker-build docker-compose-up format lint test

help:
	@echo "Available commands:"
	@echo "  setup              - Initial project setup"
	@echo "  dev-install        - Install development dependencies"
	@echo "  download-models    - Download NLP models"
	@echo "  db-init           - Initialize database"
	@echo "  db-migrate        - Run database migrations"
	@echo "  db-seed           - Seed database with sample data"
	@echo "  train-intent      - Train intent classifier"
	@echo "  evaluate-model    - Evaluate model performance"
	@echo "  api               - Start API server"
	@echo "  docker-build      - Build Docker image"
	@echo "  docker-compose-up - Start services with Docker Compose"
	@echo "  format            - Format code with black"
	@echo "  lint              - Lint code with flake8"
	@echo "  test              - Run tests"

setup:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

dev-install:
	pip install -r requirements-dev.txt
	pip install -e .

download-models:
	pip install spacy
	python -m spacy download en_core_web_sm
	python -m spacy download fr_core_news_sm

db-init:
	python scripts/init_db.py

db-migrate:
	alembic upgrade head

db-seed:
	python scripts/seed_db.py

download-dataset:
	python scripts/create_sample_dataset.py

train-intent:
	python scripts/mlops/train_model.py

fine-tune:
	python scripts/mlops/fine_tune_model.py

evaluate-model:
	python scripts/mlops/evaluate_model.py

api:
	@echo "Starting API server..."
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

api-dev:
	@echo "Starting API in development mode (no Docker required)..."
	python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

docker-build:
	docker build -t customer-support-chatbot .

docker-compose-up:
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "❌ Docker not found. Please install Docker Desktop and enable WSL2 integration."; \
		echo "Visit: https://docs.docker.com/go/wsl2/"; \
		exit 1; \
	fi
	@command -v "docker-compose" >/dev/null 2>&1 && docker-compose up -d || docker compose up -d

format:
	black src tests
	isort src tests

lint:
	flake8 src tests
	mypy src

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=xml