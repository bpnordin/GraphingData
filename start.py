import dash
from plotly.subplots import make_subplots
import HybridSubscriber
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
'''
def get_data(stream_id,data,state,log,ctrl,data_queue=None):
    return data_queue.put((stream_id,data))
    '''

def serve_layout():
    return html.Div(
        html.Div([
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=2*1000, # in milliseconds
                n_intervals=0
            ),
            dcc.Slider(
                id='time-slider',
                min = 5,
                max = 600,
                step = 5,
                value = 60,
                marks={
        0: {'label': '5 seconds ', 'style': {'color': '#77b0b1'}},
        60: {'label': '60 seconds'},
        300: {'label': '5 minutes'},
        600: {'label': '10 minutes', 'style': {'color': '#f50'}}
    }
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
reader = origin_reader.Reader(config,logging.getLogger(__name__))

@app.callback(Output('live-update-graph','figure'),
              [Input('interval-component', 'n_intervals'),
              Input('time-slider','value')])
def updateGraph(n,time_value):
    global stream_test_list
    global DATA
    global reader
    ctx = dash.callback_context
    #we want to get the data from all subscribed streams from now
    #back until time_value
    current_time = int(time.time()) - time_value
    for stream in stream_test_list:
        try:
            DATA[stream] = reader.get_stream_raw_data(stream,start=current_time)
        except Exception as e:
            print e
            raise dash.exceptions.PreventUpdate

    epsilon = max(DATA['Hybrid_Beam_Balances']['X1'])*.001
    fig = make_subplots(rows = 2,cols = 1)
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Mux']['measurement_time'],
                             y=DATA['Hybrid_Mux']['FORT'],
                    mode='lines',
                    name='FORT'),
                    row = 1,col = 1
    )

    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=np.array(DATA['Hybrid_Beam_Balances']['X1'])+epsilon,
                    mode='lines',
                    name='X1'),
                    row = 2,col = 1
                    )
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=np.array(DATA['Hybrid_Beam_Balances']['Y1'])+epsilon*2,
                    mode='lines',
                    name='Y1'),
                    row = 2,col = 1
                    )
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=np.array(DATA['Hybrid_Beam_Balances']['Y2'])+epsilon*3,
                    mode='lines',
                    name='Y2'),
                    row = 2,col = 1
                    )
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=np.array(DATA['Hybrid_Beam_Balances']['X2'])+epsilon*4,
                    mode='lines',
                    name='X2'),
                    row = 2,col = 1
                    )
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=np.array(DATA['Hybrid_Beam_Balances']['Z1'])+epsilon*5,
                    mode='lines',
                    name='Z1'),
                    row = 2,col = 1
                    )
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Beam_Balances']['measurement_time'],
                             y=np.array(DATA['Hybrid_Beam_Balances']['Z2'])+epsilon*6,
                    mode='lines',
                    name='Z2'),
                    row = 2,col = 1
                    )
    fig.update_layout(uirevision = time_value)

    return fig


'''
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
'''

if __name__ == '__main__':
    print "running server"
    app.run_server(debug=True,use_reloader=False,host = '0.0.0.0')
    print "exiting"



