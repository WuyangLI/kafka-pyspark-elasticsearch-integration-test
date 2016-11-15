FROM elasticsearch

RUN apt-get update && \
    apt-get install -y supervisor net-tools python

# Add scripts
ADD scripts/create-index.sh /usr/bin/create-index.sh

RUN mkdir /opt/create-es-index

ADD scripts/__init__.py /opt/create-es-index/__init__.py
ADD scripts/es_config.py  /opt/create-es-index/es_config.py
ADD scripts/es_create_index.py  /opt/create-es-index/es_create_index.py
ADD scripts/es_drop.py /opt/create-es-index/es_drop.py

# Supervisor config
ADD supervisor/start-elasticsearch.conf supervisor/create-index.conf /etc/supervisor/conf.d/

RUN chown -R elasticsearch:elasticsearch /tmp/

CMD ["supervisord", "-n"]
