import streamlit as st
from helpers import available_balance

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text

st.header(f'**:red[{text["transfer_success_title"].upper()}]**', width='stretch',text_alignment='center')

if st.session_state.transfer_state == 0:
    st.switch_page('pages/re_submit.py')    
elif st.session_state.transfer_state == 1:
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0     
    st.session_state.dem_sai_mk = 0
    st.session_state.transfer_state = 0
    st.switch_page('pages/re_submit.py')
elif st.session_state.transfer_state == 2:
    
    st.session_state.transfer_state = 0

    st.balloons()
    st.success(f'{text["transfer_success_title"]}')    
    st.write(f'{text["available_balance"]}: :green[{format(available_balance(st.session_state.acc_num), ",")} VNĐ]')
    col1, col2= st.columns(2)

    with col1:
        if st.button(f'{text["continue_transfer_button"]}', icon='💸'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/transfer.py')
    
    with col2:
        if st.button(f'{text["back_to_home_button"]}', icon='🏡'):
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/home.py')