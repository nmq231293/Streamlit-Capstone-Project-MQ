import streamlit as st
import time

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text

# --- THAY THẾ ST.HEADER BẰNG VŨ KHÍ INLINE CSS (ĐẢM BẢO NỔI KHỐI 100%) ---
login_title_text = text["login_success_title"].upper()

st.markdown(f"""
    <h3 style="
        text-align: center; 
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 46px; 
        font-weight: 900; 
        color: #00ffcc !important; 
        letter-spacing: 2px;
        margin-bottom: 30px;
        /* HIỆU ỨNG TẠO KHỐI 3D VÀ PHÁT QUANG NEON CHUẨN FINTECH */
        text-shadow: 0 1px 0 #00b38f,
                    0 2px 0 #00997a,
                    0 3px 0 #008066,
                    0 4px 0 #006652,
                    0 5px 10px rgba(0, 0, 0, 0.7),
                    0 0 15px rgba(0, 255, 204, 0.8),
                    0 0 30px rgba(0, 255, 204, 0.4);
    ">
        {login_title_text}
    </h3>
""", unsafe_allow_html=True)

# Giữ nguyên toàn bộ logic chạy ngầm của bạn
st.balloons()

with st.spinner(f'{text["login_success_spinner"]}'):
    time.sleep(3)
    st.switch_page('pages/home.py')
