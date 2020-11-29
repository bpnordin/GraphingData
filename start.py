import dash
from plotly.subplots import make_subplots
import readStream
from dash.exceptions import PreventUpdate
import HybridSubscriber as hybrid_sub
import datetime
import plotly.graph_objects as go
import multiprocessing
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import logging
import plotly
import sys
import os
import random
import time
import zmq
import json
import pandas as pd

logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)
# first find ourself

fullBinPath  = os.path.abspath(os.getcwd() + "/" + sys.argv[0])
fullBasePath = os.path.dirname(os.path.dirname(fullBinPath))
fullLibPath  = os.path.join(fullBasePath, "lib")
fullCfgPath  = os.path.join(fullBasePath, "config")
sys.path.append(fullLibPath)

from origin.client import server, random_data, origin_subscriber,origin_reader

import ConfigParser
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
configfile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configfile)
stream_test_list = ["Hybrid_Mux","Hybrid_Beam_Balances"]
stream_id_list = {}

def initialData(startTimeSec = 300):

    global stream_test_list
    global stream_id_list
    #this can throw an error if it cant connect to the server
    read = readStream.readStream()
    #get the data on start up
    data = {stream_id_list[stream]: pd.DataFrame(read.read_streams(stream,start=time.time(),stop=time.time()-startTimeSec)) for stream in stream_test_list}

    for key in data.keys():
        data[key]['measurement_time'] = pd.to_datetime(data[key]['measurement_time']/float(2**32),unit="s")
        s = data[key]['measurement_time'].iloc[-1] - data[key]['measurement_time'].iloc[0]
        data[key] = data[key].resample("{}S".format(int(s.seconds/100)),on='measurement_time').mean()
        data[key].index.name = 'measurement_time'
        data[key].reset_index(inplace=True)
        data[key] = data[key].to_dict('series')

    read.close()

    return data



@app.callback([Output('24hr-graph','figure'),Output('24hr-graph-container','style')],[Input('24hr-switch','on')])
def overviewGraph(value,windowSize = 1000):

    #24 hour graph
    global stream_test_list
    global stream_id_list
    data = {}
    if value:
        read = readStream.readStream()
        for stream in stream_test_list:
            data[stream_id_list[stream]] =read.read_streams(stream,start = time.time(),stop = time.time()-24*100) 
            for index,unixTime in enumerate(data[stream_id_list[stream]]['measurement_time']):
                data[stream_id_list[stream]]['measurement_time'][index] = datetime.datetime.fromtimestamp(float(unixTime)/float(2**32))
        read.close()
        df = pd.DataFrame(data)
        print df['0038']['FORT'].rolling(window = windowSize).mean()
        print df['0013']['measurement_time']
        #plotData = df.iloc[0].rolling(window = windowSize).mean()


def serve_layout_graph():
    
    return html.Div(
        html.Div([
            dcc.Store(id='dataID',
                data = initialData()),
            dcc.Store(id='live'),
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=10*1000, # in milliseconds
                n_intervals=0,
                disabled = False
            ),
            dcc.Interval(
                id='disableInterval',
                interval=9*1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Slider(
                id='time-slider',
                min = 1,
                max = 7200,
                step = 1,
                value = 300,
                marks = {
                    300: "5 minutes",
                    600: "10 minutes",
                    3600: "1 hour",
                    1800: "30 minutes",
                    7200: "2 hours"
                }
            ),
            daq.BooleanSwitch(id = '24hr-switch',on = False),
            html.Div(id = '24hr-graph-container',
                children = [dcc.Graph(id='24hr-graph')]),
        ])
    )

def serve_layout_home():
    print "test"
    return html.Div([
        dcc.Checklist(
        options=[{'label': i, 'value': i} for i in sub_list ],
        ),
        dcc.Button('Submit', id='submit-val', n_clicks=0)
    ])


@app.callback([Output('interval-component','disabled'),Output('live','data')],
              [Input('time-slider','value'),
               Input('disableInterval', 'n_intervals')],
              [State('interval-component','disabled'),State('interval-component','n_intervals'),
               State('live','data')])
def stopInterval(value,n,boolean,nMain,dataLive):
    ctx = dash.callback_context
    if "time-slider" in ctx.triggered[0]['prop_id']:
        print ctx.triggered
        #then we should turn off auto updates
        print "disabledi unitl {} is {}".format(n,n+10)
        return True,n+10
    elif boolean == True:
        print n
        if n == dataLive:
            print "enabled"
            return False,None
        return True,dataLive
    else:
        return False,None


@app.callback(Output('dataID','data'),
              [Input('interval-component', 'n_intervals')],
              [State('dataID','data')])
def updateData(n,timeValue,oldData):
    global data_queue
    global stream_test_list
    global stream_id_list
    ctx = dash.callback_context
    data = {}

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
    return data



@app.callback(Output('live-update-graph','figure'),
              [Input('dataID', 'modified_timestamp')],
              [State('dataID','data')])
def updateGraph(ts,data):
    #create the plots
    fig = make_subplots(rows=2, cols=1)
    if data is None:
        raise PreventUpdate
    fig.add_trace(go.Scatter(x=data['0038']['measurement_time'],
                             y =data['0038']['FORT'],
                             mode = 'lines',
                             name = 'FORT'),
                             row=1,col=1)
    fig.add_trace(go.Scatter(x=data['0013']['measurement_time'],
                             y=data['0013']['X1'],
                    mode='lines',
                    name='X1'),
                    row=2,col=1)
    fig.add_trace(go.Scatter(x=data['0013']['measurement_time'],
                             y=data['0013']['Y1'],
                    mode='lines',
                    name='Y1'),
                    row=2,col=1)
    fig.add_trace(go.Scatter(x=data['0013']['measurement_time'],
                             y=data['0013']['Y2'],
                    mode='lines',
                    name='Y2'),
                    row=2,col=1)
    fig.add_trace(go.Scatter(x=data['0013']['measurement_time'],
                             y=data['0013']['X2'],
                    mode='lines',
                    name='X2'),
                    row=2,col=1)
    fig.add_trace(go.Scatter(x=data['0013']['measurement_time'],
                             y=data['0013']['Z1'],
                    mode='lines',
                    name='Z1'),
                    row=2,col=1)
    fig.add_trace(go.Scatter(x=data['0013']['measurement_time'],
                             y=data['0013']['Z2'],
                    mode='lines',
                    name='Z2'),
                    row=2,col=1)

    return fig





if __name__ == '__main__':
    data_queue = multiprocessing.Queue()

    sub = ['0038'.decode('ascii'),'0013'.decode('ascii')]
    sub = hybrid_sub.HybridSubscriber(config,logging.getLogger("__sub__"),
                                       data_queue,
                    sub_list = sub)
    for stream in stream_test_list:
        stream_id_list[stream] = sub.get_stream_filter(stream)

    print "getting class"
    read = readStream.readStream()
    print "getting list"
    sub_list =  read.stream_list()

    print "running server"
    app.layout = serve_layout_home()
    app.run_server(debug=True,use_reloader=False)
    print "exiting"




