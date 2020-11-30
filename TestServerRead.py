from origin.client import origin_reader,origin_subscriber
import time
import ConfigParser
import logging
import pandas as pd

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
def subCallback(stream_id,data,state,log,crtl):
    #store data locally in some file
    #with all of the timedate stuff and all that already in there
    print data
    df = pd.DataFrame([data])
    df.to_csv('test' + str(stream_id).strip()+ '.csv',mode = 'a',header=False,index=False)
    return state

reader = origin_reader.Reader(config,logger)
sub = origin_subscriber.Subscriber(config,logger)
test_streams = ['Hybrid_Mux','Hybrid_Beam_Balances']
for stream in test_streams:
    data = {stream: 
        pd.DataFrame(reader.get_stream_raw_data(stream,start = time.time(),stop = time.time()-300))
                        }
    data[stream].to_csv('test' + str(stream).strip()+ '.csv',index=False)
    sub.subscribe(stream,callback = subCallback)
reader.close()
time.sleep(10)
sub.close()
for stream in test_streams:
    print pd.read_csv('test' + str(stream).strip()+ '.csv').tail()
