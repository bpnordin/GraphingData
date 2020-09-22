import dash
import HybridSubscriber as hybrid_sub
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
data_queue = None
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
    global data_queue
    tempStorage = {}

    start = 0
    #get the data
    while not data_queue.empty():
        #get data and figure out which stream it is for
        data =  data_queue.get()
        print data
#        measurement['measurement_time'] = change to normal time
        if streamId == '0038':
            #fort
            pass
        elif streamId == '0013':
            #MOT beam balances
            pass
    fig = go.Figure()
    '''
    fig.add_trace(go.Scatter(x=DATA['Hybrid_Mux']['measurement_time'],
                             y=DATA['Hybrid_Mux']['FORT'],
                    mode='lines',
                    name='FORT'))

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

'''
    return fig





if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    sub = hybrid_sub.HybridSubscriber(config,logging.getLogger(__name__),
                                       data_queue)
    print "running server"
    app.run_server(debug=True,use_reloader=False)
    print "exiting"
    sub.close()



