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

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        host = config.get('Server','ip')
        port = config.getint('Server','read_port')
        socket.connect("tcp://%s:%s" % (host,port))

        stream_test_list = ["Hybrid_Mux"]

    time.sleep(5)

    def read_streams():
        for stream in stream_test_list:
            print "sending read request for stream `{}`....".format(stream)
            request_obj = { 'stream': stream }
            socket.send(json.dumps(request_obj))
            response = socket.recv()
            print "sever responds with: "
            print response
            print "+"*80
            time.sleep(3)
        for stream in stream_test_list:
            print "sending raw read request for stream `{}`....".format(stream)
            request_obj = { 'stream': stream, 'raw': True } 
            socket.send(json.dumps(request_obj))
            response = socket.recv()
            print "sever responds with: "
            print response
            data = json.loads(response)
            print "+"*80
            time.sleep(3)
        return data
