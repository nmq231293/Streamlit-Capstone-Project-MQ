import streamlit as st
import time

st.header('NHẬP SAI MẬT KHẨU QUÁ 3 LẦN, QUÝ KHÁCH SẼ ĐƯỢC ĐƯA VỀ TRANG CHỦ SAU 5 GIÂY', width='stretch',text_alignment='center')

with st.spinner('Đang điều hướng về trang chủ ...'):
    time.sleep(5)
    st.switch_page('pages/home.py')