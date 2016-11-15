#!/usr/bin/env python

################################
### Creates Elastic Search index 
################################
import sys
sys.path.append('/opt/create-es-index/')
import es_drop # to drop index

import json
import httplib
import sys


def create_index(cnx,config):
    """Delete index and re-create its mapping and settings

    Parameters:
      cnx:    HTTP connection to Elastic Search
      config: Some settings (including index name and settings, mapping...)

    """

    sys.stderr.write( "Creating Elastic Search index\n")

    # prepare settings object
    settings={}
    settings["settings"]={}
    settings["settings"]["number_of_shards"]=config.shard_nb
    settings["settings"]["number_of_replicas"]=config.replica_nb
    settings["mappings"]={}
        
    # Decode JSON settings 
    settings["mappings"][config.typ]=config.mapping
    # re-encode the result into JSON
    settings_json=json.dumps(settings)
    
    # dropping the index in case it exists. 
    es_drop.drop_index(cnx, config)
    
    # Creation of the settings
    sys.stderr.write( "  Creating settings for index %s\n" % config.index)
    ###############################################
    cnx.request("PUT",config.index,settings_json) #
    ###############################################
    resp=cnx.getresponse()
    sys.stderr.write( resp.read() + "\n")
    if resp.status != httplib.OK:
        raise Exception("ERROR when creating " + config.index + ": %d %s" % (resp.status, resp.reason))
    sys.stderr.write( "  Index successfully created\n")

    # Retrieval and display of the just created mapping
    sys.stderr.write( "Retrieving mapping\n")
    #####################################################
    cnx.request("GET",config.index+"/_mapping/?pretty") #
    #####################################################
    resp=cnx.getresponse()
    sys.stderr.write( resp.read() + "\n")
    if resp.status != httplib.OK:
        raise Exception("ERROR when retrieving mapping of index %s: %d %s" % (config.index,resp.status, resp.reason))
   
    # Retrieval and display of the settings
    sys.stderr.write( "Retrieving settings\n")
    ######################################################
    cnx.request("GET",config.index+"/_settings/?pretty") #
    ######################################################
    resp=cnx.getresponse()
    sys.stderr.write( resp.read() + "\n")
    if resp.status != httplib.OK:
        raise Exception("ERROR when retrieving settings of index %s: %d %s" % (config.index,resp.status, resp.reason))

    sys.stderr.write( "  Index successfully created\n" )


########
# MAIN #    
########

if __name__ == '__main__':

    import es_config # All our config variables

    import argparse

    # Parsing arguments
    parser = argparse.ArgumentParser(description='Delete Elastic Search index and re-create it (i.e. set mapping and settings).')
    args = parser.parse_args()
     
    # Connection to Elsatic Search
    sys.stderr.write( "Connecting to %s on port %d\n" % (es_config.host,es_config.port) )
    cnx=httplib.HTTPConnection(es_config.host,es_config.port)
    cnx.connect()
    
    ############################# 
    create_index(cnx,es_config) #
    #############################

    cnx.close()
    
