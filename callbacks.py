from dash.dependencies import Input, Output,State
import numpy as np
import dash_html_components as html
import dash_core_components as dcc
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
import re

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

def reset():
    #delete all of the csv data
    fileList = os.listdir()
    r = re.compile('data\w*.csv')
    csvList = list(filter(r.match, fileList))
    map(os.remove,csvList)



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
def updateData(n,subList,oldData,streamID,subTime):
    data = {}

    if subList is None or subTime is None:
        raise PreventUpdate

    if oldData is None:
        #get the data
        timeWindow = 300
        read = reader.Reader(config,logger) 
        SUB_TIME = time.time()
#        SUB_TIME = subTime
        
        data = {stream : pd.DataFrame(read.get_stream_raw_data(stream,start = SUB_TIME,
                stop = SUB_TIME-timeWindow)) for stream in subList}
        #save to file
        read.close()
        
        for stream in data:
            if not data[stream].empty:
                df = data[stream]
                df['measurement_time'] = df['measurement_time']/(2**32)
                data[stream] = df.to_json()
        return data

    else:
        #read the data from the sub file
        for stream in subList:
            file = 'data'+streamID[stream]+'.csv'
            try:
                try:
                    df = pd.read_csv(file)
                    os.remove(file)
                    #now convert to datetime object
                    if not df.empty:

                        df['measurement_time'] = pd.to_datetime(df['measurement_time']/(2**32),unit='s')
                        data[stream] = df
                    #clear the data in that file
                    length = len(data[stream].index)
                except Exception as e:
                    logger.exception(e)

                oldData[stream] = pd.read_json(oldData[stream]).iloc[length:]
                #now add the data together
                data[stream] = pd.concat([oldData[stream],data[stream]], axis=0, join='outer', ignore_index=True, keys=None,
                        levels=None, names=None, verify_integrity=False, copy=True)
                
                data[stream] = data[stream].to_json()
            except KeyError:
                logger.exception("The data csv got messed up")
                reset()

        return data



@app.callback(Output('live-update-graph-container','children'),
                Input('dataID','modified_timestamp'),
                State('dataID','data'))
def graph(n,data):
    if data is None:
        raise PreventUpdate
    graphs = []
    for stream in data:
        #graph
        df = pd.read_json(data[stream])
        meas = 'measurement_time'
        xx = df[meas]
        #graph 
        figure = {
            'data':[],
            'layout':{'title':'Graph of {} '.format(stream)}
        }
        for var in df.columns:
            if var != meas:
                figure['data'].append({'x':xx,'y':df[var],'type':'line','name':var})
        graphs.append(dcc.Graph(
            id='graph-{}'.format(stream),
            figure = figure))
        return html.Div(graphs)

@app.callback(Output('24hr-graph-container','style'),
            Input('24hr-switch','on'))
def show_graph(onBoolean):
    if onBoolean:
        return {'display': 'block'}
    else:
        return {'display':'none'}

@app.callback(Output('24hr-graph-container','children'),
    Input('24hr-switch','on'),
    State('keyValues','data'))
def graph_average(onBoolean,subList):
    if onBoolean:
        #start averaging over 24hrs
        start = time.time()
        stop = time.time()-60*60*24 #24hrs 
        window = 60*60
        read = reader.Reader(config,logger)
        data = {}
        figure = {}
        for stream in subList:
            data[stream] = []
            for count,t in enumerate(np.arange(start,stop,window)):
                start = start - window
                stop = stop - window
                val = read.get_stream_stat_data(stream,start=start,stop=stop)
                data[stream].append(val)

        read.close()

    else:
        raise PreventUpdate




