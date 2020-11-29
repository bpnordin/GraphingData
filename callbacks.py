import readStream
import pandas as pd
from dash.dependencies import Input, Output,State
import dash
from app import app
import time
import HybridSubscriber as hybrid_sub
import multiprocessing
import ConfigParser
import logging

configfile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configfile)

data_queue = multiprocessing.Queue()

sub = hybrid_sub.HybridSubscriber(config,logging.getLogger("__sub__"),
                                    data_queue,
                sub_list = None)

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
def updateData(n,keyList,oldData):
    ctx = dash.callback_context
    global data_queue
    data = {}

    if oldData is None:
        #get the data
        if keyList is None:
            return None
        #this can throw an error if it cant connect to the server
        read = readStream.readStream()
        sub_dict = read.stream_list()['streams']
        stream_id_list = {}
        for key in keyList:
            stream_id_list[key] = (str(sub_dict[key]['id']).zfill(4))
        #get the data on start up
        startTimeSec = 300
        data = {stream_id_list[stream]: pd.DataFrame(read.read_streams(stream,start=time.time(),stop=time.time()-startTimeSec)) for stream in keyList}
        

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