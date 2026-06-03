import streamlit as st
from helpers import available_balance

st.header('**:red[TRANG CHỦ]**', width='stretch',text_alignment='left')
# st.session_state.current_page = 'pages/home.py'

st.session_state.available_id_list = []

if not st.session_state.login_state:
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Đăng nhập', icon='🔑'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/login.py')

    with col2:
        if st.button('Đăng ký', icon='🔐'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/signup.py')

else:
    if st.session_state.login_noti:
        st.success('Đăng nhập thành công')
        st.session_state.login_noti = False
    st.markdown(f'Xin chào **:green[{st.session_state.acc_name}]**')
    st.write(f'Số dư khả dụng: **:green[{format(available_balance(st.session_state.acc_num), ',')} VNĐ]**')

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('Chuyển khoản', icon='💸'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/transfer.py')

    with col2:                
        if st.button('Nạp tiền', icon='💵'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/deposit.py')

    with col3:
        if st.button('Rút tiền', icon='💰'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/withdraw.py')