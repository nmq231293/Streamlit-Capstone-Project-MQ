import streamlit as st
import time 

st.header('**:red[TRANG KHÔNG KHẢ DỤNG, QUÝ KHÁCH SẼ QUAY VỀ TRANG CHỦ SAU 5 GIÂY]**', width='stretch',text_alignment='center')

with st.spinner('Đang điều hướng về trang chủ ...'):
    time.sleep(5)
    st.switch_page('pages/home.py')