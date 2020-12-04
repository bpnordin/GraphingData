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
    dcc.Store(id='subscribeBoolean',
            data = False),

])
@app.callback(Output('subscribeBoolean','data'),Input('keyValues','modified_timestamp'),State('keyValues','data'),State('subscribeBoolean','data'))
def start_sub(n,streamList,subscribed):
    if streamList is None:
        #too early
        raise  dash.exceptions.PreventUpdate
    if subscribed == False:
        try:
            for stream in streamList:
                sub.subscribe(stream)
                logger.debug('subbed to {}'.format(stream))
            return True
        except Exception as e:
            logger.error(e)
    return False

@app.callback(Output('streamID','data'),
        Input('interval-component',"n_intervals"),[State('keyValues','data'),State('streamID','data')])
def get_streamID(n_intervals,subList,data):
    if data is None or data == []:
        data = []
        for stream in subList:
            data.append(sub.get_stream_filter(stream)) 
        logger.debug(data)
        return data
    else:
        return data

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/home':
        sub.unsubscribe_all()
        return serve_layout_home()
    elif pathname == '/apps/graph':
        return serve_layout_graph()
    else:
        return '404'

if __name__ == '__main__':
    sub = subscriber.Subscriber(config,logger)
    app.run_server(debug=True)
    sub.close()