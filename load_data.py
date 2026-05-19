# Cleaning data and loading it into a database
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

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
    
    # Saving cleaned data to a new CSV file
    df.to_csv('data/cleaned_county_health_rankings.csv', index=False)
    
    # ----Loading---- #
    # Create a SQLAlchemy engine
    engine = create_engine(db_url)

    # Build 3 dataframes for the 3 tables
    county_df = df[['fipscode', 'state_name', 'county_name']].drop_duplicates()
    measure_df = df[['measure_id', 'measure_name']].drop_duplicates()
    fact_observations_df = df[['fipscode', 'measure_id', 'year_start', 'year_end', 'numerator', 'denominator', 'raw_value', 'raw_value_missing', 'ci_lower', 'ci_upper']]

    # Loading tables in order
    county_df.to_sql('county', con=engine, if_exists='append', index=False)
    measure_df.to_sql('measure', con=engine, if_exists='append', index=False)
    fact_observations_df.to_sql('fact_observations', con=engine, if_exists='append', index=False)

# Calling the function
if __name__ == '__main__':
    load_data('data/County_Health_Rankings.csv', os.getenv('DATABASE_URL'), None)


