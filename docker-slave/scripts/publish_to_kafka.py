import sys
from time import sleep
from kafka import KafkaProducer

def main():
    data = sys.argv[1]
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    with open(data, 'r') as fd:
        for line in fd:
            producer.send('word_count', line)
    print("data sent to kafka")
    sleep(30)


if __name__=="__main__":
    main()
