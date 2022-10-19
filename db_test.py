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
        
        con = psycopg2.connect(host=config.server_log,
                                database=config.database_log,
                                user=config.user_log,
                                password=config.password_log)	
        # create a cursor
        return (con)
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print ('Could not connect to DB. Exiting..')
        return(error)


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
    cur.close()
        
def get_tables_as_csv():
    con = connect_db()
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
        cmd = "select * from {}".format(t_name)
        cur.execute(cmd)
        cnt = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cnt_rec = len(cnt)
        print("Found {} rows in table {}".format(cnt_rec,t_name))
        if (cnt_rec>0): 
            #print("in cnt rec > 0")
            df = pd.DataFrame(cnt)
            df.columns = colnames
            df.to_csv("tmp/{}.csv".format(t_name), index=False)
        else: 
            df = pd.DataFrame(columns = colnames)
    cur.close()
    con.close()
    writer = pd.ExcelWriter('tmp/sales_org_data.xlsx', engine='xlsxwriter') 
    csvfiles = ['customers.csv', 'employees.csv', 'offices.csv', 'orderdetails.csv', 'orders.csv', 'payments.csv',\
        'payments.csv', 'productlines.csv', 'products.csv']
    dir = 'tmp/'
    for csvfilename in csvfiles:
        out_sheet_name = os.path.splitext(csvfilename)[0]
        print("writing {} to {}\n".format(csvfilename, out_sheet_name))
        df = pd.read_csv('tmp/{}'.format(csvfilename))
        df.to_excel(writer,sheet_name= out_sheet_name, index=False)
    writer.save()

def gen_api_input(q_txt): 
    con= connect_db()
    t = get_schema_as_text(con)
    q = get_query_in_api_format(q_txt)
    final_query_for_api = t + q 
    return(final_query_for_api)

def log_sql_to_db():
    con=connect_db()
    cur = con.cursor()
    log_date = datetime.today().strftime('%Y-%m-%d')
    question = "How many customers from France"
    sql_generated = "Select count(*) from customers where country = 'France'"
    sage_version = "0.3"
    sql_run_status = "success"
    sql_result_rows = 12
    var_list=[log_date, question, sql_generated, sage_version, sql_run_status, sql_result_rows]
    var_list = [w.replace("'", "''")  if isinstance(w,str) else w for w in var_list ]

    qu = "INSERT INTO sage.sql_log(log_date, sage_version, question,sql_generated,\
        sql_run_status, sql_result_rows) VALUES (\'{}\', \'{}\', \'{}\',\'{}\',\
        \'{}\', {})".format(var_list[0], var_list[1], var_list[2], var_list[3], var_list[4],\
            var_list[5])
    print(qu)
    cur.execute(qu)
    con.commit()
    print("record inserted")
    cur.close()
    con.close()




if __name__ == "__main__":
   con = connect_db()
   print(con) 
   cur = con.cursor()
   # Get the list of tables in the DB
   cur.execute("SELECT * FROM sage.sql_log")
   recs = cur.fetchall()
   print('\tFound {} Rows'.format(len(recs)))
   cur.close()
   con.close()
   
   log_sql_to_db()



