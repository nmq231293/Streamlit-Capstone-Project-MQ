import streamlit as st
from helpers import df, embed_chatbot, switch_page_check
from auth import restore_login_session, logout, session_expired
from styles import apply_main_styles, apply_background_image
from dictionary_data import DICTIONARY


st.set_page_config(layout='wide')


if "lang" not in st.session_state:
    st.session_state.lang = st.query_params.get("lang", "vi")


st.query_params["lang"] = st.session_state.lang


st.session_state.text = DICTIONARY[st.session_state.lang]


LANG_LABELS = {
    "vi": "Tiếng Việt",
    "en": "English"
}

st.title(f'**:rainbow[{st.session_state.text["main_title"]}]**', text_alignment='center', anchor=False)

col1, col2, col3, col4 = st.columns(4)
with col4:
    lang_options = ['vi', 'en']

    if chosen_lang := st.menu_button(
        f'{st.session_state.text["language"]}',
        lang_options,
        icon='🌐',
        type='secondary',
        width='content',
        format_func=lambda x: LANG_LABELS[x],
        key='lang_menu_btn',
    ):
        new_lang = st.session_state.get('lang_menu_btn', 'vi')
        st.session_state.lang = new_lang
        st.query_params["lang"] = new_lang
        st.rerun()


# Khôi phục đăng nhập từ token (logic chi tiết nằm trong auth.py)
restore_login_session(df)


# Gọi chức năng chatbot
embed_chatbot()


# Khởi tạo các trang và danh sách trang
home = st.Page('pages/home.py', title=st.session_state.text['home_title'], icon='🏡')
signup = st.Page('pages/signup.py', title=st.session_state.text['signup_title'], icon='🔐')
signup_success = st.Page('pages/signup_success.py', title=st.session_state.text['signup_success_title'], icon='🔐')
login = st.Page('pages/login.py', title=st.session_state.text['login_title'], icon='🔑')
login_success = st.Page('pages/login_success.py', title=st.session_state.text['login_success_title'], icon='🔑')
transfer = st.Page('pages/transfer.py', title=st.session_state.text['transfer_title'], icon='💸')
transfer_rehearsal = st.Page('pages/transfer_rehearsal.py', title=st.session_state.text['transfer_rehearsal_title'], icon='💸')
transfer_success = st.Page('pages/transfer_success.py', title=st.session_state.text['transfer_success_title'], icon='💸')
savings = st.Page('pages/savings.py', title=st.session_state.text['deposit_title'], icon='🏦')
loans = st.Page('pages/loans.py', title=st.session_state.text['withdraw_title'], icon='💳')
re_submit = st.Page('pages/re_submit.py', title=st.session_state.text['re_submit_title'], icon='😵')
password_wrong = st.Page('pages/password_wrong.py', title=st.session_state.text['password_wrong_title'], icon='❌')
account_settings = st.Page('pages/account_settings.py', title=st.session_state.text['account_settings_title'], icon='⚙️')
summary = st.Page('pages/summary.py', title=st.session_state.text['summary_title'], icon='📊')
history = st.Page('pages/history.py', title=st.session_state.text['history_title'], icon='📋')
admin_power = st.Page('pages/admin_power.py', title=st.session_state.text['admin_power_title'], icon='👑')

pg = st.navigation([home, signup, signup_success, login, login_success,
                    summary, transfer, transfer_success, transfer_rehearsal,
                    savings, loans, history,
                    re_submit, password_wrong, account_settings, admin_power], position='hidden')

# Khởi tạo các biến session_state
if 'wrong_password_count' not in st.session_state:
    st.session_state.wrong_password_count = 0
if 'acc_num' not in st.session_state:
    st.session_state.acc_num = ''
if 'acc_name' not in st.session_state:
    st.session_state.acc_name = ''
if 'signup_state' not in st.session_state:
    st.session_state.signup_state = False
if 'pr_temp_DoB' not in st.session_state:
    st.session_state.pr_temp_DoB = '00000001'
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
if 'power_level' not in st.session_state:
    st.session_state.power_level = 0
if 'password_change_need' not in st.session_state:
    st.session_state.password_change_need = False
if 'session_token' not in st.session_state:
    st.session_state.session_token = ''
if 'history_page' not in st.session_state:
    st.session_state.history_page = 1

# Áp ảnh nền (đã cache, không còn đọc lại file mỗi lần rerun)
if not apply_background_image("Simple Bank App/wallpaper/reynoldbank.png"):
    st.error("Không tìm thấy tệp ảnh 'Simple Bank App/wallpaper/reynoldbank.jpg'. Vui lòng kiểm tra lại đường dẫn.")

# Áp toàn bộ CSS giao diện
apply_main_styles()


st.session_state.current_page = pg._page

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(st.session_state.text['home_title'], icon='🏡'):
        if st.session_state.current_page != 'pages/home.py':
            switch_page_check('pages/home.py')
    if st.session_state.previous_page != []:
        if st.button(st.session_state.text['back_button'], icon='🔙'):
            switch_page_check(st.session_state.previous_page[-1], False)

with col4:
    if st.session_state.login_state:
        setting_options = [f'🙎🏻‍♂️ :green[{st.session_state.text["account_button"]}]', f'🔑 :red[{st.session_state.text["logout_button"]}]']
        if st.session_state.power_level > 0:
            setting_options.insert(0, f'👑 :violet[{st.session_state.text["admin_power_title"]}]')
        if settings_menu := st.menu_button(f'{st.session_state.text["settings_button"]}', setting_options, icon='⚙️', type='secondary', width='content', key='settings_menu_btn'):
            if settings_menu == f'👑 :violet[{st.session_state.text["admin_power_title"]}]':
                st.session_state.previous_page.append(st.session_state.current_page)
                switch_page_check('pages/admin_power.py')
            elif settings_menu == f'🙎🏻‍♂️ :green[{st.session_state.text["account_button"]}]':
                st.session_state.previous_page.append(st.session_state.current_page)
                switch_page_check('pages/account_settings.py')
            elif settings_menu == f'🔑 :red[{st.session_state.text["logout_button"]}]':
                logout()

pg.run()