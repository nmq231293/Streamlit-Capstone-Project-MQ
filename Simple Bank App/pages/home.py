import streamlit as st
from helpers import available_balance

text = st.session_state.text

st.header(f'**:red[{text["home_title"].upper()}]**', width='stretch',text_alignment='left')

st.session_state.available_id_list = []

if not st.session_state.login_state:
    if st.session_state.logout_state:
        st.success(f'{text["logged_out_noti"]}')
        st.session_state.logout_state = False
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f'{text["login_title"]}', icon='🔑'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/login.py')

    with col2:
        if st.button(f'{text["signup_title"]}', icon='🔐'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/signup.py')

else:
    if st.session_state.login_noti:
        st.success(f'{text["logged_in_noti"]}')
        st.session_state.login_noti = False
    st.markdown(f'{text["greetings"]}: **:green[{st.session_state.acc_name}]**')
    st.write(f'{text["available_balance"]}: **:green[{format(available_balance(st.session_state.acc_num), ",")} VNĐ]**')

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f'{text["transfer_title"]}', icon='💸'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/transfer.py')

    with col2:                
        if st.button(f'{text["deposit_title"]}', icon='💵'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/deposit.py')

    with col3:
        if st.button(f'{text["withdraw_title"]}', icon='💰'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/withdraw.py')