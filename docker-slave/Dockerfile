FROM java:openjdk-8-jre

RUN apt-get update && \
    apt-get install -y python python-pip 

RUN pip install kafka-python

RUN apt-get update && \
    apt-get install -y supervisor && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Scripts for publishing messages to kafka
ADD scripts/publish-raw-data.sh /usr/bin/publish-raw-data.sh
ADD scripts/publish_to_kafka.py /usr/bin/publish_to_kafka.py

# Supervisor config
ADD supervisor/publish-raw-data.conf /etc/supervisor/conf.d/

RUN apt-get clean

WORKDIR /app/

CMD ["supervisord", "-n"]
