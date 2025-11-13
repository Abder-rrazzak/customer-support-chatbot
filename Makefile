# Makefile professionnel pour le projet Customer Support Chatbot
# Fournit des commandes standardisées pour le développement, les tests et le déploiement

# Variables de configuration
PYTHON := python3
PIP := pip
VENV_DIR := venv
SRC_DIR := src
TEST_DIR := tests
MODEL_DIR := models
DATA_DIR := data
DOCS_DIR := docs
DOCKER_IMAGE := customer-support-chatbot
DOCKER_TAG := latest

# Détection de l'OS pour les commandes spécifiques
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	ACTIVATE := source $(VENV_DIR)/bin/activate
	PYTHON_VENV := $(VENV_DIR)/bin/python
	PIP_VENV := $(VENV_DIR)/bin/pip
else ifeq ($(UNAME_S),Darwin)
	ACTIVATE := source $(VENV_DIR)/bin/activate
	PYTHON_VENV := $(VENV_DIR)/bin/python
	PIP_VENV := $(VENV_DIR)/bin/pip
else
	ACTIVATE := $(VENV_DIR)\Scripts\activate
	PYTHON_VENV := $(VENV_DIR)\Scripts\python
	PIP_VENV := $(VENV_DIR)\Scripts\pip
endif

# Couleurs pour les messages
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m

# Cibles principales
.PHONY: help setup install dev-install lint format test test-cov train-intent api websocket clean clean-all docker-build docker-run docs security audit pre-commit

# Cible par défaut : afficher l'aide
help: ## Afficher cette aide
	@echo "$(BLUE)🤖 Commandes disponibles pour le Customer Support Chatbot:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-25s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)📋 Workflow recommandé:$(NC)"
	@echo "  1. make setup              # Configuration initiale"
	@echo "  2. make dev-install        # Installation complète"
	@echo "  3. make train-intent       # Entraînement du classificateur"
	@echo "  4. make test               # Tests"
	@echo "  5. make api                # Lancer l'API"

## === CONFIGURATION ET INSTALLATION ===

setup: ## Configuration rapide de l'environnement
	@echo "$(BLUE)🔧 Configuration de l'environnement chatbot...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP_VENV) install --upgrade pip setuptools wheel
	$(PIP_VENV) install -e .
	@echo "$(GREEN)✅ Environnement configuré$(NC)"

dev-setup: ## Configuration complète pour le développement
	@echo "$(BLUE)🛠️ Configuration développement...$(NC)"
	./scripts/setup_dev.sh
	@echo "$(GREEN)✅ Environnement de développement prêt$(NC)"

install: ## Installation des dépendances de base
	$(PIP_VENV) install -e .

dev-install: ## Installation complète avec outils de développement
	$(PIP_VENV) install -e ".[dev,docs,viz,mlops,prod]"
	$(PIP_VENV) install pre-commit
	pre-commit install

download-models: ## Télécharger les modèles NLP pré-entraînés
	@echo "$(BLUE)📥 Téléchargement des modèles NLP...$(NC)"
	$(PYTHON_VENV) -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
	$(PYTHON_VENV) -m spacy download fr_core_news_sm
	$(PYTHON_VENV) -m spacy download en_core_web_sm
	@echo "$(GREEN)✅ Modèles téléchargés$(NC)"

## === QUALITÉ DU CODE ===

lint: ## Vérification du style de code avec flake8
	@echo "$(BLUE)🔍 Vérification du code...$(NC)"
	$(PYTHON_VENV) -m flake8 $(SRC_DIR)/ $(TEST_DIR)/ --max-line-length=88 --statistics
	@echo "$(GREEN)✅ Code vérifié$(NC)"

