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
from dash.dependencies import Input, Output, State
import logging
import plotly
import sys
import os
import random
import time
import zmq
import json

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
def initialData():

    global stream_test_list
    global stream_id_list
    data = {}
    timeValue = 60
    read = readStream.readStream()
    #get the data on start up
    print "getting data"
    for stream in stream_test_list:
        data[stream_id_list[stream]] =read.read_streams(stream,stop = time.time()-timeValue) 
        time.sleep(1)
        for index,unixTime in enumerate(data[stream_id_list[stream]]['measurement_time']):
            data[stream_id_list[stream]]['measurement_time'][index] = datetime.datetime.fromtimestamp(float(unixTime)/float(2**32))
    read.close()
    print "got data and closed read"
    return data

def serve_layout():
    
    return html.Div(
        html.Div([
            dcc.Store(id='dataID',
                data = initialData()),
            dcc.Store(id='live'),
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=1*1000, # in milliseconds
                n_intervals=0,
                disabled = False
            ),
            dcc.Interval(
                id='disableInterval',
                interval=1*1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Slider(
                id='time-slider',
                min = 5,
                max = 90,
                step = 1,
                value = 45,
            )
        ])
    )


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
              [Input('interval-component', 'n_intervals'),
              Input('time-slider','value')],
              [State('dataID','data')])
def updateData(n,timeValue,oldData):
    global data_queue
    global stream_test_list
    global stream_id_list
    ctx = dash.callback_context
    data = {}
    if oldData is None or "time-slider" in ctx.triggered[0]["prop_id"]:

        read = readStream.readStream()
        #get the data on start up
        print "getting data"
        for stream in stream_test_list:
            data[stream_id_list[stream]] =read.read_streams(stream,stop = time.time()-timeValue) 
            for index,unixTime in enumerate(data[stream_id_list[stream]]['measurement_time']):
                data[stream_id_list[stream]]['measurement_time'][index] = datetime.datetime.fromtimestamp(float(unixTime)/float(2**32))
        read.close()
        print "got data and closed read"
        return data
    else:
        data = oldData
    #get the data
    while not data_queue.empty():
        #get data and figure out which stream it is for
        streamID,mesDict= data_queue.get()
        for key in mesDict.keys():
            if key == 'measurement_time':
                date = datetime.datetime.fromtimestamp(float(mesDict['measurement_time'])/float(2**32))
                data[streamID][key].append(date)
                data[streamID][key].pop(0)
            else:
                data[streamID][key].append(mesDict[key])
                data[streamID][key].pop(0)
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
    sub = hybrid_sub.HybridSubscriber(config,logging.getLogger(__name__),
                                       data_queue, 
                    sub_list = sub)
    for stream in stream_test_list:
        stream_id_list[stream] = sub.get_stream_filter(stream)
    print "running server"
    app.layout = serve_layout()
    app.run_server(debug=True,use_reloader=False,host = '0.0.0.0')
    print "exiting"
    sub.close()



