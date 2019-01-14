from fabric.api import task, sudo, cd, run
from fabric.contrib.files import upload_template

from utils import Config


@task
def config_monit(config_dir):
    config_instance = Config(config_dir)

    monit_template_dir = config_instance.config_path('monit')

    remote_conf_path = config_instance.remote_path('conf')
    run('mkdir -p {}'.format(remote_conf_path))

    upload_template('monitrc', remote_conf_path, template_dir=monit_template_dir,
                    context=config_instance.context, use_sudo=True, use_jinja=True)
    sudo('chown root:root %s' % config_instance.remote_path('conf/', 'monitrc'))
    sudo('chmod 700 %s' % config_instance.remote_path('conf/', 'monitrc'))

    if config_instance.MONIT_SLACK_NOTIFICATIONS:
        upload_template('notify_and_execute.py', remote_conf_path, template_dir=monit_template_dir,
                        context=config_instance.context, use_sudo=True, use_jinja=True)
        with cd(remote_conf_path):
            sudo('chmod +x notify_and_execute.py')

    sudo('monit -c %s reload' % config_instance.remote_path('conf/', 'monitrc'))


@task
def start_monit(config_dir):
    config_instance = Config(config_dir)

    sudo('monit -c %s' % config_instance.remote_path('conf/', 'monitrc'))


@task
def kill_monit(config_dir):
    config_instance = Config(config_dir)

    sudo("kill `sudo cat /var/run/monit-%s.pid`" % config_instance.project_name)
