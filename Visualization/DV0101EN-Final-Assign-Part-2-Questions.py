
import dash
#import more_itertools
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('historical_automobile_sales.csv')
#data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

#---------------------------------------------------------------------------------
# Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]

# List of years 
year_list = [i for i in range(1980, 2024, 1)]

#---------------------------------------------------------------------------------------
# Create the layout of the app
app.layout = html.Div([
    # TASK 2.1 Add title to the dashboard
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'fontSize': 24
        }
    ),

    # TASK 2.2: Add two dropdown menus
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            value='Yearly Statistics',
            placeholder='Select a report type',
            style={
                'width': '80%',
                'padding': '3px',
                'fontSize': 20,
                'textAlignLast': 'center'
            }
        )
    ]),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value=1980,   # default year
            placeholder='Select Year',
            style={
                'width': '80%',
                'padding': '3px',
                'fontSize': 20,
                'textAlignLast': 'center'
            }
        )
    ]),

    # TASK 2.3: Add a division for output display
    html.Div([
        html.Div(
            id='output-container',
            className='chart-grid',
            style={'display': 'flex'}
        )
    ])
])

# -------------------------
# TASK 2.4: Creating Callbacks
# -------------------------

# Enable/disable the Year dropdown based on selected report type
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True


# Update the output container with 4 plots depending on selections
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [
        Input(component_id='dropdown-statistics', component_property='value'),
        Input(component_id='select-year', component_property='value')
    ]
)
def update_output_container(selected_statistics, selected_year):
    # Always return *something* so the spinner stops even if data is missing
    def note(msg):
        return html.Div(msg, style={'padding': '10px', 'border': '1px solid #eee', 'margin': '6px', 'borderRadius': '6px'})

    cols = set(data.columns)
    children = []

    if selected_statistics == 'Recession Period Statistics':
        # Basic column check
        if 'Recession' not in cols:
            return [note("Column 'Recession' not found in the dataset.")]
        recession_data = data[data['Recession'] == 1].copy()

        # Plot 1
        if {'Year', 'Automobile_Sales'}.issubset(cols):
            yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
            R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales',
                                                title="Average Automobile Sales fluctuation over Recession Period"))
        else:
            R_chart1 = note("Missing columns for Plot 1: need 'Year' and 'Automobile_Sales'.")

        # Plot 2
        if {'Vehicle_Type', 'Automobile_Sales'}.issubset(cols):
            average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
            R_chart2 = dcc.Graph(figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales',
                                               title="Average Vehicles Sold by Vehicle Type during Recessions"))
        else:
            R_chart2 = note("Missing columns for Plot 2: need 'Vehicle_Type' and 'Automobile_Sales'.")

        # Plot 3
        if {'Vehicle_Type', 'Advertising_Expenditure'}.issubset(cols):
            exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
            R_chart3 = dcc.Graph(figure=px.pie(exp_rec, names='Vehicle_Type', values='Advertising_Expenditure',
                                               title='Total Advertisement Expenditure Share by Vehicle Type (Recessions)'))
        else:
            R_chart3 = note("Missing columns for Plot 3: need 'Vehicle_Type' and 'Advertising_Expenditure'.")

        # Plot 4
        if {'unemployment_rate', 'Vehicle_Type', 'Automobile_Sales'}.issubset(cols):
            unemp_data = (recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales']
                          .mean().reset_index())
            R_chart4 = dcc.Graph(figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales',
                                               color='Vehicle_Type',
                                               labels={'unemployment_rate': 'Unemployment Rate',
                                                       'Automobile_Sales': 'Average Automobile Sales'},
                                               title='Effect of Unemployment Rate on Vehicle Type and Sales'))
        else:
            R_chart4 = note("Missing columns for Plot 4: need 'unemployment_rate', 'Vehicle_Type', 'Automobile_Sales'.")

        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart1, style={'flex': 1, 'minWidth': 320}),
                               html.Div(children=R_chart2, style={'flex': 1, 'minWidth': 320})],
                     style={'display': 'flex', 'flexWrap': 'wrap'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=R_chart3, style={'flex': 1, 'minWidth': 320}),
                               html.Div(children=R_chart4, style={'flex': 1, 'minWidth': 320})],
                     style={'display': 'flex', 'flexWrap': 'wrap'})
        ]

    elif selected_statistics == 'Yearly Statistics':
        # Guard if 'Year' missing
        if 'Year' not in cols:
            return [note("Column 'Year' not found in the dataset.")]
        yearly_data = data[data['Year'] == selected_year].copy()

        # Plot 1
        if {'Year', 'Automobile_Sales'}.issubset(cols):
            yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
            Y_chart1 = dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales',
                                                title='Average Automobile Sales by Year (All Years)'))
        else:
            Y_chart1 = note("Missing columns for Plot 1: need 'Year' and 'Automobile_Sales'.")

        # Plot 2 (selected year only, months sorted)
        if {'Month', 'Automobile_Sales'}.issubset(cols):
            mas = (yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index())
            mas['Month'] = pd.to_numeric(mas['Month'], errors='coerce')
            mas = mas.sort_values('Month')
            Y_chart2 = dcc.Graph(figure=px.line(mas, x='Month', y='Automobile_Sales',
                                                title=f'Total Monthly Automobile Sales in {selected_year}'))
        else:
            Y_chart2 = note("Missing columns for Plot 2: need 'Month' and 'Automobile_Sales'.")

        # Plot 3
        if {'Vehicle_Type', 'Automobile_Sales'}.issubset(cols):
            avr_vdata = (yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index())
            Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                                               title=f'Average Vehicles Sold by Vehicle Type in {selected_year}'))
        else:
            Y_chart3 = note("Missing columns for Plot 3: need 'Vehicle_Type' and 'Automobile_Sales'.")

        # Plot 4
        if {'Vehicle_Type', 'Advertising_Expenditure'}.issubset(cols):
            exp_data = (yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index())
            Y_chart4 = dcc.Graph(figure=px.pie(exp_data, names='Vehicle_Type', values='Advertising_Expenditure',
                                               title=f'Total Advertisement Expenditure by Vehicle Type in {selected_year}'))
        else:
            Y_chart4 = note("Missing columns for Plot 4: need 'Vehicle_Type' and 'Advertising_Expenditure'.")

        return [
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart1, style={'flex': 1, 'minWidth': 320}),
                               html.Div(children=Y_chart2, style={'flex': 1, 'minWidth': 320})],
                     style={'display': 'flex', 'flexWrap': 'wrap'}),
            html.Div(className='chart-item',
                     children=[html.Div(children=Y_chart3, style={'flex': 1, 'minWidth': 320}),
                               html.Div(children=Y_chart4, style={'flex': 1, 'minWidth': 320})],
                     style={'display': 'flex', 'flexWrap': 'wrap'})
        ]

    # Default safe return
    return [note("No selection yet.")]

# Run the Dash app
if __name__ == "__main__":
    app.run(debug=True)