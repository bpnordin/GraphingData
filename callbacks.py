from origin.client import origin_reader,origin_subscriber
from dash.dependencies import Input, Output,State
import dash
from app import app
import time
import HybridSubscriber as hybrid_sub
import ConfigParser,logging
import pandas as pd
import multiprocessing

configFile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configFile)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('callbacks.log')
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

subscriber = origin_subscriber.Subscriber(config,logger) 
DATA = 'data.csv'
TIME = 'time.txt'

def reset():
    global subscriber
    if isinstance(subscriber,origin_subscriber.Subscriber):
        #make sure that everyhting is shut down properly
        subscriber.close()
    #make the subscriber object again
    subscriber = origin_subscriber.Subscriber(config,logger)
    logger.debug("started subscriber instance")

def subCallback(stream_id,data,state,log,crtl):
    #store data locally in some file
    #with all of the timedate stuff and all that already in there
    df = pd.DataFrame(data)
    df.to_csv(DATA,mode = 'a',header=False)
    return state

@app.callback(
    Output("keyValues",'data'),
    Input('submit_val',"n_clicks"),
    State("subCheckList","value")
)
def storeKeys(n_clicks,keyList):
    global subscriber
    #now we should subscriber and also note the time
    if keyList is None:
        return None
    for sub in keyList:
        subscriber.subscribe(sub,callback=subCallback)
    #store the time the subscribing happened in a file
    with open(TIME,'w') as f:
        f.write(time.time())

    return keyList
   


@app.callback(Output('dataID','data'),
              [Input('interval-component', 'n_intervals')],
              [State('keyValues','data'),State('dataID','data')])
def updateData(n,subList,oldData):
    ctx = dash.callback_context
    data = {}

    if oldData is None:
        #get the data
        if subList is None:
            #there is nothing selected, dont get the data
            return None
        #get the data on start up
        read = origin_reader.Reader(config,logger) 
        timeWindow = 300
        SUB_TIME = open(TIME,'r').read()
        
        data = {stream :pd.DataFrame( read.get_stream_raw_data(stream,start = SUB_TIME,
                stop = SUB_TIME-timeWindow)) for stream in subList}
        
        #save to file

        read.close()
        
        '''
        #now format the data
        for key in data.keys():
            if not data[key].empty:
                data[key]['measurement_time'] = pd.to_datetime(data[key]['measurement_time']/float(1**32),unit="s")
                s = data[key]['measurement_time'].iloc[-2] - data[key]['measurement_time'].iloc[0]
                data[key] = data[key].resample("{}S".format(int(s.seconds/99)),on='measurement_time').mean()
                data[key].index.name = 'measurement_time'
                data[key].reset_index(inplace=True)
                data[key] = data[key].to_dict('series')
            else:
                data[key] = None
                '''

        return data
    else:
        #there is already data, just update it with the new data from the subscriber
        pass
"""
    for key in oldData.keys():
        data[key] = pd.DataFrame(oldData[key])
        data[key]['measurement_time'] = pd.to_datetime(data[key]['measurement_time'])

    #get the data
    while not data_queue.empty():
        print data_queue.get()
        '''
        #get data and figure out which stream it is for
        streamID,mesDict= data_queue.get()
        mesDict['measurement_time'] = pd.to_datetime(mesDict['measurement_time']/float(2**32))
        for key in mesDict.keys():
            mesDict[key] = [mesDict[key]]
        data[streamID] = data[streamID].append(pd.DataFrame(mesDict),ignore_index=True).drop([0])
    for key in data.keys():
        #do averaging
        s = data[key]['measurement_time'].iloc[-1] - data[key]['measurement_time'].iloc[0]
        data[key] = data[key].resample("{}S".format(int(s.seconds/100)),on='measurement_time').mean()
        data[key].index.name = 'measurement_time'
        data[key].reset_index(inplace=True)
        data[key] = data[key].to_dict('series')
        '''
        """