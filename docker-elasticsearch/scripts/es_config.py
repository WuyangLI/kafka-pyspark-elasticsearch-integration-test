#################################
### Elastic Search Configuration
#################################


### Elastic Search access

host="elasticsearch"                  # Elastic Search server
port=9200                             # Elastic Search port



### Index description

index="es_test"
typ="word_count"                      # Type name
shard_nb=2                            # number of shards
replica_nb=0                          # replication factor

### Data load

bulk_buffer_size_max=5000           # Bulk size for load and delete
load_refresh_interval=1000          # Elastic Search setting to prevent permanent and inefficient indexing of new inserts
nb_retry_max=10                     # Number of allowed retries when loading a directory


### Data mapping

mapping={ "_routing":{ "required":False },
          "_all": { "enabled": True },
          "properties" : {
             "word" : { "type" : "text", "index" : "not_analyzed" },
             "count": { "type" : "short", "index" : "not_analyzed"}
          }
      }

