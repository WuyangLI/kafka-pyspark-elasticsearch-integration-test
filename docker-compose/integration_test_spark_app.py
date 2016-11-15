from __future__ import print_function

import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json

def saveToES(rdd, es_conf):
    rdd_es = rdd.map(lambda e: json.dumps({'word': e[0], 'count': e[1]})) \
                .map(lambda x: ('id', x))

    rdd_es.saveAsNewAPIHadoopFile(
        path="-",
        outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
        keyClass="org.apache.hadoop.io.NullWritable",
        valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
        conf=es_conf)
    return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='kafka-spark-streaming-elasticsearch integration test')
    parser.add_argument('--brokers', default='kafka:9092', required=True)
    parser.add_argument('--topic', default='word_count', required=True)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--es_host', default='elasticsearch', required=True)
    parser.add_argument('--es_port', default='9200', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    es_conf = {"es.nodes": args.es_host,
               "es.port": args.es_port,
               "es.resource": '/'.join(['es_test', 'word_count']),
               "es.input.json": "true",
               "es.batch.size.entries": '5000'}

    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
    ssc = StreamingContext(sc, 30)
    ssc.checkpoint(args.checkpoint)

    brokers=args.brokers
    topic=args.topic
    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
    lines = kvs.map(lambda x: x[1])
    counts = lines.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a, b: a+b)
    counts.pprint()
    counts.saveAsTextFiles(args.output)
    counts.foreachRDD(lambda x: saveToES(x, es_conf))


    ssc.start()
    ssc.awaitTermination()
