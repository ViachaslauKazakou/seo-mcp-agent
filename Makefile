.PHONY: help install update clean test lint format run-web run-desktop docs docs-live
.PHONY: db-start db-stop db-migrate db-create-migration db-reset db-shell db-logs db-init
.PHONY: docker-up docker-down docker-build docker-logs
.DEFAULT_GOAL := help

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo ""
	@echo "$(BLUE)SEO MCP Agent - Available Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Installation & Setup

install: ## Install all dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	poetry install
	@echo "$(BLUE)🎭 Installing Playwright browsers...$(NC)"
	poetry run playwright install chromium
	@echo "$(GREEN)✅ Installation complete!$(NC)"

update: ## Update dependencies
	@echo "$(BLUE)🔄 Updating dependencies...$(NC)"
	poetry update
	@echo "$(GREEN)✅ Dependencies updated!$(NC)"

clean: ## Clean cache and build files
	@echo "$(BLUE)🧹 Cleaning cache and build files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .coverage htmlcov dist build
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

##@ Database Management

db-start: ## Start PostgreSQL database
	@echo "$(BLUE)🚀 Starting PostgreSQL...$(NC)"
	@./scripts/start-db.sh

db-stop: ## Stop PostgreSQL database
	@echo "$(BLUE)🛑 Stopping PostgreSQL...$(NC)"
	@./scripts/stop-db.sh

db-migrate: ## Apply database migrations
	@echo "$(BLUE)🔄 Running migrations...$(NC)"
	@./scripts/migrate.sh

db-create-migration: ## Create new migration (usage: make db-create-migration MSG="message")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)❌ Error: MSG parameter required$(NC)"; \
		echo "$(YELLOW)Usage: make db-create-migration MSG=\"Add new table\"$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📝 Creating migration: $(MSG)$(NC)"
	@./scripts/create-migration.sh "$(MSG)"

db-init: ## Initialize database (create tables)
	@echo "$(BLUE)🔧 Initializing database...$(NC)"
	@./scripts/init-db.sh

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "$(RED)⚠️  WARNING: This will delete all data!$(NC)"
	@./scripts/reset-db.sh

db-shell: ## Open PostgreSQL CLI
	@echo "$(BLUE)🔗 Connecting to PostgreSQL CLI...$(NC)"
	@./scripts/db-shell.sh

db-logs: ## View PostgreSQL logs
	@echo "$(BLUE)📋 PostgreSQL logs (Ctrl+C to exit):$(NC)"
	@./scripts/db-logs.sh

db-status: ## Check database status
	@echo "$(BLUE)📊 Database Status:$(NC)"
	@docker-compose ps postgres

##@ Application

run-web: ## Run FastAPI web application
	@echo "$(BLUE)🌐 Starting web application...$(NC)"
	poetry run uvicorn src.main:app --host 0.0.0.0 --port 8030 --reload

run-desktop: ## Run PySide6 desktop application
	@echo "$(BLUE)🖥️  Starting desktop application...$(NC)"
	poetry run python desktop/main.py

dev: db-start run-web ## Start database and web app (development mode)

##@ Testing & Quality

test: ## Run tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	poetry run pytest -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)🧪 Running tests with coverage...$(NC)"
	poetry run pytest -v --cov=src --cov-report=html --cov-report=term

lint: ## Run code linting
	@echo "$(BLUE)🔍 Running linting...$(NC)"
	poetry run flake8 src/ tests/ --max-line-length=120 --exclude=__pycache__,migrations

format: ## Format code with black
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	poetry run black src/ tests/ desktop/ --line-length=120

format-check: ## Check code formatting without changes
	@echo "$(BLUE)🔍 Checking code format...$(NC)"
	poetry run black src/ tests/ desktop/ --check --line-length=120

typecheck: ## Run type checking with mypy
	@echo "$(BLUE)🔍 Running type checks...$(NC)"
	poetry run mypy src/ --ignore-missing-imports

quality: format lint typecheck ## Run all quality checks

##@ Documentation

docs: ## Build documentation (HTML)
	@echo "$(BLUE)📚 Building documentation...$(NC)"
	cd docs && poetry run sphinx-build -b html . _build/html
	@echo "$(GREEN)✅ Documentation built: docs/_build/html/index.html$(NC)"

docs-open: docs ## Build and open documentation
	@echo "$(BLUE)🌐 Opening documentation...$(NC)"
	@open docs/_build/html/index.html || xdg-open docs/_build/html/index.html || start docs/_build/html/index.html

docs-live: ## Start documentation live-reload server
	@echo "$(BLUE)📚 Starting documentation server on http://localhost:8080$(NC)"
	poetry run sphinx-autobuild docs docs/_build/html --port 8080

docs-clean: ## Clean documentation build
	@echo "$(BLUE)🧹 Cleaning documentation build...$(NC)"
	rm -rf docs/_build
	@echo "$(GREEN)✅ Documentation cleaned!$(NC)"

