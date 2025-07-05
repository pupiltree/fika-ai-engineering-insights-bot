VENV_DIR := .venv
ENTRY := slack_app.py

setup:
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. $(VENV_DIR)/bin/activate && python $(ENTRY)

clean:
	rm -rf logs/*
	rm -rf output/*

