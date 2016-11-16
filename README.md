#Kafka-Pyspark-Elasticsearch integration test using docker-compose
##Overview
This is piece of work based on my two-week experience on Docker and Docker compose, inspired by Anatoliy Plastinin’s blog[1].  If you use scala, Anatoliy’s blog is strongly recommended. If you play with pyspark or more familiar with python, maybe this would be a good start. As I'm a newbie to Docker and Docker compose, I would appreciate if you point out any bad practices or wrong doings in my code and blog.
This is an example of integration test for a spark streaming job. The spark job retrieves data from kafka, processes it, and then save the output to elasticsearch. The versions of all the components are listed below:
|Name	        |version               |
|---------------|:--------------------:|
|Elasticsearch	|5                     |
|Kafka	        |0.8.2.1               |
|Pyspark	|Spark 1.6 + python 2.7|

###Prerequisites:
####Docker
Docker is an open-source project that automates the deployment of Linux applications inside software containers. Docker containers wrap up a piece of software in a complete filesystem that contains everything it needs to run: code, runtime, system tools, system libraries – anything you can install on a server. This guarantees that it will always run the same, regardless of the environment it is running in

####Docker-compose
Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a Compose file to configure your application’s services.
By default Compose sets up a single network for your app. Each container for a service joins the default network and is both reachable by other containers on that network, and discoverable by them at a hostname identical to the container name.

