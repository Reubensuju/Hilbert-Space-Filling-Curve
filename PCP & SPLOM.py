import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

app = dash.Dash()
df = pd.read_csv('C:\Reuben\QCRI 2020\iris_data.csv')
index_vals = df['CLASS'].astype('category').cat.codes





app.layout = html.Div(children=[
        html.H1(
        	children='PCP & SPLOM',
        	style={
        		'textAlign': 'center'
        	}
        ),

        html.Div(dcc.Graph(
        	figure={
        		'data' : [
        			go.Parcoords(
        				dimensions = list([
           					dict(range = [0,8],
        				        constraintrange = [0,8],
        				        label = 'Sepal Length', values = df['sepal.length']),
      					    dict(range = [0,8],
      		 			        label = 'Sepal Width', values = df['sepal.width']),
      					    dict(range = [0,8],
      					        label = 'Petal Length', values = df['petal.length']),
           					dict(range = [0,8],
          					    label = 'Petal Width', values = df['petal.width'])
        				])

        			)
        		]
        	},

          style= {
            'width' : 800,
            'height' : 600
          }
        ),style={'display': 'inline-block'}),


        html.Div(dcc.Graph(
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
                'width' : 800,
                'height' : 600,
                'hovermode': 'closest'
            }
        ),style={'display': 'inline-block'}),


    ],

    style={'width': '100%', 'display': 'inline-block'}

    )





if __name__ == '__main__':
    app.run_server(debug=True,port=3948)