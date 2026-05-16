# A quick script to test the connection to Supabase
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