format: ## Formatage automatique du code avec Black et isort
	@echo "$(BLUE)🎨 Formatage du code...$(NC)"
	$(PYTHON_VENV) -m black $(SRC_DIR)/ $(TEST_DIR)/ --line-length=88
	$(PYTHON_VENV) -m isort $(SRC_DIR)/ $(TEST_DIR)/ --profile=black
	@echo "$(GREEN)✅ Code formaté$(NC)"

type-check: ## Vérification des types avec MyPy
	@echo "$(BLUE)🔬 Vérification des types...$(NC)"
	$(PYTHON_VENV) -m mypy $(SRC_DIR)/ --ignore-missing-imports

security: ## Analyse de sécurité avec Bandit
	@echo "$(BLUE)🔒 Analyse de sécurité...$(NC)"
	$(PYTHON_VENV) -m bandit -r $(SRC_DIR)/ -f json -o security-report.json
	$(PYTHON_VENV) -m bandit -r $(SRC_DIR)/

audit: ## Audit des vulnérabilités des dépendances
	@echo "$(BLUE)🛡️ Audit des dépendances...$(NC)"
	$(PIP_VENV) audit

pre-commit: ## Exécuter tous les hooks pre-commit
	@echo "$(BLUE)🪝 Exécution des hooks pre-commit...$(NC)"
	pre-commit run --all-files

## === TESTS ===

test: ## Exécuter les tests unitaires
	@echo "$(BLUE)🧪 Exécution des tests...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m pytest $(TEST_DIR)/ -v

test-cov: ## Tests avec couverture de code
	@echo "$(BLUE)📊 Tests avec couverture...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m pytest $(TEST_DIR)/ -v --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "$(GREEN)📈 Rapport de couverture: htmlcov/index.html$(NC)"

test-api: ## Tests spécifiques à l'API
	@echo "$(BLUE)🌐 Tests API...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m pytest $(TEST_DIR)/test_api.py -v

test-chatbot: ## Tests spécifiques au chatbot
	@echo "$(BLUE)🤖 Tests chatbot...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m pytest $(TEST_DIR)/test_chatbot.py -v

test-integration: ## Tests d'intégration
	@echo "$(BLUE)🔗 Tests d'intégration...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m pytest $(TEST_DIR)/integration/ -v

## === MACHINE LEARNING ET NLP ===

train-intent: ## Entraîner le classificateur d'intentions
	@echo "$(BLUE)🎯 Entraînement du classificateur d'intentions...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.chatbot.train --component intent_classifier
	@echo "$(GREEN)✅ Classificateur entraîné$(NC)"

train-all: ## Entraîner tous les modèles ML
	@echo "$(BLUE)🚀 Entraînement de tous les modèles...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.chatbot.train --component all

evaluate-model: ## Évaluer les performances du modèle
	@echo "$(BLUE)📊 Évaluation du modèle...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.chatbot.evaluate

generate-training-data: ## Générer des données d'entraînement synthétiques
	@echo "$(BLUE)🔄 Génération de données d'entraînement...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.data.generate_training_data

## === API ET SERVICES ===

api: ## Lancer l'API FastAPI en mode développement
	@echo "$(BLUE)🌐 Lancement de l'API chatbot...$(NC)"
	@echo "$(YELLOW)📡 API disponible sur: http://localhost:8000$(NC)"
	@echo "$(YELLOW)📚 Documentation: http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)💬 WebSocket: ws://localhost:8000/ws$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.api.main

api-prod: ## Lancer l'API en mode production avec Gunicorn
	@echo "$(BLUE)🏭 Lancement API production...$(NC)"
	gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

websocket: ## Tester la connexion WebSocket
	@echo "$(BLUE)🔌 Test WebSocket...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.api.websocket_client

cli: ## Interface en ligne de commande du chatbot
	@echo "$(BLUE)💬 Interface CLI du chatbot...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.chatbot.cli

## === BASE DE DONNÉES ===

db-init: ## Initialiser la base de données
	@echo "$(BLUE)🗄️ Initialisation de la base de données...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.database.init_db

