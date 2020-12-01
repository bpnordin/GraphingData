import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import HybridSubscriber as hybrid_sub
import multiprocessing
import ConfigParser
import logging

from app import app
from layouts import serve_layout_graph,serve_layout_home
import callbacks

configFile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configFile)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('index.log')
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


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/home':
        callbacks.reset()
        return serve_layout_home()
    elif pathname == '/apps/graph':
        return serve_layout_graph()
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
    callbacks.subscriber.close()