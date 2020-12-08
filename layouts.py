import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import configparser,logging
import reader,subscriber,reciever

configFile = "origin-server.cfg"
config = configparser.ConfigParser(inline_comment_prefixes=';')
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
    
    layout =  [
            dcc.Store(id='dataID',storage_type = 'memory',data=None),
            dcc.Store(id='keyValues'),
            dcc.Store(id='streamID'),
            dcc.Store(id='subTime'),
            dcc.Store(id='24hr-graph-store',data=None),
            dcc.Link(html.Button('Home', id='home_val', n_clicks=0),href = '/apps/home'),
            dcc.Interval(
                id='interval-component',
                interval=2*1000, # in milliseconds
                n_intervals=0,
                disabled = False
                ),
            html.Div(id = 'live-update-graph-container',
                children = []),
            daq.BooleanSwitch(id = '24hr-switch',
                color="#9B51E0",
                label="24hr Graph Toggle",
                labelPosition="top",
                on = False),
            dcc.Checklist(id='refresh-24hr',
                options=[{'label':'Refresh Data','value':'Refresh Data'}]),
            html.Div(id='hidden-container',
                style= {'display': 'block'},
                children =[
                    html.Div(id = '24hr-graph-container', children = [] )
                    ]
                )
        ]
    return html.Div(layout)

def get_sub_list():
    read = reader.Reader(config,logger)
    sub_list = sorted(read.known_streams) 
    read.close()
    return sub_list

def serve_layout_home():
    return html.Div([
        dcc.Store(id='keyValues',
                data = None),
        dcc.Store(id='subTime',
                data = None ),
        dcc.Link(html.Button('Submit', id='submit_val', n_clicks=0),href = '/apps/graph'),
        dcc.Checklist(id = "subCheckList",
        options=[{'label': i, 'value': i} for i in get_sub_list()])
    ])