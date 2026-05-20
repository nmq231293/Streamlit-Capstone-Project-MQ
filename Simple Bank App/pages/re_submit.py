import streamlit as st

st.header('TRANG KHÔNG KHẢ DỤNG, VUI LÒNG KIỂM TRA LẠI', width='stretch',text_alignment='center')

col1, col2, col3 = st.columns(3)
with col2:
    if st.button('Quay lại trang trước', icon='🔙'):
        backward = st.session_state.previous_page.pop(-1)
        st.switch_page(backward)
    if st.button('Quay về trang chủ', icon='🏡'):
        st.session_state.transfer_state == 0
        st.switch_page('pages/home.py')