# Variables
VENV           = .venv
VENV_BIN       = $(VENV)/bin
VENV_PYTHON    = $(VENV_BIN)/python
VENV_PIP       = $(VENV_BIN)/pip

SRC_DIR        = src
APP_NAME       = annotation
APP_DIR        = $(SRC_DIR)/$(APP_NAME)

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

# Create the Django app
app: init
	if [ ! -d $(SRC_DIR) ]; then \
	    $(VENV_BIN)/django-admin startproject config; \
	    mv config $(SRC_DIR); \
	fi; \
	if [ ! -d $(APP_DIR) ]; then \
	    cd $(SRC_DIR); \
	    ../$(VENV_PYTHON) manage.py startapp $(APP_NAME); \
	fi;

# Run the development server
start: init
	$(VENV_PYTHON) $(SRC_DIR)/manage.py runserver
