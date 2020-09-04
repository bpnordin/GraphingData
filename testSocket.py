import zmq
import time
import logging
import sys
import os

fullBinPath  = os.path.abspath(os.getcwd() + "/" + sys.argv[0])
fullBasePath = os.path.dirname(os.path.dirname(fullBinPath))
fullLibPath  = os.path.join(fullBasePath, "lib")
fullCfgPath  = os.path.join(fullBasePath, "config")
sys.path.append(fullLibPath)

from origin.client import server, random_data, origin_subscriber
import ConfigParser 


configfile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configfile)


sub = origin_subscriber.Subscriber(config,logging.getLogger(__name__))
sub.subscribe("Hybrid_Mux")
time.sleep(10)
sub.close()
'''
context = zmq.Context()
socket = context.socket(zmq.SUB)
host = config.get('Server','ip')
port = config.getint('Server','read_port')
socket.connect("tcp://%s:%s" % (host,port))
sub_filter = str(38).zfill(filter_len).decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, sub_filter)
print socket.recv()
'''