####Three-step process
According to Docker official docs [2](https://docs.docker.com/compose/overview/)
>Using Compose is basically a three-step process.
>1.	Define your app’s environment with a Dockerfile so it can be reproduced anywhere.
>2.	Define the services that make up your app in docker-compose.yml so they can be run together in an isolated environment.
>3.	Lastly, run docker-compose up and Compose will start and run your entire app.

The next section is going to unroll in this three-step process
 
##Get hands dirty
###STEP ONE,  Define your app’s environment with a Dockerfile so it can be reproduced anywhere[2] 
You can build the images yourself or pull them from docker hub
Elasticsearch
```bash
intedocker-elasticsearch$ docker build -t integration-test-elasticsearch .
```
Kafka
```bash
integration_test_docker/docker-kafka$ docker build -t integration-test-kafka .
```
Pyspark
```bash
integration_test_docker/docker-pyspark$ docker build -t integration-test-pyspark .
```
Slave
```bash
integration_test_docker/docker-slave$ docker build -t integration-test-slave .
```
###STEP TWO, Define the services that make up your app in docker-compose.yml so they can be run together in an isolated environment[2]
```
version: '2'
services:
  kafka:
    image: integration-test-kafka
    expose:
      - "2181"
      - "9092"

  pyspark:
    image: integration-test-pyspark
    expose:
      - "9000"
    command: bash
    volumes:
      - .:/app/
      - ./dependencies:/app_dependencies
      - ./tmp:/test_output
    links:
      - kafka
      - elasticsearch

  slave:
    image: integration-test-slave
    volumes:
      - ./:/app
      - ./data:/data
      - ./tmp:/test_output
    links:
      - kafka

  elasticsearch:
    image: integration-test-elasticsearch
    environment:
      - Des.network.host=0.0.0.0
    expose:
      - "9200"
```
1. version: 
Compose files using the version 2 syntax must indicate the version number at the root of the document. All services must be declared under the services key.[3]

2. services:
A service definition contains configuration which will be applied to each container started for that service, much like passing command-line parameters to docker run.[3] 

..1. Image:
...Specify the image to start the container from. Can either be a repository/tag or a partial image ID. If the image does not exist, Compose attempts to pull it, unless you have also specified build, in which case it builds it using the specified options and tags it with the specified tag.[3]

...2. Volumes:
...mount a path on the host[3]

...3. links:
...Containers for the linked service will be reachable at a hostname identical to the alias, or the service name if no alias was specified.[3]
...Links also express dependency between services in the same way as depends on, so they determine the order of service startup.[3]


###STEP THREE, run `docker-compose up` and Compose will start and run your entire app.[3]
Wait………………don't run `docker-compose up`
####First of all, before you start, check if your system satisfy elasticsearch docker prerequisite: `vm.max_map_count` sysctl must be set to at least 262144.
```bash
sudo sysctl -w vm.max_map_count=262144
```
with this setting, elasticsearch container could start and run normally.
####Secondly, start kafka, elasticsearch services. Note that in our test, a topic ‘word-count’ in kafka and an index ‘es_test’ as well as a type ‘word_count’ in elasticsearch are automatically created, I’ll explain how they are created in the next section.
```bash
docker-compose up
```
wait until you see the process of creating a topic in kafka exits with status 0. 
```
kafka_1          | 2016-11-15 09:18:14,632 INFO exited: topic (exit status 0; expected)
```
which means the kafka service is up running and the topic word-count has been created. Otherwise, an exception will be thrown because spark can’t find the topic ‘word_count’. Actually,  You can create a topic manually as described in Anatoliy’s blog[1].
####Start the spark streaming application with the following command line:
```bash
docker-compose run --workdir="/app/" pyspark spark-submit --jars /app_dependencies/kafka_2.10-0.8.2.1.jar,/app_dependencies/kafka-clients-0.8.2.1.jar,/app_dependencies/metrics-core-2.2.0.jar,/app_dependencies/spark-streaming-kafka_2.10-1.6.0.jar,/app_dependencies/elasticsearch-hadoop-5.0.0.jar --conf spark.io.compression.codec=lz4 /app/integration_test_spark_app.py --brokers kafka --topic word_count --checkpoint /test_output/checkpoint_word_count --es_host elasticsearch --es_port 9200 --output /test_output/streaming_output/word-count
```
it looks a little bit messy. Let’s simplify it a little bit:
```bash
docker-compose run [service name] [command line]
```
we set the work directory to `/app` in the container by using `–workdir` option. The command line above starts a container of pyspark, in the container, we launch the spark application defined in `/app/integration_test_spark_app.py` with command spark-submit along with some customer settings like `–jars`, `–conf`. The application has a lot of input arguments, like kafka brokersm topic, checkpoint for the streaming job, elasticsearch host and etc.

####Check data insertion
Once you see the output printed on the screen and inserted into elasticsearch, we may check for confirmation whether the documents have been inserted successfully.
```bash
docker-compose$ docker exec -it $(docker-compose ps -q slave) bash
```
A simple query for counting the number of inserted documents:
```bash
curl -XGET 'elasticsearch:9200/es_test/word_count/_count?pretty' -d '                                                                                    
 {
"query":{ 
"match_all":{}
}
}'
```
If you get the following response, congratulations !  you made this integration test work!
```bash
{
  "count" : 135,
  "_shards" : {
    "total" : 2,
    "successful" : 2,
    "failed" : 0
  }
}
```
###Lastly, tear down all the services
```bash
docker-compose down
```

##Docker on VM
If your disk has a very limited capacity or you run docker on a virtual machine, hopefully you may find the following section quite useful.

1. Delete all containers:
```bash
docker ps -a | grep 'ago' | awk '{print $1}' | xargs --no-run-if-empty docker rm
```
2. Delete images:
```bash
docker rmi –f 
```
3. Delete all untagged images:
when you use `docker images` to display all the images in your system, if you find some weird ones like <none><none>, the post [What are Docker <none>:<none> images?](http://www.projectatomic.io/blog/2015/07/what-are-docker-none-none-images/) is definitely worth reading.

####Why my virtual disk keeps growing even after clearing cache and deleting all images and containers?
[Virtual Disk Size Much Greater than File System Disk Size](https://forums.virtualbox.org/viewtopic.php?f=6&t=54411) [4]
>In fact, dynamic disks do not grow because data is added. They grow when sectors on the disk are written to, which can happen for many reasons other than adding what the user might think of as data. For example, moving a file from one folder to another adds no data to the system, but it may involve a bunch of new sectors being written to.
>Since there is no concept of un-writing a sector it means that dynamic disks can only grow, never shrink: at least not unless you run a compaction tool on it, such as CloneVDI. It's also best to avoid Snapshots if you want to minimize wasted disk space.
>So: the guest will show you what capacity the disk has, and how much data has been stored. VirtualBox on the other hand will tell you the disk capacity and the amount of it which has been "used", i.e. which has been written to even once.

[How to compact VirtualBox's VDI file size?](http://superuser.com/questions/529149/how-to-compact-virtualboxs-vdi-file-size) [5]
```bash
#compact vdi
PATH=%PATH%;C:\Program Files\Oracle\VirtualBox
```
With a Linux Guest run this:
install pv
```bash
sudo dd if=/dev/zero | pv | sudo dd of=/bigemptyfile bs=4096k
sudo rm -rf /bigemptyfile
```
With a Windows Host run this:
```bash
VBoxManage.exe modifyhd "path\to\your\xxx.vdi" --compact
```

##Reference:
[1] http://blog.antlypls.com/blog/2015/10/05/getting-started-with-spark-streaming-using-docker/
[2] https://docs.docker.com/compose/overview/
[3] https://docs.docker.com/compose/compose-file/
[4] https://forums.virtualbox.org/viewtopic.php?f=6&t=54411 
[5] http://superuser.com/questions/529149/how-to-compact-virtualboxs-vdi-file-size
