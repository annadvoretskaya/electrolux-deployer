from fabric.context_managers import cd, warn_only
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import sudo, run, get

from utils import Config


@task
def clone_project(config_dir):
    config_instance = Config(config_dir)

    with cd(config_instance.deploy_dir):
        if not exists(config_instance.project_name):
            sudo('git clone -b %s %s %s' % (config_instance.branch, config_instance.repository, config_instance.project_name))
            sudo('chown -R %s:%s %s' % (config_instance.user, config_instance.user, config_instance.project_name))

    with cd(config_instance.project_dir):
        run('mkdir -p static logs pid')


@task
def deploy_files(config_dir):
    config_instance = Config(config_dir)

    with cd(config_instance.deploy_dir):
        if not exists(config_instance.project_name):
            clone_project(config_dir)
            return

    with cd(config_instance.project_dir):
        run('git fetch origin')

        branch_exists = True
        with warn_only():
            result = run('git rev-parse --verify %s' % config_instance.branch)
            if result.failed:
                branch_exists = False

        if branch_exists:
            run('git checkout %s' % config_instance.branch)
        else:
            run('git checkout -b {0} origin/{0}'.format(config_instance.branch))
        run('git merge origin/%s' % config_instance.branch)


@task
def download(config_dir, *paths):
    config_instance = Config(config_dir)
    for path in paths:
        with cd(config_instance.project_dir):
            get(path)
