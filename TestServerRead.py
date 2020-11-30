from origin.client import origin_reader
import time
import ConfigParser
import logging

configFile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configFile)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('TestServerRead.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

reader = origin_reader.Reader(config,logger)
test_streams = ['Hybrid_Mux']
for stream in test_streams:
    print reader.get_stream_raw_data(stream,start = time.time(),stop = time.time()-300)
reader.close()