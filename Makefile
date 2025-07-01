.PHONY: install seed run docker-up docker-down clean

# Install dependencies
install:
	pip install -r requirements.txt

# Seed database with fake data
seed:
	python data/seed_github_events.py

# Run the application
run: install seed
	python bot/slack_bot.py

# Run with Docker Compose
docker-up:
	docker-compose up --build

# Stop Docker containers
docker-down:
	docker-compose down

# Clean up
clean:
	rm -f fika_ai_insights.db
	docker-compose down --rmi all --volumes

# Test the analytics pipeline
test:
	python main.py

# Default target
all: run 