import dash
import datetime
import plotly.graph_objects as go
import multiprocessing
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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

def serve_layout():
    return html.Div(
        html.Div([
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=.5*1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Slider(
                id='time-slider',
                min = 5,
                max = 600,
                step = 5,
                value = 150,
            ),html.P(id='placeholder')
        ])
    )

app.layout = serve_layout()
stream_test_list = ["Hybrid_Mux","Hybrid_Beam_Balances"]
DATA = {}
COUNT = {}
for stream in stream_test_list:
    DATA[stream] = {'measurement_time':[]}
    COUNT[stream] = 0
START = 0

@app.callback(Output('live-update-graph','figure'),
              [Input('interval-component', 'n_intervals')])
def updateGraph(n):
    #create the plots
    global DATA
    global COUNT
    tempStorage = {}

    start = 0
    #get the data
    while not data_queue.empty():
        #get data and figure out which stream it is for
        streamId,measurement = data_queue.get()
#        measurement['measurement_time'] = change to normal time
        if streamId == '0038':
            #fort

            stream = 'Hybrid_Mux'
            length = len(DATA[stream]['measurement_time'])
            if COUNT[stream] >= length:
                COUNT[stream] = 0
            tempStorage[stream]['measurement_time'][COUNT[stream]] = measurement['measurement_time']
            tempStorage[stream]['FORT'][COUNT[stream]] = measurement['FORT']
            COUNT[stream] = COUNT[stream] + 1
            start = start + 1
        elif streamId == '0013':
            #MOT beam balances
            stream = 'Hybrid_Beam_Balances'
            length = len(DATA[stream]['measurement_time'])
            if COUNT[stream] >= length:
                COUNT[stream] = 0
            DATA[stream]['measurement_time'][length -1- COUNT[stream]] = measurement['measurement_time']
            DATA[stream]['X1'][length -1- COUNT[stream]] = measurement['X1']
            DATA[stream]['X2'][length - 1-COUNT[stream]] = measurement['X2']
            DATA[stream]['Y2'][length - 1-COUNT[stream]] = measurement['Y2']
            DATA[stream]['Y1'][length - 1-COUNT[stream]] = measurement['Y1']
            DATA[stream]['Z1'][length - 1-COUNT[stream]] = measurement['Z1']
            DATA[stream]['Z2'][length - 1-COUNT[stream]] = measurement['Z2']
            COUNT[stream] = COUNT[stream] + 1
            start = start + 1

    '''
        if len(DATA['measurement_time']) < MAXSIZE:
            mes = data_queue.get()
            DATA['measurement_time'].append(mes['measurement_time'])
            DATA['FORT'].append(mes['FORT'])
            START = DATA['measurement_time'][0]
        elif COUNT < MAXSIZE:
            #start replacing earlier measurments
            mes = data_queue.get()
            DATA['measurement_time'][COUNT] = mes['measurement_time']
            DATA['FORT'][COUNT] =mes['FORT']
            COUNT = COUNT + 1
        else:
            COUNT = 0
            #get the start of where we overwrite
            START = DATA['measurement_time'][0]


    if COUNT > 0:
        fig.add_trace(go.Scatter(x=[i-DATA['measurement_time'][-1]+START for i in DATA['measurement_time'][0:COUNT]], y=DATA['FORT'][0:COUNT],
                        mode='lines',
                        name='lines-overwrite'))
        fig.add_trace(go.Scatter(x=np.full(2,DATA['measurement_time'][COUNT-1]-DATA['measurement_time'][-1]+START ),
                                 y=[min(DATA['FORT']),max(DATA['FORT'])],
                        mode='lines',
                        name='verticle-line'))
    '''
    fig = go.Figure()
    '''
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Mux']['measurement_time'],
                             y=DATA['Hybrid_Mux']['FORT'],
                    mode='lines',
                    name='FORT'))
'''

    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=DATA['Hybrid_Beam_Balances']['X1'],
                    mode='lines',
                    name='X1'))
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=DATA['Hybrid_Beam_Balances']['Y1'],
                    mode='lines',
                    name='Y1'))
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=DATA['Hybrid_Beam_Balances']['Y2'],
                    mode='lines',
                    name='Y2'))
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=DATA['Hybrid_Beam_Balances']['X2'],
                    mode='lines',
                    name='X2'))
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=DATA['Hybrid_Beam_Balances']['Z1'],
                    mode='lines',
                    name='Z1'))
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=DATA['Hybrid_Beam_Balances']['Z2'],
                    mode='lines',
                    name='Z2'))

    return fig



@app.callback(Output('placeholder','children'),
              [Input('time-slider','value')])
def updateTimeLength(time_value):
    global stream_test_list
    global DATA
    global COUNT
    reader = origin_reader.Reader(config,logging.getLogger(__name__))
    #we want to get the data from all subscribed streams from now
    #back until time_value
    current_time = int(time.time()) - time_value
    for stream in stream_test_list:
        DATA[stream] = reader.get_stream_raw_data(stream,start=current_time)
        print DATA['Hybrid_Beam_Balances'].keys()
        COUNT[stream] = 0
    reader.close()
    return None

data_queue = None

if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    sub = origin_subscriber.Subscriber(config,logging.getLogger(__name__),
                                       data_queue)
    for stream in stream_test_list:
        sub.subscribe(stream)
    print "running server"
    app.run_server(debug=True,use_reloader=False)
    print "exiting"
    sub.close()



