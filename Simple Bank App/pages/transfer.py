import streamlit as st
from helpers import money_transfer_form, available_balance, beneficiary_list_dialog

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text

st.header(text["transfer_title"].upper(), anchor=False)

if st.session_state.login_state == True:
    st.write(f'{text["available_balance"]}: :green[{format(available_balance(st.session_state.acc_num), ",")} VNĐ]')

btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button(text['history_title'], icon='📋', key='btn_transfer_history'):
        st.session_state.previous_page.append(st.session_state.current_page)
        st.switch_page('pages/history.py')
with btn_col2:
    if st.button(text['tf_btn_beneficiary_list'], icon='📇', key='btn_open_beneficiary_list'):
        beneficiary_list_dialog()

if st.session_state.transfer_state == 0:
    money_transfer_form()
elif st.session_state.transfer_state == 2:
    st.session_state.transfer_state = 0
    money_transfer_form()
else:
    st.session_state.previous_page.append(st.session_state.current_page)
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0     
    st.session_state.transfer_state = 0
    st.switch_page('pages/re_submit.py')