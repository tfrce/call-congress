#!/bin/bash
#set -e

if [ ! -e "/opt/dev.db" ]; then
	python manager.py migrate up
	python manager.py assets build
fi

case "$FLASK_ENV" in
    "production")
        exec bash -l -c "uwsgi uwsgi.ini"
        ;;

    "development" | "")
        exec bash -l -c "python manager.py runserver"
        ;;
esac
