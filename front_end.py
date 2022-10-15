from concurrent.futures.process import _threads_wakeups
import streamlit as st
import os
import openai
from io import StringIO
import pandas as pd
import sys
from datetime import datetime

from main import get_sql_response
from main import get_data_from_sql
from main import get_openai_api_key
from main import log_sql_to_db

sage_version = "0.3"

start_tab, main_tab = st.tabs(["Read Me", "Try Sage"])

with start_tab:
    st.header("READ ME")
    st.markdown('###### Just ask a question in English. Sage will \
                translate that into a SQL query and run the query to fetch the result')
    st.markdown('###### Sage demo is set-up with a Sales organization. \
                The organization has customers, products, orders, payments and employees.\
                    The Entity-Relationship diagram of the databse is below.')                

    st.image('images/erdiagram.png', width =600)
    st.markdown('###### Sample Questions to ask:')
    st.markdown('###### 1. Find Customers from France')
    st.markdown('###### 2. Show me unique job titles')
    st.markdown('###### [Download](https://sage-mvp1.s3.amazonaws.com/sales_org_data.xlsx) the data as xl file')
    st.markdown('###### Click on the next tab to try Sage')


    
with main_tab:
    @st.cache
    def fetch_response(query_text: str):
        ## Get the API key  
        openai.api_key = get_openai_api_key()
        ## Get the API response 
        response = get_sql_response(openai.api_key, query_text)
        st.session_state['qgen'] = "SELECT" + response.choices[0]['text'] + '\n'
        #if response is 200 then send the sql  query to the database and get a response 
        
        #Prepare arguments to log_sql_to_db: log_date, question, sql_generated, sage_version, sql_run_status, sql_result_rows
        
        # 
        return (response)

    query_text = ""
    
    st.session_state.dis_fetch = True

    st.markdown('## Sage Version  **V0.1**')

    st.markdown("#### Ask a question")

    qu = st.text_area(label="Ask in natural language", key='qask')
    #print (qu) 

    if len(qu) > 0:
        st.session_state.dis_fetch = False

    res = st.button("Fetch", on_click=fetch_response, args=(qu,), disabled=st.session_state['dis_fetch'])

    if 'qgen' in st.session_state: 
        st.markdown("#### Query Generated")
        qdis = st.text_area(label='Query Returned by Sage',value = st.session_state['qgen'],key='qdis', height = 100)
        try:
            df = get_data_from_sql(st.session_state['qgen'])
            row_cnt_txt = 'Found {} rows'.format(df.shape[0])
            st.session_state['row_cnt_txt'] = row_cnt_txt
            st.session_state['ret_df'] = df
            st.session_state['sql_run_status'] = "success"
            st.session_state['sql_result_rows'] =  df.shape[0]
        
        except (Exception) as error:
            st.session_state['sql_run_status'] = "failure"
            st.session_state['sql_result_rows'] = 0
        

    if 'sql_run_status' in st.session_state: 
        st.markdown("#### Data Result")
        if st.session_state['sql_run_status'] == "failure":
            st.markdown("###### Query failed to execute. The error has been logged")
        elif (st.session_state['sql_run_status'] == "success") & ('ret_df' in st.session_state):
            st.markdown("###### {}".format(st.session_state['row_cnt_txt']))
            st.dataframe(st.session_state['ret_df'])
        else:
             st.markdown("###### Query executed, but no data returned. The error has been logged")
        
    if 'qgen' in st.session_state:
        try: 
            log_date = datetime.today().strftime('%Y-%m-%d')
            question = qu
            sql_generated = st.session_state['qgen']
            sage_version = "0.3"
            log_sql_to_db(log_date, question, \
                sql_generated, sage_version, st.session_state['sql_run_status'], st.session_state['sql_result_rows'])
        except (Exception) as error:
            print ("Error writing to log DB")
            

    
