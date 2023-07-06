import base64
import datetime
import io
import plotly.graph_objs as go
import plotly.express as px
import cufflinks as cf
import csv
import json

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
import numpy as np


from Hilbert_transform import*
from Hilbert_Mapping import*

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd',
        '#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
groups = [1,2,3,4,5,6,7,8,9,10]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

Hilbert_df = pd.DataFrame()

app.layout = html.Div(children=[
    html.H1(
            children='Space Filling Curve For High Dimensional Data',
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
            'margin': '10px',
            'display': 'inline-block'
        }),

    html.Div(style={
            'width': '650px',
            'display': 'inline-block'}),

    html.Div(children = [
        html.Label('Brush Group'),
        dcc.RadioItems(
            id = 'brush-group',
            options=[
                {'label':'1', 'value':'1'},
                {'label':'2', 'value':'2'},
                {'label':'3', 'value':'3'},
                {'label':'4', 'value':'4'},
                {'label':'5', 'value':'5'}
            ],
            labelStyle={'display': 'inline-block'}
            )],
        style={
            'margin': '10px',
            'display': 'inline-block'
        }),


    html.Div(children = [
        html.Button(
            'Paint',
            id = 'paint-button', n_clicks=0)
        ],
        style={
            'margin': '10px',
            'display': 'inline-block'
        }),


    html.Div(),


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
            'margin': '10px',
            'display': 'inline-block'
        }),

    html.Div(style={
            'width': '350px',
            'display': 'inline-block'}),

    html.Div(children = [
        html.Label('Color Control'),
        dcc.Dropdown(
            id = 'Color-Column',
            value = ['class-group'])],
        style={
            'width': '30%',
            'margin': '10px',
            'display': 'inline-block'
        }),


    html.Div(children = [
        html.Label('Display Columns'),
        dcc.Dropdown(
            id = 'Select-Column',
            multi=True)],
        style={
            'width': '30%',
            'margin': '10px'
        }),


    html.Div(dcc.Graph(id='PCP'),style={'display': 'inline-block'}),
    html.Div(dcc.Graph(id='SPLOM'),style={'display': 'inline-block'}),
    html.Div(dcc.Graph(id='HISTOGRAM')),
    html.Div(id='textarea-state-example-output', style={'whiteSpace': 'pre-line'}),
    html.Div(id='output-data-upload'),

    # Hidden div inside the app that stores the idataframe
    html.Div(id='Hilbert-Dataframe', style={'display': 'none'})
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
    
    #class group mapping - mapping class labels with groups
    unique_classes = set(labels)
    g = []
    for i in unique_classes:
        g.append(i)
    col_dict = {}
    for i in g:
        col_dict[i] = groups[g.index(i)]
    class_map = []
    for i in labels:
        class_map.append(col_dict[i])
    
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
    d['class-group'] = class_map
    d['brush-group'] = 0

    #create the dataframe
    global df,columns
    df=pd.DataFrame(d)
    df=df.copy()
    original_df = parse_data(contents, filename)
    original_df = original_df.select_dtypes(['number'])
    df = pd.concat([df, original_df], axis=1)
    print(df)
    
    return df
    
@app.callback(Output('Hilbert-Dataframe', 'children'),
            [
                Input('upload-data', 'contents')
            ],
            [
                State('paint-button', 'n_clicks'),
                State('upload-data', 'filename'),
                State('value-k', 'value'),
                State('value-order', 'value')
            ])
def generate_data(contents, n_clicks, filename, k, order):

    global Hilbert_df
    if contents:
        contents = contents[0]
        filename = filename[0]
        Hilbert_df = get_data(contents,filename,k,order)

        return Hilbert_df.to_json(date_format='iso', orient='split')



@app.callback(
            [Output('Color-Column', 'options'),
            Output('Color-Column', 'value')],
            [
                Input('upload-data', 'contents'),
                Input('Hilbert-Dataframe', 'children')
            ])
