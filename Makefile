# start the stack
up:
	docker compose up

# stop the stack and remove containers
down:
	docker compose down

# build a new Docker image
build:
	docker build -t pycon .

# run Django migrations
migrate:
	docker compose run web python manage.py migrate

# create new Django migrations
makemigrations:
	docker compose run web python manage.py makemigrations

# connect to Django shell
shell:
	docker compose run web python manage.py shell

# linting & formatting
# TODO: fix linters in Docker
lint:
	docker compose run --rm web bash -c "isort . && black . & ruff"

# create a superuser to log in to Django admin & Wagtail
create-user:
	docker compose run web python manage.py createsuperuser

# default WagTail content used only on localhost
default-content:
	docker compose run web python content/default_content.py
