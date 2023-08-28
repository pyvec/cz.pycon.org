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
	docker compose build

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

# Run tests
test:
	$(DC_RUN) web pytest -s

# Compile dependencies using `pip-tools`
# Takes requiremenents.in file and outputs new requirements.txt with specific
# versions of all dependencies, including dependencies of dependencies.
# `pip-sync` step is not needed because of `make build`
dependencies/compile:
	pip-compile

ci/build:
	docker build . -t ${TAG}


ci/lint:
	isort . && black . && ruff . --fix

ci/test:
	pytest

# linting & formatting
lint:
	$(DC_RUN) web bash -c "isort . && black . && ruff . --fix"

# create a superuser to log in to Django admin & Wagtail
create-user:
	$(DC_RUN) web python manage.py createsuperuser

# default WagTail content used only on localhost
default-content:
	$(DC_RUN) web python content/default_content.py

# Sync from pretalx
.PHONY: pretalx-sync-submissions
pretalx-sync-submissions:
	$(DC_RUN) web python manage.py pretalx_sync_submissions

# Sync from pretalx to production
.PHONY: pretalx-sync-submissions-prod
pretalx-sync-submissions-prod:
	flyctl ssh console -a pycon-cz-prod -q -C "bash -c 'python manage.py pretalx_sync_submissions'"

.PHONY: generate-og-images
generate-og-images:
	$(DC_RUN) og_generator


.PHONY: link-og-images
link-og-images:
	$(DC_RUN) web python manage.py program_link_og_images

# Data sync
.PHONY: copy-db-prod-to-local
# Copy database from production to local database (starts the database when necessary).
copy-db-prod-to-local:
	docker compose up db --detach --wait

	# Run pg_dump on remote database and download the file (local file must be removed, flyctl would fail otherwise).
	flyctl ssh console -a pycon-cz-db -q -u postgres -C "pg_dump -p 5433 --format=custom pycon_cz_prod --file=/data/tmp-prod-local-dump.backup"
	rm -f ./tmp-prod-local-dump.backup
	flyctl ssh sftp get -a pycon-cz-db /data/tmp-prod-local-dump.backup
	flyctl ssh console -a pycon-cz-db -q -u postgres -C "rm /data/tmp-prod-local-dump.backup"

	# Run pg_restore in a local container
	cat ./tmp-prod-local-dump.backup | docker compose exec --user postgres --no-TTY db pg_restore --clean --dbname=pycon --no-owner

	# Cleanup local files
	rm ./tmp-prod-local-dump.backup

.PHONY: copy-media-prod-to-local
# Copy media files from production to local folder.
copy-media-prod-to-local:
	# Ensure local media dir exists
	mkdir -p data/mediafiles

	# Create a TAR archive with mediafiles on remote and download it. Delete it after the download.
	flyctl ssh console -a pycon-cz-prod -q -C "tar -c -f /code/data/tmp-mediafiles.tar -C /code/data/ mediafiles"
	rm -f tmp-mediafiles.tar
	flyctl ssh sftp get -a pycon-cz-prod /code/data/tmp-mediafiles.tar
	flyctl ssh console -a pycon-cz-prod -q -C "rm /code/data/tmp-mediafiles.tar"

	# Extract the tar locally and delete it afterwards. Please note that this does not delete any files, only adds new ones.
	tar -x -f tmp-mediafiles.tar -C data/
	rm tmp-mediafiles.tar

.PHONY: copy-db-prod-to-beta
# Copy database from production to beta. This overwrites ALL data in the beta database!
copy-db-prod-to-beta:
	# Run pg_dump on remote database and re-import it to beta database, then delete the file.
	flyctl ssh console -a pycon-cz-db -q -u postgres -C "bash -c 'pg_dump -p 5433 --format=custom pycon_cz_prod --file=/data/tmp-prod-beta-dump.backup && pg_restore -p 5433 --clean --dbname=pycon_cz_beta --no-owner --role=pycon_cz_beta /data/tmp-prod-beta-dump.backup; rm /data/tmp-prod-beta-dump.backup'"

.PHONY: copy-media-prod-to-beta
# Copy media files from production to beta.
# Unfortunately, this operation must copy the the files to local machine first, because there is no SSH between machines in fly.io.
copy-media-prod-to-beta:
	# Create a TAR archive with mediafiles on production and download it. Delete it after the download.
	flyctl ssh console -a pycon-cz-prod -q -C "tar -c -f /code/data/tmp-mediafiles.tar -C /code/data/ mediafiles"
	rm -f tmp-mediafiles.tar
	flyctl ssh sftp get -a pycon-cz-prod /code/data/tmp-mediafiles.tar
	flyctl ssh console -a pycon-cz-prod -q -C "rm /code/data/tmp-mediafiles.tar"

	# Upload the TAR archive to beta and extract it.
	echo "cd /code/data \n put tmp-mediafiles.tar" | flyctl ssh sftp shell -a pycon-cz-beta
	rm tmp-mediafiles.tar
	flyctl ssh console -a pycon-cz-beta -q -C "bash -c 'tar -x -f /code/data/tmp-mediafiles.tar -C /code/data; rm /code/data/tmp-mediafiles.tar'"

.PHONY: upload-og-images
upload-og-images:
	# Create TAR archive with OG images locally and upload it to production.
	tar -c -f tmp-og-images.tar -C data/ mediafiles/og-images
	echo "cd /code/data \n put tmp-og-images.tar" | flyctl ssh sftp shell -a pycon-cz-prod
	rm tmp-og-images.tar

	# Extract the TAR file with OG images.
	flyctl ssh console -a pycon-cz-prod -q -C "bash -c 'tar -x -f /code/data/tmp-og-images.tar -C /code/data; rm /code/data/tmp-og-images.tar'"

.PHONY: publish-og-images
# Uploads OG images to production and links it to sessions in the database.
publish-og-images: upload-og-images
	flyctl ssh console -a pycon-cz-prod -q -C "bash -c 'python manage.py program_link_og_images'"
