#!/bin/bash
#set -e

if [ ! -e "/opt/dev.db" ]; then
	python manager.py migrate up
	python manager.py assets build
fi

exec "$@"
