import streamlit as st
import pandas as pd
from helpers import signup_form, switch_page_confirm


if st.session_state.login_state == True:
    st.switch_page('pages/re_submit.py')

text = st.session_state.text

st.header(text["signup_title"].upper(), anchor=False)


signup_form()

if st.button(f'{text["login_button"]}', icon='🔑'):
    st.session_state.available_id_list = []
    st.session_state.previous_page.append(st.session_state.current_page)
    st.switch_page('pages/login.py')