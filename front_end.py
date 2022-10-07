from concurrent.futures.process import _threads_wakeups
import streamlit as st
import os
import openai
from io import StringIO
import pandas as pd
import sys

from main import get_sql_response

@st.cache
def fetch_response(query_text: str):
    ## Get the API key  
    openai.api_key = os.getenv("OPENAI_API_KEY")
    ## Get the API response 
    response = get_sql_response(openai.api_key, query_text)
    #print(response.choices[0]['text'])
    #st.caption(response.choices[0]['text'])
    st.session_state['qres'] = "SELECT" + response.choices[0]['text']
    return (response)

query_text = ""
st.session_state.dis_fetch = True

st.markdown('## Sage Version  **V0.1**')

st.markdown("#### Query File ")

qu = st.text_area(label="Ask a question", key='qask')
#print (qu) 

if len(qu) > 0:
    st.session_state.dis_fetch = False

res = st.button("Fetch", on_click=fetch_response, args=(qu,), disabled=st.session_state['dis_fetch'])

qres = st.text_area(label='The Query',key='qres', height = 250)


    
