#!/bin/bash
set -e

if [[ -z "$START_TIMEOUT" ]]; then
    START_TIMEOUT=600
fi

echo "checking if spark service is up"
start_timeout_exceeded=false
count=0
step=10
while true; do 
    if [ -d "/test_output/checkpoint_word_count" ]; then
        break
    fi
    echo "waiting for spark to be ready"
    sleep $step;
    count=$(expr $count + $step)
    if [ $count -gt $START_TIMEOUT ]; then
        start_timeout_exceeded=true
        break
    fi
done

if $start_timeout_exceeded; then
    echo "Not able to detect spark service (waited for $START_TIMEOUT sec)"
    exit 1
else
    sleep 30
    echo "spark treaming is ready, start pushing messages to kafka"
    python /usr/bin/publish_to_kafka.py /data/word_count.txt
    echo "raw data has been published to kafka"
fi
