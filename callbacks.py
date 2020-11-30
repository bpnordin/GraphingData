from origin.client import origin_reader,origin_subscriber
from dash.dependencies import Input, Output,State
import dash
from app import app
import time
import HybridSubscriber as hybrid_sub
import ConfigParser,logging
import pandas as pd

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

@app.callback(
    Output("keyValues",'data'),
    Input('submit_val',"n_clicks"),
    State("subCheckList","value")
)
def storeKeys(n_clicks,keyList):
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
        t = time.time()
        data = {stream : pd.DataFrame(read.get_stream_raw_data(stream,start = t,stop = t-timeWindow))
            for stream in subList}
        
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
        read.close()

        return data
    print data_queue
    return "test"
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