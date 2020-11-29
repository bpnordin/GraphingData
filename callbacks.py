import readStream
import pandas as pd
from dash.dependencies import Input, Output,State
from app import app
import time

@app.callback(
    Output("dataID",'data'),
    Input('submit_val',"n_clicks"),
    State("subCheckList","value")
)
def initialData(n_clicks,keyList):
    print "triggered"
    if keyList is None:
        return None
    #this can throw an error if it cant connect to the server
    read = readStream.readStream()
    sub_dict = read.stream_list()['streams']
    stream_id_list = {}
    for key in keyList:
        stream_id_list[key] = (str(sub_dict[key]['id']).zfill(4))
    #get the data on start up
    startTimeSec = 300
    data = {stream_id_list[stream]: pd.DataFrame(read.read_streams(stream,start=time.time(),stop=time.time()-startTimeSec)) for stream in keyList}
    

    for key in data.keys():
        print key
        print data[key]
        if not data[key].empty:
            data[key]['measurement_time'] = pd.to_datetime(data[key]['measurement_time']/float(1**32),unit="s")
            s = data[key]['measurement_time'].iloc[-2] - data[key]['measurement_time'].iloc[0]
            data[key] = data[key].resample("{}S".format(int(s.seconds/99)),on='measurement_time').mean()
            data[key].index.name = 'measurement_time'
            data[key].reset_index(inplace=True)
            data[key] = data[key].to_dict('series')
        else:
            data[key] = None
    read.close()

    return data