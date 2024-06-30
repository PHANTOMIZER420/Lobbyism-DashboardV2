from fuzzywuzzy import process
import Levenshtein as lev
import pandas as pd
import plotly.express as px
import re


# Read cleaned dataset
filepath = '/Users/phantom/Documents/GitHub/Lobbyism-DashboardV2/Datasets/cleanedLobbyregister2024.csv'
cleanedDataset = pd.read_csv(filepath)

def truncate_label(label, max_length=15):
        return label if len(label) <= max_length else label[:max_length] + '...'

# 
def dfEntities(type):
# Count the number of individual interest areas
    
    def count_interests(row):
        if type == 1:
            return len(row['Interessen'])  # Splitting on semicolon to count interests
        else:
            if isinstance(row['Interessen'], str):
                return len(row['Interessen'].split(';'))  # Assuming interests are separated by semicolons
            else:
                return 0  # Return 0 if 'Interessen' is NaN or not a string

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

    return df_entities

# -------------------------------------- Chapter 1 --------------------------------------


# Plot 1

def createFigUniqueInterests():
    # Split the values in "Interessen- und Vorhabenbereiche" column and create new rows
    df_exploded = cleanedDataset.copy()

    df_exploded['Interessen'] = cleanedDataset['Interessen'].str.split('; ')
    df_exploded = df_exploded.explode('Interessen')

    # Ensure "Interessen" is of string type, then truncate strings to the first 20 characters
    #df_exploded['Tätigkeit'] = df_exploded['Tätigkeit'].apply(lambda x: x[:15])

    df_exploded['short_entity'] = [truncate_label(label) for label in df_exploded['Tätigkeit']]

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

    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                       'paper_bgcolor': 'rgba(0,0,0,0)',
                       },
                       xaxis=dict(
                           tickmode='array',
                           tickvals=taetigkeit_interessen_counts['Tätigkeit'],
                           ticktext=taetigkeit_interessen_counts['short_entity']
                        )
    )

    return fig


#Plot 2

def createFigAverageInterests():

    df_entities = dfEntities(1)

    fig = px.bar(
        df_entities, 
        x='Entity type', 
        y=[df_entities['Mean Interests'], 
        df_entities['Median Interests']], 
        barmode="group",
        hover_name='Entity type',
        hover_data=['Entity type', 'Number of entities']
    )

    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                       'paper_bgcolor': 'rgba(0,0,0,0)'},
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

    df_exploded = cleanedDataset.copy()

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
    flattened_interests = df_exploded['Interessen']
    # Remove leading and trailing punctuation
    flattened_interests = flattened_interests.str.replace('^\W+|\W+$', '', regex=True)

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

    interest_counts_df['shortInterest'] = [truncate_label(label) for label in interest_counts_df['Interest']]

    # Create a bar chart using Plotly
    fig = px.bar(interest_counts_df, y='Count', x='Interest', orientation='v',
                title='Biggest interest areas for Lobbies in Germany', 
                labels={'Count': 'Number of lobbies', 'Interest': ''})

    fig.update_yaxes(range=[0, 800], dtick=200)

    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                       'paper_bgcolor': 'rgba(0,0,0,0)'},
        width=500,
        height=399,
        xaxis=dict(
            tickmode='array',
            tickvals=interest_counts_df['Interest'],
            ticktext=interest_counts_df['shortInterest']
        )
    )


    return fig

# -------------------------------------- Chapter 2 --------------------------------------

# Plot 1

def createFigSpendingsPie():

    df_entities = dfEntities(0)

    figPie = px.pie(df_entities, values='Total Spending', hover_name='Entity type',  hole=0.3)
    figPie.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                          'paper_bgcolor': 'rgba(0,0,0,0)'},
                         uniformtext_minsize=12, 
                         uniformtext_mode='hide',
                         width=450,
                         height=800
    )
    
    figPie.update_traces(textposition='inside')

    return figPie


# Plot 2

def createFigSpendingsScatter():

    figScatter = px.scatter(cleanedDataset, x="Beschäftigte", y="Betrag", labels={'Name': "Name", 'Betrag': "Betrag", 'Beschäftigte': "Beschäftigte"}, color="Betrag", color_continuous_scale=px.colors.sequential.Bluered)

    figScatter.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black',
        },
        width=600,
        height=399
    )

    return figScatter

# Plot 3

def createFigSpendingsPerEmployee():

    df_entities = dfEntities(0)

    figSpendingPerEmployee = px.bar(df_entities, x='Entity type', hover_name='Entity type', y='Spending per Employee', color='Total Spending', color_continuous_scale=px.colors.sequential.Bluered)

    figSpendingPerEmployee.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black'},
        width=600,
        height=399,
        xaxis=dict(
            tickmode='array',
            tickvals=df_entities['Entity type'],
            ticktext=df_entities['short_entity']
        )
    )

    return figSpendingPerEmployee


# -------------------------------------- Chapter 3 --------------------------------------

# Plot 1

