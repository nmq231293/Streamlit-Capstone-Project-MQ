import streamlit as st
from helpers import available_balance

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text

transfer_success_title = text["transfer_success_title"].upper()

st.markdown(f"""
    <h3 style="
        text-align: center; 
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 46px; 
        font-weight: 900; 
        color: #ff4d4d !important; 
        letter-spacing: 2px;
        margin-top: 20px;
        margin-bottom: 25px;
        /* HIỆU ỨNG TẠO KHỐI 3D VÀ PHÁT QUANG NEON ĐỎ */
        text-shadow: 0 1px 0 #cc0000,
                    0 2px 0 #b30000,
                    0 3px 0 #990000,
                    0 4px 0 #800000,
                    0 5px 10px rgba(0, 0, 0, 0.8),
                    0 0 15px rgba(255, 77, 77, 0.8),
                    0 0 30px rgba(255, 77, 77, 0.4);
    ">
        {transfer_success_title}
    </h3>
""", unsafe_allow_html=True)

if st.session_state.transfer_state == 0:
    st.switch_page('pages/re_submit.py')    
elif st.session_state.transfer_state == 1:
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0     
    st.session_state.dem_sai_mk = 0
    st.session_state.transfer_state = 0
    st.switch_page('pages/re_submit.py')
elif st.session_state.transfer_state == 2:

    st.balloons()
    st.success(f'{text["transfer_success_title"]}')    
    st.write(f'{text["available_balance"]}: :green[{format(available_balance(st.session_state.acc_num), ",")} VNĐ]')
    col1, col2= st.columns(2)

    with col1:
        if st.button(f'{text["continue_transfer_button"]}', icon='💸'):
            st.session_state.transfer_state = 0
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/transfer.py')
    
    with col2:
        if st.button(f'{text["back_to_home_button"]}', icon='🏡'):
            st.session_state.transfer_state = 0
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/home.py')