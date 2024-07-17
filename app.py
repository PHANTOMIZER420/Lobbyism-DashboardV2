# -------------------------------------- IMPORTS --------------------------------------

# Dash
from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash.dash_table as dash_table

# Plotly
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt

# Networkx
import networkx as nx 

# Numpy, Pandas, Random
import numpy as np
import pandas as pd
import random

# Import dataset preprocessing function
from datasetPreprocessingExplore import preprocess_dataset

# Import graph network function 
import graphNetwork

# Import dashboard preprocessing function
import datasetPreprocessingInsights

# -------------------------------------- APP SETUP --------------------------------------

# Create a Dash app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.FLATLY])

# -------------------------------------- DATA PREPROCESSING --------------------------------------

filepath = 'Datasets/Lobbyregister2024_full.csv'

# Load original dataset 
oDf = pd.read_csv(filepath)

# Set original dataset index
oDf[' index'] = range(1, len(oDf) + 1)

# Preprocess the dataset
cDf = preprocess_dataset(filepath)

# -------------------------------------- PLOTS --------------------------------------

# Create an example plot
fig = go.Figure(
    go.Scattergl(
        x = np.random.randn(100),
        y = np.random.randn(100),
        mode='markers',
        marker=dict(color=random.sample(['#ecf0f1']*500 + ["#3498db"]*500, 1000), line_width=1)
    )
)
figX = go.Figure(
    go.Scattergl(
        x = np.random.randn(100),
        y = np.random.randn(100),
        mode='markers',
        marker=dict(color=random.sample(['#ecf0f1']*500 + ["#3498db"]*500, 1000), line_width=1)
    )
)

# Update the layout of the plot
fig.update_layout(plot_bgcolor='#010103', width=380, height=380,
                  xaxis_visible=False, yaxis_visible=False, showlegend=False, margin=dict(l=0,r=0,t=0,b=0))

# Update the layout of the plot
figX.update_layout(plot_bgcolor='#010103', width=500, height=760,
                  xaxis_visible=False, yaxis_visible=False, showlegend=False, margin=dict(l=0,r=0,t=0,b=0))

# -------------------------------------- Network Plot --------------------------------------

# Create network
networkGraphInterests = graphNetwork.createNetworkInterests()
networkFigureInterests = graphNetwork.plotlyNetworkInterests(networkGraphInterests)

networkFigureInterests.update_layout(
    plot_bgcolor='black',  # Sets the plot background color to black
    paper_bgcolor='black',  # Sets the background color of the entire figure to black
    font=dict(color='white')  # Changes the font color to white for better contrast
)

# Create network
networkGraphEntities = graphNetwork.createNetworkEntities()
networkFigureEntities = graphNetwork.plotlyNetworkEntities(networkGraphEntities)

networkFigureEntities.update_layout(
    plot_bgcolor='black',  # Sets the plot background color to black
    paper_bgcolor='black',  # Sets the background color of the entire figure to black
    font=dict(color='white')  # Changes the font color to white for better contrast
)

# -------------------------------------- Insights Plots --------------------------------------

# Interests 

# Plot 1
figUniqueInterests = datasetPreprocessingInsights.createFigUniqueInterests()

# Plot 2
figAverageInterests = datasetPreprocessingInsights.createFigAverageInterests()

# Plot 3
figBiggestInterestAreas = datasetPreprocessingInsights.createFigBiggestInterestAreas()


# Spendings

figEmployeePie = datasetPreprocessingInsights.createFigEmployeesPie()

# Plot 1
figSpendingsPie = datasetPreprocessingInsights.createFigSpendingsPie()

# Plot 2
figSpendingsScatter = datasetPreprocessingInsights.createFigSpendingsScatter()

# Plot 3
figSpendingPerEmployee = datasetPreprocessingInsights.createFigSpendingsPerEmployee()



# Entities

# Plot 1
figNumberOfEntities = datasetPreprocessingInsights.createFigNumberOfEntities()

# Plot 2
figAverageEmployees = datasetPreprocessingInsights.createFigAverageEmployees()

