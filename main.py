
# Make the API call to OpenAI codex API 

import os
import openai
import getopt, sys
import psycopg2
import config
import pandas as pd

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
        print ('Could not connect to DB.')
        return (error)

def connect_db_log():
    """ Connect to the PostgreSQL database server """
    con = None
    try:
        # connect to the PostgreSQL server
        con = psycopg2.connect(host=config.server_log,
                                database=config.database_log,
                                user=config.user_log,
                                password=config.password_log)	
        return (con)    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print ('Could not connect to log DB.')
        return(error)


def get_schema_as_text():
    con= connect_db()
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
    
    cur.close()
    con.close()
    return(t)

def get_sql_response(api_key, query_text):
    #Get the Table Schema and format as api input 
    
    t = get_schema_as_text()

    # Format the query_text as api input 
    q = "#\n### " + query_text + "\nSELECT"

    final_query_for_api = t + q
    print(final_query_for_api)

    response = openai.Completion.create(model="code-davinci-002",
    prompt=final_query_for_api,
    temperature=0,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,presence_penalty=0,
    stop=["#", ";"]
    )
    return (response)

def main(argv): 
    try: 
        opts, args = getopt.getopt(argv,"q:", ["query="])
    except getopt.GetoptError:
        print("Usage: python3 main.py --query=<query_path>")
        sys.exit(2)
    
    req_options = 0
    for opt, arg in opts:
        if opt == '--query':
            query_file = arg
            req_options = 1

    if (req_options == 0):
        print("Usage: python3 main.py --query=<query_path>")
        sys.exit(2)
    
    ## Get the API key  
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    ## Read the query_file
    with open(query_file) as f:
        query_text = f.readlines()

    ## Get the API response 
    response = get_sql_response(openai.api_key, query_text)
    print (response.choices[0]['text'])

def get_data_from_sql(sql_query):
    con = connect_db()
    cur = con.cursor()
    cur.execute(sql_query)
    cnt = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cnt_rec = len(cnt)
    print("Found {} rows, header {}".format(cnt_rec,colnames))
    if (cnt_rec>0): 
        df = pd.DataFrame(cnt)
        df.columns = colnames
    else: 
        df = pd.DataFrame(columns = colnames)

    return(df)

def get_openai_api_key():
    return(config.OPENAI_API_KEY)

def log_sql_to_db(log_date, question, sql_generated, sage_version, sql_run_status, sql_result_rows):
    con=connect_db_log()
    cur = con.cursor()
    
    #Replace quotation marks inside the text fields with double quotation marks
    var_list=[log_date, sage_version, question, sql_generated, sql_run_status, sql_result_rows]
    var_list = [w.replace("'", "''")  if isinstance(w,str) else w for w in var_list ]

    qu = "INSERT INTO sage.sql_log(log_date, sage_version, question,sql_generated,\
        sql_run_status, sql_result_rows) VALUES (\'{}\', \'{}\', \'{}\',\'{}\',\
        \'{}\', {})".format(var_list[0], var_list[1], var_list[2], var_list[3], var_list[4],\
            var_list[5])
    cur.execute(qu)
    con.commit()
    print("Record Inserted in log DB {}".format(qu))
    cur.close()
    con.close()

if __name__ == "__main__":
   main(sys.argv[1:])

