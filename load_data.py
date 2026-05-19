# Cleaning data and loading it into a database
import pandas as pd
from sqlalchemy import create_engine

def load_data(file_path, db_url, table_name):
    # Load data from CSV file
    df = pd.read_csv(file_path)

    # Clean data
    df = df[df['measure_name'].notna()]
    df = df.drop(columns=['Data Release Year', 'State Code', 'County Code'])

    df['Year span'].str.split('-', expand=True)

    df = df.rename(columns={'Old Name': 'new_name'})
