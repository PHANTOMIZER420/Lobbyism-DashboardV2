from fuzzywuzzy import process
import Levenshtein as lev
import pandas as pd
import plotly.express as px
import re

# Read cleaned dataset
filepath = '/Users/phantom/Documents/GitHub/Lobbyism-DashboardV2/Datasets/cleanedLobbyregister2024.csv'
cleanedDataset = pd.read_csv(filepath)

# -------------------------------------- Chapter 1 --------------------------------------


# Plot 1

def createFigUniqueInterests():
    # Split the values in "Interessen- und Vorhabenbereiche" column and create new rows
    df_exploded = cleanedDataset

    df_exploded['Interessen'] = cleanedDataset['Interessen'].str.split('; ')
    df_exploded = df_exploded.explode('Interessen')

    # Ensure "Interessen" is of string type, then truncate strings to the first 20 characters
    df_exploded['Tätigkeit'] = df_exploded['Tätigkeit'].astype(str).apply(lambda x: x[:15])

    # Group by "Tätigkeit" and count the number of unique "Interessen" for each
    taetigkeit_interessen_counts = df_exploded.groupby('Tätigkeit')['Interessen'].nunique().reset_index()
    taetigkeit_interessen_counts.columns = ['Tätigkeit', 'Unique_Interessen_Count']

    # Create a bubble chart using Plotly
    fig= px.bar(taetigkeit_interessen_counts, x='Tätigkeit', y='Unique_Interessen_Count', #size='Unique_Interessen_Count',
                        color='Unique_Interessen_Count', # Color the bubbles according to the count of unique interests
                        title='Number of Unique Interests per Entity',
                        width=526,
                        height=798,
                        labels={'Unique_Interessen_Count': 'Unique Interests', 'Tätigkeit': 'Entity'})

    fig.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black',
    })

    return fig


#Plot 2

def createFigAverageInterests():

        # Count the number of individual interest areas
    def count_interests(row):
        return len(row['Interessen'])  # Splitting on semicolon to count interests

    cleanedDataset['Nummer Interessen'] = cleanedDataset.apply(count_interests, axis=1)

    df_entities = cleanedDataset.value_counts('Tätigkeit').to_frame()
    df_entities['Total Spending'] = cleanedDataset.groupby('Tätigkeit')['Betrag'].sum()
    df_entities['Total Employees'] = cleanedDataset.groupby('Tätigkeit')['Beschäftigte'].sum()
    df_entities['Spending per Employee'] = df_entities['Total Spending']/df_entities['Total Employees']
    df_entities['Median Interests'] = cleanedDataset.groupby('Tätigkeit')['Nummer Interessen'].median()
    df_entities['Mean Interests'] = cleanedDataset.groupby('Tätigkeit')['Nummer Interessen'].mean()
    df_entities['Median Employees'] = cleanedDataset.groupby('Tätigkeit')['Beschäftigte'].median()
    df_entities['Mean Employees'] = cleanedDataset.groupby('Tätigkeit')['Beschäftigte'].mean()


    def truncate_label(label, max_length=15):
        return label if len(label) <= max_length else label[:max_length] + '...'


    # Funktion zum Kürzen der Labels
    def truncate_label(label, max_length=15):
        return label if len(label) <= max_length else label[:max_length] + '...'

    # Labels kürzen
    df_entities = df_entities.reset_index().rename(columns={"index": "Entity type", "count": "Number of entities"})
    df_entities = df_entities.rename(columns={"Tätigkeit": "Entity type"})

    # Labels kürzen
    df_entities['short_entity'] = [truncate_label(label) for label in df_entities['Entity type']]

    fig = px.bar(
    df_entities, 
    x='Entity type', 
    y=[df_entities['Mean Interests'], 
    df_entities['Median Interests']], 
    barmode="group",
    hover_name='Entity type',
    hover_data=['Entity type', 'Number of entities']
    )

    fig.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black',
        },
        width=500,
        height=399,
        xaxis=dict(
            tickmode='array',
            tickvals=df_entities['Entity type'],
            ticktext=df_entities['short_entity']
    )
    )

    return fig


#   Plot 3

def createFigBiggestInterestAreas():

    df_exploded = cleanedDataset

    df_exploded['Interessen'] = cleanedDataset['Interessen'].str.split('; ')
    df_exploded = df_exploded.explode('Interessen')

    # A function to homogenize the interests
    unique_interests = df_exploded['Interessen'].unique()
    def homogenize_interests(interests, max_distance=2):
        interest_map = {}
        for interest in interests:
            # Find the closest match with the existing interests already in the map
            closest_matches = process.extract(interest, interest_map.keys(), limit=1)
            if closest_matches and lev.distance(interest, closest_matches[0][0]) < max_distance:
                # If a match is found within the distance threshold, map to the existing interest
                interest_map[interest] = interest_map[closest_matches[0][0]]
            else:
                # Otherwise add it as a new unique interest
                interest_map[interest] = interest
        return interest_map

    interest_map = homogenize_interests(unique_interests)
    df_exploded['Interessen'] = df_exploded['Interessen'].map(interest_map)

    # Flatten the list of interests in each row, considering empty interest rows
    flattened_interests = df_exploded['Interessen'].astype(str)

    # Remove leading and trailing punctuation
    flattened_interests = flattened_interests.str.replace(r'^\W+|\W+$', '', regex=True)

    # Strip leading and trailing whitespace
    flattened_interests = flattened_interests.str.strip()

    # Drop any empty interests
    flattened_interests = flattened_interests[flattened_interests != '']
    

    # Count the occurrences of each interest
    interest_counts = flattened_interests.value_counts()

    interest_counts_df = interest_counts.reset_index()
    interest_counts_df.columns = ['Interest', 'Count']
    interest_counts_df = interest_counts_df.sort_values(by='Count', ascending=False)
    interest_counts_df = interest_counts_df[interest_counts_df['Count'] > 434]

    # Create a bar chart using Plotly
    fig = px.bar(interest_counts_df, y='Count', x='Interest', orientation='v',
                title='Biggest interest areas for Lobbies in Germany', 
                labels={'Count': 'Number of lobbies', 'Interest': ''})

    fig.update_yaxes(range=[0, 800], dtick=200)

    fig.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black',
        },
        width=500,
        height=399
    )

    return fig