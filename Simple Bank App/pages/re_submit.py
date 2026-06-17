import streamlit as st
import time 

text = st.session_state.text

# --- THAY THẾ ST.HEADER BẰNG VŨ KHÍ INLINE CSS (MÀU ĐỎ NEON TẠO KHỐI 3D) ---
re_submit_text = text["re_submit_title"].upper()

st.markdown(f"""
    <h3 style="
        text-align: center; 
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 42px; 
        font-weight: 900; 
        color: #ff4d4d !important; 
        letter-spacing: 2px;
        margin-top: 20px;
        margin-bottom: 30px;
        /* HIỆU ỨNG TẠO KHỐI 3D VÀ PHÁT QUANG NEON ĐỎ CYBERPUNK */
        text-shadow: 0 1px 0 #cc0000,
                    0 2px 0 #b30000,
                    0 3px 0 #990000,
                    0 4px 0 #800000,
                    0 5px 10px rgba(0, 0, 0, 0.8),
                    0 0 15px rgba(255, 77, 77, 0.8),
                    0 0 30px rgba(255, 77, 77, 0.4);
    ">
        {re_submit_text}
    </h3>
""", unsafe_allow_html=True)

# Giữ nguyên cấu trúc vòng lặp tải và chuyển trang của bạn
with st.form(key="form_hidden_resubmit", border=False):
    with st.spinner(f'{text["redirecting_message"]}'):
        time.sleep(3)
        st.switch_page('pages/home.py')
