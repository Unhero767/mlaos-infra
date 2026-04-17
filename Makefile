.PHONY: help build up down logs test lint clean docker-build docker-push

help:
	@echo "MLAOS ML Infrastructure - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make up              - Start dev environment (api + postgres)"
	@echo "  make down            - Stop all containers"
	@echo "  make logs            - View API logs"
	@echo "  make test            - Run test suite"
	@echo "  make shell           - Open shell in API container"
	@echo ""
	@echo "Audits & Analysis:"
	@echo "  make pruning         - Run feature pruning analysis"
	@echo "  make skew            - Run skew analysis"
	@echo ""
	@echo "Production:"
	@echo "  make prod-up         - Start production stack"
	@echo "  make prod-down       - Stop production stack"
	@echo "  make prod-logs       - View production logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-shell        - Connect to PostgreSQL"
	@echo "  make db-reset        - Reset database (dev only)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-push     - Push image to registry"
	@echo ""
	@echo "Utilities:"
	@echo "  make lint            - Run code linting"
	@echo "  make clean           - Remove generated files"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	docker compose --profile test up test

shell:
	docker compose exec api bash

pruning:
	docker compose --profile audits up pruning

skew:
	docker compose --profile audits up skew-analysis

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f api

db-shell:
	docker compose exec postgres psql -U mlaos -d mlaos_db

db-reset:
	docker compose down -v
	docker compose up -d postgres
	sleep 5
	docker compose exec postgres psql -U mlaos -d mlaos_db < sql/001_feature_registry.sql
	docker compose exec postgres psql -U mlaos -d mlaos_db < sql/002_serving_logs.sql

docker-build:
	docker build -t mlaos-api:latest .

docker-push:
	docker push mlaos-api:latest

lint:
	docker compose exec api python -m pytest --cov=src --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov .pytest_cache
	docker compose down -v
