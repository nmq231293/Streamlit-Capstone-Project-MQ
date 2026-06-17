import streamlit as st
from helpers import transfer_rehearsal

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text

st.header(text["transfer_rehearsal_title"].upper(), anchor=False)

if st.session_state.transfer_state == 0:
    st.switch_page('pages/re_submit.py')
elif st.session_state.transfer_state == 1:
    transfer_rehearsal()
    if st.button(f'{text["rh_transfer_button"]}', icon='💸'):
        st.switch_page('pages/transfer.py')  
else:
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0     
    st.session_state.dem_sai_mk = 0
    st.session_state.transfer_state = 0
    st.switch_page('pages/re_submit.py')
