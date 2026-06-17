import streamlit as st

if st.session_state.power_level == 0:
    st.switch_page('pages/home.py')
    
text = st.session_state.text

st.header(text["admin_power_title"].upper(), anchor=False)