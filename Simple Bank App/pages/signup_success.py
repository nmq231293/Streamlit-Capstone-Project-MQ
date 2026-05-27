import streamlit as st

if st.session_state.login_state == True or st.session_state.signup_state == False:
    st.switch_page('pages/re_submit.py')
st.header('**:red[ĐĂNG KÝ THÀNH CÔNG]**', width='stretch',text_alignment='center')
st.session_state.current_page = 'pages/signup_success.py'

st.balloons()
col1, col2, col3 = st.columns(3)
with col2:
    st.success(f'Đăng ký tài khoản thành công! Số tài khoản của bạn là {st.session_state.acc_num}')
    if st.button('Đến trang đăng nhập', icon='🔑'):
        st.session_state.previous_page.append(st.session_state.current_page)
        st.session_state.signup_state = False
        st.switch_page('pages/login.py')
    if st.button('Quay về trang chủ', icon='🏡'):
        st.session_state.previous_page.append(st.session_state.current_page)
        st.session_state.signup_state = False
        st.switch_page('pages/home.py')