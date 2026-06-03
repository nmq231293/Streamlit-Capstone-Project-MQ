import streamlit as st

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

st.header('**:red[NẠP TIỀN]**', width='stretch',text_alignment='left')
# st.session_state.current_page = 'pages/deposit.py'
