import sys
import os
import random
import time
import zmq
import json
import logging


from origin.client import server, random_data
import ConfigParser

class readStream():

    def __init__(self,debug=True,configfile = "origin-server.cfg"):
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfile)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        host = self.config.get('Server','ip')
        port = self.config.getint('Server','read_port')
        try:
            self.socket.connect("tcp://%s:%s" % (host,port))
        except:
            print "error"
            pass
            #log something, throw error for other places to catch??



    def read_streams(self,stream,start=None,stop=None):
        data = None
        try:
            request_obj = { 'stream': stream, 'raw': True,'start' : start,'stop' : stop } 
            self.socket.send(json.dumps(request_obj))
            response = self.socket.recv()
            data = json.loads(response)
        except Exception as e:
            pass
        
        if data[0] == 1:
            if data[1]['error'] == "Stream declared, but no data in range.":
                return None
            return data[1]
        

    def stream_list(self):
        data = None
        try:
            self.socket.send(json.dumps(''))
            response = self.socket.recv()
            data = json.loads(response)
        except Exception as e:
            print e
        #list of keys sorted
        if (data[0] == 1):
            return data[1]
        else:
            return "error"
    def close(self):
        self.socket.close()
        self.context.term()
        print "closed"

