from fuzzywuzzy import process
import Levenshtein as lev
import pandas as pd

# Read cleaned dataset
filepath = '/Users/phantom/Documents/GitHub/Lobbyism-DashboardV2/Datasets/cleanedLobbyregister2024.csv'
cleanedDataset = pd.read_csv(filepath)

def dfExploded():
    # Split the values in "Interessen- und Vorhabenbereiche" column and create new rows
    df_exploded = cleanedDataset

    df_exploded['Interessen'] = cleanedDataset['Interessen'].str.split('; ')
    df_exploded = df_exploded.explode('Interessen')

    return df_exploded