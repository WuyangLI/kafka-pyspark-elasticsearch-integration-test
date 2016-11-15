#!/usr/bin/env python

##################################
### Drop the Elastic Search index
##################################

import httplib
import sys

def drop_index(cnx, config):
    """Delete index

    Parameters:
      cnx:    HTTP connection to Elastic Search
      config: Some settings (including the name of the index)

    """

    sys.stderr.write( "Deleting Elastic Search index %s\n" % config.index)

    ####################################
    cnx.request("DELETE",config.index) #
    ####################################

    resp=cnx.getresponse()
    sys.stderr.write( resp.read()+"\n")
    if resp.status == httplib.NOT_FOUND:
        sys.stderr.write( "  WARNING: Index %s does not exist - cannot delete\n" % config.index)
    elif resp.status != httplib.OK:
        raise Exception("  ERROR when deleting " + config.index + ": %d %s" % (resp.status, resp.reason))
    else:
        sys.stderr.write( "  Index deleted\n")


########
# MAIN #    
########

if __name__ == '__main__':

    # All our config variables
    import pb_config

    import argparse

    # Parsing arguments
    parser = argparse.ArgumentParser(description='Drops Elastic Search index.')
    args = parser.parse_args()

    # Connection to Elsatic Search
    sys.stderr.write( "Connecting to %s on port %d\n" % (pb_config.host,pb_config.port))
    cnx=httplib.HTTPConnection(pb_config.host,pb_config.port)
    cnx.connect()

    ############################
    drop_index(cnx, pb_config) #
    ############################

    cnx.close()
    
