import os

from fabric.context_managers import warn_only
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import sudo, local, run

from fabfile.db import create_database
from fabfile.celery import install_rabbitmq, config_celery
from fabfile.django import compress
from fabfile.django import deploy_static, migrate
from fabfile.env import config_django_env
from fabfile.files import deploy_files
from fabfile.newrelic import config_newrelic_monitor
from fabfile.python import prepare_virtualenv, clean_pyc
from fabfile.reqs import upgrade_pip, install_packages, install_dependencies, install_req
from fabfile.server import config_gunicorn, config_letsencrypt, config_target, prepare_journal
from fabfile.server import config_nginx
from fabfile.monit import config_monit
from utils import Config, cast_to_bool


@task
def shell(config_dir):
    config_instance = Config(config_dir)

    key_file = os.path.join(config_instance.project_config_dir, config_instance.key_filename)
    local('ssh -C -i {key} {user}@{host}'.format(
        key=key_file,
        user=config_instance.user,
        host=config_instance.host,
    ))


@task
def start_project(config_dir):
    prepare(config_dir)
    deploy(config_dir, with_restart=False, edit_env_variables=True)
    config(config_dir, with_restart=False)
    restart(config_dir)


@task
def prepare(config_dir):
    config_instance = Config(config_dir)

    prepare_journal(config_dir)

    install_packages(config_dir, config_instance.packages)
    prepare_virtualenv(config_dir)
    install_rabbitmq(config_dir)

    # Removing default site for nginx
    with warn_only():
        sudo('rm /etc/nginx/sites-enabled/default')


@task
def config(config_dir, with_restart=True):
    config_instance = Config(config_dir)

    config_target(config_dir)
    config_gunicorn(config_dir)
    config_nginx(config_dir)
    if getattr(config_instance, 'USE_HTTPS', '').lower() in ['true', 'on']:
        config_letsencrypt(config_dir)

    if getattr(config_instance, 'USE_MONIT', '').lower() in ['true', 'on']:
        config_monit(config_dir)

    config_celery(config_dir)
    if getattr(config_instance, 'NEWRELIC_DJANGO_ACTIVE', '').lower() in ['true', 'on']:
        config_newrelic_monitor(config_dir)

    sudo('systemctl daemon-reload')
    if with_restart:
        restart(config_dir)


@task
def restart(config_dir):
    config_instance = Config(config_dir)

    sudo('systemctl restart nginx.service')
    sudo('systemctl restart {}.target'.format(config_instance.project_name))


@task
def deploy(config_dir, with_restart=True, edit_env_variables=False):
    config_instance = Config(config_dir)

    deploy_files(config_dir)

    if cast_to_bool(edit_env_variables):
        config_django_env(config_dir)

    install_dependencies(config_dir)
    create_database(config_dir)
    clean_pyc(config_dir)
    upgrade_pip(config_dir)
    install_req(config_dir)
    deploy_static(config_dir)

    if config_instance.USE_COMPRESSOR.lower() in ['true', 'on']:
        compress(config_dir)

    migrate(config_dir)

    if cast_to_bool(with_restart):
        restart(config_dir)
