ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir is created automatically when necessary.
WORKDIR /code

# Use of --mount=type=bind reduces number of layers in the Docker image, while maintaining ability to cache the
# layer with dependencies depending on the contents of requirements.txt file.
RUN --mount=type=bind,source=./requirements.txt,target=/tmp/requirements.txt \
    set -ex && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt
COPY . /code

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "wsgi"]
