#!/bin/sh

pipenv run gunicorn -b $HOST:$PORT --workers 4 tjdests.wsgi