db-migrate: ## Appliquer les migrations de base de données
	@echo "$(BLUE)🔄 Application des migrations...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m alembic upgrade head

db-seed: ## Peupler la base de données avec des données de test
	@echo "$(BLUE)🌱 Peuplement de la base de données...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.database.seed_data

## === DOCKER ===

docker-build: ## Construire l'image Docker
	@echo "$(BLUE)🐳 Construction de l'image Docker...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Lancer le conteneur Docker
	@echo "$(BLUE)🚀 Lancement du conteneur...$(NC)"
	docker run -p 8000:8000 -p 8080:8080 $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-compose-up: ## Lancer tous les services avec Docker Compose
	@echo "$(BLUE)🐳 Lancement des services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Services démarrés:$(NC)"
	@echo "  • API: http://localhost:8000"
	@echo "  • Redis: localhost:6379"
	@echo "  • PostgreSQL: localhost:5432"

docker-compose-dev: ## Lancer en mode développement
	@echo "$(BLUE)🛠️ Mode développement...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

docker-compose-down: ## Arrêter tous les services
	docker-compose down

## === DOCUMENTATION ===

docs: ## Générer la documentation avec Sphinx
	@echo "$(BLUE)📚 Génération de la documentation...$(NC)"
	mkdir -p $(DOCS_DIR)
	$(PYTHON_VENV) -m sphinx-quickstart -q -p "Customer Support Chatbot" -a "Abder Rrazzak" $(DOCS_DIR)
	$(PYTHON_VENV) -m sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html
	@echo "$(GREEN)📖 Documentation: $(DOCS_DIR)/_build/html/index.html$(NC)"

docs-serve: ## Servir la documentation localement
	@echo "$(BLUE)🌐 Service de documentation...$(NC)"
	$(PYTHON_VENV) -m http.server 8080 -d $(DOCS_DIR)/_build/html

api-docs: ## Générer la documentation API
	@echo "$(BLUE)📋 Documentation API...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -c "
	from src.api.main import app
	import json
	with open('api-schema.json', 'w') as f:
	    json.dump(app.openapi(), f, indent=2)
	"

## === NOTEBOOKS ET ANALYSE ===

jupyter: ## Lancer Jupyter Lab
	@echo "$(BLUE)📓 Lancement de Jupyter Lab...$(NC)"
	@echo "$(YELLOW)🔗 Interface: http://localhost:8888$(NC)"
	$(PYTHON_VENV) -m jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

