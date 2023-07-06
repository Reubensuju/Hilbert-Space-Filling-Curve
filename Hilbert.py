import base64
import datetime
import io
import plotly.graph_objs as go
import plotly.express as px
import cufflinks as cf
import csv

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from Hilbert_transform import*
from Hilbert_Mapping import*

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd',
        '#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.layout = html.Div(children=[
    html.H1(
            children='PCP & SPLOM 2',
            style={
                'textAlign': 'center'
            }
        ),

    html.Div(dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '30%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    )),

    html.Div(children = [
        html.Label('Value of K'),
        dcc.Input(
            id = 'value-k',
            value = 5,
            type = 'number')],
        style={
            'margin': '10px'
        }),

    html.Div(children = [
        html.Label('Order'),
        dcc.Slider(
            id = 'value-order',
            min=1,
            max=10,
            step = 1,
            value = 3,
            marks = {1:{'label':'1'},2:{'label':'2'},3:{'label':'3'},4:{'label':'4'},5:{'label':'5'},
                    6:{'label':'6'},7:{'label':'7'},8:{'label':'8'},9:{'label':'9'},10:{'label':'10'}
            })],
        style={
            'width': '30%',
            'margin': '10px'
        }),

    html.Div(children = [
        html.Label('Columns'),
        dcc.Dropdown(
            id = 'Select-Column',
            multi=True)],
        style={
            'width': '30%',
            'margin': '10px'
        }),


    html.Div(dcc.Graph(id='PCP'),style={'display': 'inline-block'}),
    html.Div(dcc.Graph(id='SPLOM'),style={'display': 'inline-block'}),
    html.Div(id='output-data-upload')
])



def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    

    return df


''' This function loads data from the file selected on button input and extracts data into two lists: class and datapoints'''
def get_data(contents,filename,k,order):
    global labels,data
    
    with open(filename,'r') as f:
        reader = csv.reader(f,delimiter = ',')
        file_data = [(column[1:]) for column in reader]
        
    labels = []   #class values
    data = []     #data points (D1,D2,D3,D4....)
    for x in file_data:
        if 'CLASS' not in x:
            labels.append(x[0])
#            data.append([float(x[i]) for i in range(1,len(file_data[0]))])
            data.append([float(x[i]) for i in range(1,5)])   #7 works for data_subset but restrict to 6 for plot
    
    #color mapping - mapping class labels with colors
    unique_classes = set(labels)
    g = []
    for i in unique_classes:
        g.append(i)
    col_dict = {}
    for i in g:
        col_dict[i] = colors[g.index(i)]
    color_map = []
    for i in labels:
        color_map.append(col_dict[i])
    
    m = k   #number of hilbert indices
    data_transform,max_order = Hilbert_data_transform(deepcopy(data),order, m)
    
    #creating the dictionary required for the dataframe
    names = ['H'+str(i) for i in range(m)]
    d = {}
    for i in range(m):
        q = []
        for j in range(len(data_transform)):
            q.append(data_transform[j][i])
        d[names[i]] = q
    d['class'] = labels
    d['colors'] = color_map
    d['selected'] = 0

    #create the dataframe
    global df,columns
    df=pd.DataFrame(d)
    df=df.copy()
    print(df)
    dat=df.to_dict('rows')
    columns=[{'name': i, 'id': i} for i in df.columns]

    
    return df,dat,columns
    

''' This function creates a pandas dataframe after performing hilbert transform on the intial dataset. The initial NxD dataset will be reduced to Nxm dataset, where m is the number of hilbert curves. The dataframe makes it easier to use with other bokeh widgets and plots'''
def create_dataframe(k,order):
    global x,y,controls,layout,labels,data,max_order, col_dict

    
     
    #color mapping - mapping class labels with colors
    unique_classes = set(labels)
    g = []
    for i in unique_classes:
        g.append(i)
    col_dict = {}
    for i in g:
        col_dict[i] = colors[g.index(i)]
    color_map = []
    for i in labels:
        color_map.append(col_dict[i])
    
    m = k   #number of hilbert indices
    data_transform,max_order = Hilbert_data_transform(deepcopy(data),order, m)
    
    #creating the dictionary required for the dataframe
    names = ['H'+str(i) for i in range(m)]
    d = {}
    for i in range(m):
        q = []
        for j in range(len(data_transform)):
            q.append(data_transform[j][i])
        d[names[i]] = q
    d['class'] = labels
    d['colors'] = color_map

    #create the dataframe
    global df,columns
    df=pd.DataFrame(d)
    df=df.copy()
    print(df)
    dat=df.to_dict('rows')
    columns=[{'name': i, 'id': i} for i in df.columns]

    return df,dat,columns
    

   

@app.callback(
            [Output('Select-Column', 'options'),
            Output('Select-Column', 'value')],
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('value-k', 'value'),
                Input('value-order', 'value')
            ])
def update_Dropdown(contents, filename,k,order):
    
    options=[]
    value=[]
    if contents:
        contents = contents[0]
        filename = filename[0]
        df,dat,col = get_data(contents,filename,k,order)
        df = df.select_dtypes(['number'])
        options=[{'label':i, 'value':i}for i in df.columns]
        value = [df.columns[0],df.columns[1]]

    return options,value



@app.callback(Output('PCP', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('value-k', 'value'),
                Input('value-order', 'value'),
                Input('Select-Column', 'value')
            ])
def update_graph_PCP(contents, filename,k,order,column):
    fig = {
        'layout': go.Layout(
            width= 800,
            height= 600
            )
    }

    if contents:
        contents = contents[0]
        filename = filename[0]
        df,dat,col = get_data(contents,filename,k,order)
        for i in df.columns:
            if i not in column:
                df=df.drop(columns=i)
        fig =px.parallel_coordinates(df, labels=[{i:i}for i in column])


    return fig


@app.callback(Output('SPLOM', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('value-k', 'value'),
                Input('value-order', 'value'),
                Input('Select-Column', 'value')
            ])
def update_graph_SPLOM(contents, filename,k,order,column):
    fig = {
        'layout': go.Layout(
            dragmode='select',
            width= 800,
            height= 600,
            hovermode='closest'
            )
    }

    if contents:
        contents = contents[0]
        filename = filename[0]
        df,dat,col = get_data(contents,filename,k,order)
        for i in df.columns:
            if i not in column:
                df=df.drop(columns=i)
        fig =px.scatter_matrix(df, labels=[{i:i}for i in column])


    return fig



@app.callback(Output('output-data-upload', 'children'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('value-k', 'value'),
                Input('value-order', 'value')
            ])
def update_table(contents, filename,k,order):
    table = html.Div()

    if contents:
        contents = contents[0]
        filename = filename[0]
        df,dat,col = get_data(contents,filename,k,order)
        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=dat,
                columns=col
            ),
            html.Hr(),
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...', style={
                'whiteSpace': 'pre-wrap',
                'wordBreak': 'break-all'
            })
        ])

    return table




if __name__ == '__main__':
    app.run_server(debug=True,port=3978)