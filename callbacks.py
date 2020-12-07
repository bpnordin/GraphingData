from dash.dependencies import Input, Output,State
import reader,subscriber
import dash
from app import app
import time
import configparser,logging
import pandas as pd
import multiprocessing
import os
import reciever
import pickle
from dash.exceptions import PreventUpdate

configFile = "origin-server.cfg"
config = configparser.ConfigParser(inline_comment_prefixes=';')
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
def storeKeys(n_clicks,subList):
    return subList
   


@app.callback(Output('dataID','data'),
              [Input('interval-component', 'n_intervals')],
              [State('keyValues','data'),State('dataID','data'),State('streamID','data'),
              State('subTime','data')])
def updateData(n,subList,oldData,streamID,time):
    data = {}

    if subList is None:
        return None

    if oldData is None:
        #get the data
        timeWindow = 300
        read = reader.Reader(config,logger) 
#        SUB_TIME = time.time()
        SUB_TIME = time
        logger.debug(time)
        
        data = {stream : pd.DataFrame(read.get_stream_raw_data(stream,start = SUB_TIME,
                stop = SUB_TIME-timeWindow)) for stream in subList}
        #save to file
        read.close()
        for stream in data:
            df = data[stream]
            df['measurement_time'] = df['measurement_time']/(2**32)
            data[stream] = df.to_json()
        return data

    else:
        #read the data from the sub file
        for stream in subList:
            #can store these values locally in a store probably
            file = 'data'+streamID[stream]+'.csv'
            try:
                df = pd.read_csv(file)
                #now convert to datetime object
                df['measurement_time'] = pd.to_datetime(df['measurement_time']/(2**32),unit='s')
                data[stream] = df
                #clear the data in that file
                os.remove(file)
            except Exception as e:
                logging.exception(e)

            length = len(data[stream].index)
            oldData[stream] = pd.read_json(oldData[stream]).iloc[length:]
            #now add the data together
            data[stream] = pd.concat([oldData[stream],data[stream]], axis=0, join='outer', ignore_index=True, keys=None,
                    levels=None, names=None, verify_integrity=False, copy=True)
            
            data[stream] = data[stream].to_json()
        return data

@app.callback(Output('live-update-graph','figure'),
                Input('dataID','modified_timestamp'),
                State('dataID','data'))
def graph(n,data):
    if data is None:
        raise PreventUpdate
    for stream in data:
        #graph
        df = pd.read_json(data[stream])
        meas = 'measurement_time'
        xx = df[meas]
        #graph 
        figure = {
            'data':[]
        }
        for var in df.columns:
            if var != meas:
                figure['data'].append({'x':xx,'y':df[var],'type':'line','name':var})
        return figure


