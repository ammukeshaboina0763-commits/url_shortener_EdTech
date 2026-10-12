
import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def get_connection():
    external_url = os.getenv("EXTERNAL_DB_URL")

    if external_url:
        return psycopg2.connect(external_url)

    return psycopg2.connect(
        user=os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
