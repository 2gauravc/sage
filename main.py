
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
    #print(final_query_for_api)

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
    #print ("Response Received from API")

def get_data_from_sql(sql_query):
    con = connect_db()
    cur = con.cursor()
    try: 
        cur.execute(sql_query)
        status = 'success'
        pgerror = ""
        pgcode = ""
        cnt = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cnt_rec = len(cnt)
        if (cnt_rec>0): 
            df = pd.DataFrame(cnt)
            df.columns = colnames
        else: 
            df = pd.DataFrame(columns = colnames)

    
    except Exception as err:
        err_type, err_obj, traceback = sys.exc_info()
        pgerror = err.pgerror
        pgcode = str(err.pgcode)
        status = 'error'
        df = pd.DataFrame()

    err_dict = {'pgerror': pgerror, 'pgcode':pgcode}   
    
    return(status, df, err_dict)

def get_openai_api_key():
    return(config.OPENAI_API_KEY)

def log_sql_to_db(log_date, question, sql_generated, sage_version, sql_run_status, sql_result_rows, pgerror, pgcode):
    con=connect_db_log()
    cur = con.cursor()
    
    #Replace quotation marks inside the text fields with double quotation marks
    var_list=[log_date, sage_version, question, sql_generated, sql_run_status, sql_result_rows, pgerror, pgcode]
    var_list = [w.replace("'", "''")  if isinstance(w,str) else w for w in var_list ]

    qu = "INSERT INTO sage.sql_log(log_date, sage_version, question,sql_generated,\
        sql_run_status, sql_result_rows, pgerror, pgcode) VALUES (\'{}\', \'{}\', \'{}\',\'{}\',\
        \'{}\', {}, \'{}\', \'{}\')".format(var_list[0], var_list[1], var_list[2], var_list[3], var_list[4],\
            var_list[5], var_list[6], var_list[7])
    cur.execute(qu)
    con.commit()
    #print("Record Inserted in log DB")
    cur.close()
    con.close()

def update_log_sql_to_db(log_id, right_sql): 
    con=connect_db_log()
    cur = con.cursor()
    
    #Replace quotation marks inside the text fields with double quotation marks
    var_list=[log_id, right_sql]
    var_list = [w.replace("'", "''")  if isinstance(w,str) else w for w in var_list ]

    qu = "UPDATE sage.sql_log SET right_sql = \'{}' WHERE log_id = {}".format(var_list[1], var_list[0])
    
    cur.execute(qu)
    con.commit()
    print("Record updated in log DB")
    cur.close()
    con.close()


def get_accuracy_stats():
    #print("Getting accuracy stats get_accuracy__stats")
    query ="select  question,sql_generated, count(*) as num_q, \
        sum(case when sql_run_status = 'success' then 1 else 0 end) as num_q_success\
            from sage.sql_log\
                group by question, sql_generated"
    con = connect_db_log() 
    cur = con.cursor()
    cur.execute(query)
    cnt = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cnt_rec = len(cnt)
    if (cnt_rec>0): 
        df = pd.DataFrame(cnt)
        df.columns = colnames
    else: 
        df = pd.DataFrame(columns = colnames)
    
    cur.close()
    con.close()
    num_q = sum(df.num_q)
    num_q_success = sum(df.num_q_success)

    return(num_q, num_q_success)
    
def get_failed_sql():
    #print("Getting failed SQL get_failed_sql")
    query =" SELECT log_id, log_date,question, sql_generated  from sage.sql_log WHERE sql_run_status = 'failure' "
    con = connect_db_log() 
    cur = con.cursor()
    cur.execute(query)
    cnt = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cnt_rec = len(cnt)
    if (cnt_rec>0): 
        df = pd.DataFrame(cnt)
        df.columns = colnames
    else: 
        df = pd.DataFrame(columns = colnames)
    
    cur.close()
    con.close()

    return (df)

if __name__ == "__main__":
   df=get_failed_sql()
   print("rows {}".format(df.shape[0]))
   print(df)

