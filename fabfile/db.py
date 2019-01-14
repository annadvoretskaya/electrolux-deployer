from fabric.context_managers import warn_only
from fabric.decorators import task
from fabric.operations import run
from six.moves.urllib.parse import urlparse

from utils import Config


@task
def create_database(config_dir):
    config_instance = Config(config_dir)

    database_url = urlparse(config_instance.DATABASE_URL)

    if database_url.scheme not in ['postgres', 'postgresql', 'pgsql', 'psql']:
        return

    host = database_url.hostname
    port = database_url.port

    user = database_url.username
    password = database_url.password

    database = database_url.path[1:]
    database = database.split('?', 2)[0]

    command = 'createdb'

    if host:
        command += ' -h %s' % host
    if port:
        command += ' -p %s' % port
    if user:
        command += ' -U%s' % user
    if password:
        command = ('export PGPASSWORD="%s" && ' % password) + command

    command += ' %s' % database

    with warn_only():
        result = run(command)

    if 'already exists' in result:
        print('Database %s already exists' % database)
