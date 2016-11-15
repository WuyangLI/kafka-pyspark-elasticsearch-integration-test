#!/bin/bash
#calculate the size of the files in a dir

function dir() { ls -l "${@}"| grep '^d' | awk -v pdir="${@}" {'print pdir"/"$9"/part-00000"'} | xargs ls -l | grep "^-r" | awk '{print $5}'; }

step=10

while [ ! -d 'tmp/streaming_output' ]; do
   echo "spark job hasn't started yet"
   sleep $step
done

flag=true
while $flag; do
    #list the size of all the subdirs
    dir_sizes=$(dir 'tmp/streaming_output')
    for size in $dir_sizes; do
        echo $size
        if [ $size -gt 0 ]; then
            echo "reco data has been successfully saved as textfile in the file system"
            flag=false
            sleep 30
            break
        else
            sleep $step
        fi
    done
done

echo "going to shut down the spark, kafka, mqhub service"
docker-compose ps | awk {'print $1'} | grep "pyspark" | xargs docker stop
docker-compose stop kafka
docker-compose stop mqhub

echo "check if data are inserted into the elasticsearch node"

docker-compose run --no-deps mqhub curl -XGET 'elasticsearch:9200/es_test/word_count/_count?pretty' -d'{"query" : {"match_all" : {}}}'

docker-compose down
