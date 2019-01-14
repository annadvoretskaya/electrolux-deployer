import os

from fabric.context_managers import cd
from fabric.contrib.files import upload_template, exists
from fabric.decorators import task
from fabric.operations import sudo, run

from utils import Config


@task
def prepare_journal(config_dir):
    Config(config_dir)

    sudo('mkdir -p /var/log/journal')
    sudo('systemctl restart systemd-journald')


@task
def config_nginx(config_dir, conf_template='nginx.conf'):
    config_instance = Config(config_dir)

    nginx_configs = config_instance.config_path('nginx')
    remote_sa_path = '/etc/nginx/sites-available/%s' % config_instance.project_name
    upload_template(conf_template, remote_sa_path, template_dir=nginx_configs,
                    context=config_instance.context, use_sudo=True, use_jinja=True)
    sudo('ln -sf %s /etc/nginx/sites-enabled' % remote_sa_path)


@task
def config_letsencrypt(config_dir):
    config_instance = Config(config_dir)

    nginx_configs = config_instance.config_path('nginx')
    remote_conf_path = config_instance.remote_path('conf')
    letsencrypt_dir = getattr(config_instance, 'LETSENCRYPT_DIR')
    if not letsencrypt_dir:
        letsencrypt_dir = config_instance.LETSENCRYPT_DIR = '/opt/letsencrypt/'
    upload_template('letsencrypt/letsencrypt_config.ini', remote_conf_path, template_dir=nginx_configs,
                    context=config_instance.context, use_sudo=True, mode=0o750, use_jinja=True)

    sudo('mkdir -p %s' % letsencrypt_dir)
    with cd(letsencrypt_dir):
        sudo('wget https://dl.eff.org/certbot-auto')
        sudo('chmod a+x certbot-auto')

    config_nginx(config_dir, conf_template='letsencrypt/nginx_getting_cert.conf')
    sudo('service nginx restart')

    with cd(letsencrypt_dir):
        sudo('./certbot-auto certonly --non-interactive --agree-tos --expand --config %s' %
             config_instance.remote_path('conf', 'letsencrypt_config.ini'))

    sudo('chmod -R 755 /etc/letsencrypt/archive /etc/letsencrypt/live')

    # TODO Check this on a server this domain name.
    remote_conf_path = '/etc/systemd/system/'
    upload_template('letsencrypt/systemd/service', os.path.join(remote_conf_path, 'letsencrypt-updater.service'),
                    template_dir=nginx_configs, context=config_instance.context, use_sudo=True, use_jinja=True)
    upload_template('letsencrypt/systemd/timer', os.path.join(remote_conf_path, 'letsencrypt-updater.timer'),
                    template_dir=nginx_configs, context=config_instance.context, use_sudo=True, use_jinja=True)

    sudo('systemctl reenable letsencrypt-updater.timer')

    config_nginx(config_dir)
    sudo('service nginx restart')


@task
def config_gunicorn(config_dir):
    config_instance = Config(config_dir)

    gunicorn_configs = config_instance.config_path('gunicorn', 'systemd')
    remote_conf_path = '/etc/systemd/system/'

    upload_template('service',
                    os.path.join(remote_conf_path, '{}.service'.format(config_instance.gunicorn_name)),
                    template_dir=gunicorn_configs, context=config_instance.context, use_sudo=True, use_jinja=True)
    sudo('systemctl reenable {}.service'.format(config_instance.gunicorn_name))


@task
def config_target(config_dir):
    config_instance = Config(config_dir)

    remote_conf_path = '/etc/systemd/system/'
    upload_template('target', os.path.join(remote_conf_path, '{}.target'.format(config_instance.project_name)),
                    template_dir=config_instance.config_path(), context=config_instance.context, use_sudo=True, use_jinja=True)
    sudo('systemctl reenable {}.target'.format(config_instance.project_name))


@task
def add_swap(size_in_mb=1000):
    n = 0
    filename = '/swapfile{}'.format(n)
    # Generate name for the new swap (format: /swapfileN)
    while exists(filename):
        n += 1
        filename = '/swapfile{}'.format(n)

    # Allocate disk space for swap
    sudo('fallocate -l {0}M {1}'.format(size_in_mb, filename))
    sudo('chmod 600 {}'.format(filename))
    # Activate swap
    sudo('mkswap {}'.format(filename))
    sudo('swapon {}'.format(filename))
    # Make swap file permanent
    sudo('sed -i -e \'$a{} none swap sw 0 0\' /etc/fstab'.format(filename))

    # This settings should be added only for /swapfile0
    if not n:
        # The swappiness parameter configures how often your system swaps data out of RAM to the swap space.
        # This is a value between 0 and 100 that represents a percentage.
        # With values close to zero, the kernel will not swap data to the disk unless absolutely necessary.
        # Default value - 60.
        sudo('sysctl vm.swappiness=10')
        # Make this setting permanent
        sudo('sed -i -e \'$avm.swappiness = 10\' /etc/sysctl.conf')
        # The following setting configures how much the system will choose to cache inode
        # and dentry information over other data.
        # Default value - 100, system removes inode information from the cache too quickly.
        sudo('sysctl vm.vfs_cache_pressure=50')
        # Make this setting permanent
        sudo('sed -i -e \'$avm.vfs_cache_pressure = 50\' /etc/sysctl.conf')
