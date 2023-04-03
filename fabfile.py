from fabric.api import task, cd, env, run

PROJECT_ROOT = '/srv/app/'
DOCKER_IMAGE_NAME = 'pycon'

def _deploy(c, branch='main'):
    with c.cd(PROJECT_ROOT):
        c.run("ssh-agent bash -c 'ssh-add ~/.ssh/github_pyconcz && git fetch'")
        c.run(f'git reset --hard origin/{branch}')
        c.run(f'docker build -t {DOCKER_IMAGE_NAME} .')
        c.run(f'docker run -d -p 8000:8000 --name {DOCKER_IMAGE_NAME} {DOCKER_IMAGE_NAME}')
        c.run('supervisorctl restart app')

@task(hosts=['app@node-13.rosti.cz:13128'])
def beta(c, branch='main'):
    _deploy(c, branch=branch)


@task(hosts=['app@node-12.rosti.cz:12768'])
def deploy(c, branch='main'):
    _deploy(c, branch=branch)
