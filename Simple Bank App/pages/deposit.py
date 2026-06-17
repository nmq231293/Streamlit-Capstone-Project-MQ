import streamlit as st

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text

st.header(text["deposit_title"].upper(), anchor=False)
