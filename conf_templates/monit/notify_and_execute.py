#!/usr/bin/python3

from subprocess import call
import os
import json
import sys

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

if len(sys.argv) > 1:
    log = open('/var/log/monit-{{ config.project_name }}.log', 'a+')
    try:
        call(sys.argv[1:], stdout=log, stderr=log)
    finally:
        log.close()

url = "{{ config.MONIT_SLACK_WEBHOOCK_URL }}"
headers = {'Content-Type': 'application/json'}
data = json.dumps({
    "channel": "#{{ config.MONIT_SLACK_CHANNEL }}",
    "username": "monit: {{ config.server_domains[0] }}",
    "text": "<!channel> {}: {} - {}".format(os.environ.get("MONIT_SERVICE"), os.environ.get("MONIT_EVENT"), os.environ.get("MONIT_DESCRIPTION"))
})

req = Request(url, data, headers)
response = urlopen(req)