def update_Color_Dropdown(contents, jsonified_data):
    
    options=[]
    value=[]
    if contents:
        df = Hilbert_df.copy()
        df = df.select_dtypes(['number'])
        options=[{'label':i, 'value':i}for i in df.columns]
        value = [df.columns[0]]

    return options,value


@app.callback(
            [Output('Select-Column', 'options'),
            Output('Select-Column', 'value')],
            [
                Input('upload-data', 'contents'),
                Input('Hilbert-Dataframe', 'children')
            ])
def update_Select_Dropdown(contents, jsonified_data):
    
    options=[]
    value=[]
    if contents:
        df = Hilbert_df.copy()
        df = df.select_dtypes(['number'])
        options=[{'label':i, 'value':i}for i in df.columns]
        value = [df.columns[0],df.columns[1]]

    return options,value


@app.callback(Output('SPLOM', 'figure'),
            [
                Input('paint-button', 'n_clicks'),
                Input('Select-Column', 'value'),
                Input('Color-Column', 'value'),
                Input('upload-data', 'contents')],
            [
                State('SPLOM', 'selectedData'),
                State('brush-group', 'value')
            ])
def update_graph_SPLOM(n_clicks, col_val, selec_color, contents, selectedData, brush_val):
    global Hilbert_df
    fig = {
        'layout': go.Layout(
            dragmode='select',
            width= 800,
            height= 600,
            hovermode='closest'
            )
    }

    if contents:
        df = Hilbert_df.copy()
        col_val = sorted(col_val)

        if type(selectedData) is dict:
            for i in range(len(selectedData['points'])):
                point_id = selectedData['points'][i]['pointNumber']
                Hilbert_df.at[point_id, 'brush-group'] = int(brush_val)
            df = Hilbert_df.copy()

        if selec_color is None:
            selec_color = 'class-group'

        for i in df.columns:
            if (i not in col_val and i != selec_color):
                df=df.drop(columns=i)
        fig =px.scatter_matrix(df, color = selec_color, labels=[{i:i}for i in col_val])

    return fig



@app.callback(Output('PCP', 'figure'),
            [
                Input('paint-button', 'n_clicks'),
                Input('Select-Column', 'value'),
                Input('Color-Column', 'value'),
                Input('upload-data', 'contents')
            ],
            )
def update_graph_PCP(n_clicks, col_val, selec_color, contents):
    fig = {
        'layout': go.Layout(
            width= 800,
            height= 600
            )
    }

    if contents:
        df = Hilbert_df.copy()
        col_val = sorted(col_val)

        if selec_color is None:
            selec_color = 'class-group'

        for i in df.columns:
            if (i not in col_val and i != selec_color):
                df=df.drop(columns=i)
        fig =px.parallel_coordinates(df,color = selec_color, labels=[{i:i}for i in col_val])


    return fig


@app.callback(Output('HISTOGRAM', 'figure'),
            [
                Input('paint-button', 'n_clicks'),
                Input('Select-Column', 'value'),
                Input('Color-Column', 'value'),
                Input('upload-data', 'contents')
            ],
            )
def update_graph_HIST(n_clicks, col_val, selec_color, contents):
    fig = {
        'layout': go.Layout(
            width= 800,
            height= 600
            )
    }

    if contents:
        df = Hilbert_df.copy()
        col_val = sorted(col_val)

        if selec_color is None:
            selec_color = 'class-group'

        for i in df.columns:
            if (i not in col_val and i != selec_color):
                df=df.drop(columns=i)
        fig =px.histogram(df,color = selec_color, labels=[{i:i}for i in col_val])


    return fig




@app.callback(Output('output-data-upload', 'children'),
            [
                Input('paint-button', 'n_clicks'),
                Input('upload-data', 'contents')
            ],
            [
                State('Hilbert-Dataframe', 'children')
            ])
def update_table(n_clicks, contents, jsonified_data):
    table = html.Div()

    if contents:
        df = Hilbert_df.copy()

        table = html.Div([
            html.H5("Dataframe"),
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),
            html.Hr(),
            html.Div('Raw Content')
        ])

    return table



if __name__ == '__main__':
    app.run_server(debug=True,port=9193)