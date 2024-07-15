from fuzzywuzzy import process
import Levenshtein as lev
import pandas as pd
import plotly.express as px
import re


# Read cleaned dataset
filepath = 'Datasets/cleanedLobbyregister2024.csv'
cleanedDataset = pd.read_csv(filepath)

# Select text for selected insights section
def selectInsightsText(chapter):
    if chapter == 1:
        return ("For the interests page, we chose to include these three plots. The first one illustrates the average number of interests of the different lobbyists in the dataset. For this graph we illustrated the mean interests in blue and the median interests in red. So when we hover over the first bar, we can see that enterprises have an average interest count of 14, where science has an average count of 2.",
               "Sticking to the enterprise example, all enterprises in the dataset have 170 unique interests in total. Interestingly, of all interests Sustainability is the biggest interest area for Lobbies in Germany.")
    elif chapter == 2:
        return ("The top left plot shows the average spending per employee for all the entity types and the color coding is an indicator for the total spending of those entities - blue is low spending, red is high spending.",
                "The lower left has a similar color coding but for each individual entity. It shows the spending in relation to the number of employees and shows very well that larger entities not necessarilly spend more.",
                "Lastly the pie/donut charts on the right just shows how big of a slice each entity type has of the total spending and employees of all entities in our cleaend datasets.")
    elif chapter == 3:
        return "In this chapter, we will focus on the number of entities, the average number of employees, and the interests per entity in the German lobby registry. We will explore the distribution of entities, the average number of employees, and the distribution of interests across different entity types."
    else:
        return "No insights available for this chapter."

# Truncate labels 
def truncate_label(label, max_length=15):
        return label if len(label) <= max_length else label[:max_length] + '...'

# Df
def dfTIG():
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

    return taetigkeit_interessen_counts


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

    # Group by "Tätigkeit" and count the number of unique "Interessen" for each
    taetigkeit_interessen_counts = df_exploded.groupby('Tätigkeit')['Interessen'].nunique().reset_index()
    taetigkeit_interessen_counts.columns = ['Tätigkeit', 'Unique_Interessen_Count']

    taetigkeit_interessen_counts['short_entity'] = [truncate_label(label) for label in taetigkeit_interessen_counts['Tätigkeit']]

    # Create a bar chart using Plotly
    fig= px.bar(taetigkeit_interessen_counts, x='Tätigkeit', y='Unique_Interessen_Count', #size='Unique_Interessen_Count',
                        color='Unique_Interessen_Count', # Color the bubbles according to the count of unique interests
                        title='Number of Unique Interests per Entity',
                        width=526,
                        height=798,
                        labels={'Unique_Interessen_Count': 'Unique Interests', 'Tätigkeit': 'Entity type'})

    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                       'paper_bgcolor': 'rgba(0,0,0,0)',
                       },
                        font=dict(color='white'),
                        xaxis=dict(
                            visible=True,
                            showticklabels=False
                        ),
    )

    return fig


#Plot 2

def createFigAverageInterests():

    df_entities = dfEntities(0)

    fig = px.bar(
        df_entities, 
        x='Entity type', 
        y=[df_entities['Mean Interests'], 
        df_entities['Median Interests']], 
        barmode="group",
        title="Average number of Interests",
        hover_name='Entity type',
        hover_data=['Entity type', 'Number of entities'],
        labels={'value':'Average interests'}
    )

    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                       'paper_bgcolor': 'rgba(0,0,0,0)'},
                        width=500,
                        height=399,
                        showlegend=False,
                        font=dict(color='white'),
                        xaxis=dict(
                            visible=True,
                            showticklabels=False
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
                title='Biggest Interest areas for Lobbies in Germany', 
                labels={'Count': 'Number of lobbies', 'Interest': ''})

    fig.update_yaxes(range=[0, 800], dtick=200)

    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                       'paper_bgcolor': 'rgba(0,0,0,0)'},
        width=500,
        height=399,
        font=dict(color='white'),
        xaxis=dict(
            tickmode='array',
            tickvals=interest_counts_df['Interest'],
            ticktext=interest_counts_df['shortInterest'],
            visible=True,
            showticklabels=False
        )
    )


    return fig

# -------------------------------------- Chapter 2 --------------------------------------

