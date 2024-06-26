# -------------------------------------- Import Libraries --------------------------------------
# Dash
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import dash.dash_table as dash_table
import dash_ag_grid as dag

# Plotly
import plotly.graph_objects as go

# Numpy, Pandas, Random
import numpy as np
import pandas as pd
import random

# Import dataset preprocessing function
from datasetPreprocessing import preprocess_dataset

# Create a Dash app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])


# -------------------------------------- Data Preparation/Preprocessing --------------------------------------

file_path = '/Users/phantom/Documents/GitHub/Lobbyism-Dashboard/Datasets/Lobbyregister2024_full.csv'

# Load original dataset 
oDf = pd.read_csv(file_path)

# Set original/cleaned dataset index
oDf[' index'] = range(1, len(oDf) + 1)

cDf = preprocess_dataset(file_path)


# -------------------------------------- Plot --------------------------------------

# Create an example plot
fig = go.Figure(
    go.Scattergl(
        x = np.random.randn(500),
        y = np.random.randn(500),
        mode='markers',
        marker=dict(color=random.sample(['#ecf0f1']*500 + ["#3498db"]*500, 1000), line_width=1)
    )
)

# Update the layout of the plot
fig.update_layout(plot_bgcolor='#010103', width=790, height=730,
                  xaxis_visible=False, yaxis_visible=False, showlegend=False, margin=dict(l=0,r=0,t=0,b=0))

