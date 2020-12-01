#test the pandas reading csv
import pandas as pd

df = pd.read_csv('data0038.csv',names=['FORT','measurement_time'],index_col=None)
print df.head()
print df.to_dict('list')
