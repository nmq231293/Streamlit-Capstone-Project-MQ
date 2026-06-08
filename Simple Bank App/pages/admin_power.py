import streamlit as st

if st.session_state.power_level == 0:
    st.switch_page('pages/home.py')
st.header('**:red[QUẢN TRỊ TRANG]**', width='stretch',text_alignment='left')