##@ Docker

docker-up: ## Start all Docker services
	@echo "$(BLUE)🐳 Starting Docker services...$(NC)"
	docker-compose up -d

docker-down: ## Stop all Docker services
	@echo "$(BLUE)🐳 Stopping Docker services...$(NC)"
	docker-compose down

docker-build: ## Build Docker images
	@echo "$(BLUE)🐳 Building Docker images...$(NC)"
	docker-compose build

docker-logs: ## View Docker logs
	@echo "$(BLUE)📋 Docker logs (Ctrl+C to exit):$(NC)"
	docker-compose logs -f

docker-ps: ## Show Docker container status
	@echo "$(BLUE)📊 Docker Status:$(NC)"
	@docker-compose ps

docker-clean: ## Remove Docker containers and volumes
	@echo "$(RED)⚠️  WARNING: This will delete all Docker data!$(NC)"
	@read -p "Are you sure? (yes/no): " -n 3 -r; \
	if [ "$$REPLY" = "yes" ]; then \
		echo ""; \
		echo "$(BLUE)🧹 Cleaning Docker...$(NC)"; \
		docker-compose down -v; \
		echo "$(GREEN)✅ Docker cleaned!$(NC)"; \
	else \
		echo ""; \
		echo "$(YELLOW)❌ Cancelled$(NC)"; \
	fi

##@ Project Setup

setup: install db-start db-migrate ## Complete project setup (install + DB)
	@echo ""
	@echo "$(GREEN)✅ Project setup complete!$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run: make run-web"
	@echo "  3. Open: http://localhost:8030"
	@echo ""

env-example: ## Create .env from .env.example
	@if [ ! -f .env ]; then \
		echo "$(BLUE)📝 Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✅ Created .env file$(NC)"; \
		echo "$(YELLOW)⚠️  Please edit .env with your settings$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  .env already exists$(NC)"; \
	fi

check-env: ## Check if required environment variables are set
	@echo "$(BLUE)🔍 Checking environment variables...$(NC)"
	@if [ -f .env ]; then \
		echo "$(GREEN)✅ .env file exists$(NC)"; \
	else \
		echo "$(RED)❌ .env file not found$(NC)"; \
		echo "$(YELLOW)Run: make env-example$(NC)"; \
	fi

##@ CI/CD

ci-test: ## Run CI tests
	@echo "$(BLUE)🔄 Running CI tests...$(NC)"
	poetry install
	poetry run pytest -v --cov=src --cov-report=xml

ci-lint: ## Run CI linting
	@echo "$(BLUE)🔄 Running CI linting...$(NC)"
	poetry run black src/ tests/ desktop/ --check --line-length=120
	poetry run flake8 src/ tests/ --max-line-length=120

ci-docs: ## Build docs for CI
	@echo "$(BLUE)🔄 Building documentation for CI...$(NC)"
	cd docs && poetry run sphinx-build -b html . _build/html -W

ci: ci-lint ci-test ## Run all CI checks

##@ Utilities

version: ## Show project version
	@echo "$(BLUE)📦 Project Version:$(NC)"
	@poetry version

shell: ## Open Poetry shell
	@echo "$(BLUE)🐚 Opening Poetry shell...$(NC)"
	poetry shell

info: ## Show project information
	@echo "$(BLUE)ℹ️  Project Information:$(NC)"
	@echo ""
	@echo "  Name: SEO MCP Agent"
	@echo "  Python: $$(poetry run python --version)"
	@echo "  Poetry: $$(poetry --version)"
	@echo "  Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "$(BLUE)📂 Project Structure:$(NC)"
	@tree -L 2 -I '__pycache__|*.pyc|.venv|node_modules' . || ls -la

scripts-help: ## Show database scripts help
	@echo "$(BLUE)🔧 Database Management Scripts:$(NC)"
	@echo ""
	@echo "  $(GREEN)start-db.sh$(NC)          - Start PostgreSQL database"
	@echo "  $(GREEN)stop-db.sh$(NC)           - Stop PostgreSQL database"
	@echo "  $(GREEN)migrate.sh$(NC)           - Apply database migrations"
	@echo "  $(GREEN)create-migration.sh$(NC)  - Create new migration"
	@echo "  $(GREEN)init-db.sh$(NC)           - Initialize database"
	@echo "  $(GREEN)reset-db.sh$(NC)          - Reset database (deletes data)"
	@echo "  $(GREEN)db-shell.sh$(NC)          - Open PostgreSQL CLI"
	@echo "  $(GREEN)db-logs.sh$(NC)           - View PostgreSQL logs"
	@echo ""
	@echo "$(YELLOW)See scripts/README.md for detailed usage$(NC)"

##@ Quick Commands

quick-start: setup run-web ## Quick start: setup everything and run web app

quick-test: lint test ## Quick test: lint and test

quick-fix: format lint ## Quick fix: format and lint code

.PHONY: all
all: help
