# Variables
VENV           = .venv
VENV_BIN       = $(VENV)/bin
VENV_PYTHON    = $(VENV_BIN)/python
VENV_PIP       = $(VENV_BIN)/pip

SRC_DIR        = src
APP_NAME       = annotation
APP_DIR        = $(SRC_DIR)/$(APP_NAME)

LOG_DIR        = logs

STATIC_DIR     = $(APP_DIR)/static/annotation
DATA_DIR       = $(STATIC_DIR)/data
IMPORT_DIR     = $(DATA_DIR)

STATIC_ROOT    = static

PORT           = 8000
# Recipes

# Initialize the development environment
init: requirements.txt
	if [ ! -d "$(VENV)" ]; then \
	    python3.11 -m venv $(VENV);\
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
superuser: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py createsuperuser --no-input;

# Run the development server
start: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py runserver 0.0.0.0:$(PORT);

# Create or update the .po file containing the translation strings
messages: $(SRC_DIR)/manage.py
	if [ ! -d $(APP_DIR)/locale ]; then \
	    mkdir $(APP_DIR)/locale; \
	fi; \
	$(VENV_BIN)/django-admin makemessages --locale ro;

# Compile the translations
translations: $(APP_DIR)/locale/ro/LC_MESSAGES/django.po
	$(VENV_BIN)/django-admin compilemessages;

# Make migrations
migrations: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py makemigrations;

# Apply migrations
schema: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py migrate;

# Collect static files
static-files: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py collectstatic --no-input;

# Import the data into the database
# make import STATIC_DIR=<path to static directory> IMPORT_DIR=<path to import directory> VOLUME="volume name"
# The IMPORT_DIR should be a subdirectory of STATIC_DIR
import: $(SRC_DIR)/manage.py
	test -n "$(VOLUME)"
	$(VENV_PYTHON) $(SRC_DIR)/manage.py importdata \
		--entries-directory $(IMPORT_DIR)/entries \
		--images-directory $(IMPORT_DIR)/images \
		--static-directory $(STATIC_DIR) \
		--mappings-file $(IMPORT_DIR)/mappings.csv \
		--page-offset $(PAGE_OFFSET) \
		--volume "$(VOLUME)";


# Expand the template files from the `templates` directory:
# - `.env.template` into the `.env` file containing application settings,
# - `edtlr-annotator.service.template` into `edtlr-annotator.service` file
#   containing the configuration of the systemd application service,
# - `edtlr-annotator.socket.template` into `edtlr-annotator.socket` file
#   which contains the configuration of the application socket,
# - `nginx-config.template` into `edtlr-annotator` file which contains the
#   NginX configuration for the application site.
# Example invocation:
# make template-expansion \
#     SECRET_KEY='<secret-key>' \
#     DATABASE_HOST='<database server>' \
#     DATABASE_NAME='<database name>' \
#     DATABASE_USER='<database user>' \
#     DATABASE_PASSWORD='<password>' \
#     DATABASE_PORT=<port> \
#     USER=<user> \
#     GROUP=<group> \
#     SERVER_NAME=<server name>
# The schema of the database URI is defined in
# https://pypi.org/project/python-environ/
DEBUG = False
MAX_CONCURRENT_ANNOTATORS = 2
NUM_WORKERS=4
GUNICORN_PATH = $(realpath $(VENV_BIN)/gunicorn)
PYTHON_PATH=$(realpath $(SRC_DIR))
APP_ROOT=$(realpath $(SRC_DIR)/..)
template-expansion: $(SRC_DIR)/manage.py
	$(VENV_PIP) install -I gunicorn;

	cp templates/.env.template templates/.env;
	sed -i "s/__DEBUG__/$(DEBUG)/g" templates/.env;
	sed -i "s/__SECRET_KEY__/$(SECRET_KEY)/g" templates/.env;
	sed -i "s/__STATIC_ROOT__/$(STATIC_ROOT)/g" templates/.env;
	sed -i "s/__MAX_CONCURRENT_ANNOTATORS__/$(MAX_CONCURRENT_ANNOTATORS)/g" templates/.env;
	sed -i "s/__DATABASE_HOST__/$(DATABASE_HOST)/g" templates/.env;
	sed -i "s/__DATABASE_NAME__/$(DATABASE_NAME)/g" templates/.env;
	sed -i "s/__DATABASE_USER__/$(DATABASE_USER)/g" templates/.env;
	sed -i "s/__DATABASE_PASSWORD__/$(DATABASE_PASSWORD)/g" templates/.env;
	sed -i "s/__DATABASE_PORT__/$(DATABASE_PORT)/g" templates/.env;

	cp templates/gunicorn.conf.py.template templates/gunicorn.conf.py;
	sed -i "s~__GUNICORN_PATH__~$(GUNICORN_PATH)~g" templates/gunicorn.conf.py;
	sed -i "s~__SRC_DIR_PATH__~$(PYTHON_PATH)~g" templates/gunicorn.conf.py;
	sed -i "s/__NUM_WORKERS__/$(NUM_WORKERS)/g" templates/gunicorn.conf.py;

	cp templates/edtlr-annotator.service.template templates/edtlr-annotator.service;
	sed -i "s~__GUNICORN_PATH__~$(GUNICORN_PATH)~g" templates/edtlr-annotator.service;
	sed -i "s~__SRC_DIR_PATH__~$(PYTHON_PATH)~g" templates/edtlr-annotator.service;
	sed -i "s/__USER__/$(USER)/g" templates/edtlr-annotator.service;
	sed -i "s/__GROUP__/$(GROUP)/g" templates/edtlr-annotator.service;

	cp templates/edtlr-annotator.socket.template templates/edtlr-annotator.socket;

	cp templates/nginx-config.template templates/edtlr-annotator;
	sed -i "s/__SERVER_NAME__/$(SERVER_NAME)/g" templates/edtlr-annotator;
	sed -i "s/__STATIC_ROOT__/$(STATIC_ROOT)/g" templates/edtlr-annotator;
	sed -i "s~__APP_ROOT__~$(APP_ROOT)~g" templates/edtlr-annotator;

.PHONY: update
update:
	$(VENV_PIP) install -r requirements.txt;
	make static-files;
	make translations;
	make schema;
	mkdir -p $(LOG_DIR);
	sudo systemctl restart edtlr-annotator.service;
	sudo systemctl restart edtlr-annotator.socket;
	sudo systemctl restart nginx;

# Update the values of metadata columns from the database
fresh-metadata: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py updatemetadata;

# Replaces diacritics with cedilla to diacritics with comma below.
correct-diacritics: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py correctdiacritics;

# Import references from the file specified by REFERENCES_FILE variable
REFERENCES_FILE=references.txt
references: $(REFERENCES_FILE)
	$(VENV_PYTHON) $(SRC_DIR)/manage.py importreferences \
		--input-file $(REFERENCES_FILE);
