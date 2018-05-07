import psycopg2
import os
from flask import g

def get_conn():
    dsn_database = "amazon_review_insight"
    dsn_hostname = "insight.c0lqcrqaigco.us-east-1.rds.amazonaws.com"
#    dsn_hostname = "micro-pg-test.c0lqcrqaigco.us-east-1.rds.amazonaws.com"
    dsn_port = "5432"        
    dsn_uid = "mijik"   
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
