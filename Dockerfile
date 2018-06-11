FROM ubuntu:xenial
RUN apt-get update && apt-get -y install python-pip python-dev npm git uwsgi libpq-dev curl unzip

RUN  mkdir /ngrok && \
     cd /ngrok && \
     curl -sLo ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip && \
     unzip ngrok.zip ngrok -d /bin && \
     rm -r /ngrok

WORKDIR /opt

# We need to remove the os version of setuptools
# It's incompatible with a dependency in gevent-psycopg2
RUN easy_install -m setuptools
RUN rm -r /usr/lib/python2.7/dist-packages/setuptools*
RUN pip install setuptools

ADD requirements.txt ./
ADD requirements ./requirements
RUN pip install -r requirements/production.txt -r requirements/development.txt

ADD bower.json ./
ADD .bowerrc ./
RUN npm install -g bower
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN bower --allow-root --config.interactive=false install

ADD alembic.ini manager.py Procfile uwsgi.ini entrypoint.sh ./
ADD scripts ./scripts/
ADD tests ./tests/
ADD call_server ./call_server/
ADD alembic ./alembic/
ADD instance ./instance/

ENTRYPOINT ["/opt/entrypoint.sh"]
