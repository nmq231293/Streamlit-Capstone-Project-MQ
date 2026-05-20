import streamlit as st
from helpers import money_transfer, available_ballance

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

st.header('CHUYỂN KHOẢN THÀNH CÔNG', width='stretch',text_alignment='center')
st.session_state.current_page = 'pages/transfer_success.py'

if st.session_state.transfer_state == 0:
    st.switch_page('pages/re_submit.py')    
elif st.session_state.transfer_state == 1:
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0     
    st.session_state.dem_sai_mk = 0
    st.session_state.transfer_state = 0
    st.switch_page('pages/re_submit.py')
elif st.session_state.transfer_state == 2:
    
    st.session_state.transfer_state == 0

    st.balloons()
    
    col1, col2= st.columns(2)
    
    with col1:
        st.success('Chuyển khoản thành công')
        if st.session_state.login_state == True:
            st.write(f'Số dư khả dụng: {format(available_ballance(st.session_state.acc_num), ',')} VNĐ')
        if st.button('Tiếp tục chuyển khoản', icon='💸'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/transfer.py')
    
    with col2:
        if st.button('Quay về trang chủ', icon='🏡'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/home.py')