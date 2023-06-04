# get the current user ID and group ID
UID := $(shell id -u)
GID := $(shell id -g)

# pass the user ID and group ID as env vars
# so not to run commands as root
DC_RUN := UID=$(UID) GID=$(GID) docker compose run --rm

# start the stack
up:
	docker compose up

# stop the stack and remove containers
down:
	docker compose down

# build a new Docker image
build:
	docker build -t pycon .

# run bash inside Docker
bash:
	$(DC_RUN) web bash

# run manage.py, usage: make manage "[commands and parameters here]"
manage:
	$(DC_RUN) web python manage.py $(filter-out $@,$(MAKECMDGOALS))

# run Django migrations
migrate:
	$(DC_RUN) web python manage.py migrate

# create new Django migrations
makemigrations:
	$(DC_RUN) web python manage.py makemigrations

# connect to Django shell
shell:
	$(DC_RUN) web python manage.py shell

# linting & formatting
lint:
	$(DC_RUN) web bash -c "isort . && black . && ruff . --fix"

# create a superuser to log in to Django admin & Wagtail
create-user:
	$(DC_RUN) web python manage.py createsuperuser

# default WagTail content used only on localhost
default-content:
	$(DC_RUN) web python content/default_content.py
