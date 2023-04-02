from fabric.api import task, cd, env, run

PROJECT_ROOT = '/srv/app/'
DOCKER_IMAGE_NAME = 'pycon'

env.hosts = []

@task
def beta():
    env.hosts = ['app@node-13.rosti.cz:13128']
    env.environment = 'beta'
    env.branch = 'main'


def restart():
    run('supervisorctl restart app')


@task
def deploy():
    with cd(PROJECT_ROOT):
        run('git pull origin %s' % env.branch)

    # Build the Docker image
    run('docker build -t %s .' % DOCKER_IMAGE_NAME)

    # Start the container
    run('docker run -d -p 8000:8000 --name %s %s' % (DOCKER_IMAGE_NAME, DOCKER_IMAGE_NAME))

    # Restart the supervisor service
    restart()
