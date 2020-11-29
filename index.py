import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import HybridSubscriber as hybrid_sub
import multiprocessing
import ConfigParser
import logging

from app import app
from layouts import serve_layout_graph,serve_layout_home
import callbacks
configfile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configfile)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/home':
         return serve_layout_home()
    elif pathname == '/apps/graph':
         return serve_layout_graph()
    else:
        return '404'

if __name__ == '__main__':
    
    app.run_server(debug=True)