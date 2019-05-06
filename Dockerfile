FROM python:2.7-stretch
RUN apt-get update && \
  curl -sL https://deb.nodesource.com/setup_4.x | bash && \
  apt-get -y install git uwsgi libpq-dev curl unzip nodejs

RUN  mkdir /ngrok && \
     cd /ngrok && \
     curl -sLo ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip && \
     unzip ngrok.zip ngrok -d /bin && \
     rm -r /ngrok

WORKDIR /opt

ADD requirements.txt ./
ADD requirements ./requirements
RUN pip install -r requirements/production.txt -r requirements/development.txt

ADD bower.json ./
ADD .bowerrc ./
RUN npm install -g bower
RUN bower --allow-root --config.interactive=false install

ADD alembic.ini manager.py Procfile uwsgi.ini entrypoint.sh ./
ADD scripts ./scripts/
ADD tests ./tests/
ADD call_server ./call_server/
ADD alembic ./alembic/
ADD instance ./instance/

ENTRYPOINT ["/opt/entrypoint.sh"]
