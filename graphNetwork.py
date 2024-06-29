# Import Libraries
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def createNetwork(cDf) :

    # Create an empty graph
    G = nx.Graph()

    # Add nodes with attributes from the dataset
    for index, row in cDf.iterrows():
        # Assuming 'Entity' is a column in your DataFrame for node names
        # Add or update node for EntityA
        if not G.has_node(row['Entity']):
            G.add_node(row['Entity'])
        else:
            # Update node attributes if necessary
            pass

        # Add or update node for EntityB
        if not G.has_node(row['Interests']):
            G.add_node(row['Interests'])
        else:
            # Update node attributes if necessary
            pass

        # Add edges between EntityA and EntityB
        # This assumes each row in your DataFrame represents a relationship between EntityA and EntityB
        G.add_edge(row['Entity'], row['Interests'])

    return G

def plotlyNetwork(G):
    pos = nx.spring_layout(G)  # Generate layout for nodes

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])  # Add None to create a break between lines
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='blue'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)  # Assuming you want to display the node's name

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=1, t=0),
                        width=700, 
                        height=700,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    return fig