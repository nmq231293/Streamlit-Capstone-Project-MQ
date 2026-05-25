import streamlit as st
from helpers import transfer_rehearsal

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')


st.header('**:red[KIỂM TRA THÔNG TIN CHUYỂN KHOẢN]**', width='stretch',text_alignment='center')
st.session_state.current_page = 'pages/transfer_rehearsal.py'

if st.session_state.transfer_state == 0:
    st.switch_page('pages/re_submit.py')
elif st.session_state.transfer_state == 1:
    transfer_rehearsal()
else:
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0     
    st.session_state.dem_sai_mk = 0
    st.session_state.transfer_state = 0
    st.switch_page('pages/re_submit.py')
col1, col2 = st.columns(2)
with col1:
    if st.button('Quay lại trang trước', icon='🔙'):
        st.session_state.transfer_state == 0
        backward = st.session_state.previous_page.pop(-1)
        st.switch_page(backward)
with col2:
    if st.button('Quay về trang chủ', icon='🏡'):
        st.session_state.transfer_state == 0
        st.session_state.previous_page.append(st.session_state.current_page)
        st.switch_page('pages/home.py')