def createFigEmployeesPie():

    df_entities = dfEntities(0)

    figPieEmployees = px.pie(df_entities, 
                    values='Total Employees', 
                    hover_name='Entity type',
                    hole=0.3,
                    title='Total employees per entity type')

    figPieEmployees.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                          'paper_bgcolor': 'rgba(0,0,0,0)'},
                         uniformtext_minsize=12, 
                         uniformtext_mode='hide',
                         font=dict(color='white'),
                         width=450,
                         height=398
    )

    figPieEmployees.update_traces(textposition='inside')

    return figPieEmployees


# Plot 1

def createFigSpendingsPie():

    df_entities = dfEntities(0)

    figPie = px.pie(df_entities, 
                    values='Total Spending', 
                    hover_name='Entity type',  
                    hole=0.3,
                    title='Total spendings per entity type')
    
    figPie.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                          'paper_bgcolor': 'rgba(0,0,0,0)'},
                         uniformtext_minsize=12, 
                         uniformtext_mode='hide',
                         font=dict(color='white'),
                         width=450,
                         height=398
    )
    
    figPie.update_traces(textposition='inside')

    return figPie


# Plot 2

def createFigSpendingsScatter():

    figScatter = px.scatter(cleanedDataset, 
                            x="Beschäftigte", 
                            y="Betrag", 
                            labels={'Name': "Name", 'Betrag': "Spending", 'Beschäftigte': "Employees"}, 
                            title='Spending in relation to number of employees', 
                            color="Betrag", 
                            color_continuous_scale=px.colors.sequential.Bluered)

    figScatter.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black',
        },
        font=dict(color='white'),
        xaxis=dict(
            visible=True,
            showticklabels=False
        ),
        width=600,
        height=399
    )

    return figScatter

# Plot 3

def createFigSpendingsPerEmployee():

    df_entities = dfEntities(0)

    figSpendingPerEmployee = px.bar(df_entities, 
                                    x='Entity type', 
                                    hover_name='Entity type', 
                                    y='Spending per Employee', 
                                    color='Total Spending', 
                                    color_continuous_scale=px.colors.sequential.Bluered)

    figSpendingPerEmployee.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black'},
        width=600,
        height=399,
        title='Spending/Employee per entity type',
        font=dict(color='white'),
        xaxis=dict(
            tickmode='array',
            tickvals=df_entities['Entity type'],
            ticktext=df_entities['short_entity'],
            visible=True,
            showticklabels=False
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
        height=798,
        title='Number of entities',
        font=dict(color='white'),
        xaxis=dict(
            tickmode='array',
            tickvals=df_entities['Entity type'],
            ticktext=df_entities['short_entity'],
            visible=True,
            showticklabels=False
        )
    )

    return fig 


# Plot 2

def createFigAverageEmployees():

    df_entities = dfEntities(0)

    fig = px.bar(df_entities, 
                 x='Entity type', 
                 y=[df_entities['Mean Employees'], 
                    df_entities['Median Employees']],
                 barmode="group",
                 title='Average Employees per Entity',
                 hover_name='Entity type',
                 hover_data=['Entity type', 'Number of entities'],
                 color_discrete_sequence=["blue", "red"] 
    )

    fig.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black'},
        width=500,
        height=798,
        showlegend=False,
        font=dict(color='white'),
        xaxis=dict(
            tickmode='array',
            tickvals=df_entities['Entity type'],
            ticktext=df_entities['short_entity'],
            visible=True,
            showticklabels=False
        )
    )

    return fig


#Plot 3

def createFigInterestPerEntity():

    taetigkeit_interessen_counts = dfTIG()

    # Create a bubble chart using Plotly
    fig = px.scatter(taetigkeit_interessen_counts, 
                     x='Tätigkeit',
                     y='Supercategory',
                     size='Count', 
                     color='Count',
                     hover_name='Tätigkeit',
                     width=1020,
                     height=798,
                     title='Interests per Entity in German Lobbies',
                     labels={'Tätigkeit': 'Entity', 'Supercategory': 'Supercategory', 'Count': 'Number of Occurrences'}
    )

    fig.update_xaxes(showgrid=True, gridwidth=0.1)  # Make x-axis grid lines thinner
    fig.update_yaxes(showgrid=True, gridwidth=0.1)  # Make y-axis grid lines thinner

    fig.update_layout({
        'plot_bgcolor': 'black',
        'paper_bgcolor': 'black'},
        font=dict(color='white'),
        xaxis=dict(
            tickmode='array',
            tickvals=taetigkeit_interessen_counts['Tätigkeit'],
            ticktext=taetigkeit_interessen_counts['short_entity'],
        ),
    )

    return fig