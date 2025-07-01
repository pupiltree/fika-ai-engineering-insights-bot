FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database and seed data
RUN python data/seed_github_events.py

# Expose port (optional, mainly for documentation)
EXPOSE 3000

# Default command
CMD ["python", "bot/slack_bot.py"] 