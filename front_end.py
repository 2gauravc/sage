from concurrent.futures.process import _threads_wakeups
import streamlit as st
import os
import openai
from io import StringIO
import pandas as pd
import sys

from main import get_sql_response
from main import get_data_from_sql

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
    st.markdown('###### Click on the next tab to try Sage')

    
with main_tab:
    @st.cache
    def fetch_response(query_text: str):
        ## Get the API key  
        openai.api_key = os.getenv("OPENAI_API_KEY")
        ## Get the API response 
        response = get_sql_response(openai.api_key, query_text)
        st.session_state['qres'] = "SELECT" + response.choices[0]['text'] + '\n'
        
        #if response is 200 then send the sql  query to the database and get a response 
        try:
            df = get_data_from_sql(st.session_state['qres'])
            row_cnt_txt = 'Found {} rows'.format(df.shape[0])
            st.session_state['row_cnt_txt'] = row_cnt_txt
            st.session_state['ret_df'] = df
        except (Exception) as error:
            print(error)


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

    st.markdown("#### Query Generated")
    qres = st.text_area(label='Query Returned by Sage',key='qres', height = 100)

    if 'ret_df' in st.session_state:
        st.markdown("#### Data Result")
        st.markdown("###### {}".format(st.session_state['row_cnt_txt']))
        st.dataframe(st.session_state['ret_df'])


    
