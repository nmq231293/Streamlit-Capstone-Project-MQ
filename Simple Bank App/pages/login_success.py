import streamlit as st
import time

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

st.header('**:red[ĐĂNG NHẬP THÀNH CÔNG]**', width='stretch',text_alignment='center')
# st.session_state.current_page = 'pages/login_success.py'

st.balloons()

with st.spinner('Quý khách sẽ quay về trang chủ sau 5 giây ...'):
    time.sleep(5)
    st.switch_page('pages/home.py')