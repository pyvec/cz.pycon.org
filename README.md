# PyCon CZ webpage

## How to run on localhost

### Prerequisites
For local development you need Docker and make.
Tested with Docker version 23.0.2.

For Docker installation manuals check the following links:
* Ubuntu - install Docker engine using the [apt repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and add user to `docker` group as described [here](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) so you can run Docker locally as a non-root user
* Windows & Mac - you can use Docker Desktop, check out [this](https://docs.docker.com/desktop/install/windows-install/) manual for Windows and [this](https://docs.docker.com/desktop/install/mac-install/) for Mac 

### Local setup
1. Build an image
```bash
make build
```
2. Run migrations 
```bash
make migrate
```

3. Run dev stack
```bash
make up
```

4. You can stop the server by pressing Ctrl+C, optionally you can run 
```bash
make down
```
if there are any hanging containers

### Front end tooling
This is optional just in the case you need to work with CSS.

#### Instalation

1. Install latest [node.js](https://nodejs.org/)

2. Install all packages from `package.json` locally
```shell
npm ci
```

#### Usage
To develop with automatic compilation and browser refreshing run
```shell
npm start
```
And see the result on `http://localhost:3366/`

To build everything once for production
```shell
npm run build
```
_note: `removeUnusedCss` will throw “Error: Could not load script:…” but it doesn’t make stop it from working. Just ignore it.

### Admin & Wagtail
In case you want to access admin page, either Django or Wagtail one, you need to create a superuser and log in with its credentials:
```bash
make create-user
```

The development server runs at the address http://0.0.0.0:8000/. Beta instance on fly.io runs on https://pycon-cz-beta.fly.dev/team/.

### Configuration

The application can be configured using the following environment variables. Reasonable defaults for local development
are already set in the provided `docker-compose.yaml`.

| Variable              | Description                                                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| `DATABASE_URL`        | *Required.* URL defining database connection parameter. See https://github.com/jazzband/dj-database-url#url-schema for syntax.                       |
| `SECRET_KEY`          | *Required.* Secret key for Django, will be used to sign cookies for the admin.                                                                       |
| `DEBUG`               | Set to `1` or `true` to enable Django debug mode. Debug mode is disabled by default.                                                                 |
| `EXTRA_ALLOWED_HOSTS` | Comma separated list of hosts to allow in addition to the production ones. Can be used for debugging production configuration locally.               |
| `DEFAULT_LOG_LEVEL`   | Log level for the root logger. Can be `DEBUG`, `INFO`, `WARNING` (default), `ERROR`, or `CRITICAL`.                                                  |
| `SENTRY_DSN`          | DSN of the project in Sentry. When not set, Sentry will be disabled.                                                                                 |
| `SENTRY_RELEASE`      | Current release for Sentry reporting. Will be set to a short commit hash during deployment and baked to the Docker container.                        |
| `SENTRY_ENVIRONMENT`  | Identifier of the environment for Sentry reporting. Set in `fly.toml` and `fly.prod.toml` for beta and production.                                   |
| `HTTP_AUTH`           | When set, `nginx` will enable HTTP Basic Auth and use contents of this variable as its htpasswd file. No effect when running with Django dev server. |
| `PRETALX_TOKEN`       | Token for authentication to the pretalx API.                                                                                                         |
| `PRETALX_EVENT_SLUG`  | Slug of the pretalx event with speakers and submissions. Defaults to `pycon-cz-23`.                                                                  |

## Deployment
We’re using [fly.io](https://fly.io). Deployment is automatic to [cz.pycon.org](https://cz.pycon.org) from `main` branch and to [beta (staging)](https://pycon-cz-beta.fly.dev) from `beta` branch.

For more control [install flyctl](https://fly.io/docs/hands-on/install-flyctl/).

## Database and media synchronization

The following commands can be used to copy database and media files between environments:

* `copy-db-prod-to-local`: Copy database from production to local container. Starts the container with the database when necessary.
* `copy-media-prod-to-local`: Copy media files from production to `./data/mediafiles`.
* `copy-db-prod-to-beta`: Copy database from production to beta, overwriting ALL data on beta. Operation is performed remotely.
* `copy-media-prod-to-beta`: Copy media files from production to beta. The media files are copied to local folder and then uploaded to beta.

All command requires access to fly.io and `flyctl` must be installed. Before running these commands, [install flyctl](https://fly.io/docs/hands-on/install-flyctl/)
and authenticate using the following command:

```bash
fly auth login
```

If you use WSL, you need to perform additional step - see [official login instructions](https://fly.io/docs/hands-on/sign-in/).

## Pretalx synchronization

The database of speakers, talks and workshops can be created and updated from pretalx event. To use the integration,
set the `PRETALX_TOKEN` environment variable for the container.

For development, this can be done by creating an `.env` file in the project root and adding the variable:

```shell
PRETALX_TOKEN="<YOUR TOKEN HERE>"
```

The variable from this file will be automatically used by `docker compose`.

You can perform initial synchronization by running:

```bash
make pretalx-sync-submissions
```

## Contributing
If you want to contribute, please run `make lint` before pushing BE code to format it. This step will be automated in the future.

## Monitoring
We use [Sentry](https://sentry.monitora.cz/) to monitor both beta and production.

## Debugging
<details>
  <summary>How to restart machine in fly.io if something gets stuck</summary>

```
fly machines list --app pycon-cz-beta-db
fly machines restart machine-id --app pycon-cz-beta-db
```
</details>
