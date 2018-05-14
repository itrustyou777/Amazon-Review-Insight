import psycopg2
from psycopg2.extensions import adapt
import os
from flask import g

def get_conn():
    dsn_database = os.environ['RDS_DB']
    dsn_hostname =  os.environ['RDS_HOST']
    dsn_port = os.environ['RDS_PORT']
    dsn_uid = os.environ['RDS_USER']
    dsn_pwd = os.environ['RDS_PASSWORD']

    conn_string = "host="+dsn_hostname+" port="+dsn_port+" dbname="+dsn_database+" user="+dsn_uid+" password="+dsn_pwd
    
    if not hasattr(g, 'db_conn'):
        print ("Connecting to database\n  ->" + conn_string)
        g.db_conn = psycopg2.connect(conn_string)

    return g.db_conn


def fetchone(conn, query):
    print(query)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()


def fetchall(conn, query):
    print(query)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def quote(x):
    return adapt(x).getquoted()

