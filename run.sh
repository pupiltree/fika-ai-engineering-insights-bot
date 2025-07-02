#!/usr/bin/env bash
set -e

# Create venv if needed
if [ ! -d "venv" ]; then
  python3.13 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed database with fake data
python scripts/seed_fake_data.py

# Start agents & bot (in background)
python -m agents.harvester --since 2025-06-01 &
python -m agents.analyst &
python -m bot.main
