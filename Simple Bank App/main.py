import streamlit as st
from helpers import switch_page_check#, embed_chatbot

st.set_page_config(layout='wide')
st.title('**:rainbow[NGÂN HÀNG KACHÀPÚ]**', width='stretch', text_alignment='center')

#embed_chatbot()

home = st.Page('pages/home.py', title='Trang chủ', icon='🏡')
signup = st.Page('pages/signup.py', title='Đăng ký', icon='🔐')
signup_success = st.Page('pages/signup_success.py', title='Đăng ký thành công', icon='🔐')
login = st.Page('pages/login.py', title='Đăng nhập', icon='🔑')
login_success = st.Page('pages/login_success.py', title='Đăng nhập thành công', icon='🔑')
transfer = st.Page('pages/transfer.py', title='Chuyển khoản', icon='💸')
transfer_rehearsal = st.Page('pages/transfer_rehearsal.py', title='Kiểm tra chuyển khoản', icon='💸')
transfer_success = st.Page('pages/transfer_success.py', title='Chuyển khoản thành công', icon='💸')
deposit = st.Page('pages/deposit.py', title='Nạp tiền', icon='💵')
deposit_success = st.Page('pages/deposit_success.py', title='Nạp tiền thành công', icon='💵')
withdraw = st.Page('pages/withdraw.py', title='Rút tiền', icon='💰')
withdraw_success = st.Page('pages/withdraw_success.py', title='Rút tiền thành công', icon='💰')
re_submit = st.Page('pages/re_submit.py', title='Không khả dụng', icon='😵')
password_wrong = st.Page('pages/password_wrong.py', title='Sai mật khẩu', icon='❌')
account_settings = st.Page('pages/account_settings.py', title='Sai mật khẩu', icon='⚙️')
AI_assistant = st.Page('pages/AI_assistant.py', title='AI hỗ trợ', icon='🤖')


pg = st.navigation([home, signup, signup_success, login, login_success, transfer, transfer_success,
                    transfer_rehearsal, deposit, deposit_success, withdraw, withdraw_success,
                    re_submit, password_wrong, account_settings, AI_assistant], position='hidden')

if 'dem_sai_mk' not in st.session_state:
    st.session_state.dem_sai_mk = 0
if 'acc_num' not in st.session_state:
    st.session_state.acc_num = ''
if 'acc_name' not in st.session_state:
    st.session_state.acc_name = ''
if 'signup_state' not in st.session_state:
    st.session_state.signup_state = False
if 'pr_temp_DoB' not in st.session_state:
    st.session_state.pr_temp_DoB = '00000001'
if 'login_state' not in st.session_state:
    st.session_state.login_state = False
if 'login_noti' not in st.session_state:
    st.session_state.login_noti = False
if 'previous_page' not in st.session_state:
    st.session_state.previous_page = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = ''
if 'transfer_state' not in st.session_state:
    st.session_state.transfer_state = 0
if 'receiver_num' not in st.session_state:
    st.session_state.receiver_num = ''
if 'transfer_amount' not in st.session_state:
    st.session_state.transfer_amount = 0
if 'available_id_list' not in st.session_state:
    st.session_state.available_id_list = []
if 'logout_state' not in st.session_state:
    st.session_state.logout_state = False
    
    
st.markdown(
    """
    <style>
    [data-testid="stWidgetLabel"] p {
        font-weight: bold;
        color: #ffaf53 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.session_state.current_page = pg._page

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button('Trang chủ', icon='🏡'):
        if st.session_state.current_page != 'pages/home.py':
            switch_page_check('pages/home.py')
    if st.session_state.previous_page != []:
        if st.button('Quay lại trang trước', icon='🔙'):
            switch_page_check(st.session_state.previous_page[-1], False)

with col4:
    if st.session_state.login_state:
        with st.popover('Cài đặt', icon='⚙️',type='secondary',use_container_width=False,width='content'):
            if st.button('**:green[Tài khoản]**', icon='🙎🏻‍♂️'):
                st.session_state.previous_page.append(st.session_state.current_page)
                st.switch_page('pages/account_settings.py')
            if st.button('**:red[Đăng xuất]**', icon='🔑'):
                st.session_state.login_state = False
                st.session_state.login_noti = False
                st.session_state.acc_num = ''
                st.session_state.receiver_num = ''
                st.session_state.transfer_amount = 0
                st.session_state.dem_sai_mk = 0
                st.session_state.transfer_state = 0
                st.session_state.signup_state = False
                st.session_state.available_id_list = []
                st.session_state.logout_state = True
                if st.session_state.current_page != 'pages/home.py':
                    st.session_state.previous_page.append(st.session_state.current_page)
                st.switch_page('pages/home.py')
    if st.button('**:violet[AI hỗ trợ]**', icon='🤖'):
        st.session_state.previous_page.append(st.session_state.current_page)
        st.switch_page('pages/AI_assistant.py')        

pg.run()