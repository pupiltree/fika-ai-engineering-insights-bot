# PowerBiz Developer Analytics - Makefile

.PHONY: install run test clean seed docker-build docker-run help

# Default target
help:
	@echo "PowerBiz Developer Analytics"
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make run         - Run the application locally"
	@echo "  make test        - Run tests"
	@echo "  make seed        - Populate database with demo data"
	@echo "  make clean       - Clean up generated files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run  - Run with Docker Compose"

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	python -m powerbiz

# Run tests
test:
	python -m pytest tests/ -v

# Seed database with demo data
seed:
	python seed_data/seed.py

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f powerbiz.db

# Docker commands
docker-build:
	docker build -t powerbiz .

docker-run:
	docker-compose up --build

# Development setup
dev-setup: install seed
	@echo "Development environment ready!"
	@echo "1. Copy .env.example to .env and configure your tokens"
	@echo "2. Run 'make run' to start the application"
