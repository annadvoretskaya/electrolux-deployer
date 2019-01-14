from fabric.context_managers import cd, prefix
from fabric.decorators import task
from fabric.operations import run, get

from utils import Config, cast_to_bool


@task
def deploy_static(config_dir):
    config_instance = Config(config_dir)

    with cd(config_instance.project_dir), prefix('workon %s' % config_instance.project_name):
        run('python manage.py collectstatic --noinput --settings ' + config_instance.settings_module)


@task
def compress(config_dir):
    config_instance = Config(config_dir)

    with cd(config_instance.project_dir), prefix('workon %s' % config_instance.project_name):
        run('python manage.py compress --settings ' + config_instance.settings_module)


@task
def migrate(config_dir):
    config_instance = Config(config_dir)

    with cd(config_instance.project_dir), prefix('workon %s' % config_instance.project_name):
        run('python manage.py migrate --settings ' + config_instance.settings_module)


@task
def make_admin(config_dir):
    config_instance = Config(config_dir)

    with cd(config_instance.project_dir), prefix('workon %s' % config_instance.project_name):
        run('python manage.py createsuperuser --settings ' + config_instance.settings_module)


@task
def dumpdata(config_dir, app_name='', filename=None, use_indent=False):
    config_instance = Config(config_dir)

    if not filename:
        if app_name:
            filename = '%s.json' % app_name
        else:
            filename = 'all.json'

    indent = '--indent=4' if cast_to_bool(use_indent) else ''

    with cd(config_instance.project_dir), prefix('workon %s' % config_instance.project_name):
        run('./manage.py dumpdata %s --natural-foreign %s > %s' % (app_name, indent, filename))

        get(filename, filename)
        run('rm %s' % filename)
