import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

app = dash.Dash()
df = pd.read_csv('C:\Reuben\QCRI 2020\Python Code\iris_data.csv')

app.layout = html.Div(children=[
        html.H1(
        	children='PCP Iris ',
        	style={
        		'textAlign': 'center'
        	}
        ),

        dcc.Graph(
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
        	}
        )
        
    ])


if __name__ == '__main__':
    app.run_server(debug=True)