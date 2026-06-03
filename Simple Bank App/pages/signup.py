import streamlit as st
import pandas as pd
from helpers import signup_form, switch_page_check


if st.session_state.login_state == True:
    st.switch_page('pages/re_submit.py')

st.header('**:red[ĐĂNG KÝ]**', width='stretch',text_alignment='left')
# st.session_state.current_page = 'pages/signup.py'

signup_form()

if st.button('Quay về trang chủ', icon='🏡'):
    switch_page_check('pages/home.py')