notebook-convert: ## Convertir les notebooks en HTML
	@echo "$(BLUE)🔄 Conversion des notebooks...$(NC)"
	mkdir -p $(DOCS_DIR)/notebooks
	for notebook in notebooks/*.ipynb; do \
		$(PYTHON_VENV) -m jupyter nbconvert --to html --output-dir $(DOCS_DIR)/notebooks "$$notebook"; \
	done

## === MONITORING ET ANALYTICS ===

monitor: ## Lancer le monitoring avec Prometheus et Grafana
	@echo "$(BLUE)📊 Lancement du monitoring...$(NC)"
	docker-compose -f docker-compose.monitoring.yml up -d
	@echo "$(GREEN)✅ Monitoring disponible:$(NC)"
	@echo "  • Prometheus: http://localhost:9090"
	@echo "  • Grafana: http://localhost:3000"

logs: ## Afficher les logs en temps réel
	@echo "$(BLUE)📋 Logs en temps réel...$(NC)"
	tail -f logs/chatbot.log

analytics: ## Générer un rapport d'analytics
	@echo "$(BLUE)📈 Génération du rapport d'analytics...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.analytics.generate_report

## === DÉPLOIEMENT ===

deploy-staging: ## Déployer en staging
	@echo "$(BLUE)🚀 Déploiement staging...$(NC)"
	./scripts/deploy_staging.sh

deploy-prod: ## Déployer en production
	@echo "$(BLUE)🏭 Déploiement production...$(NC)"
	./scripts/deploy_production.sh

backup-models: ## Sauvegarder les modèles entraînés
	@echo "$(BLUE)💾 Sauvegarde des modèles...$(NC)"
	tar -czf models-backup-$(shell date +%Y%m%d_%H%M%S).tar.gz $(MODEL_DIR)/

## === NETTOYAGE ===

clean: ## Nettoyer les fichiers temporaires
	@echo "$(BLUE)🧹 Nettoyage des fichiers temporaires...$(NC)"
	rm -rf __pycache__/
	rm -rf $(SRC_DIR)/__pycache__/
	rm -rf $(TEST_DIR)/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

clean-models: ## Supprimer les modèles entraînés
	@echo "$(YELLOW)⚠️ Suppression des modèles...$(NC)"
	rm -rf $(MODEL_DIR)/*.pkl
	rm -rf $(MODEL_DIR)/*.joblib

clean-data: ## Supprimer les données traitées
	@echo "$(YELLOW)⚠️ Suppression des données traitées...$(NC)"
	rm -rf $(DATA_DIR)/processed/*
	rm -rf $(DATA_DIR)/conversations/*

clean-all: clean clean-models ## Nettoyage complet
	@echo "$(BLUE)🧹 Nettoyage complet...$(NC)"
	rm -rf $(VENV_DIR)/
	rm -rf logs/
	rm -rf .mlruns/
	docker system prune -f
	@echo "$(GREEN)✅ Nettoyage complet terminé$(NC)"

## === UTILITAIRES ===

status: ## Afficher le statut du projet
	@echo "$(BLUE)📊 Statut du projet:$(NC)"
	@echo "  • Python: $$($(PYTHON) --version)"
	@echo "  • Environnement virtuel: $$(if [ -d $(VENV_DIR) ]; then echo '✅ Présent'; else echo '❌ Absent'; fi)"
	@echo "  • Modèles entraînés: $$(if [ -f $(MODEL_DIR)/intent_classifier.pkl ]; then echo '✅ Présent'; else echo '❌ Absent'; fi)"
	@echo "  • Base de données: $$(if [ -f chatbot.db ]; then echo '✅ Initialisée'; else echo '❌ Non initialisée'; fi)"

check-deps: ## Vérifier les dépendances obsolètes
	@echo "$(BLUE)🔍 Vérification des dépendances...$(NC)"
	$(PIP_VENV) list --outdated

update-deps: ## Mettre à jour les dépendances
	@echo "$(BLUE)⬆️ Mise à jour des dépendances...$(NC)"
	$(PIP_VENV) install --upgrade pip setuptools wheel
	$(PIP_VENV) install -e ".[dev,docs,viz,mlops,prod]" --upgrade

benchmark: ## Exécuter les benchmarks de performance
	@echo "$(BLUE)⚡ Benchmarks de performance...$(NC)"
	PYTHONPATH=. $(PYTHON_VENV) -m src.benchmarks.run_benchmarks

## === CI/CD ===

ci: ## Pipeline CI (utilisé par GitHub Actions)
	@echo "$(BLUE)🔄 Pipeline CI...$(NC)"
	make lint
	make type-check
	make security
	make test-cov
	@echo "$(GREEN)✅ Pipeline CI réussi$(NC)"

build: ## Build complet du projet
	@echo "$(BLUE)🏗️ Build du projet...$(NC)"
	make clean
	make dev-install
	make download-models
	make lint
	make type-check
	make test-cov
	make train-intent
	@echo "$(GREEN)✅ Build terminé avec succès$(NC)"

release: ## Préparer une release
	@echo "$(BLUE)🚀 Préparation de la release...$(NC)"
	make clean-all
	make setup
	make build
	make docker-build
	@echo "$(GREEN)✅ Release prête$(NC)"

# Cible par défaut si aucune n'est spécifiée
.DEFAULT_GOAL := help