from origin.client import origin_reader,origin_subscriber
from dash.dependencies import Input, Output,State
import dash
from app import app
import time
import HybridSubscriber as hybrid_sub
import ConfigParser,logging
import pandas as pd
import multiprocessing
import os

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

def start():
    global subscriber
    subscriber = origin_subscriber.Subscriber(config,logger) 
lengthFile = 'length.txt'

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
    fileName = 'data'+str(stream_id)+'.csv'
    df = pd.DataFrame([data])
    if os.path.isfile(fileName):
        #make the header
        df.to_csv('data'+str(stream_id)+'.csv',mode = 'a',header=True,index=False)
    else:
        df.to_csv('data'+str(stream_id)+'.csv',mode = 'a',header=False,index=False)
    log.debug('appended data to file')
    return state

@app.callback(
    Output("keyValues",'data'),
    Input('submit_val',"n_clicks"),
    State("subCheckList","value")
)
def storeKeys(n_clicks,subList):
    global subscriber

    #now subscribe
    for sub in subList:
        subscriber.subscribe(sub,callback=subCallback)

    return subList
   


@app.callback(Output('dataID','data'),
              [Input('interval-component', 'n_intervals')],
              [State('keyValues','data'),State('dataID','data')])
def updateData(n,subList,oldData):
    global subscriber
    data = {}
    logger.debug('went into update data')


    if not isinstance(subscriber,origin_subscriber.Subscriber):
        return None

    if subList is None:
        return None

    if oldData is None:
        #get the data
        timeWindow = 300
        read = origin_reader.Reader(config,logger) 
        SUB_TIME = time.time()
            
        data = {stream : read.get_stream_raw_data(stream,start = SUB_TIME,
                stop = SUB_TIME-timeWindow) for stream in subList}
        logger.debug(data)
        #save to file
        read.close()
        return data
    else:
        #read the data from the sub file
        for stream in subList:
            #can store these values locally in a store probably
            streamId = subscriber.get_stream_filter(stream)
            file = 'data'+streamId+'.csv'
            data[stream] = pd.read_csv(file).to_dict('list')
            #clear the data in that file
            os.remove(file)
            logger.debug('read from subscriber file')
            #now add the data together
            '''
            data[stream] = pd.concat([oldData[stream],data[stream]], axis=0, join='outer', ignore_index=False, keys=None,
                    levels=None, names=None, verify_integrity=False, copy=True)
                    '''
        return data





    # put the data through filters
    # remove the old data    
   
        
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