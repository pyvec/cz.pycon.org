# Container for generating images for social media.
# Installs the playwright library and uses it to install required browsers.
#
# This container should be run locally with project code mounted under `/code/`.
# See `docker-compose.yaml` to get the idea how it is run.
#
# Do not try to run it in production!

ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir is created automatically when necessary.
WORKDIR /code

RUN --mount=type=bind,source=./requirements.txt,target=/tmp/requirements.txt \
    --mount=type=bind,source=./requirements-og-generator.txt,target=/tmp/requirements-og-generator.txt \
    set -ex && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements-og-generator.txt;

RUN set -ex && \
    playwright install --with-deps chromium
