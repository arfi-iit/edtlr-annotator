# Variables
VENV           = .venv
VENV_PYTHON    = $(VENV)/bin/python
VENV_PIP       = $(VENV)/bin/pip


# Recipes

# Initialize the development environment
init: requirements.txt
	if [ ! -d "$(VENV)" ]; then \
	    python -m venv $(VENV);\
	fi; \
	$(VENV_PIP) install -U pip;
	if [ -f requirements-dev.txt ]; then \
	    $(VENV_PIP) install -r requirements-dev.txt;\
	fi;\
	$(VENV_PIP) install -r requirements.txt;

