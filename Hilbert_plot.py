'''Boken Interface for Hilbert Plot'''

import pandas as pd
import numpy as np
import csv


from bokeh.layouts import column, row, layout, widgetbox,grid
from bokeh.models import Select, HoverTool, CategoricalColorMapper, FileInput, Button, ColumnDataSource, TextInput, Slider
from bokeh.plotting import curdoc, figure, output_file,show
from bokeh.palettes import Category10


from Hilbert_transform import*
from Hilbert_Mapping import*


output_file("Bokeh_Interface_Hilbert_Plot.html")
colors = Category10[10]


''' This function loads data from the file selected on button input and extracts data into two lists: class and datapoints'''
def get_data():
    global labels,data
    
    with open(button_input.filename,'r') as f:
        reader = csv.reader(f,delimiter = ',')
        file_data = [(column[1:]) for column in reader]
        
    labels = []   #class values
    data = []     #data points (D1,D2,D3,D4....)
    for x in file_data:
        if 'CLASS' not in x:
            labels.append(x[0])
#            data.append([float(x[i]) for i in range(1,len(file_data[0]))])
            data.append([float(x[i]) for i in range(1,5)])   #7 works for data_subset but restrict to 6 for plot
    
    create_dataframe()
    

''' This function creates a pandas dataframe after performing hilbert transform on the intial dataset. The initial NxD dataset will be reduced to Nxm dataset, where m is the number of hilbert curves. The dataframe makes it easier to use with other bokeh widgets and plots'''
def create_dataframe():
    global x,y,controls,layout,k,labels,data,order,max_order, col_dict

    while(len(layout.children) > 0):      #clearing current layout for new data file inputs
        {layout.children.pop()}
     
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
    
    m = int(k.value)    #number of hilbert indices
    data_transform,max_order = Hilbert_data_transform(deepcopy(data),hilbert_order.value, m)
    
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
    global df,columns,source
    df=pd.DataFrame(d)
    df=df.copy()
    print(df)
    col = sorted(df.columns)
    columns = [i for i in col if 'class' not in i and 'colors' not in i]
    source = ColumnDataSource(df)
    
    coord_of_plots(columns)
    
    
'''This function changes the X and Y coordinate of the plot; What does the plot look like for different hilbert indices on it's X and Y coordinates?'''
def coord_of_plots(columns):
    global x,y,controls,layout,order,max_order,hilbert_order
    
    x = Select(title='X-Axis', value='H0', options=columns)
    x.on_change('value', update_xy)
    y = Select(title='Y-Axis', value='H0', options=columns)
    y.on_change('value', update_xy)
    
    controls = widgetbox(x,y,width=200)
    layout = row(column(button_input,k,hilbert_order,controls),create_figure())
    curdoc().add_root(layout)


'''The bokeh plot'''
def create_figure():
    global x,y,df
    
    x_title = x.value.title()
    y_title = y.value.title()
    
    kw = dict()
    kw['title'] = "%s vs %s" % (x_title, y_title)
    
    hover = HoverTool(tooltips=[('index', '$index'),('Class','@class')])
    p = figure(plot_height=600, plot_width=800, tools=['pan,wheel_zoom,reset',hover], **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title
    p.circle(x=x.value, y=y.value,color='colors', size=9, alpha=0.6, hover_color='white', hover_alpha=0.5,source=source)
    
    return p

'''The following are the update functions for the different widgets'''
def update_xy(attr, old, new):
    layout.children[1] = create_figure()
    
def update_botton(attr,old,new):
    layout.children[1] = get_data()
    
def update_text(attr,old,new):
    layout.children[1] = create_dataframe()

def update_order(attr,old,new):
    hilbert_order.end = max_order
    layout.children[1] = create_dataframe()
    
    
button_input = FileInput()
button_input.on_change('value', update_botton)

k = TextInput(value = '5', title="Value of K?")
k.on_change('value',update_text)

max_order = 10
hilbert_order = Slider(title="Order of Hilbert Indices", start=1, end=max_order, value=3,step=1)
hilbert_order.on_change('value_throttled',update_order)


layout = column(button_input,k)
curdoc().add_root(layout)
curdoc().title = "Dimensionality Reduction using Hilbert Curves"
