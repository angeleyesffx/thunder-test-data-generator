.PHONY: install test debug run

PYTHON := .venv/bin/python3
PIP    := .venv/bin/pip3

install:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest tests/ -v --cov=. --cov-report=term-missing

debug:
	$(PYTHON) main.py -CONFIG_YAML config -ENV sit

run:
	$(PYTHON) main.py -CONFIG_YAML config -ENV sit -e
