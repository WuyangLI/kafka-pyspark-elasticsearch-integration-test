# kafka-pyspark-elasticsearch-integration-test
This is piece of work based on my two-week experience on Docker and Docker compose, inspired by Anatoliy Plastinin’s blog[1].  If you use scala, Anatoliy’s blog is strongly recommended. If you play with pyspark or more familiar with python, maybe this would be a good start. As a newbie to Docker and Docker compose, I would appreciate if you point out any bad practices or wrong doings in my code and blog.
This is an example of integration test for a spark streaming job. The spark job retrieves data from kafka, processes it, and then save the output to elasticsearch. The versions of all the components are listed below:
Name	version
Elasticsearch	5
Kafka	0.8.2.1
Pyspark	Spark 1.6 + python 2.7

Prerequisites:
Docker
Docker-compose
 
You can build the images yourself or pull them from docker hub
Elasticsearch
intedocker-elasticsearch$ docker build -t integration-test-elasticsearch .

Kafka
integration_test_docker/docker-kafka$ docker build -t integration-test-kafka .

Pyspark
integration_test_docker/docker-pyspark$ docker build -t integration-test-pyspark .

Slave
integration_test_docker/docker-slave$ docker build -t integration-test-slave .

Putting everything together with Docker-compose
First of all, before you start
sudo sysctl -w vm.max_map_count=262144
with this setting elasticsearch container could start and run normally.
Secondly, start kafka, elasticsearch services. Note that in our test, a topic ‘word-count’ in kafka and an index ‘es_test’ as well as a type ‘word_count’ in elasticsearch are automatically created, I’ll explain how they are created in the next section.
docker-compose up
wait until you see 
kafka_1          | 2016-11-15 09:18:14,632 INFO exited: topic (exit status 0; expected)
which means the kafka service is up running and the topic word-count has been created. Otherwise, an exception will be thrown because spark can’t find the topic ‘word_count’. Actually,  You can create a topic manually as described in Anatoliy Plastinin’s.
Lastly, start the spark streaming application with the following command line:
docker-compose run --workdir="/app/" pyspark spark-submit --jars /app_dependencies/kafka_2.10-0.8.2.1.jar,/app_dependencies/kafka-clients-0.8.2.1.jar,/app_dependencies/metrics-core-2.2.0.jar,/app_dependencies/spark-streaming-kafka_2.10-1.6.0.jar,/app_dependencies/elasticsearch-hadoop-5.0.0.jar --conf spark.io.compression.codec=lz4 /app/integration_test_spark_app.py --brokers kafka --topic word_count --checkpoint /test_output/checkpoint_word_count --es_host elasticsearch --es_port 9200 --output /test_output/streaming_output/word-count
it looks a little bit messy. Let’s simplify it a little bit:
docker-compose run [service name] [command line]
we set the work directory to /app in the container by using –workdir option. The command line above starts a container of pyspark, in the container, we launch the spark application defined in /app/integration_test_spark_app.py with command spark-submit along with some customer settings like –jars, –conf. The application has a lot of input arguments, like kafka brokersm topic, checkpoint for the streaming job, elasticsearch host and etc.
once you see the output printed on the screen and inserted into elasticsearch, we may check for confirmation whether the documents have been inserted successfully.
docker-compose$ docker exec -it $(docker-compose ps -q slave) bash
A simple query for counting the number of inserted documents:
curl -XGET 'elasticsearch:9200/es_test/word_count/_count?pretty' -d '                                                                                    
 {
"query":{ 
"match_all":{}
}
}'
If you get the following response, congratulations !  you made this integration test work!
{
  "count" : 135,
  "_shards" : {
    "total" : 2,
    "successful" : 2,
    "failed" : 0
  }
}

To tear down, use the flowing 
docker-compose down
Note that you may find a similar command docker-compose stop. The difference between these two command lines are 
