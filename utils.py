import ast
import hashlib
import os
import json
import random
import time

from fabric.context_managers import warn_only
from fabric.operations import get, put, run
from six import BytesIO
from six.moves.urllib.parse import urlparse

try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

from fabric.api import env


ROOT = os.path.dirname(__file__)

SERVER_CONFIG_FILE = 'server.json'


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


@singleton
class Config(object):
    REMOTE_CONFIG_BLACKLIST = [
        'user',
        'host',
        'key_filename',
        'password',

        'project_name',
        'repository',
        'branch',
    ]

    _workon_home = None

    def __init__(self, config_dir=None):
        assert config_dir, "`config_dir` is required param."

        self.project_config_dir = os.path.join(ROOT, config_dir)

        assert os.path.exists(self.project_config_dir), "`%s` configuration not found." % config_dir

        self.server_config_path = os.path.join(self.project_config_dir, SERVER_CONFIG_FILE)
        self.server_env_variables = {}

        with open(self.server_config_path, 'r') as f:
            self.server_configs = json.loads(f.read())

        self.deploy_dir = os.path.join('/', 'home', self.user)
        self.project_dir = os.path.join(self.deploy_dir, self.project_name)

        self.celeryd_name = 'celeryd-' + self.project_name
        self.celerybeat_name = 'celerybeat-' + self.project_name
        self.gunicorn_name = 'gunicorn-' + self.project_name

        self.service_config_path = self.remote_path('config', 'service')

        self.server_env_variables = {}

        self.config_env()

    def config_env(self):
        env.host_string = self.host
        env.user = self.user
        if hasattr(self, 'key_filename'):
            env.key_filename = os.path.join(self.project_config_dir, self.key_filename)
        if hasattr(self, 'password'):
            env.password = self.password

    def __getattr__(self, item):
        if item in self.server_configs:
            return self.server_configs[item]

        if item not in self.REMOTE_CONFIG_BLACKLIST:
            if not len(self.server_env_variables):
                self.server_env_variables = get_variables_from(self.remote_path(self.env_file))

            if item in self.server_env_variables:
                return self.server_env_variables[item]

        raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, item))

    @property
    def workon_home(self):
        if self._workon_home:
            return self._workon_home

        self._workon_home = run('echo "$WORKON_HOME"')
        if not self._workon_home:
            self._workon_home = os.path.join('/', 'home', self.user, '.virtualenvs')

        return self._workon_home

    def config_path(self, *args):
        return os.path.join(ROOT, 'conf_templates', *args)

    def remote_path(self, *args):
        return os.path.join(self.project_dir, *args)

    @property
    def context(self):
        return {
            'config': self,
        }

    def get_random_string(self, length=12,
                          allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
        if not using_sysrandom:
            random.seed(
                hashlib.sha256(
                    ("%s%s" % (
                        random.getstate(),
                        time.time())).encode('utf-8')
                ).digest())
        return ''.join(random.choice(allowed_chars) for i in range(length))

    def generate_secret_key(self):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return self.get_random_string(50, chars)


def get_variables_from(filename):
    file_buffer = BytesIO()
    with warn_only():
        get(filename, file_buffer)

    variables = dict()

    for line in file_buffer.getvalue().splitlines():
        line = line.decode('utf-8').strip()
        if not line or line.startswith('#'):
            continue

        key, value = line.split('=', 1)
        variables[key] = value

    if 'EMAIL_URL' in variables:
        email_url = urlparse(variables['EMAIL_URL'])

        email = {
            'email_scheme': email_url.scheme,
            'email_host': email_url.hostname,
            'email_port': email_url.port,
            'email_user': email_url.username,
            'email_password': email_url.password,
            'email_path': email_url.path
        }

        variables.update(email)
        admins = json.loads(variables['ADMINS'])
        variables['MONIT_ADMINS'] = [adm[1] for adm in admins]

    return variables


def put_variables_to(filename, variables):
    file_buffer = BytesIO()
    with warn_only():
        get(filename, file_buffer)

    values = file_buffer.getvalue()
    file_buffer = BytesIO()
    for line in values.splitlines():
        line = line.decode('utf-8')
        if not line.lstrip().startswith('#'):
            variable = line.lstrip().split('=')[0].strip()
            if variable in variables:
                line = line.replace('=', '=' + str(variables[variable]))

        file_buffer.write(line.encode('utf-8'))
        file_buffer.write(b'\n')

    put(file_buffer, filename)


def cast_to_bool(value):
    # Evaluate literal "True" or "False" to native type
    return ast.literal_eval(str(value))
