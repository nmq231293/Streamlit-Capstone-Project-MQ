import streamlit as st
from helpers import available_balance

text = st.session_state.text

st.header(text["home_title"].upper(), anchor=False)

st.session_state.available_id_list = []

if not st.session_state.login_state:
    if st.session_state.logout_state:
        st.success(f'{text["logged_out_noti"]}')
        st.session_state.logout_state = False
    col1, col2 = st.columns([3,1])
    with col1:
        if st.button(f'{text["login_title"]}', icon='🔑'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/login.py')

    with col2:
        if st.button(f'{text["signup_title"]}', icon='🔐'):
            st.session_state.available_id_list = []
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/signup.py')

else:
    from helpers import settle_matured_savings, settle_matured_loans
    settle_matured_savings(st.session_state.acc_num)
    settle_matured_loans(st.session_state.acc_num)

    if st.session_state.login_noti:
        st.success(f'{text["logged_in_noti"]}')
        st.session_state.login_noti = False
    st.markdown(f'{text["greetings"]}: <span class="balance-glow">**{st.session_state.acc_name}**</span>',
                unsafe_allow_html=True)
    
    # Đã bọc con số vào thẻ span có class riêng để CSS kích sáng hacker
    balance_value = format(available_balance(st.session_state.acc_num), ",")
    st.markdown(
        f'{text["available_balance"]}: <span class="balance-glow">**{balance_value} VNĐ**</span>', 
        unsafe_allow_html=True
    )


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(f'{text["summary_btn"]}', icon='📊'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/summary.py')
    with col2:
        if st.button(f'{text["transfer_title"]}', icon='💸'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/transfer.py')
    with col3:
        if st.button(f'{text["deposit_title"]}', icon='🏦'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/savings.py')
    with col4:
        if st.button(f'{text["withdraw_title"]}', icon='💳'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/loans.py')