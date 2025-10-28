.PHONY: help build up down logs test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker compose build

up: ## Start all services
	docker compose up

up-scale: ## Start all services with 3 workers
	docker compose up --scale worker=3

up-d: ## Start all services in detached mode
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Show logs from all services
	docker compose logs -f

logs-api: ## Show logs from API service
	docker compose logs -f api

logs-worker: ## Show logs from worker service
	docker compose logs -f worker

logs-redis: ## Show logs from Redis service
	docker compose logs -f redis

test-unit: ## Run unit tests only
	cd backend && pytest app/tests/test_prime.py -v

clean: ## Clean up containers, volumes, and images
	docker compose down -v
	docker system prune -f

restart: ## Restart all services
	docker compose restart

restart-worker: ## Restart worker service
	docker compose restart worker

ps: ## Show running containers
	docker compose ps


