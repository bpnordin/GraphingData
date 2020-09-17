import zmq
import multiprocessing
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


data_queue = multiprocessing.Queue()
sub = origin_subscriber.Subscriber(config,logging.getLogger(__name__),data_queue)
sub.subscribe("Hybrid_Mux")
print data_queue.get()
time.sleep(10)
while not data_queue.empty():
    print data_queue.get()
sub.close()
'''
context = zmq.Context()
socket = context.socket(zmq.SUB)
host = config.get('Server','ip')
port = config.getint('Server','read_port')
socket.connect("tcp://%s:%s" % (host,port))


socket.setsockopt(zmq.SUBSCRIBE, "0038")
print socket.recv()
'''
