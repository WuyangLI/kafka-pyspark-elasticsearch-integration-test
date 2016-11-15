# Kafka and Zookeeper
FROM spotify/kafka

RUN apt-get update && \
    apt-get install -y net-tools

#ADD scripts/start-kafka.sh /usr/bin/start-kafka.sh
ADD scripts/create-topic.sh /usr/bin/create-topic.sh

# Supervisor config
#ADD supervisor/kafka.conf supervisor/zookeeper.conf supervisor/topic.conf /etc/supervisor/conf.d/
ADD supervisor/topic.conf /etc/supervisor/conf.d/

CMD ["supervisord", "-n"]
