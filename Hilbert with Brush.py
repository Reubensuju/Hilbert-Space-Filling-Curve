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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div>My Custom header</div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div>My Custom footer</div>
    </body>
</html>
'''

app.layout = html.Div(children=[
    html.H1(
            children='HILBERT WITH BRUSH',
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
            id = 'paint-button')
        ],
        style={
            'margin': '10px',
            'display': 'inline-block'
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
    html.Div(id='textarea-state-example-output', style={'whiteSpace': 'pre-line'}),
    html.Div(id='selected-data'),
    html.Div(id='output-data-upload')
])



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
    d['brush-group'] = 0

    #create the dataframe
    global df,columns
    df=pd.DataFrame(d)
    df=df.copy()
    print(df)
    
    return df
    


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
        df= get_data(contents,filename,k,order)
        df = df.select_dtypes(['number'])
        options=[{'label':i, 'value':i}for i in df.columns]
        value = [df.columns[0],df.columns[1]]

    return options,value



@app.callback(Output('PCP', 'figure'),
            [Input('paint-button', 'n_clicks')],
            [
                State('upload-data', 'contents'),
                State('upload-data', 'filename'),
                State('value-k', 'value'),
                State('value-order', 'value'),
                State('Select-Column', 'value'),
                State('SPLOM', 'selectedData'),
                State('brush-group', 'value')
            ])
def update_graph_PCP(n_clicks, contents, filename, k, order, col_val, selectedData, brush_val):
    fig = {
        'layout': go.Layout(
            width= 800,
            height= 600
            )
    }

    if contents:
        contents = contents[0]
        filename = filename[0]
        col_val = sorted(col_val)
        df= get_data(contents,filename,k,order)

        if type(selectedData) is dict:
            for i in range(len(selectedData['points'])):
                point_id = selectedData['points'][i]['pointNumber']
                df.at[point_id, 'brush-group'] = int(brush_val)

        for i in df.columns:
            if (i not in col_val and i != 'brush-group'):
                df=df.drop(columns=i)
        fig =px.parallel_coordinates(df,color = 'brush-group', labels=[{i:i}for i in col_val])


    return fig


@app.callback(Output('SPLOM', 'figure'),
            [Input('paint-button', 'n_clicks')],
            [
                State('upload-data', 'contents'),
                State('upload-data', 'filename'),
                State('value-k', 'value'),
                State('value-order', 'value'),
                State('Select-Column', 'value'),
                State('SPLOM', 'selectedData'),
                State('brush-group', 'value')
            ])
def update_graph_SPLOM(n_clicks, contents, filename, k, order, col_val, selectedData, brush_val):
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
        col_val = sorted(col_val)
        df= get_data(contents,filename,k,order)

        if type(selectedData) is dict:
            for i in range(len(selectedData['points'])):
                point_id = selectedData['points'][i]['pointNumber']
                df.at[point_id, 'brush-group'] = int(brush_val)

        for i in df.columns:
            if (i not in col_val and i != 'brush-group'):
                df=df.drop(columns=i)
        fig =px.scatter_matrix(df, color = 'brush-group', labels=[{i:i}for i in col_val])


    return fig



'''@app.callback(Output('output-data-upload', 'children'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename'),
                Input('value-k', 'value'),
                Input('value-order', 'value'),
                Input('SPLOM', 'selectedData'),
                Input('Select-Column', 'value')
            ])
def update_table(contents, filename,k,order,selectedData,col_val):
    table = html.Div()

    if contents:
        contents = contents[0]
        filename = filename[0]
        df,dat,col = get_data(contents,filename,k,order)
        col_val = sorted(col_val)
        data=[{x:[]}for x in col_val]
        select_df = pd.DataFrame(data)

        

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

    return table'''


@app.callback(Output('output-data-upload', 'children'),
            [Input('paint-button', 'n_clicks')],
            [
                State('upload-data', 'contents'),
                State('upload-data', 'filename'),
                State('value-k', 'value'),
                State('value-order', 'value'),
                State('SPLOM', 'selectedData'),
                State('brush-group', 'value')
            ])
def update_table(n_clicks, contents, filename, k,order, selectedData, brush_val):
    table = html.Div()

    if contents:
        contents = contents[0]
        filename = filename[0]
        df= get_data(contents,filename,k,order)
        
        if type(selectedData) is dict:
            for i in range(len(selectedData['points'])):
                point_id = selectedData['points'][i]['pointNumber']
                df.at[point_id, 'brush-group'] = int(brush_val)

        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(
                data=df.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),
            html.Hr(),
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...', style={
                'whiteSpace': 'pre-wrap',
                'wordBreak': 'break-all'
            })
        ])

    return table



'''@app.callback(
    Output('textarea-state-example-output', 'children'),
    [Input('paint-button', 'n_clicks')],
    [State('SPLOM', 'selectedData'),
     State('Select-Column', 'value')])
def display_click_data(n_clicks,selectedData,col_val):
    json_string = json.dumps(selectedData)
    json_dictionary = json.loads(json_string)
    if type(selectedData) == "<class 'dict'>":
        value = selectedData['points'][0]['pointNumber']
    else:

    pe = type(selectedData)
    j=0
    return '\n{}'.format(value)
'''


if __name__ == '__main__':
    app.run_server(debug=True,port=6525)