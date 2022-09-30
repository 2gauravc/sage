from concurrent.futures.process import _threads_wakeups
import streamlit as st
import os
import openai
from io import StringIO

from main import get_sql_response

@st.cache
def fetch_response(query_text):
    ## Get the API key  
    openai.api_key = os.getenv("OPENAI_API_KEY")
    ## Get the API response 
    response = get_sql_response(openai.api_key, query_text)
    print(response.choices[0]['text'])
    #st.caption(response.choices[0]['text'])
    st.session_state['qres'] = "SELECT" + response.choices[0]['text']
    return (response)

query_text = ""
st.session_state.dis_fetch = True

st.markdown('## Sage Version  **V0.1**')

st.markdown("#### Query File ")

uploaded_file = st.file_uploader(" ", type='txt', accept_multiple_files=False, label_visibility="visible")

if uploaded_file is not None:
    # To read file as bytes:
    query_text = StringIO(uploaded_file.getvalue().decode("utf-8"))
    #st.write(query_text)
    st.session_state.dis_fetch = False

res = st.button("Fetch", on_click=fetch_response, args=(query_text), disabled=st.session_state['dis_fetch'])

qres = st.text_area(label='The Query',key='qres', height = 250)


    
