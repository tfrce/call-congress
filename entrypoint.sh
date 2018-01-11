#!/bin/bash
#set -e

if [ ! -e "/opt/dev.db" ]; then
	python manager.py migrate up
	python manager.py assets build
fi

start_ngrok() {
    (
        ngrok http --log stdout --log-level debug 5000 \
            | grep --line-buffered -oE 'https://[[:alnum:]]+.ngrok.io'
    ) >/var/log/ngrok.log &

    while [ -z "$(cat /var/log/ngrok.log)" ]; do
        echo "Waiting on ngrok..." >&2
        sleep 0.2
    done

    grep -oE '[[:alnum:]]+.ngrok.io' /var/log/ngrok.log
}

case "$FLASK_ENV" in
    "production")
        python manager.py loadpoliticaldata
        exec bash -l -c "uwsgi uwsgi.ini"
        ;;

    "development-expose")
        external_host="$(start_ngrok)"
        echo "External address is https://$external_host" >&2

        exec bash -l -c "python manager.py runserver --external $external_host"
        ;;

    "development" | "")
        exec bash -l -c "python manager.py runserver"
        ;;
esac
