import os

from fabric.context_managers import cd, warn_only
from fabric.contrib.files import exists, contains, append
from fabric.decorators import task
from fabric.operations import sudo, run

from utils import Config


@task
def clean_pyc(config_dir):
    """Removes .pyc file"""
    config_instance = Config(config_dir)

    with cd(config_instance.project_dir):
        sudo("find . -name '*.pyc'")
        sudo('find . -name \*.pyc -delete')


@task
def prepare_virtualenv(config_dir):
    config_instance = Config(config_dir)

    sudo('pip3 install virtualenv')
    sudo('pip3 install virtualenvwrapper')
    # Additional steps to install virtualenvwrapper

    user_home = os.path.join('/', 'home', config_instance.user)

    user_profile_file = os.path.join(user_home, '.profile')
    if not exists(user_profile_file):
        run('touch %s' % user_profile_file)

    python_path = "VIRTUALENVWRAPPER_PYTHON='/usr/bin/python3'"
    virtualenv_source = 'source /usr/local/bin/virtualenvwrapper.sh'
    workon_home_export = 'export WORKON_HOME=\'{}\''.format(config_instance.workon_home)

    if not contains(user_profile_file, python_path):
        append(user_profile_file, '\n' + python_path)
    if not contains(user_profile_file, virtualenv_source):
        append(user_profile_file, '\n' + virtualenv_source)
    if not contains(user_profile_file, 'export WORKON_HOME='):
        append(user_profile_file, '\n' + workon_home_export)

    run('source %s' % user_profile_file)

    # Creating new virtualenv if it doesn't exist
    with warn_only():
        res = run('workon')

    if config_instance.project_name not in res:
        run('mkvirtualenv %s' % config_instance.project_name)
    else:
        print('Virtual environment exists!')

    postactivate = os.path.join('$WORKON_HOME', config_instance.project_name, 'bin', 'postactivate')
    settings_module_config = 'export DJANGO_SETTINGS_MODULE="%s"' % config_instance.settings_module

    with warn_only():
        res = run('grep \'%s\' "%s"' % (settings_module_config, postactivate))

    if res.failed:
        run('echo \'%s\' >> "%s"' % (settings_module_config, postactivate))
