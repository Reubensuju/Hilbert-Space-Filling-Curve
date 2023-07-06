import base64
import datetime
import io
import plotly.graph_objs as go
import plotly.express as px
import cufflinks as cf

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from Hilbert_transform import*
from Hilbert_Mapping import*

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.layout = html.Div(children=[
    html.H1(
            children='PCP & SPLOM 3',
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
            value = '5',
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

   

@app.callback(
            [Output('Select-Column', 'options'),
            Output('Select-Column', 'value')],
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_Dropdown(contents, filename):
    
    options=[]
    value=[]
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df = df.select_dtypes(['number'])
        df = df.set_index(df.columns[0])
        options=[{'label':i, 'value':i}for i in df.columns]
        value = [df.columns[0],df.columns[1]]

    return options,value



@app.callback(Output('PCP', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_graph_PCP(contents, filename):
    fig = {
        'layout': go.Layout(
            width= 800,
            height= 600
            )
    }

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df = df.set_index(df.columns[0])
        fig =px.parallel_coordinates(df, labels=[{i:i}for i in df.columns])


    return fig


@app.callback(Output('SPLOM', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_graph_SPLOM(contents, filename):
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
        df = parse_data(contents, filename)
        df = df.set_index(df.columns[0])
        fig =px.scatter_matrix(df, labels=[{i:i}for i in df.columns])


    return fig


@app.callback(Output('output-data-upload', 'children'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
def update_table(contents, filename):
    table = html.Div()

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
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




if __name__ == '__main__':
    app.run_server(debug=True,port=3948)