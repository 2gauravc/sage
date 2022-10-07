from main import connect_db
import pandas as pd
from main import get_sql_response
import openai
import os 

def connect_db():
    """ Connect to the PostgreSQL database server """
    
    con = None
    try:
        
        # connect to the PostgreSQL server
        
        con = psycopg2.connect(host=config.server,
                                database=config.database,
                                user=config.database,
                                password=config.password)	
        # create a cursor
        return (con)
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print ('Could not connect to DB. Exiting..')
        sys.exit(2)


def get_query_in_api_format(q_txt):
    q_txt1 = "#\n### " + q_txt + "\nSELECT"
    return q_txt1


def get_schema_as_text(con):
    cur = con.cursor()
    # Get the list of tables in the DB
    cur.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = %s Order By table_name", ('public',))
    recs = cur.fetchall()
    #print('\tFound {} Columns'.format(len(recs)))
    df = pd.DataFrame(recs)
    df.columns = ['table_name','column_name']
    #print(df.table_name.unique())

    t = "### Postgres SQL tables, with their properties:\n#\n"
    for t_name in df.table_name.unique(): 
        t_txt = '# {}('.format(t_name)
        col_txt = ','.join(df.loc[df.table_name == t_name,'column_name'])
        t = t + t_txt+col_txt + ")\n"
    
    return(t)
        
#\n### A query to list the names of the departments which employed more than 10 employees in the last 3 months

    cur.close()

def gen_api_input(q_txt): 
    con= connect_db()
    t = get_schema_as_text(con)
    q = get_query_in_api_format(q_txt)
    final_query_for_api = t + q 
    return(final_query_for_api)

## Get the API key  
openai.api_key = os.getenv("OPENAI_API_KEY")

## Get the API response 
response = get_sql_response(openai.api_key, final_query_for_api)
print (response.choices[0]['text'])


con.close()





