#!/bin/bash
set -e

if [[ -z "$START_TIMEOUT" ]]; then
    START_TIMEOUT=600
fi

if [[ -z "$KAFKA_PORT" ]]; then
    KAFKA_PORT=9092
fi

echo "checking if kafka service is up"
start_timeout_exceeded=false
count=0
step=10
while netstat -lnt | awk '$4 ~ /:'$KAFKA_PORT'$/ {exit 1}'; do
    echo "waiting for kafka to be ready"
    sleep $step;
    count=$(expr $count + $step)
    if [ $count -gt $START_TIMEOUT ]; then
        start_timeout_exceeded=true
        break
    fi
done

if $start_timeout_exceeded; then
    echo "Not able to auto-create topic (waited for $START_TIMEOUT sec)"
    exit 1
fi

echo "kafka is ready, creating a topic"

#zookeeper is hard coded as localhost:2181
$KAFKA_HOME/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partition 1 --topic word_count
echo "the topic word_count has been automatically created !"
