import os

from fabric.context_managers import cd, prefix
from fabric.contrib.files import upload_template, sudo
from fabric.decorators import task
from fabric.operations import run

from utils import Config


@task
def config_celery(config_dir):
    config_instance = Config(config_dir)

    celery_configs = config_instance.config_path('celery', 'systemd')
    remote_conf_path = '/etc/systemd/system/'

    upload_template('celeryd', os.path.join(remote_conf_path, '{}.service'.format(config_instance.celeryd_name)),
                    template_dir=celery_configs, context=config_instance.context, use_sudo=True, use_jinja=True)
    sudo('systemctl reenable {}.service'.format(config_instance.celeryd_name))

    upload_template('celerybeat', os.path.join(remote_conf_path, '{}.service'.format(config_instance.celerybeat_name)),
                    template_dir=celery_configs, context=config_instance.context, use_sudo=True, use_jinja=True)
    sudo('systemctl reenable {}.service'.format(config_instance.celerybeat_name))


@task
def install_rabbitmq(config_dir):
    config_instance = Config(config_dir)

    sudo('echo "deb http://www.rabbitmq.com/debian/ testing main" |'
         ' tee  /etc/apt/sources.list.d/rabbitmq.list > /dev/null')
    with cd('/tmp'):
        run('wget -O rabbitmq-release-signing-key.asc'
            ' http://www.rabbitmq.com/rabbitmq-release-signing-key.asc')
        sudo('apt-key add rabbitmq-release-signing-key.asc')
    sudo('apt-get update')
    sudo('apt-get -y install rabbitmq-server')
    sudo('service rabbitmq-server start')

    systemd_override_dir = '/etc/systemd/system/rabbitmq-server.service.d'
    sudo('mkdir -p {}'.format(systemd_override_dir))
    systemd_override = os.path.join(systemd_override_dir, 'override.conf')
    upload_template('override', systemd_override, template_dir=config_instance.config_path('rabbitmq'),
                    context=config_instance.context, use_sudo=True, use_jinja=True)
    sudo('systemctl daemon-reload')


@task
def kill_celery(config_dir):
    config_instance = Config(config_dir)

    run("ps auxww | grep -F 'celery worker' | grep -F 'app={}.taskapp' | grep -v -F 'grep' "
        "| awk '{{print $2}}' | xargs sudo kill -9".format(config_instance.project_name))


@task
def purge_celery(config_dir):
    config_instance = Config(config_dir)

    with cd(config_instance.project_dir), prefix('workon %s' % config_instance.project_name):
            run('celery --app={}.taskapp purge'.format(config_instance.project_name))
