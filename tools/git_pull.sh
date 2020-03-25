#!/bin/sh

cd /home/apps/myenv/bin/Dokosumi
git pull origin master

python ./manage.py makemigrations
python ./manage.py migrate
python ./manage.py collectstatic --noinput

sed -i -e "s/DEBUG = True/DEBUG = False/g" ./dokosumi/settings.py

sudo service httpd restart