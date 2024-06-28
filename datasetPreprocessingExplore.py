import pandas as pd
from pandas import to_datetime

def preprocess_dataset(file_path):

    # Load cleaned dataset 
    cDf = pd.read_csv(file_path)

    # Set original/cleaned dataset index
    cDf[' index'] = range(1, len(cDf) + 1)

    # Clean Up
    cDf['Betrag'] = cDf['Betrag'].str.replace('.', '')
    cDf.loc[cDf['LetzteÄnd']=="–",'LetzteÄnd'] = ''

    ## Spendings
    # Extract the lower and upper bounds of the range
    cDf['lower_bound_amount'] = cDf['Betrag'].str.extract(r'(\d+)').fillna(0).astype(int)
    cDf['upper_bound_amount'] = cDf['Betrag'].str.extract(r'bis (\d+(?:\.\d+)?) Euro').fillna(0).astype(int) 

    # Calculate the average spending
    cDf['Durchschnitt Betrag'] = ((cDf['lower_bound_amount'] + cDf['upper_bound_amount']) / 2).fillna(0).astype(int)

    ## Employees
    # Extract the lower and upper bounds of the range
    cDf['lower_bound_emp'] = cDf['Beschäftigte'].str.extract(r'(\d+)').fillna(0).astype(int)
    cDf['upper_bound_emp'] = cDf['Beschäftigte'].str.extract(r'bis (\d+)').fillna(0).astype(int)

    # Calculate the average number of employees
    cDf['Durchschnitt Beschäftigte'] = ((cDf['lower_bound_emp'] + cDf['upper_bound_emp']) / 2).fillna(0).astype(int)
    cDf.loc[cDf['Beschäftigte'] == '0','Durchschnitt Beschäftigte'] = 0

    # Average spending per employee
    cDf['Betrag / Beschäftigte'] = cDf['Durchschnitt Betrag'] / cDf['Durchschnitt Beschäftigte']

    # Extract the start and end date from the "Geschäftsjahr" column
    def extract_dates(row):
        if pd.isna(row) or 'Keine Zuwendungen oder Zuschüsse' in row:  # Überprüfung auf NaN und nicht konforme Werte
            return pd.Series([pd.NaT, pd.NaT])  # Rückgabe von NaT für fehlende oder nicht konforme Daten
        start_date, end_date = row.split(' bis ')
        start_date = pd.to_datetime('01/' + start_date, format='%d/%m/%y', errors='coerce').date()
        end_date = pd.to_datetime('01/' + end_date, format='%d/%m/%y', errors='coerce').date()
        return pd.Series([start_date, end_date])

    # Anwenden der Funktion auf die Spalte "Geschäftsjahr"
    cDf[['GeschäftsjahrStart', 'GeschäftsjahrEnde']] = cDf['Geschäftsjahr'].apply(extract_dates)

    # Changing Columns to numeric values and converting to int
    cDf['lower_bound_amount'] = pd.to_numeric(cDf['lower_bound_amount'], errors='coerce').fillna(0).astype(int)
    cDf['upper_bound_amount'] = pd.to_numeric(cDf['upper_bound_amount'], errors='coerce').fillna(0).astype(int)
    cDf['lower_bound_emp'] = pd.to_numeric(cDf['lower_bound_emp'], errors='coerce').fillna(0).astype(int)
    cDf['upper_bound_emp'] = pd.to_numeric(cDf['upper_bound_emp'], errors='coerce').fillna(0).astype(int)
    cDf['Durchschnitt Betrag'] = pd.to_numeric(cDf['Durchschnitt Betrag'], errors='coerce').fillna(0).astype(int)
    cDf['Durchschnitt Beschäftigte'] = pd.to_numeric(cDf['Durchschnitt Beschäftigte'], errors='coerce').fillna(0).astype(int)

    # Convert to datetime
    cDf['GeschäftsjahrStart'] = to_datetime(cDf['GeschäftsjahrStart'])
    cDf['GeschäftsjahrEnde'] = to_datetime(cDf['GeschäftsjahrEnde'])

    # Filter out rows with unnecessary data
    cDf= cDf[((cDf['Durchschnitt Betrag'] > 5000) & (cDf['Durchschnitt Beschäftigte'] > 5)) | (cDf['Durchschnitt Beschäftigte'] > 1) & (cDf['Durchschnitt Betrag']/cDf['Durchschnitt Beschäftigte'] > 20000)].sort_values('Name')

    # Rename columns
    cDf.rename(columns={'Durchschnitt Betrag': 'Ø Amount', 
                        'Durchschnitt Beschäftigte': 'Ø Employees',
                        'Betrag / Beschäftigte': 'Ø Amount/Employee',
                        'GeschäftsjahrStart': 'Fiscal Year Start',
                        'GeschäftsjahrEnde': 'Fiscal Year End',
                        'Geschäftsjahr': 'Fiscal Year',
                        'Tätigkeit': 'Entity',
                        'Interessen': 'Interests'}, 
                        inplace=True)

    return cDf