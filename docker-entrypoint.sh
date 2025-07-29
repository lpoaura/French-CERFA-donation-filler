#!/bin/bash


shopt -s dotglob nullglob

cd /app

python3 -m manage compilemessages
python3 -m manage migrate
python3 -m manage collectstatic --noinput

if [ $DEBUG = true ]
then
    echo "Starting dev mode"
    python -m manage runserver 0.0.0.0:8000
else
    echo "Starting prod mode"
    gunicorn -b 0.0.0.0:8000 -t ${GUNICORN_TIMEOUT:-180} settings.wsgi
fi
