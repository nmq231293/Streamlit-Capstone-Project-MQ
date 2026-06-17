import streamlit as st
from helpers import login_form, switch_page_confirm

if st.session_state.login_state == True:
    st.switch_page('pages/re_submit.py')

text = st.session_state.text

st.header(text["login_title"].upper(), anchor=False)

login_form()
if st.button(f'{text['signup_button']}', icon='🔐'):
    st.session_state.available_id_list = []
    st.session_state.previous_page.append(st.session_state.current_page)
    st.switch_page('pages/signup.py')