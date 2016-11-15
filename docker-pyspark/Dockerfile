FROM java:openjdk-8-jre

#general dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get install -y bash

#python 2
RUN apt-get update && \
    apt-get install -y python \
    python-pip \
    && apt-get clean

#support for Hadoop 2.6.0
RUN curl -s http://d3kbcqa49mib13.cloudfront.net/spark-1.6.0-bin-hadoop2.6.tgz | tar -xz -C /usr/local/
RUN cd /usr/local && ln -s spark-1.6.0-bin-hadoop2.6 spark
ENV SPARK_HOME /usr/local/spark

ENV PYSPARK_PYTHON python

ENV PATH $PATH:$SPARK_HOME/bin

# Define working directory
WORKDIR /app

# Define default command.
CMD ["bash"] 
