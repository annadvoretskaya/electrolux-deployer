Intro
=====

This is a tool which is used to manage projects on remote servers. It's based on Python 3 + Fabric.

Installation instructions
=========================

1. Clone deployer repository: ``git clone https://XXXXXXX@bitbucket.org/razortheory/{{ project_name }}-deployer.git {{ project_name }}-deployer``
2. Create virtual environment using virtualevnwrapper: ``mkvirtualenv --python=python3 {{ project_name }}-deployer``
3. Install requirements: ``pip install -r requirements.txt``

Setting up
==========
1. Copy remote servers `.pem` keys to configuration folders (i.e. `prod`, `staging`) and set ``chmod 600 *.pem``

Base usage rules
================

1. Do not forget to activate virtual environment: ``workon {{ project_name }}-deployer``
2. Common template of fabric tasks is ``fab task_name:config_name,arg1,arg2,kwarg=value`` where `config_name` is the name of folder with `.pem` file and `server.json`. Examples: ``fab deploy:staging``, ``fab shell:prod``, ``fab add_swap:eu_server,2048``
3. Most used fabric tasks call another tasks inside and you can call these "small" tasks directly. For example: many tasks like ``fab deploy:prod`` calls ``restart`` task and you can initiate restarting manually by ``fab restart:prod``

Most used commands
==================

- ``fab start_project:config_name`` - to initiate project on a remote server, i.e. ``fab start_project:prod``
- ``fab deploy:config_name,with_restart,edit_env_variables`` - to update remote project by last changes, i.e. ``fab deploy:staging,False,True`` or ``fab deploy:prod,edit_env_variables=True``, default values of `with_restart` and `edit_env_variables` are True and False
- ``fab restart:config_name`` - to reboot remote project (not server), i.e. ``fab restart:prod``
- ``fab shell:config_name`` - to get access to remote server command line using SSH, i.e. ``fab shell:staging``
- ``fab dumpdata:config_name,app_name.model_name,file_name,use_indent`` - to get data from remote database, i.e. ``fab dumpdata:prod,custom_auth.applicationuser,users.json,True``
- ``fab add_swap:config_name,size`` - to add swap file to a remote server, i.e. ``fab add_swap:prod,2000``, default size of swap file is 1000Mb
- ``fab purge_celery:config_name`` - to drop Celery queues, i.e. ``fab purge_celery:prod``

Setup deployer from template for new projects
=================================================

You have to make a copy of [base deployer](https://bitbucket.org/razortheory/django-deployer) and configure this copy to use with new projects. 
Also you can change behaviour of existing tasks in your deployer copy and add more tasks if necessary.
Check these [instructions](deployer_setup.md) for more information.
