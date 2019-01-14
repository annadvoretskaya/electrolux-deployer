from fabric.contrib.files import exists, upload_template
from fabric.decorators import task
from fabric.operations import sudo

from utils import Config


@task
def setup_newrelic_server_monitor(config_dir):
    config_instance = Config(config_dir)

    apt_sources_file = '/etc/apt/sources.list.d/newrelic.list'
    apt_repository = 'deb http://apt.newrelic.com/debian/ newrelic non-free'
    newrelic_gpg_key = 'https://download.newrelic.com/548C16BF.gpg'

    server_monitor_package = 'newrelic-sysmond'

    if exists(apt_sources_file):
        # Check if repository already in file. Otherwise, add to the end.
        sudo("grep -q '{0}' {1} || sudo echo '{0}' >> {1}".format(apt_repository, apt_sources_file))
    else:
        sudo("echo '{0}' >> {1}".format(apt_repository, apt_sources_file))

    # Trust the New Relic GPG key
    sudo("wget -O- {0} | apt-key add -".format(newrelic_gpg_key))

    # Install the Server Monitor package
    sudo('apt-get update', warn_only=True, quiet=True)
    sudo('apt-get -y --no-upgrade install {}'.format(server_monitor_package))

    # Add license key to config file
    newrelic_sysmon_config_path = '/etc/newrelic/nrsysmond.cfg'
    if not exists(newrelic_sysmon_config_path, use_sudo=True):
        # Upload config file with New Relic account license key (set in settings.base)
        upload_template('newrelic_system_monitor.cfg',
                        newrelic_sysmon_config_path,
                        template_dir=config_instance.config_path('new_relic'),
                        context=config_instance.context, use_sudo=True, use_jinja=True)
    else:
        print('New Relic System Monitor configuration file is already exist. '
              'Make sure it contains the right new relic license key for Razortheory account.')

    # Start the daemon
    sudo('/etc/init.d/newrelic-sysmond start')


@task
def stop_newrelic_server_monitor(config_dir):
    Config(config_dir)
    sudo('/etc/init.d/newrelic-sysmond stop')


@task
def delete_newrelic_server_monitor(config_dir):
    Config(config_dir)
    apt_sources_file = '/etc/apt/sources.list.d/newrelic.list'
    server_monitor_package = 'newrelic-sysmond'

    stop_newrelic_server_monitor()
    sudo('apt-get purge {} -y'.format(server_monitor_package), warn_only=True)
    sudo('rm {}'.format(apt_sources_file), warn_only=True)
    sudo('apt-get update', quiet=True)


@task
def config_newrelic_monitor(config_dir):
    config_instance = Config(config_dir)

    upload_template('newrelic.ini',
                    config_instance.NEWRELIC_INI,
                    template_dir=config_instance.config_path('new_relic'),
                    context=config_instance.context, use_jinja=True)
