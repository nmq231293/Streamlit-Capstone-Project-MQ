import streamlit as st

# Giữ nguyên phần kiểm tra trạng thái ban đầu của bạn (nếu có)
if not st.session_state.get("signup_state", False):
    st.switch_page("pages/home.py")

text = st.session_state.text
acc_num = st.session_state.get("acc_num", "00000000")

# ==============================================================================
# 1. TIÊU ĐỀ "ĐĂNG KÝ THÀNH CÔNG" MÀU ĐỎ NEON TẠO KHỐI 3D
# ==============================================================================
signup_success_title = text["signup_success_title"].upper()

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
        {signup_success_title}
    </h3>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. KHUNG KÍNH MỜ GLASSMORPHISM GIÚP DÒNG THÔNG BÁO SIÊU DỄ ĐỌC
# ==============================================================================
# Tách nội dung chữ và số tài khoản để kích màu riêng biệt
success_msg = text["signup_success_message"]

st.markdown(f"""
    <div style="
        background-color: rgba(15, 10, 30, 0.65); /* Nền tối mờ che bớt chi tiết đồng xu */
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 18px 25px;
        margin: 0 auto 35px auto;
        max-width: 650px;
        text-align: center;
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    ">
        <p style="
            color: #e2e8f0 !important; /* Chữ màu trắng bạc dịu mắt */
            font-size: 16px;
            font-weight: 500;
            margin: 0;
            line-height: 1.6;
        ">
            {success_msg} 
            <span style="
                color: #00ffcc !important; /* Số tài khoản bừng sáng màu Xanh Mint Neon */
                font-weight: 800;
                font-size: 20px;
                letter-spacing: 1px;
                margin-left: 5px;
                text-shadow: 0 0 8px rgba(0, 255, 204, 0.6);
            ">
                {acc_num}
            </span>
        </p>
    </div>
""", unsafe_allow_html=True)


# ==============================================================================
# 3. GIỮ NGUYÊN CÁC NÚT BẤM ĐIỀU HƯỚNG PHÍA DƯỚI CỦA BẠN
# ==============================================================================
# Sắp xếp các nút bấm như code hiện tại của bạn
c1, c2, c3 = st.columns(3)
with c2:
    empty_c1, button_c2, empty_c3 = st.columns([1,2,1])
    with button_c2:
        if st.button(text["to_login_button"], icon='🔑'):
            st.switch_page("pages/login.py")

        if st.button(text["back_to_home_button"], icon='🏠'):
            st.switch_page("pages/home.py")
