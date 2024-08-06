#!/usr/bin/env bash

python manage.py migrate

python manage.py compilemessages -l ru -l en

python manage.py collectstatic --noinput

# sudo chmod +x ./load_data.py

# python load_data.py

set -e

sudo chown www-data:www-data /var/log

uwsgi --strict --ini uwsgi.ini