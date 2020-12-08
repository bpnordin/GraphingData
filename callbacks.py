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
    

    if subList is None or subTime is None or len(subList) == 0:
        raise PreventUpdate

    if oldData is None or n == 1:
        #get the data
        timeWindow = 300
        logger.debug("reading the streams") 
        read = reader.Reader(config,logger) 
        SUB_TIME = time.time()
#        SUB_TIME = subTime
        
        for stream in subList:
            data[stream] = pd.DataFrame(read.get_stream_raw_data(stream,start = SUB_TIME,
                stop = SUB_TIME-timeWindow))

        #save to file
        read.close()
        
        for stream in data.keys():
            df = data[stream]
            df['measurement_time'] = df['measurement_time']/(2**32)
            data[stream] = df.to_json()

        return data

    else:
        #read the data from the sub file
        for stream in subList:
            #this is the structure of the csv file system
            #that the subscriber is writing to
            fileName = 'data'+streamID[stream]+'.csv'
            #if the user is on this page without subbing
            #there will be no new data
            try:
                df = pd.read_csv(fileName)
            except pd.errors.EmptyDataError:
                logger.exception("No data to get, probably not subscribed to any stream")
                raise PreventUpdate
            #now overwrite the old data
            open(fileName, 'w').close()

            #now convert to datetime object
            if not df.empty:
                df['measurement_time'] = pd.to_datetime(df['measurement_time']/(2**32),unit='s')
                data[stream] = df

            #get the amount of data we just got
            length = len(data[stream].index)
            #and delete that amount of old data
            oldData[stream] = pd.read_json(oldData[stream]).iloc[length:]
            #now add the data together
            data[stream] = pd.concat([oldData[stream],data[stream]], axis=0, join='outer', ignore_index=True, keys=None,
                    levels=None, names=None, verify_integrity=False, copy=True)
            #and pickle the data 
            data[stream] = data[stream].to_json()

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

@app.callback(Output('hidden-container','style'),
            Input('24hr-switch','on'))
def show_graph(onBoolean):
    if onBoolean:
        return {'display': 'block'}
    else:
        return {'display':'none'}

@app.callback([Output('24hr-loading','children'),Output('24hr-graph-store','data')],
    Input('24hr-switch','on'),
   [ State('keyValues','data'),State('24hr-graph-store','data'),State('refresh-24hr','value')])
def graph_average(onBoolean,subList,graphData,refresh):
    
    if subList is None:
        logger.debug("cant graph 24hr b/c there are no streams selected")
        raise PreventUpdate

    logger.debug(refresh)

    if graphData is not None and refresh is None:
        return graphData,graphData
    if onBoolean:
        graphs = []
        #start averaging over 24hrs
        window = 60*60
        start = time.time()
        stop = time.time()-window 
        read = reader.Reader(config,logger)
        for stream in subList:
            figure = {
                'data':[],
                'layout':{'title':'Graph of {} averaged over 24hrs'.format(stream)}
            }
            #get the averages
            data = []
            logger.debug("starting read for stream {}".format(stream))
            for i in range(24):
                start = start - window
                stop = stop - window
                data.append(read.get_stream_stat_data(stream,start=start,stop=stop))
                logger.debug("done with read {}/{} for stream {}".format(i+1,24,stream))
            #now format the data
            xx = []
            yy = {}
            for val in data:
                xx.append(pd.to_datetime(val['measurement_time']['start']/(2**32),unit='s'))
                for keys in val:
                    if keys != 'measurement_time':
                        if keys not in yy.keys():
                            yy[keys] = []
                        yy[keys].append(val[keys]['average'])

            for key in yy:
                figure['data'].append({'x':xx,'y':yy[key],'type':'scatter','name':key})

            graphs.append(dcc.Graph(
                id='graph-{}'.format(stream),
                figure = figure))
        read.close()
        return html.Div(graphs),html.Div(graphs)
        

    else:
        raise PreventUpdate




