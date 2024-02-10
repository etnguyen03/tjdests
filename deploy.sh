#!/bin/sh

cd /site/public
git pull
TMPDIR=/site/tmp pipenv sync
pipenv run ./manage.py migrate
pipenv run ./manage.py collectstatic --no-input
echo "Deploy complete. Restart the site process to wrap up."
