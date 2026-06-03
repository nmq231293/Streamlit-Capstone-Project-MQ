import streamlit as st
from helpers import login_form

if st.session_state.login_state == True:
    st.switch_page('pages/home.py')
    
st.header('**:red[ĐĂNG NHẬP]**', width='stretch',text_alignment='left')
# st.session_state.current_page = 'pages/login.py'

login_form()
if st.button('Quay về trang chủ', icon='🏡'):
    st.session_state.previous_page.append(st.session_state.current_page)
    st.switch_page('pages/home.py')