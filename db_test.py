from main import connect_db
import pandas as pd
from main import get_sql_response
import openai
import os 
import psycopg2
import sys
import config

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

if __name__ == "__main__":
   get_tables_as_csv()


