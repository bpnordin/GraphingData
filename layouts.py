import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import readStream


def serve_layout_graph():
    
    return html.Div(
        html.Div([
            dcc.Store(id='dataID',
                data = None),
            dcc.Store(id='live'),
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
    read = readStream.readStream()
    sub_list =sorted(read.stream_list()['streams'].keys()) 
    read.close()
    print "closed"
    return sub_list

def serve_layout_home():
    return html.Div([
        dcc.Link(html.Button('Submit', id='submit-val', n_clicks=0),href = '/apps/graph'),
        dcc.Checklist(id = "subCheckList",
        options=[{'label': i, 'value': i} for i in get_sub_list()],
       # labelStyle={'display': 'inline-block'}
        )
    ])