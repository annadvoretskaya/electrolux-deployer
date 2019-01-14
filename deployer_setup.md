Installation instructions
=========================

1. Clone base deployer repository: ``git clone https://XXXXXXX@bitbucket.org/razortheory/django-deployer.git myproject-deployer``
2. Create virtual environment using virtualevnwrapper: ``mkvirtualenv --python=python3 myproject-deployer``. In common case you can use one virtual environment for all deployers on your machine and can create separated environments if you need some special variables or you have deployer based on old versions of Python/Fabric
3. Install requirements: ``pip install -r requirements.txt``

Setting up
==========

1. Create configuration folders in deployer root folder (i.e. `prod`, `staging`, `eu_server` etc.) for each remote server. You will use that folder names as `config_name` in calling of tasks later
2. Copy remote servers `.pem` keys to these folders and set ``chmod 600 *.pem``
3. Configure `server.json` for each remote host

Newrelic
========

Check instructions [here](newrelic.md)

Environment variables
=====================

First deployment of project will prompt data for .env file thru nano editor. This file is a storage for virtual environment variables which is useful to keep in secret. Like credentials for the database. 

Fill this file by host-specific data according to `config/settings/base_env` template of your project. For example:

```
ADMINS=[["Ivan Ivanov", "ivanov@razortheory.com"], ]
ALLOWED_HOSTS=example.com,api.example.com
DATABASE_URL=postgress://username:password@host:port/database_name
...
```

Than save .env file by Ctrl+X hotkey of nano.

On your dev machine for your project you can use local .env file (do not pull it to repo) or you can specify variables in `$VIRTUAL_ENV/bin/postactivate` file by any text editor using following format: `export VAR_NAME=VAR_VALUE`. For example:

```
export ALLOWED_HOSTS=example.com,api.example.com
export DATABASE_URL=postgress://username:password@host:port/database_name
export DEV_ADMIN_EMAIL=ivanov@razortheory.com
...
```

For sure your dev variables won't be the same as remote. Avoid to use remote database for example.

Do not forget to reload environment (use `workon` command) after editing of `postactivate` file. 

You can check your variables by ``echo $VAR_NAME`` command in activated environment.