# Create a Dash container
app.layout = dbc.Container([
    # -------------------------------------- Layout Tabs & Dropdown Filters --------------------------------------

    html.Div([
        html.Div([
            # Title
            html.H1([ html.Span("Lobbyism"), html.Br(),html.Span("in Germany")]),
            # Info text
            html.P("This dashboard shows you some insights from the german parliament lobby register."
              )
        ],style={"vertical-alignment": "top", "height": 300}),
        html.Div([
            html.Div(
                # Radio buttons for tab selection
                dbc.RadioItems(
                    id='radio-button-group',
                    className='btn-group',
                    inputClassName='btn-check',
                    labelClassName="btn btn-outline-light",
                    labelCheckedClassName="btn btn-light",
                    options=[
                        {"label": "Insights", "value": 'INSIGHTS'},
                        {"label": "Explore", "value": 'EXPLORE'},
                        {"label": "Cluster", "value": 'CLUSTER'}
                    ],
                    value='EXPLORE',
                    style={'width': '100%'}
                ), 
                style={'width': 312}
            ),
            html.Div(
                # About button
                dbc.Button(
                    "About",
                    className="btn btn-info",
                    n_clicks=0
                ), style={'width': 104})
        ], style={'margin-left': 15, 'margin-right': 15, 'display': 'flex'}),
        html.Div([
            # Dropdowns section for filtering
            html.H2(html.Span("Filter for Cleaned Dataset:")),
            html.Div([
                # Fiscal Year Dropdown
                html.H2('Fiscal Year:'),
                dcc.Dropdown(
                    id='fiscal-year-dropdown',
                    options=[
                        {'label': '2021', 'value': 1},
                        {'label': '2022', 'value': 2},
                        {'label': '2023', 'value': 3}
                    ],
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black'}
                )
            ]),
            html.Div([
                # Employee Dropdown
                html.H2('Average Employees:'),
                dcc.Dropdown(
                    id='average-employees-dropdown',
                    options=[
                        {'label': '>5', 'value': 1},
                        {'label': '>10', 'value': 2},
                        {'label': '>50', 'value': 3},
                        {'label': '>100', 'value': 4}
                    ],
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black'}
                )
            ]),
            html.Div([
                # Spending Dropdown
                html.H2('Average Spending:'),
                dcc.Dropdown(
                    id='average-spending-dropdown',
                    options=[
                        {'label': '>5.000', 'value': 1},
                        {'label': '>10.000', 'value': 2},
                        {'label': '>50.000', 'value': 3},
                        {'label': '>100.000', 'value': 4},
                        {'label': '>500.000', 'value': 5},
                        {'label': '>1.000.000', 'value': 6}
                    ],
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black'}
                )
            ]),
            html.Div([
                # Spending/Employee Dropdown
                html.H2('Spending/Employee:'),
                dcc.Dropdown(
                    id='spending-per-employee-dropdown',
                    options=[
                        {'label': '>1.000', 'value': 1},
                        {'label': '>5.000', 'value': 2},
                        {'label': '>10.000', 'value': 3},
                        {'label': '>50.000', 'value': 4},
                        {'label': '>100.000', 'value': 5}
                    ],
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black'}
                )
            ]),
            html.Div([
                # Entity Dropdown
                html.H2('Entity'),
                dcc.Dropdown(
                    id='entity-dropdown',
                    options=[
                        {'label': i, 'value': i} for i in sorted(cDf['Tätigkeit'].unique())
                    ],
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black'}
                )
            ])
        ], 
        style={'margin-left': 15, 'margin-right': 15, 'margin-top': 30})
    ], 
    style={'width': 340, 'margin-left': 25, 'margin-top': 25, 'margin-bottom': 25}),


    # -------------------------------------- Insights Tab --------------------------------------

    html.Div([
        html.Div([
            # Title
            html.H2('Insights'),
            # Plot
            dcc.Graph(figure=fig)
        ],
        id='insights-tab',
        style={
            'display': 'none',
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        })
    ]),


    # -------------------------------------- Explore Tab --------------------------------------

    html.Div([
        html.Div([ 
            html.H2('Selected Original Dataset Columns:'),
                # Dropdown for column filtering
                dcc.Dropdown(
                    id='column-dropdown-filter-original',
                    options=[{'label': col, 'value': col} for col in sorted(oDf.columns)],
                    clearable=True,
                    multi=True,
                    value=[oDf.columns[0],   # Name
                           oDf.columns[7],   # Spending
                           oDf.columns[8],   # Fiscal Year
                           oDf.columns[4],   # Entity
                           oDf.columns[13],  # Employees
                           oDf.columns[5]],  # Interests]
                    optionHeight=40,
                    className='customDropdown',
                    style={'margin-bottom': 10, 'background-color': 'black'}
                ),
                html.H2('Selected Cleaned Dataset Columns:'),
                dcc.Dropdown(
                    id='column-dropdown-filter-cleaned',
                    options=[{'label': col, 'value': col} for col in sorted(cDf.columns)],
                    clearable=True,
                    multi=True,
                    value=[cDf.columns[0],   # Name
                           cDf.columns[18],  # AVG Spending
                           cDf.columns[21],   # Fiscal Year
                           cDf.columns[4]],   # Entity
                    optionHeight=40,
                    className='customDropdown',
                    style={'margin-bottom': 25, 'background-color': 'black'}
                ),
                # Tabs for switching tables
                html.Div([
                dcc.Tabs(
                    id='table-tabs', 
                    value='cleaned-tab', 
                    children=[
                        dcc.Tab(
                            label='Cleaned Dataset', 
                            value='cleaned-tab',
                            style={'backgroundColor': 'black',
                                   'color': 'white',
                                   'border-top':'0px',
                                   'border-left':'0px',                 
                                   'border-right':'0px',                 
                                   'border-bottom':'0px'},
                            selected_style={'backgroundColor': 'black', 
                                            'color': '#3498db',
                                            'border-top':'0px',
                                            'border-left':'0px',                 
                                            'border-right':'0px',                 
                                            'border-bottom':'0px'},
                            ),
                        dcc.Tab(
                            label='Original Dataset', 
                            value='original-tab',
                            style={'backgroundColor': 'black',
                                   'color': 'white',
                                   'border-top':'0px',
                                   'border-left':'0px',                 
                                   'border-right':'0px',                 
                                   'border-bottom':'0px'},
                            selected_style={'backgroundColor': 'black', 
                                            'color': '#3498db',
                                            'border-top':'0px',
                                            'border-left':'0px',                 
                                            'border-right':'0px',                 
                                            'border-bottom':'0px'},
                            )
                ]),
                html.Div(id='table-tabs-content')
                ]),
                # Display data tables
                ],
                # Style for the tables
                style={'width': 990, 'margin-top': 25, 'margin-bottom': 25}),
        ],
        id='explore-tab',
        style={
            'display': 'none',
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        }),


    # -------------------------------------- Cluster Tab --------------------------------------

    html.Div([
        html.Div([
            # Title
            html.H2('Cluster Analysis'),
            # Plot
            dcc.Graph(figure=fig)
        ],
        id='cluster-tab',
        style={
            'display': 'none',
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        })
    ]),    

],
    # Style for the dash container
    fluid=True,
    style={'display': 'flex'},
    className='dashboard-container')


#-------------------------------------- Callbacks -------------------------------------

