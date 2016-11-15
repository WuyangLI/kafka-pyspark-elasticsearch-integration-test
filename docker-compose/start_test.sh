set -e
# requirement for elasticsearch
sudo sysctl -w vm.max_map_count=262144

# launch kafka, mqhub service in the background before starting the pyspark app
docker-compose up -d

# parsing the filtered data
docker-compose run --workdir="/app/" pyspark spark-submit --jars /app_dependencies/kafka_2.10-0.8.2.1.jar,/app_dependencies/kafka-clients-0.8.2.1.jar,/app_dependencies/metrics-core-2.2.0.jar,/app_dependencies/spark-streaming-kafka_2.10-1.6.0.jar,/app_dependencies/elasticsearch-hadoop-5.0.0.jar --conf spark.io.compression.codec=lz4 /app/integration_test_spark_app.py --brokers kafka --topic word_count --checkpoint /test_output/checkpoint_word_count --es_host elasticsearch --es_port 9200 --output /test_output/streaming_output/word-count
