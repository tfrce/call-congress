FROM ubuntu
RUN apt-get update
RUN apt-get -y install python-pip python-dev npm git

WORKDIR /opt

ADD requirements.txt ./
ADD requirements ./requirements
RUN pip install -r requirements/development.txt

ADD bower.json ./
RUN npm install -g bower
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN bower --allow-root --config.interactive=false install

ADD alembic.ini manager.py newrelic.ini Procfile uwsgi.ini entrypoint.sh ./
ADD scripts ./scripts/
ADD tests ./tests/
ADD call_server ./call_server/
ADD alembic ./alembic/

CMD ["bash", "-l", "-c", "python manager.py run"]
ENTRYPOINT ["/opt/entrypoint.sh"]
