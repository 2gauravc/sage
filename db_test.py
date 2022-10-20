from main import connect_db
import pandas as pd
from main import get_sql_response
import openai
import os 
import psycopg2
import sys
import config
from datetime import datetime


def connect_db():
    """ Connect to the PostgreSQL database server """
    
    con = None
    try:
        
        # connect to the PostgreSQL server
        
        con = psycopg2.connect(host=config.server,
                                database=config.database,
                                user=config.user,
                                password=config.password)	
        # create a cursor
        return (con)
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print ('Could not connect to DB. Exiting..')
        return(error)

def extract_psycopg2_exception(err):
    err_type, err_obj, traceback = sys.exc_info()
    return(err.pgerror, err.pgcode)

def get_data_from_sql(sql_query):
    con = connect_db()
    cur = con.cursor()
    try: 
        cur.execute(sql_query)
    except Exception as err:
        pgerror, pgcode = extract_psycopg2_exception(err)
        print("pgerror: {}".format(pgerror))
        print("pgcode: {}".format(pgcode))




if __name__ == "__main__":
   con = connect_db() 
   cur = con.cursor()
   # Get the list of tables in the DB
   sql_query = """SELECT * FROM orders WHERE status = 'Cancelled' AND total_order_value > 10000
"""
   get_data_from_sql(sql_query)
   cur.close()
   con.close()   



