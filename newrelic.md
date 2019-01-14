New Relic installation instructions
===================================

To properly setup New Relic monitoring tools, you need to supply account License key (further referred to as LICENSE-KEY). 
[Find your license key guide](https://docs.newrelic.com/docs/accounts-partnerships/accounts/account-setup/license-key)


Application Monitoring setup
============================

Run `config_newrelic_monitor` fabric task.
> $ fab config_newrelic_monitor:config_name


Availability Monitoring setup
=============================

See instructions in `availability_monitor/install.md`.


System Monitor for server
=========================

Run `setup_newrelic_server_monitor` fabric task for production server.
> $ fab setup_newrelic_server_monitor:config_name
