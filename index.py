import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
import multiprocessing
import configparser
import logging
import reader,subscriber

from app import app
from layouts import serve_layout_graph,serve_layout_home
import callbacks

configFile = "origin-server.cfg"
config = configparser.ConfigParser(inline_comment_prefixes=';')
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


import os
import pandas as pd

def subCallback(stream_id,data,state,log,crtl):
    #store data locally in some file
    fileName = 'data'+str(stream_id)+'.csv'
    df = pd.DataFrame([data])
    if os.path.isfile(fileName):
        #make the header
        df.to_csv('data'+str(stream_id)+'.csv',mode = 'a',header=True,index=False)
    else:
        df.to_csv('data'+str(stream_id)+'.csv',mode = 'a',header=False,index=False)
    return state


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='keyValues'),
    dcc.Store(id='streamId',
            data = None,storage_type = 'session'),

])

@app.callback([Output('page-content', 'children'),Output('streamId','data')],
              Input('url', 'pathname'),
              State('keyValues','data'))
def display_page(pathname,stream_list):
    if pathname == '/apps/home':
        return serve_layout_home(),None
    elif pathname == '/apps/graph':
        #check to see if they have selected things to sub to
        #then sub here, make sure only once tho
        streamId = None
        try: 
            streamId = {}
            if stream_list is not None:
                for stream in stream_list:
                    subscriber.subscribe(stream,callback=subCallback)
                    streamId[stream] = subscriber.get_stream_filter(stream)

        except Exception as e:
            logger.debug(e)

        logger.debug(streamId)
        return serve_layout_graph(),streamId
    else:
        return '404',None

if __name__ == '__main__':
    subscriber = subscriber.Subscriber(config,logger)
    app.run_server(debug=True)
    subscriber.close()