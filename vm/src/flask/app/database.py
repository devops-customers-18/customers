"""Database connections."""

import psycopg2
import config

def db_connect():
    """Connect to Test or Live Database Depending on Debug"""
    try:
        connection = psycopg2.connect(host=config.db_connect_info['host'],
                                      database=config.db_connect_info['database'],
                                      user=config.db_connect_info['user'],
                                      password=config.db_connect_info['password'])
        print("Postgre is Good.")
        return connection

    except Exception as e:
        print("Database connection exception.")
        print(e)
    return None

db_connect()