# -------------------------------------- Insights --------------------------------------

# Define callback to toggle insights tab visibility
@app.callback(
    Output('insights-tab', 'style'), # Show the insights
    Input('radio-button-group', 'value') # Radio button for selecting tabs
)
   
# Toggle insights tab visibility
def toggle_insights_tab_visibility(selected_tab):
    if selected_tab == 'INSIGHTS':
        return {'display': 'flex'}  # Change to 'flex' to make it visible
    else:
        return {'display': 'none'}  # Change to 'none' to hide it
    

# -------------------------------------- Explore --------------------------------------    

# Define callback to toggle explore tab visibility
@app.callback(
    Output('explore-tab', 'style'), # Show the explore tab      
    Input('radio-button-group', 'value') # Radio button for selecting tabs
)
   
# Toggle explore tab visibility
def toggle_explore_tab_visibility(selected_tab):
    if selected_tab == 'EXPLORE':
        return {'display': 'flex'} # Change to 'flex' to make it visible
    else:
        return {'display': 'none'} # Change to 'none' to hide it
    
# Table Tabs 

@app.callback(
    Output('table-tabs-content', 'children'),
    [Input('table-tabs', 'value')]
)

def render_content(tab):
    if tab == 'cleaned-tab':
        return dash_table.DataTable(
                    id='cleaned-data-table',
                    columns=[{'name': i, 'id': i, 'deletable': True} for i in sorted(cDf.columns)],
                    page_current=0,
                    page_size=15,
                    page_action='custom',
                    sort_action='custom',
                    sort_mode='single',
                    sort_by=[],
                    style_table={'overflowX': 'auto', 'overflowY': 'auto'},
                    style_header={'backgroundColor': 'black','color': '#3498db','fontWeight': 'bold', 'fontFamily': 'sans-serif'},
                    style_cell={'backgroundColor': 'black','color': 'white','textAlign': 'left', 'fontFamily': 'sans-serif'},
                )
    elif tab == 'original-tab':
        return dash_table.DataTable(
                    id='original-data-table',
                    columns=[{'name': i, 'id': i, 'deletable': True} for i in sorted(oDf.columns)],
                    page_current=0,
                    page_size=15,
                    page_action='custom',
                    sort_action='custom',
                    sort_mode='single',
                    sort_by=[],
                    style_table={'overflowX': 'auto', 'overflowY': 'auto'},
                    style_header={'backgroundColor': 'black','color': '#3498db','fontWeight': 'bold', 'fontFamily': 'sans-serif'},
                    style_cell={'backgroundColor': 'black','color': 'white','textAlign': 'left', 'fontFamily': 'sans-serif'},
                )
    

# -------------------------------------- Cluster --------------------------------------

# Define callback to toggle cluster tab visibility
@app.callback(
    Output('cluster-tab', 'style'), # Show the explore tab      
    Input('radio-button-group', 'value') # Radio button for selecting tabs
)
   
# Toggle cluster tab visibility
def toggle_cluster_tab_visibility(selected_tab):
    if selected_tab == 'CLUSTER':
        return {'display': 'flex'}  # Change to 'flex' to make it visible
    else:
        return {'display': 'none'}  # Change to 'none' to hide it


# -------------------------------------- Update Original Datatable --------------------------------------

# Define callback to update table
@app.callback(
    [Output('original-data-table', 'data'),
    Output('original-data-table', 'columns')], # Update columns dynamically
    [Input('original-data-table', "page_current"),
    Input('original-data-table', "page_size"),
    Input('original-data-table', 'sort_by'),
    Input('column-dropdown-filter-original', 'value')] # Update table based on selected columns
)

# Update table
def update_table(page_current, page_size, sort_by, selected_columns):
    # Filter DataFrame based on selected columns
    if selected_columns:
        oDff = oDf[selected_columns]
    else:
        oDff = oDf.copy()

    # Sort if there is a sort_by criteria
    if len(sort_by):
        oDff = oDff.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )

    # Paginate
    page_start = page_current * page_size
    page_end = page_start + page_size
    oDff = oDff.iloc[page_start:page_end]

    # Prepare columns for the DataTable
    columns = [{'name': i, 'id': i} for i in selected_columns] if selected_columns else [{'name': i, 'id': i} for i in oDf.columns]
    
    # Return data and columns
    return oDff.to_dict('records'), columns


# -------------------------------------- Update Cleanded Datatable ----------------------------------