def createFigNumberOfEntities():#

    df_entities = dfEntities(0)

    fig = px.bar(df_entities, x='Entity type', y='Number of entities', hover_name='Entity type')

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


# Plot 2

def createFigAverageEmployees():

    df_entities = dfEntities(0)

    fig = px.bar(
    df_entities, 
    x='Entity type', 
    y=[df_entities['Mean Employees'], 
    df_entities['Median Employees']], 
    barmode="group",
    hover_name='Entity type',
    hover_data=['Entity type', 'Number of entities'],
    color_discrete_sequence=["green", "purple"] 
    )

    fig.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black'},
        width=500,
        height=399,
        xaxis=dict(
            tickmode='array',
            tickvals=df_entities['Entity type'],
            ticktext=df_entities['short_entity']
        )
    )

    return fig


#Plot 3

def createFigInterestPerEntity():

    df_exploded = cleanedDataset.copy()
    df_exploded['Interessen'] = df_exploded['Interessen'].astype(str)
    df_exploded['Interessen'] = df_exploded['Interessen'].str.split('; ')
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
    flattened_interests = df_exploded['Interessen']

    # Remove leading and trailing punctuation
    #flattened_interests = flattened_interests.str.replace('^\W+|\W+$', '', regex=True)

    # Strip leading and trailing whitespace
    flattened_interests = flattened_interests.str.strip()

    # Drop any empty interests
    flattened_interests = flattened_interests[flattened_interests != '']


    # Define the mapping of interests to supercategories based on the German Lobby registry website
    interest_to_supercategory = {
        'Arbeit und Beschäftigung': ['Arbeit und Beschäftigung', 'Arbeitsmarkt', 'Arbeitsrecht/Arbeitsbedingungen', 'Sonstiges im Bereich "Arbeit und Beschäftigung"'],
        'Außenpolitik und internationale Beziehungen': ['Außenpolitik und internationale Beziehungen', 'Außenpolitik', 'Auswärtige Kultur- und Bildungspolitik', 'Internationale Beziehungen', 'Menschenrechte', 'Sonstiges im Bereich "Außenpolitik und internationale Beziehungen"'],
        'Außenwirtschaft': ['Außenwirtschaft'],
        'Bildung und Erziehung': ['Bildung und Erziehung', 'Berufliche Bildung', 'Hochschulbildung', 'Schulische Bildung','Vorschulische Bildung', 'Sonstiges im Bereich "Bildung und Erziehung"'],
        'Bundestag': ['Bundestag', 'Parlamentarisches Verfahren', 'Rechtsstellung der Abgeordneten', 'Wahlrecht', 'Sonstiges im Bereich "Bundestag"'],
        'Deutsche Einheit': ['Deutsche Einheit', 'Aufarbeitung SED-Unrecht','Gewährleistung gleichwertiger Lebensverhältnisse','Sonstiges im Bereich "Deutsche Einheit"'],
        'Energie': ['Energie', 'Allgemeine Energiepolitik', 'Atomenergie','Energienetze', 'Erneuerbare Energien', 'Fossile Energien','Sonstiges im Bereich "Energie"'],
        'Entwicklungspolitik': ['Entwicklungspolitik'],
        'Europapolitik und Europäische Union': ['Europapolitik und Europäische Union', 'EU-Binnenmarkt','EU-Gesetzgebung','Gemeinsame Außen- und Sicherheitspolitik der EU','Institutionelle Fragen der EU','Polizeiliche und justizielle Zusammenarbeit in der EU','Sonstiges im Bereich "Europapolitik und Europäische Union"'],
        'Gesellschaftspolitik und soziale Gruppen': ['Gesellschaftspolitik und soziale Gruppen', 'Diversitätspolitik','Familienpolitik','Geschlechterpolitik','Kinder- und Jugendpolitik','Rechte von Menschen mit Behinderung','Religion/Weltanschauung','Seniorenpolitik','Sonstiges im Bereich "Gesellschaftspolitik und soziale Gruppen"'],
        'Gesundheit': ['Gesundheit', 'Arzneimittel','Gesundheitsförderung','Gesundheitsversorgung','Pflege', 'Sonstiges im Bereich "Gesundheit"'],
        'Innere Sicherheit': ['Innere Sicherheit', 'Bevölkerungsschutz und Katastrophenhilfe','Cybersicherheit','Extremismusbekämpfung','Kriminalitätsbekämpfung','Opferschutz','Terrorismusbekämpfung','Sonstiges im Bereich "Innere Sicherheit"'],
        'Kultur': ['Kultur'],
        'Landwirtschaft und Ernährung': ['Landwirtschaft und Ernährung', 'Fischerei/Aquakultur','Land- und Forstwirtschaft','Lebensmittelsicherheit','Lebens- und Genussmittelindustrie','Sonstiges im Bereich "Landwirtschaft und Ernährung"'],
        'Medien, Kommunikation und Informationstechnik': ['Medien, Kommunikation und Informationstechnik', 'Datenschutz und Informationssicherheit','Digitalisierung','Internetpolitik','Kommunikations- und Informationstechnik','Massenmedien','Meinungs- und Pressefreiheit','Urheberrecht','Werbung','Sonstiges im Bereich "Medien, Kommunikation und Informationstechnik"'],
        'Migration, Flüchtlingspolitik und Integration': ['Migration, Flüchtlingspolitik und Integration', 'Asyl und Flüchtlingsschutz', 'Ausländer- und Aufenthaltsrecht', 'Integration','Migration','Sonstiges im Bereich "Migration, Flüchtlingspolitik und Integration"'],
        'Öffentliche Finanzen, Steuern und Abgaben': ['Öffentliche Finanzen, Steuern und Abgaben'],
        'Politisches Leben, Parteien': ['Politisches Leben, Parteien'],
        'Raumordnung, Bau- und Wohnungswesen': ['Raumordnung, Bau- und Wohnungswesen', 'Bauwesen und Bauwirtschaft','Ländlicher Raum','Stadtentwicklung','Wohnen','Sonstiges im Bereich "Raumordnung, Bau- und Wohnungswesen"'],
        'Recht': ['Recht', 'Öffentliches Recht','Rechtspolitik','Strafrecht','Zivilrecht','Sonstiges im Bereich "Recht"'],
        'Soziale Sicherung': ['Soziale Sicherung', 'Arbeitslosenversicherung','Grundsicherung','Krankenversicherung','Pflegeversicherung','Rente/Alterssicherung','Unfallversicherung','Sonstiges im Bereich "Soziale Sicherung"'],
        'Sport, Freizeit und Tourismus': ['Sport, Freizeit und Tourismus', 'Breitensport','Profisport','Tourismus','Sonstiges im Bereich "Sport, Freizeit und Tourismus"'],
        'Staat und Verwaltung': ['Staat und Verwaltung', 'Öffentlicher Dienst und öffentliche Verwaltung','Staatsorganisation','Verwaltungstransparenz/Open Government','Sonstiges im Bereich "Staat und Verwaltung"'],
        'Umwelt': ['Umwelt', 'Artenschutz/Biodiversität', 'Immissionsschutz', 'Klimaschutz', 'Nachhaltigkeit und Ressourcenschutz', 'Tierschutz', 'Sonstiges im Bereich "Umwelt"'],
        'Verkehr': ['Verkehr', 'Güterverkehr','Luft- und Raumfahrt','Personenverkehr','Schienenverkehr','Schifffahrt','Straßenverkehr','Verkehrsinfrastruktur','Verkehrspolitik','Sonstiges im Bereich "Verkehr"'],
        'Verteidigung': ['Verteidigung', 'Bundeswehrangelegenheiten','Rüstungsangelegenheiten','Verteidigungspolitik','Sonstiges im Bereich "Verteidigung"'],
        'Wirtschaft': ['Wirtschaft', 'Automobilwirtschaft', 'Bank- und Finanzwesen', 'E-Commerce', 'Handel und Dienstleistungen', 'Handwerk', 'Industriepolitik','Kleine und mittlere Unternehmen','Verbraucherschutz','Versicherungswesen','Wettbewerbsrecht','Sonstiges im Bereich "Wirtschaft"'],
        'Wissenschaft, Forschung und Technologie': ['Wissenschaft, Forschung und Technologie'],
        'Sonstige Interessenbereiche':['Sonstige Interessenbereiche']
    }

    # Create a reverse mapping from interest to supercategory
    interest_to_supercategory_reverse = {interest: supercategory for supercategory, interests in interest_to_supercategory.items() for interest in interests}

    # Map the interests in df_exploded to their supercategories
    df_exploded_small = df_exploded.copy()
    df_exploded_small['Supercategory'] = df_exploded_small['Interessen'].map(interest_to_supercategory_reverse)

    # Drop rows where the supercategory is not defined
    #df_exploded_small = df_exploded_small.dropna(subset=['Supercategory'])
    df_exploded_small = df_exploded_small.fillna('Sonstige Interessenbereiche')

    # Group by 'Tätigkeit' and 'Interessen' and count the occurrences
    taetigkeit_interessen_counts = df_exploded_small.groupby(['Tätigkeit', 'Supercategory']).size().reset_index(name='Count')

    taetigkeit_interessen_counts['short_entity'] = [truncate_label(label) for label in taetigkeit_interessen_counts['Tätigkeit']]

    # Create a bubble chart using Plotly
    fig = px.scatter(taetigkeit_interessen_counts, 
                     x='Tätigkeit',
                     y='Supercategory',
                     size='Count', 
                     color='Count',
                     hover_name='Tätigkeit',
                     width=500,
                     height=798,
                     title='Interests per Activity (Tätigkeit) in German Lobbies',
                     labels={'Tätigkeit': 'Activity (Tätigkeit)', 'Supercategory': 'Supercategory', 'Count': 'Number of Occurrences'}
    )

    fig.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black'},
        xaxis=dict(
            tickmode='array',
            tickvals=taetigkeit_interessen_counts['Tätigkeit'],
            ticktext=taetigkeit_interessen_counts['short_entity']
        )
    )

    return fig