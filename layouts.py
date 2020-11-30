import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from origin.client import origin_reader
import ConfigParser,logging

configFile = "origin-server.cfg"
config = ConfigParser.ConfigParser()
config.read(configFile)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('callbacks.log')
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

def serve_layout_graph():
    
    return html.Div(
        html.Div([
            dcc.Store(id='dataID',
            ),dcc.Store(id='keyValues',
                data = None,storage_type = 'session'),
            dcc.Store(id='live'),
            html.Button('Graph', id='graph_val', n_clicks=0),
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=10*1000, # in milliseconds
                n_intervals=0,
                disabled = False
            ),
            daq.BooleanSwitch(id = '24hr-switch',on = False),
            html.Div(id = '24hr-graph-container',
                children = [dcc.Graph(id='24hr-graph')]),
        ])
    )

def get_sub_list():
    read = origin_reader.Reader(config,logger)
    sub_list =sorted(read.known_streams) 
    read.close()
    return sub_list

def serve_layout_home():
    return html.Div([
        dcc.Store(id='keyValues',
                data = None,storage_type = 'session'),
        dcc.Link(html.Button('Submit', id='submit_val', n_clicks=0),href = '/apps/graph'),
        dcc.Checklist(id = "subCheckList",
        options=[{'label': i, 'value': i} for i in get_sub_list()],
       # labelStyle={'display': 'inline-block'}
        )
    ])