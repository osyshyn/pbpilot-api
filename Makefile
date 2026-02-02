.PHONY: help install migrate migrate-up migrate-down migrate-create migrate-current migrate-history run run-dev test format lint type-check clean setup create-admin compose-up compose-down compose-logs api-logs compose-restart

# Variables
ALEMBIC_CONFIG = models/alembic.ini
PYTHON = uv run python
UV = uv
DOCKER_COMPOSE = docker compose

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup          - Initial project setup (install deps, run migrations)"
	@echo ""
	@echo "Docker Compose:"
	@echo "  make compose-up     - Start API service"
	@echo "  make compose-down   - Stop all services"
	@echo "  make compose-logs  - View logs from all services"
	@echo "  make api-logs       - View API logs only"
	@echo ""
	@echo "Migrations:"
	@echo "  make migrate        - Run all pending migrations (alias for migrate-up)"
	@echo "  make migrate-up     - Upgrade database to latest migration"
	@echo "  make migrate-down   - Downgrade database by one migration"
	@echo "  make migrate-create - Create a new migration (usage: make migrate-create MESSAGE='description')"
	@echo "  make migrate-current - Show current migration revision"
	@echo "  make migrate-history - Show migration history"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install dependencies with UV"
	@echo "  make run            - Run the application"
	@echo "  make run-dev        - Run the application in development mode (with reload)"
	@echo "  make test           - Run tests"
	@echo "  make format         - Format code with Ruff"
	@echo "  make lint           - Lint code with Ruff"
	@echo "  make type-check     - Run type checking with mypy"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean temporary files and caches"
	@echo "  make create-admin   - Create an admin user (usage: make create-admin EMAIL=email@example.com PASSWORD=password)"

# Initial setup
setup: install migrate
	@echo "✅ Setup complete! Migrations are applied."

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	$(UV) sync

# Docker Compose commands
compose-up:
	@echo "🚀 Starting API service..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ API service started. API available at http://localhost:8000"

compose-down:
	@echo "🛑 Stopping all services..."
	$(DOCKER_COMPOSE) down
	@echo "✅ Services stopped."

compose-logs:
	@echo "📋 Viewing logs from all services:"
	$(DOCKER_COMPOSE) logs -f

compose-restart:
	@echo "🔄 Restarting all services..."
	$(DOCKER_COMPOSE) restart
	@echo "✅ Services restarted."

# Migration commands
migrate: migrate-up

migrate-up:
	@echo "⬆️  Running database migrations..."
	$(UV) run alembic -c $(ALEMBIC_CONFIG) upgrade head
	@echo "✅ Migrations applied."

migrate-down:
	@echo "⬇️  Downgrading database by one migration..."
	$(UV) run alembic -c $(ALEMBIC_CONFIG) downgrade -1
	@echo "✅ Migration downgraded."

migrate-create:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "❌ Error: MESSAGE is required. Usage: make migrate-create MESSAGE='description'"; \
		exit 1; \
	fi
	@echo "📝 Creating new migration: $(MESSAGE)"
	$(UV) run alembic -c $(ALEMBIC_CONFIG) revision --autogenerate -m "$(MESSAGE)"
	@echo "✅ Migration created. Review the file in models/migrations/versions/"

migrate-current:
	@echo "📍 Current migration revision:"
	$(UV) run alembic -c $(ALEMBIC_CONFIG) current

migrate-history:
	@echo "📜 Migration history:"
	$(UV) run alembic -c $(ALEMBIC_CONFIG) history

# Application commands
run:
	@echo "🚀 Starting application..."
	$(PYTHON) main.py

run-dev:
	@echo "🚀 Starting application in development mode..."
	$(UV) run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Testing and code quality
test:
	@echo "🧪 Running tests..."
	$(UV) run pytest

format:
	@echo "✨ Formatting code..."
	$(UV) run ruff format .

lint:
	@echo "🔍 Linting code..."
	$(UV) run ruff check .

type-check:
	@echo "🔎 Running type checks..."
	$(UV) run mypy .

create-admin:
	@if [ -z "$(EMAIL)" ] || [ -z "$(PASSWORD)" ]; then \
		echo "❌ Error: EMAIL and PASSWORD are required. Usage: make create-admin EMAIL=email@example.com PASSWORD=password"; \
		exit 1; \
	fi
	@echo "🧑🏻‍💻 Creating an admin user..."
	$(PYTHON) scripts/create_admin_user.py $(EMAIL) $(PASSWORD)

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	@echo "✅ Cleanup complete."
