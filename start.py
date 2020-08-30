import dash
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
import pandas as pd
import random as rand

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
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-graph','figure'),
              [Input('interval-component', 'n_intervals')])
def updateGraph(n):
    #get the data
    data = np.linspace(0,n,100)
    #create the plots
    fig = plotly.tools.make_subplots(rows = 3,cols = 1,vertical_spacing = .05)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    fig.append_trace({
        'x' : data,
        'y' : np.sin(data),
        'name' : "sin wave"},1,1)

    fig.append_trace({
        'x' : data,
        'y' : np.cos(data),
        'name' : "cos wave"},2,1)

    fig.append_trace({
        'x' : data,
        'y' : np.exp(data),
        'name' : "exp wave"},3,1)
    return fig
if __name__ == '__main__':
    app.run_server(debug=True,host = '0.0.0.0')

