ARG PYTHON_VERSION=3.11-slim-buster

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MULTIRUN_VERSION=1.1.3

# Workdir is created automatically when necessary.
WORKDIR /code

RUN set -ex; \
    # Install nginx from Debian repository.
    apt-get update; \
    apt-get install -y --no-install-recommends \
        make \
        nginx \
        wget \
    ; \
    rm -rf /var/lib/apt/lists/*; \
    # Download multirun - great for running both nginx and gunicorn in a single container, because it correctly forwards
    # all signals sent to the container to individual processes.
    wget -c https://github.com/nicolas-van/multirun/releases/download/${MULTIRUN_VERSION}/multirun-$(arch)-linux-gnu-${MULTIRUN_VERSION}.tar.gz -O - | tar -xz; \
    mv multirun /bin/multirun;

# Use of --mount=type=bind reduces number of layers in the Docker image, while maintaining ability to cache the
# layer with dependencies depending on the contents of requirements.txt file.
RUN --mount=type=bind,source=./requirements.txt,target=/tmp/requirements.txt \
    --mount=type=bind,source=./docker/nginx/,target=/tmp/nginx-conf/ \
    set -ex && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    # Overwrite the configuration of default site in nginx
    cp /tmp/nginx-conf/cz.pycon.org.conf /etc/nginx/sites-available/default && \
    # Configure logging for nginx
    sed -i 's|access_log /var/log/nginx/access.log;|access_log /dev/stdout combined;|g' /etc/nginx/nginx.conf && \
    sed -i 's|error_log /var/log/nginx/error.log;|error_log /dev/stdout info;|g' /etc/nginx/nginx.conf && \
    echo "error_log /dev/stdout info;" >> /etc/nginx/nginx.conf && \
    # Prepare configuration required for dynamic configuration based on env. parameters
    mkdir -p /etc/nginx/pycon-config-enabled/ && \
    mkdir -p /etc/nginx/pycon-config-available/ && \
    cp /tmp/nginx-conf/*.inc.conf /etc/nginx/pycon-config-available/ && \
    # Validate nginx configuration
    nginx -t

COPY . /code

# Prepare the application
RUN set -ex; \
    # Use fake values for required environment variables - manage.py would fail to start without these variables. \
    export SECRET_KEY=notasecret; \
    # Collect static files
    python manage.py collectstatic --noinput; \
    # Make nginx start script executable
    chmod a+x /code/docker/nginx/start-nginx.sh;

EXPOSE 8000

ARG SENTRY_RELEASE=dev
ENV SENTRY_RELEASE=${SENTRY_RELEASE}

CMD ["multirun", "gunicorn --bind unix:/code/gunicorn.sock --workers 2 wsgi", "/code/docker/nginx/start-nginx.sh"]
