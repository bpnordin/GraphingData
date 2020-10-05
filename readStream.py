import sys
import os
import random
import time
import zmq
import json


from origin.client import server, random_data
import ConfigParser

class readStream():
    def __init__(self):
        configfile = "origin-server.cfg"
        config = ConfigParser.ConfigParser()
        config.read(configfile)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        host = config.get('Server','ip')
        port = config.getint('Server','read_port')
        self.socket.connect("tcp://%s:%s" % (host,port))



    def read_streams(self,stream,start=None,stop=None):
        data = None
        print "sending raw read request for stream `{}`....".format(stream)
        request_obj = { 'stream': stream, 'raw': True,'start' : start,'stop' : stop } 
        print request_obj
        self.socket.send(json.dumps(request_obj))
        response = self.socket.recv()
        data = json.loads(response)
        print "+"*80
        return data[1]

    def close(self):
        self.socket.close()
        self.context.term()

if __name__ == "__main__":
    read = readStream()
    print read.read_streams(stop=time.time()-60)
    read.close()
