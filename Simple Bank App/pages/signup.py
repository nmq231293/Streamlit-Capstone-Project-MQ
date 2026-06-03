import streamlit as st
import pandas as pd
from helpers import signup_form


if st.session_state.login_state == True:
    st.switch_page('pages/home.py')
st.header('**:red[ĐĂNG KÝ]**', width='stretch',text_alignment='left')
# st.session_state.current_page = 'pages/signup.py'

signup_form()

if st.button('Quay về trang chủ', icon='🏡'):
    st.session_state.previous_page.append(st.session_state.current_page)
    st.switch_page('pages/home.py')