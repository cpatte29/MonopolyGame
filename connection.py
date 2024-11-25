import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


import psycopg2

def create_connection():
    database_url = input("Please enter your PostgreSQL connection URL: ").strip()
    try:
        connection = psycopg2.connect(database_url)
        print("Connection established successfully!")
        return connection
    except Exception as e:
        print("Error connecting to the database:", e)
        raise
