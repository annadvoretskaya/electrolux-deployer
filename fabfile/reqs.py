from fabric.context_managers import cd, prefix
from fabric.decorators import task
from fabric.operations import run, get, sudo
from six import BytesIO

from utils import Config


@task
def upgrade_pip(config_dir):
    config_instance = Config(config_dir)

    with prefix('workon %s' % config_instance.project_name):
        run('pip install -U pip')


@task
def install_req(config_dir):
    """install requirements in virtualenv"""
    config_instance = Config(config_dir)

    with cd(config_instance.project_dir), prefix('workon %s' % config_instance.project_name):
        run('pip install -r requirements.txt')


@task
def install_dependencies(config_dir):
    config_instance = Config(config_dir)

    file_buffer = BytesIO()

    get(config_instance.remote_path('dependencies.txt'), file_buffer)
    packages = file_buffer.getvalue().decode('utf-8').split('\n')
    install_packages(config_dir, packages)


@task
def install_packages(config_dir, packages):
    Config(config_dir)
    if isinstance(packages, (list, tuple)):
        packages = ' '.join(packages)

    sudo('apt-get update')
    sudo('apt-get -y --no-upgrade install %s' % packages)


