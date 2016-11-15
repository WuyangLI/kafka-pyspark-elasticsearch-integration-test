#!/bin/bash
set -e

if [[ -z "$ELASTICSEARCH_PORT" ]]; then
    ELASTICSEARCH_PORT=9200
fi

echo "checking if elasticsearch service is up"
count=0
step=10
while netstat -lnt | awk '$4 ~ /:'$ELASTICSEARCH_PORT'$/ {exit 1}'; do
    echo "waiting for elasticsearch to be ready"
    sleep $step;
    count=$(expr $count + $step)
done

echo "elasticsearch service is up and ready"
python /opt/create-es-index/es_create_index.py
echo "an test index created !"
