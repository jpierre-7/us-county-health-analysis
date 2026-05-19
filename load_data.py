# Cleaning data and loading it into a database
import pandas as pd
from sqlalchemy import create_engine

def load_data(file_path, db_url, table_name):
    # ----Cleaning---- #
    # Load data from CSV file
    df = pd.read_csv(file_path)

    # Drop rows with missing values in 'Measure name' and 'fipscode' columns
    df = df[df['Measure name'].notna()]
    df = df[df['fipscode'].notna()]

    # Split 'Year span' into 'year_start' and 'year_end'
    split = df['Year span'].str.split('-', expand=True)
    df['year_start'] = split[0]
    df['year_end'] = split[1].fillna(split[0]) 

    # Boolean flag for null raw_value
    df['raw_value_missing'] = df['Raw value'].isna()

    df = df.drop(columns=['Data Release Year', 'State code', 'County code', 'Year span'])

    df = df.rename(columns={
        'Measure name': 'measure_name',
        'Measure id': 'measure_id',
        'Denominator': 'denominator',
        'Numerator': 'numerator',
        'Raw value': 'raw_value',
        'Confidence Interval Upper Bound': 'ci_upper',
        'Confidence Interval Lower Bound': 'ci_lower',
        'State': 'state_name',
        'County': 'county_name'})
    
    # ----Loading---- #
