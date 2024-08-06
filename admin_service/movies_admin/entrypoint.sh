#!/usr/bin/env bash

python manage.py migrate

python manage.py compilemessages -l ru -l en

python manage.py collectstatic --noinput

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi
$@

#sudo chmod +x ./load_data.py

python load_data.py

set -e

sudo chown www-data:www-data /var/log

uwsgi --strict --ini uwsgi.ini