# Plot 3
figInterestsPerEntity = datasetPreprocessingInsights.createFigInterestPerEntity()



# Create a Dash container
app.layout = dbc.Container([
    # -------------------------------------- NAVIGATION & FILTERS --------------------------------------

    html.Div([
        # Title & Info
        html.Div([
            # Title
            html.H1([ html.Span("Lobbyism"), html.Br(),html.Span("in Germany")]),
            # Info text
            html.P("This dashboard shows selected insights from the official German parliament lobby register. It also provides an explorative feature, that allows users to search a cleaned version of the lobby dataset, as well as a network that reveals connections between different entities and their interests.")
        ],style={"vertical-alignment": "top", 'margin-bottom': 20, "height": 270}),

        # Tab selection
        html.Div([
            #Radiobuttons
            html.Div(
                dbc.RadioItems(
                    id='radio-button-group',
                    className='btn-group',
                    inputClassName='btn-check',
                    labelClassName="btn btn-outline-light",
                    labelCheckedClassName="btn btn-light",
                    options=[
                        {"label": "Insights", "value": 'INSIGHTS'},
                        {"label": "Explore", "value": 'EXPLORE'},
                        {"label": "Network", "value": 'NETWORK'}
                    ],
                    value='INSIGHTS',
                    style={'width': '100%'}
                ), 
                style={'width': 312}
            ),
            #About button
            html.Div(
                # Button
                dbc.Button("About", id="open-about-modal", className="btn btn-info", n_clicks=0), 
                style={'width': 104}),
                # About Modal
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle("About")),
                    dbc.ModalBody("..."),
                    dbc.ModalFooter([
                        html.A("GIT", href="https://github.com/PHANTOMIZER420/Lobbyism-DashboardV2", className="btn btn-primary"),
                    dbc.Button("Close", id="close-about-modal", className="ms-auto", n_clicks=0)
                    ]),
                ], id="about-modal", is_open=False),  # Initially hidden
        ], 
        style={'display': 'flex'}),

        # -------------------------------------- Filter Section --------------------------------------

        # Filter section for insights
        html.Div([

            # Chapter selection dropdown
            html.Div([
                dcc.Dropdown(
                    id='insights-chapter-dropdown',
                    options=[
                        {'label': 'Interests', 'value': 'INTERESTS'},
                        {'label': 'Spendings', 'value': 'SPENDINGS'},
                        {'label': 'Entities 1', 'value': 'ENTITIES_1'},
                        {'label': 'Entities 2', 'value': 'ENTITIES_2'}
                    ],
                    value='INTERESTS',
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black'}
                ),
                #insights chapter texts
                html.P(datasetPreprocessingInsights.selectInsightsText(1), id='interests-text'),
                html.P(datasetPreprocessingInsights.selectInsightsText(2), id='spendings-text'),
                html.P(datasetPreprocessingInsights.selectInsightsText(3), id='entities-text'),
            ]),

        ],
        id='filter-section-insights'
        ),

         # Filter section for network
        html.Div([

            # Network topic selection dropdown
            html.Div([
                dcc.Dropdown(
                    id='network-chapter-dropdown',
                    options=[
                        {'label': 'Interconnections of top level interests and entities', 'value': 'INTERESTS'},
                        {'label': 'Entities and the distribution of their unique interests', 'value': 'ENTITIES'},
                    ],
                    value='INTERESTS',
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black', 'display': 'none'}
                )
            ]),

        ],
        id='filter-section-network'
        ),

        # Filter section explore
        html.Div([

            # Fiscal Year Dropdown
            html.Div([
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

            # Employee Dropdown
            html.Div([
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
            # Spending Dropdown
            html.Div([
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
            # Spending/Employee Dropdown
            html.Div([
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
            # Entity Dropdown
            html.Div([
                html.H2('Entity'),
                dcc.Dropdown(
                    id='entity-dropdown',
                    options=[
                        {'label': i, 'value': i} for i in sorted(cDf['Entity'].unique())
                    ],
                    clearable=True,
                    optionHeight=40,
                    className='customDropdown',
                    style={'background-color': 'black', 'white-space': 'nowrap', 'text-overflow': 'ellipsis'}
                )
            ])
        ], 
        id='filter-section-explore',
        ),
    ], 
    style={'width': 340, 'margin-top': 30, 'margin-right': 5, 'margin-left': 15}),


    # -------------------------------------- Insights Tab --------------------------------------

    # Insights container
    html.Div([

        # -------------------------------------- Interests Chapter
        html.Div(
        [
            #Left Column
            dbc.Col(
            [
                #First Row
                dbc.Row(
                    html.Div(
                        #Mean/Median Interests
                        dcc.Graph(figure=figAverageInterests)
                    )
                ),
                #Second Row
                dbc.Row(
                    html.Div(
                        #Biggest interests areas
                        dcc.Graph(figure=figBiggestInterestAreas)
                    )
                ),
            ]
            ),
            #Right Column
            dbc.Col(
                html.Div(
                    #Unique Interests 
                    dcc.Graph(figure=figUniqueInterests)
                )
            ),
        ],
        id='insights-interests',
        ),

        # -------------------------------------- Spendings Chapter
        html.Div(
        [
            #Left Column
            dbc.Col(
            [
                #First Row
                dbc.Row(
                    html.Div(
                        #Spendings per employee
                        dcc.Graph(figure=figSpendingPerEmployee)
                    )
                ),
                #Second Row
                dbc.Row(
                    html.Div(
                        #Sepndings Scatter
                        dcc.Graph(figure=figSpendingsScatter)
                    )
                ),
            ]
            ),
            #Right Column
            dbc.Col([
                dbc.Row(
                    html.Div(
                        #Spendings Pie 
                        dcc.Graph(figure=figSpendingsPie)
                    )
                ),
                dbc.Row(
                    html.Div(
                        #Spendings Pie 
                        dcc.Graph(figure=figEmployeePie)
                    )
                ),
            ]),
        ],
        id='insights-spendings',
        ),

        # -------------------------------------- Entities 1 Chapter
        html.Div(
            [
                html.Div(
                    #Number of entities
                    dcc.Graph(figure=figNumberOfEntities)
                ),
                html.Div(                        #Average Employees
                    dcc.Graph(figure=figAverageEmployees)
                )
        ],
        id='insights-entities-1',
        ),

        # -------------------------------------- Entities 2 Chapter
        html.Div(
        [           
            html.Div(
                #Interests per Entity
                dcc.Graph(figure=figInterestsPerEntity)
            )            
        ],
        id='insights-entities-2',
        ),

    ],
    id='insights-tab',
    style={
            'display': 'none',
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        }
    ),


    # -------------------------------------- Explore Tab --------------------------------------
    # Explore Tab container
    html.Div([
        html.Div([ 
            html.H2('Column Filter:'),
                # Column filtering
                # Original Dataset Dropdown
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
                    style={'display':'none', 'background-color': 'black'}
                ),
                # Clean Dataset Dropdown
                dcc.Dropdown(
                    id='column-dropdown-filter-cleaned',
                    options=[{'label': col, 'value': col} for col in sorted(cDf.columns)],
                    clearable=True,
                    multi=True,
                    value=[cDf.columns[0],   # Name
                           cDf.columns[18],  # AVG Spending
                           cDf.columns[21],  # Fiscal Year
                           cDf.columns[4]],  # Entity
                    optionHeight=40,
                    className='customDropdown',
                    style={'display':'none', 'background-color': 'black'}
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
                ],
                style={'margin-top': 15}),
                # Display data tables
                ],
                # Style for the tables
                style={'width': 990, 'margin-top': 63}),
        ],
        id='explore-tab',
        style={
            'display': 'none',
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        }),


    # -------------------------------------- Network Tab --------------------------------------

    # Insights container
    html.Div([

        html.Div(
        [
            html.Div(dcc.Graph(figure=networkFigureInterests))
        ],
        id='network-interests',
        style={
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        }), 

        html.Div(
        [
            html.Div(dcc.Graph(figure=networkFigureEntities))
        ],
        id='network-entities',
        style={
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        })
    ],
    id='network-tab',
        style={
            'display': 'none',
            'width': 'auto', 
            'margin-top': 50,
            'margin-right': 25,
            'margin-bottom': 25,
        }
    ),

],
    # Style for the dash container
    fluid=True,
    style={'display': 'flex', 'background':'black'},
    className='dashboard-container')


#-------------------------------------- CALLBACKS -------------------------------------

# -------------------------------------- Insights --------------------------------------

# Define callback to toggle insights tab visibility
@app.callback(
    [Output('insights-tab', 'style'), # Show the insights
     Output('filter-section-insights', 'style')], #Show the insights filter
    [Input('radio-button-group', 'value')] # Radio button for selecting tabs
)
   
# Toggle insights tab visibility
def toggle_insights_tab_visibility(selected_tab):
    if selected_tab == 'INSIGHTS':
        return ({'display': 'flex'}, 
                {'display': 'block', 'margin-right': '20px', 'margin-top':'30px', 'background':'black'}
                )  # Change to 'flex' to make it visible
    else:
        return ({'display': 'none'}, 
                {'display': 'none'})  # Change to 'none' to hide it
    

# Inisghts chapter selection
@app.callback(
    [Output('insights-interests', 'style'),
     Output('insights-spendings', 'style'),
     Output('insights-entities-1', 'style'),
     Output('insights-entities-2', 'style'),
     Output('interests-text', 'style'),
     Output('spendings-text', 'style'),
     Output('entities-text', 'style')],
    [Input('insights-chapter-dropdown', 'value')]
)
def update_chapter_visibility(selected_chapter):
    # Default styles for hidden and visible chapters
    hidden_style = {'display': 'none'}
    visible_style = {'display': 'flex'}
    
    # Initialize all chapters to be hidden
    interests_style = hidden_style
    spendings_style = hidden_style
    entities_1_style = hidden_style
    entities_2_style = hidden_style
    interests_style_text = hidden_style
    spendings_style_text = hidden_style
    entities_style_text = hidden_style
    
    # Update the style based on the selected chapter
    if selected_chapter == 'INTERESTS':
        interests_style = visible_style
        interests_style_text = visible_style
    elif selected_chapter == 'SPENDINGS':
        spendings_style = visible_style
        spendings_style_text = visible_style
    elif selected_chapter == 'ENTITIES_1':
        entities_1_style = visible_style
        entities_style_text = visible_style
    elif selected_chapter == 'ENTITIES_2':
        entities_2_style = visible_style
        entities_style_text = visible_style

    # Return updated styles for each chapter    
    return interests_style, spendings_style, entities_1_style, entities_2_style, interests_style_text, spendings_style_text, entities_style_text  

# -------------------------------------- Explore --------------------------------------    

# Define callback to toggle explore tab visibility
@app.callback(
    [Output('explore-tab', 'style'), # Show the explore tab
    Output('filter-section-explore', 'style')], # Show the filter section      
    [Input('radio-button-group', 'value')] # Radio button for selecting tabs
)
   
# Toggle explore tab visibility
def toggle_explore_tab_visibility(selected_tab):
    if selected_tab == 'EXPLORE':
        return ({'display': 'flex'}, {'display': 'block', 'margin-right': '20px', 'margin-top': '30px', 'background':'black'}) # Change to 'flex' to make it visible
    else:
        return ({'display': 'none'}, {'display': 'none'}) # Change to 'none' to hide it
    
# Table Tabs 

@app.callback(
    [Output('table-tabs-content', 'children'),
     Output('column-dropdown-filter-cleaned', 'style'),
     Output('column-dropdown-filter-original', 'style')],
    [Input('table-tabs', 'value')]
)

def render_content(tab):
    if tab == 'cleaned-tab':
        return dash_table.DataTable(
                    id='cleaned-data-table',
                    columns=[{'name': i, 'id': i, 'deletable': True} for i in sorted(cDf.columns)],
                    sort_by=[],
                    filter_action='native',
                    sort_action='native',
                    style_data={
                    'overflow': 'ellipsis',
                    },
                    style_table={'overflowX': 'auto', 'overflowY': 'auto', 'height': 511},
                    style_header={'backgroundColor': 'black','color': '#3498db','fontWeight': 'bold', 'fontFamily': 'sans-serif'},
                    style_cell={'backgroundColor': 'black','color': 'white','textAlign': 'left', 'fontFamily': 'sans-serif'},
                ), {'display':'block', 'background-color': 'black'}, {'display':'none', 'background-color': 'black'}
    
    elif tab == 'original-tab':
        return dash_table.DataTable(
                    id='original-data-table',
                    columns=[{'name': i, 'id': i, 'deletable': True} for i in sorted(oDf.columns)],
                    sort_by=[],
                    filter_action='native',
                    sort_action='native',
                    css=[{
                        'selector': 'table',
                        'rule': 'table-layout: fixed'  # note - this does not work with fixed_rows
                    }],
                    style_data={
                    'width': '{}%'.format(100. / len(oDf.columns)),
                    'textOverflow': 'hidden'
                    },
                    style_table={'overflowX': 'auto', 'overflowY': 'auto', 'height': 511},
                    style_header={'backgroundColor': 'black','color': '#3498db','fontWeight': 'bold', 'fontFamily': 'sans-serif'},
                    style_cell={'backgroundColor': 'black','color': 'white','textAlign': 'left', 'fontFamily': 'sans-serif'},
                ), {'display':'none', 'background-color': 'black'}, {'display':'block', 'background-color': 'black'}
    
# -------------------------------------- Network --------------------------------------

# Define callback to toggle network tab visibility
@app.callback(
    [Output('network-tab', 'style'), # Show the network tab
    Output('network-chapter-dropdown', 'style')],      
    Input('radio-button-group', 'value') # Radio button for selecting tabs
)

# Toggle network tab visibility
def toggle_network_tab_visibility(selected_tab):
    if selected_tab == 'NETWORK':
        return ({'display': 'flex'}, {'display': 'block', 'margin-right': '20px', 'margin-top': '30px', 'background':'black'}) # Change to 'flex' to make it visible
    else:
        return ({'display': 'none'}, {'display': 'none'}) # Change to 'none' to hide it

    # Network chapter selection
@app.callback(
    [Output('network-interests', 'style'),
     Output('network-entities', 'style'),],
    [Input('network-chapter-dropdown', 'value')]
)

def update_chapter_visibility(selected_chapter):
    # Default styles for hidden and visible chapters
    hidden_style = {'display': 'none'}
    visible_style = {'display': 'flex'}
    
    # Initialize all chapters to be hidden
    interests_style = hidden_style
    entities_style = hidden_style
    
    # Add more chapters as needed
    
    # Update the style based on the selected chapter
    if selected_chapter == 'INTERESTS':
        interests_style = visible_style
    elif selected_chapter == 'ENTITIES':
        entities_style = visible_style
    
    return interests_style, entities_style # Return updated styles for each chapter 


# -------------------------------------- Update Original Datatable --------------------------------------

# Define callback to update table
@app.callback(
    [Output('original-data-table', 'data'),
    Output('original-data-table', 'columns')], # Update columns dynamically
    [Input('column-dropdown-filter-original', 'value')] # Update table based on selected columns
)

# Update table
def update_table(selected_columns):
    # Filter DataFrame based on selected columns
    if selected_columns:
        oDff = oDf[selected_columns]
    else:
        oDff = oDf.copy()

    # Prepare columns for the DataTable
    columns = [{'name': i, 'id': i} for i in selected_columns] if selected_columns else [{'name': i, 'id': i} for i in oDf.columns]
    
    # Return data and columns
    return oDff.to_dict('records'), columns


# -------------------------------------- Update Cleanded Datatable ----------------------------------

# -------------------------------------- Filter Values Cleaned Datatable --------------------------------------

@app.callback(
    [Output('cleaned-data-table', 'data'),
    Output('cleaned-data-table', 'columns')], # Update columns dynamically
    [
    Input('column-dropdown-filter-cleaned', 'value'),
    Input('fiscal-year-dropdown', 'value'),
    Input('average-employees-dropdown', 'value'),
    Input('average-spending-dropdown', 'value'),
    Input('spending-per-employee-dropdown', 'value'),
    Input('entity-dropdown', 'value')] # Update table based on selected columns
)
def update_table(selected_columns, selected_year, selected_employees, selected_spending, selected_spending_per_employee, selected_entity):
    filtered_df = cDf.copy() 
    
    # Filter by year
    if selected_year:
        year_mapping = {1: 2021, 2: 2022, 3: 2023}
        filtered_df = filtered_df[filtered_df['Fiscal Year Start'].dt.year == year_mapping[selected_year]]
    
    # Filter by average employees
    if selected_employees:
        if selected_employees == 1:
            filtered_df = filtered_df[filtered_df['Ø Employees'] > 5]
        elif selected_employees == 2:
            filtered_df = filtered_df[filtered_df['Ø Employees'] > 10]
        elif selected_employees == 3:
            filtered_df = filtered_df[filtered_df['Ø Employees'] > 50]
        elif selected_employees == 4:
            filtered_df = filtered_df[filtered_df['Ø Employees'] > 100]
    
    # Filter by average spending
    if selected_spending:
        if selected_spending == 1:
            filtered_df = filtered_df[filtered_df['Ø Amount'] > 5000]
        elif selected_spending == 2:
            filtered_df = filtered_df[filtered_df['Ø Amount'] > 10000]
        elif selected_spending == 3:
            filtered_df = filtered_df[filtered_df['Ø Amount'] > 50000]
        elif selected_spending == 4:
            filtered_df = filtered_df[filtered_df['Ø Amount'] > 100000]
        elif selected_spending == 5:
            filtered_df = filtered_df[filtered_df['Ø Amount'] > 500000]
        elif selected_spending == 6:
            filtered_df = filtered_df[filtered_df['Ø Amount'] > 1000000]

    # Filter by spending per employee
    if selected_spending_per_employee:
        if selected_spending_per_employee == 1:
            filtered_df = filtered_df[filtered_df['Ø Amount/Employee'] > 1000]
        elif selected_spending_per_employee == 2:
            filtered_df = filtered_df[filtered_df['Ø Amount/Employee'] > 5000]
        elif selected_spending_per_employee == 3:
            filtered_df = filtered_df[filtered_df['Ø Amount/Employee'] > 10000]
        elif selected_spending_per_employee == 4:
            filtered_df = filtered_df[filtered_df['Ø Amount/Employee'] > 50000]
        elif selected_spending_per_employee == 5:
            filtered_df = filtered_df[filtered_df['Ø Amount/Employee'] > 100000]
        

    # Filter by selected entity
    if selected_entity:
        # Ensure selected_entity is treated as a list
        entity_list = [selected_entity] if isinstance(selected_entity, str) else selected_entity
        filtered_df = filtered_df[filtered_df['Entity'].isin(entity_list)]

    # Filter DataFrame based on selected columns
    if selected_columns:
        cDff = filtered_df[selected_columns]
    else:
        cDff = filtered_df.copy()

    # Prepare columns for the DataTable
    columns = [{'name': i, 'id': i} for i in selected_columns] if selected_columns else [{'name': i, 'id': i} for i in filtered_df.columns]
    
    # Return data and columns
    return cDff.to_dict('records'), columns


# -------------------------------------- About Modal --------------------------------------
@app.callback(
    Output("about-modal", "is_open"),
    [Input("open-about-modal", "n_clicks"), 
     Input("close-about-modal", "n_clicks")],
    [State("about-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# -------------------------------------- Run the app --------------------------------------

# Run the app on port 8050
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
