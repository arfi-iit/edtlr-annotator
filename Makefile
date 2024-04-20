# Variables
VENV           = .venv
VENV_BIN       = $(VENV)/bin
VENV_PYTHON    = $(VENV_BIN)/python
VENV_PIP       = $(VENV_BIN)/pip

SRC_DIR        = src
APP_NAME       = annotation
APP_DIR        = $(SRC_DIR)/$(APP_NAME)

STATIC_DIR     = $(APP_DIR)/static/annotation
DATA_DIR       = $(STATIC_DIR)/data
IMPORT_DIR     = $(DATA_DIR)

PORT           = 8000
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

# Create super user
# make superuser DJANGO_SUPERUSER_USERNAME=<username> DJANGO_SUPERUSER_PASSWORD=<password>
superuser: init
	$(VENV_PYTHON) $(SRC_DIR)/manage.py createsuperuser --no-input;

# Run the development server
start: init
	$(VENV_PYTHON) $(SRC_DIR)/manage.py runserver 0.0.0.0:$(PORT);

# Create or update the .po file containing the translation strings
messages: init
	if [ ! -d $(APP_DIR)/locale ]; then \
	    mkdir $(APP_DIR)/locale; \
	fi; \
	$(VENV_BIN)/django-admin makemessages --locale ro;

# Compile the translations
translations: messages
	$(VENV_BIN)/django-admin compilemessages;

# Make migrations
migrations: app
	$(VENV_PYTHON) $(SRC_DIR)/manage.py makemigrations;

# Apply migrations
schema: migrations
	$(VENV_PYTHON) $(SRC_DIR)/manage.py migrate;

# Collect static files
static-files: app
	$(VENV_PYTHON) $(SRC_DIR)/manage.py collectstatic;

import: init
	$(VENV_PYTHON) $(SRC_DIR)/manage.py importdata \
		--entries-directory $(IMPORT_DIR)/entries \
		--images-directory $(IMPORT_DIR)/images \
		--static-directory $(STATIC_DIR) \
		--mappings-file $(IMPORT_DIR)/mappings.csv;
