import streamlit as st
from helpers import money_transfer_form, available_balance

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text

st.header(text["transfer_title"].upper(), anchor=False)

if st.session_state.login_state == True:
    st.write(f'{text["available_balance"]}: :green[{format(available_balance(st.session_state.acc_num), ",")} VNĐ]')

if st.session_state.transfer_state <2:
    money_transfer_form()
else:
    st.session_state.previous_page.append(st.session_state.current_page)
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0     
    st.session_state.dem_sai_mk = 0
    st.session_state.transfer_state = 0
    st.switch_page('pages/re_submit.py')