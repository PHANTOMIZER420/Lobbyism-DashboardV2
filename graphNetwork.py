# Import Libraries
import networkx as nx
import pandas as pd 
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datasetPreprocessingInsights import dfTIG, dfEntities

# Network Superinterrest
def createNetworkInterests() :

    df = dfTIG()

    # Create an empty graph
    GI = nx.Graph()

    # Add nodes with attributes from the dataset
    for index, row in df.iterrows():
        # Assuming 'Entity' is a column in your DataFrame for node names
        # Add or update node for EntityA
        if not GI.has_node(row['Tätigkeit']):
            GI.add_node(row['Tätigkeit'])
        else:
            # Update node attributes if necessary
            pass

        # Add or update node for EntityB
        if not GI.has_node(row['Supercategory']):
            GI.add_node(row['Supercategory'])
        else:
            # Update node attributes if necessary
            pass

        # Add edges between EntityA and EntityB
        # This assumes each row in your DataFrame represents a relationship between EntityA and EntityB
        GI.add_edge(row['Tätigkeit'], row['Supercategory'])

    return GI

def plotlyNetworkInterests(GI):
    pos = nx.spring_layout(GI)  # Generate layout for nodes

    # Edge trace
    edge_x = []
    edge_y = []
    for edge in GI.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='blue'),
        hoverinfo='none',
        mode='lines')

    # Node trace
    node_x = []
    node_y = []
    text = []
    node_color = []  # Store colors for each node

    # Calculate degree for each node and use it for coloring
    degrees = dict(GI.degree())
    max_degree = max(degrees.values())
    min_degree = min(degrees.values())
    # Normalize node degrees to map to colorscale
    for node in GI.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)
        node_degree = degrees[node]
        # Normalize degree to [0,1] for colorscale
        normalized_degree = (node_degree - min_degree) / (max_degree - min_degree)
        node_color.append(normalized_degree)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            color=node_color,
            size=10,
            colorbar=dict(
                thickness=20,
                title='Node Degree',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # Figure setup
    figInterests = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        width=900, 
                        height=796,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return figInterests

# Network Entities

# Network Superinterrest
def createNetworkEntities() :

    df = dfEntities(0)

    # Create an empty graph
    GE = nx.Graph()

    # Add nodes with attributes from the dataset
    for index, row in df.iterrows():
        # Assuming 'Entity' is a column in your DataFrame for node names
        # Add or update node for EntityA
        if not GE.has_node(row['Entity type']):
            GE.add_node(row['Entity type'])
        else:
            # Update node attributes if necessary
            pass

        # Add or update node for EntityB
        if not GE.has_node(row['Spending per Employee']):
            GE.add_node(row['Spending per Employee'])
        else:
            # Update node attributes if necessary
            pass

        # Add edges between EntityA and EntityB
        # This assumes each row in your DataFrame represents a relationship between EntityA and EntityB
        GE.add_edge(row['Entity type'], row['Spending per Employee'])

    return GE

def plotlyNetworkEntities(GE):
    pos = nx.spring_layout(GE)  # Generate layout for nodes

    # Edge trace
    edge_x = []
    edge_y = []
    for edge in GE.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='red'),
        hoverinfo='none',
        mode='lines')

    # Node trace
    node_x = []
    node_y = []
    text = []
    node_color = []  # Store colors for each node

    # Calculate degree for each node and use it for coloring
    degrees = dict(GE.degree())
    max_degree = max(degrees.values())
    min_degree = min(degrees.values())
    # Normalize node degrees to map to colorscale
    for node in GE.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)
        node_degree = degrees[node]
        # Handle zero division error
        if max_degree - min_degree != 0:
            normalized_degree = (node_degree - min_degree) / (max_degree - min_degree)
        else:
            normalized_degree = 0
        node_color.append(normalized_degree)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            color=node_color,
            size=10,
            colorbar=dict(
                thickness=20,
                title='Node Degree',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # Figure setup
    figEntities = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=0),
                        width=900, 
                        height=796,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )
    
    return figEntities