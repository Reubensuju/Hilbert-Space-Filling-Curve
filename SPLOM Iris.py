import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

app = dash.Dash()
df = pd.read_csv('C:\Reuben\QCRI 2020\Python Code\iris_data.csv')
index_vals = df['CLASS'].astype('category').cat.codes

app.layout = html.Div(children=[
        html.H1(
            children='SPLOM Iris ',
            style={
                'textAlign': 'center'
            }
        ),

        dcc.Graph(
            id = 'SPLOM',
            figure={
                'data' : [
                    go.Splom(
                dimensions=[dict(label='sepal.length',
                                 values=df['sepal.length']),
                            dict(label='sepal.width',
                                 values=df['sepal.width']),
                            dict(label='petal.length',
                                 values=df['petal.length']),
                            dict(label='petal.width',
                                 values=df['petal.width'])],
                text=df['CLASS'],
                marker=dict(color=index_vals,
                            showscale=False, # colors encode categorical variables
                            line_color='white', line_width=0.5)
                )
                ]
            },

            style = {
                'title' : 'SPLOM Iris Data set',
                'dragmode' :'select',
                'width' : 600,
                'height' : 600,
                'hovermode': 'closest'
            }
        ),
    html.Div(id='textarea-state-example-output', style={'whiteSpace': 'pre-line'})
        
    ])


@app.callback(
    dash.dependencies.Output('textarea-state-example-output', 'children'),
    [dash.dependencies.Input('SPLOM', 'selectedData')])
def display_click_data(selectedData):

    json_string = json.dumps(selectedData)
    json_dictionary = json.loads(json_string)
    pe = type(json_dictionary)
    j=0
    return '\n{}'.format(pe)


if __name__ == '__main__':
    app.run_server(debug=True,port=1121)