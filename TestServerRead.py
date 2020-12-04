import time
import configparser
import logging
import pandas as pd
import reciever, reader, subscriber

configFile = "origin-server.cfg"
config = configparser.ConfigParser(inline_comment_prefixes=';')
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
    df = pd.DataFrame([data])
    df.to_csv('test' + str(stream_id).strip()+ '.csv',mode = 'a',header=False,index=False)
    return state

reader = reader.Reader(config,logger)
test_streams = ['Hybrid_Mux','Hybrid_Beam_Balances']
sub = subscriber.Subscriber(config,logger)
for stream in test_streams:
    data = {stream: 
        pd.DataFrame(reader.get_stream_raw_data(stream,start = time.time(),stop = time.time()-300))
                        }
    sub.subscribe(stream)
    data[stream].to_csv('test' + str(stream).strip()+ '.csv',index=False)
reader.close()
time.sleep(10)
sub.close()
for stream in test_streams:
    print (pd.read_csv('test' + str(stream).strip()+ '.csv').tail())
