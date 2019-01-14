import os

from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import local, run

from utils import Config, get_variables_from, put_variables_to


@task
def edit_file(config_dir, target_file):
    config_instance = Config(config_dir)
    key_file = os.path.join(config_instance.project_config_dir, config_instance.key_filename)
    local('chmod 600 {key}'.format(key=key_file))
    local('ssh -t -i {key} {user}@{host} "nano {file}"'.format(
        key=key_file,
        user=config_instance.user,
        host=config_instance.host,
        file=target_file,
    ))


@task
def config_django_env(config_dir):
    config_instance = Config(config_dir)

    if exists(config_instance.remote_path(config_instance.env_file)):
        exists_variables = get_variables_from(config_instance.remote_path(config_instance.env_file))
    else:
        exists_variables = {'SECRET_KEY': config_instance.generate_secret_key()}

    run('cp --backup=numbered %s %s' % (config_instance.remote_path(config_instance.env_template), config_instance.remote_path(config_instance.env_file)))
    put_variables_to(config_instance.remote_path(config_instance.env_file), exists_variables)
    edit_file(config_dir, config_instance.remote_path(config_instance.env_file))

    config_instance.server_env_variables = get_variables_from(config_instance.remote_path(config_instance.env_file))