# -------------------------------------- Filter Values Cleaned Datatable --------------------------------------

@app.callback(
    [Output('cleaned-data-table', 'data'),
    Output('cleaned-data-table', 'columns')], # Update columns dynamically
    [Input('cleaned-data-table', "page_current"),
    Input('cleaned-data-table', "page_size"),
    Input('cleaned-data-table', 'sort_by'),
    Input('column-dropdown-filter-cleaned', 'value'),
    Input('fiscal-year-dropdown', 'value'),
    Input('average-employees-dropdown', 'value'),
    Input('average-spending-dropdown', 'value'),
    Input('spending-per-employee-dropdown', 'value'),
    Input('entity-dropdown', 'value')] # Update table based on selected columns
)
def update_table(page_current, page_size, sort_by, selected_columns, selected_year, selected_employees, selected_spending, selected_spending_per_employee, selected_entity):
    filtered_df = cDf.copy()  # Start with a copy of the original DataFrame to avoid modifying it directly
    
    # Filter by year
    if selected_year:
        year_mapping = {1: 2021, 2: 2022, 3: 2023}
        filtered_df = filtered_df[filtered_df['GeschäftsjahrStart'].dt.year == year_mapping[selected_year]]
    
    # Filter by average employees
    if selected_employees:
        if selected_employees == 1:
            filtered_df = filtered_df[filtered_df['Durchschnitt Beschäftigte'] > 5]
        elif selected_employees == 2:
            filtered_df = filtered_df[filtered_df['Durchschnitt Beschäftigte'] > 10]
        elif selected_employees == 3:
            filtered_df = filtered_df[filtered_df['Durchschnitt Beschäftigte'] > 50]
        elif selected_employees == 4:
            filtered_df = filtered_df[filtered_df['Durchschnitt Beschäftigte'] > 100]
    
    # Filter by average spending
    if selected_spending:
        if selected_spending == 1:
            filtered_df = filtered_df[filtered_df['Durchschnitt Betrag'] > 5000]
        elif selected_spending == 2:
            filtered_df = filtered_df[filtered_df['Durchschnitt Betrag'] > 10000]
        elif selected_spending == 3:
            filtered_df = filtered_df[filtered_df['Durchschnitt Betrag'] > 50000]
        elif selected_spending == 4:
            filtered_df = filtered_df[filtered_df['Durchschnitt Betrag'] > 100000]
        elif selected_spending == 5:
            filtered_df = filtered_df[filtered_df['Durchschnitt Betrag'] > 500000]
        elif selected_spending == 6:
            filtered_df = filtered_df[filtered_df['Durchschnitt Betrag'] > 1000000]

    # Filter by spending per employee
    if selected_spending_per_employee:
        if selected_spending_per_employee == 1:
            filtered_df = filtered_df[filtered_df['Betrag / Beschäftigte'] > 1000]
        elif selected_spending_per_employee == 2:
            filtered_df = filtered_df[filtered_df['Betrag / Beschäftigte'] > 5000]
        elif selected_spending_per_employee == 3:
            filtered_df = filtered_df[filtered_df['Betrag / Beschäftigte'] > 10000]
        elif selected_spending_per_employee == 4:
            filtered_df = filtered_df[filtered_df['Betrag / Beschäftigte'] > 50000]
        elif selected_spending_per_employee == 5:
            filtered_df = filtered_df[filtered_df['Betrag / Beschäftigte'] > 100000]
        

    # Filter by selected entity
    if selected_entity:
        # Ensure selected_entity is treated as a list
        entity_list = [selected_entity] if isinstance(selected_entity, str) else selected_entity
        filtered_df = filtered_df[filtered_df['Tätigkeit'].isin(entity_list)]

    # Filter DataFrame based on selected columns
    if selected_columns:
        cDff = filtered_df[selected_columns]
    else:
        cDff = filtered_df.copy()

    # Sort if there is a sort_by criteria
    if len(sort_by):
        cDff = cDff.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )

    # Paginate
    page_start = page_current * page_size
    page_end = page_start + page_size
    cDff = cDff.iloc[page_start:page_end]

    # Prepare columns for the DataTable
    columns = [{'name': i, 'id': i} for i in selected_columns] if selected_columns else [{'name': i, 'id': i} for i in filtered_df.columns]
    
    # Return data and columns
    return cDff.to_dict('records'), columns


# -------------------------------------- Run the app --------------------------------------

# Run the app on port 8050
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
