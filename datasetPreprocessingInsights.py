from fuzzywuzzy import process
import Levenshtein as lev
import pandas as pd
import plotly.express as px

# Read cleaned dataset
filepath = '/Users/phantom/Documents/GitHub/Lobbyism-DashboardV2/Datasets/cleanedLobbyregister2024.csv'
cleanedDataset = pd.read_csv(filepath)

def createFigUniqueInterests():
    # Split the values in "Interessen- und Vorhabenbereiche" column and create new rows
    df_exploded = cleanedDataset

    df_exploded['Interessen'] = cleanedDataset['Interessen'].str.split('; ')
    df_exploded = df_exploded.explode('Interessen')

    # Ensure "Interessen" is of string type, then truncate strings to the first 20 characters
    df_exploded['Tätigkeit'] = df_exploded['Tätigkeit'].astype(str).apply(lambda x: x[:25])

    # Group by "Tätigkeit" and count the number of unique "Interessen" for each
    taetigkeit_interessen_counts = df_exploded.groupby('Tätigkeit')['Interessen'].nunique().reset_index()
    taetigkeit_interessen_counts.columns = ['Tätigkeit', 'Unique_Interessen_Count']

    # Create a bubble chart using Plotly
    fig= px.bar(taetigkeit_interessen_counts, x='Tätigkeit', y='Unique_Interessen_Count', #size='Unique_Interessen_Count',
                        color='Unique_Interessen_Count', # Color the bubbles according to the count of unique interests
                        title='Number of Unique Interests per Tätigkeit',
                        width=625,
                        height=750,
                        labels={'Unique_Interessen_Count': 'Number of Unique Interests', 'Tätigkeit': 'Tätigkeit'})

    return fig

def createFigAverageInterests():

        # Count the number of individual interest areas
    def count_interests(row):
        return len(row['Interessen'])  # Splitting on semicolon to count interests

    cleanedDataset['Nummer Interessen'] = cleanedDataset.apply(count_interests, axis=1)

    df_mean_interests = cleanedDataset.groupby('Tätigkeit')['Nummer Interessen'].mean().to_frame()
    df_mean_interests['Number Entities'] = cleanedDataset.value_counts('Tätigkeit')
    df_mean_interests['Median Interests'] = cleanedDataset.groupby('Tätigkeit')['Nummer Interessen'].median()
    df_mean_interests = df_mean_interests.reset_index().rename(columns={"index": "Entity type"})

    df_spending_per_entity = cleanedDataset.groupby('Tätigkeit')['Betrag'].sum().to_frame()
    df_spending_per_entity['Total Employees'] = cleanedDataset.groupby('Tätigkeit')['Beschäftigte'].sum()
    df_spending_per_entity = df_spending_per_entity.reset_index().rename(columns={"index": "Entity type"})
    df_spending_per_entity

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

    fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=df_entities['Entity type'],
        ticktext=df_entities['short_entity']
    )
    )

    return fig