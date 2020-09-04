import dash
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

from origin.client import server, random_data, origin_subscriber
import ConfigParser
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div(
    html.Div([
        html.H4('Test for python performance'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=2*1000, # in milliseconds
            n_intervals=0
        )
    ])
)
configfile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configfile)

sub = origin_subscriber.Subscriber(config,logging.getLogger(__name__))
'''
context = zmq.Context()
socket = context.socket(zmq.SUB)
host = config.get('Server','ip')
port = config.getint('Server','read_port')
socket.connect("tcp://%s:%s" % (host,port))
'''
stream_test_list = ["Hybrid_Mux","Hybrid_Beam_Balances"]

@app.callback(Output('live-update-graph','figure'),
              [Input('interval-component', 'n_intervals')])
def updateGraph(n):
    #create the plots
    fig = plotly.tools.make_subplots(rows = 7,cols = 1,vertical_spacing = .05)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    #get the data
    data = [None,None]
    sub.subscribe("Hybrid_Mux")
    '''
    for index,stream in enumerate(stream_test_list):
        request_obj = { 'stream': stream, 'raw': True } 
        socket.send(json.dumps(request_obj))
        response = socket.recv()
        data[index] = json.loads(response)

    fig.append_trace({
        'x' : data[0][1]['measurement_time'],
        'y' : data[0][1]['FORT'],
        'name' : "FORT"},1,1)
    fig.append_trace({
        'x' : data[1][1]['measurement_time'],
        'y' : data[1][1]['X2'],
        'name' : "X2"},2,1)
    fig.append_trace({
        'x' : data[1][1]['measurement_time'],
        'y' : data[1][1]['X1'],
        'name' : "X1"},2,1)
    fig.append_trace({
        'x' : data[1][1]['measurement_time'],
        'y' : data[1][1]['Y1'],
        'name' : "Y1"},2,1)
    fig.append_trace({
        'x' : data[1][1]['measurement_time'],
        'y' : data[1][1]['Y2'],
        'name' : "Y2"},2,1)
    fig.append_trace({
        'x' : data[1][1]['measurement_time'],
        'y' : data[1][1]['Z2'],
        'name' : "Z2"},2,1)
    fig.append_trace({
        'x' : data[1][1]['measurement_time'],
        'y' : data[1][1]['Z1'],
        'name' : "Z1"},2,1)
    '''
    time.sleep(.1)
    sub.close()
    return fig
if __name__ == '__main__':
    app.run_server(debug=True,host = '0.0.0.0')

