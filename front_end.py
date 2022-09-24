import streamlit as st

st.markdown('## Sage Version  **V0.1**')

st.markdown("#### Query File ")

st.file_uploader("", type='txt', accept_multiple_files=False, label_visibility="visible")