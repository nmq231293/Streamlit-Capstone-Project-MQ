import streamlit as st
from helpers import switch_page_check, embed_chatbot
from dictionary_data import DICTIONARY

if 'text' not in st.session_state:
    st.session_state.text = {}

if "lang" not in st.session_state:
    if "lang" in st.query_params:
        st.session_state.lang = st.query_params["lang"]
else:
    if 'lang' not in st.query_params:
        st.query_params["lang"] = st.session_state.lang


LANG_LABELS = {
    "vi": "Tiếng Việt",
    "en": "English"
}

col1, col2, col3, col4 = st.columns(4)
with col4:
    if 'lang' in st.session_state:
        lang_choice = 1 if st.session_state.lang == 'en' else 0
    else:
        lang_choice = 0

    lang_code = st.selectbox(
        f"{st.session_state.text.get('language', 'Ngôn ngữ')}:",
        options=["vi", "en"],
        index=lang_choice,
        format_func=lambda x: LANG_LABELS[x],
        width=150
    )

    st.session_state.lang = lang_code
    st.query_params["lang"] = lang_code


st.session_state.text = DICTIONARY[lang_code]

st.set_page_config(layout='wide')
st.title(f'**:rainbow[{st.session_state.text["main_title"]}]**', width='stretch', text_alignment='center')

embed_chatbot()

home = st.Page('pages/home.py', title=st.session_state.text['home_title'], icon='🏡')
signup = st.Page('pages/signup.py', title=st.session_state.text['signup_title'], icon='🔐')
signup_success = st.Page('pages/signup_success.py', title=st.session_state.text['signup_success_title'], icon='🔐')
login = st.Page('pages/login.py', title=st.session_state.text['login_title'], icon='🔑')
login_success = st.Page('pages/login_success.py', title=st.session_state.text['login_success_title'], icon='🔑')
transfer = st.Page('pages/transfer.py', title=st.session_state.text['transfer_title'], icon='💸')
transfer_rehearsal = st.Page('pages/transfer_rehearsal.py', title=st.session_state.text['transfer_rehearsal_title'], icon='💸')
transfer_success = st.Page('pages/transfer_success.py', title=st.session_state.text['transfer_success_title'], icon='💸')
deposit = st.Page('pages/deposit.py', title=st.session_state.text['deposit_title'], icon='💵')
deposit_success = st.Page('pages/deposit_success.py', title=st.session_state.text['deposit_success_title'], icon='💵')
withdraw = st.Page('pages/withdraw.py', title=st.session_state.text['withdraw_title'], icon='💰')
withdraw_success = st.Page('pages/withdraw_success.py', title=st.session_state.text['withdraw_success_title'], icon='💰')
re_submit = st.Page('pages/re_submit.py', title=st.session_state.text['re_submit_title'], icon='😵')
password_wrong = st.Page('pages/password_wrong.py', title=st.session_state.text['password_wrong_title'], icon='❌')
account_settings = st.Page('pages/account_settings.py', title=st.session_state.text['account_settings_title'], icon='⚙️')
admin_power = st.Page('pages/admin_power.py', title=st.session_state.text['admin_power_title'], icon='👑')

pg = st.navigation([home, signup, signup_success, login, login_success, transfer, transfer_success,
                    transfer_rehearsal, deposit, deposit_success, withdraw, withdraw_success,
                    re_submit, password_wrong, account_settings, admin_power], position='hidden')

if 'language_num' not in st.session_state:
    st.session_state.language_num = 0
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
if 'power_level' not in st.session_state:
    st.session_state.power_level = 0

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
    if st.button(st.session_state.text['home_title'], icon='🏡'):
        if st.session_state.current_page != 'pages/home.py':
            switch_page_check('pages/home.py')
    if st.session_state.previous_page != []:
        if st.button(st.session_state.text['back_button'], icon='🔙'):
            switch_page_check(st.session_state.previous_page[-1], False)

setting_options = [f'🙎🏻‍♂️ :green[{st.session_state.text["account_button"]}]', f'🔑 :red[{st.session_state.text["logout_button"]}]']
if st.session_state.power_level > 0:
    setting_options.insert(0, f'👑 :violet[{st.session_state.text["admin_power_title"]}]')

with col4:
    if st.session_state.login_state:
        if settings_menu := st.menu_button(f'{st.session_state.text["settings_button"]}', setting_options, icon='⚙️', type='secondary', width='content'):
            if settings_menu == f'👑 :violet[{st.session_state.text["admin_power_title"]}]':
                st.session_state.previous_page.append(st.session_state.current_page)
                st.switch_page('pages/admin_power.py')
            elif settings_menu == f'🙎🏻‍♂️ :green[{st.session_state.text["account_button"]}]':
                st.session_state.previous_page.append(st.session_state.current_page)
                st.switch_page('pages/account_settings.py')
            elif settings_menu == f'🔑 :red[{st.session_state.text["logout_button"]}]':
                st.session_state.login_state = False
                st.session_state.login_noti = False
                st.session_state.acc_num = ''
                st.session_state.acc_name = ''
                st.session_state.power_level = 0
                st.session_state.receiver_num = ''
                st.session_state.transfer_amount = 0
                st.session_state.wrong_password_count = 0
                st.session_state.transfer_state = 0
                st.session_state.signup_state = False
                st.session_state.available_id_list = []
                st.session_state.logout_state = True
                if st.session_state.current_page != 'pages/home.py':
                    st.session_state.previous_page.append(st.session_state.current_page)
                    st.switch_page('pages/home.py')
        # with st.popover('Cài đặt', icon='⚙️',type='secondary',use_container_width=False,width='content'):
        #     if st.session_state.power_level > 0:
        #         if st.button('**:violet[Công cụ quản trị trang]**', icon='👑'):
        #             st.session_state.previous_page.append(st.session_state.current_page)
        #             st.switch_page('pages/admin_power.py')
        #     if st.button('**:green[Tài khoản]**', icon='🙎🏻‍♂️'):
        #         st.session_state.previous_page.append(st.session_state.current_page)
        #         st.switch_page('pages/account_settings.py')
        #     if st.button('**:red[Đăng xuất]**', icon='🔑'):
        #         st.session_state.login_state = False
        #         st.session_state.login_noti = False
        #         st.session_state.acc_num = ''
        #         st.session_state.acc_name = ''
        #         st.session_state.power_level = 0
        #         st.session_state.receiver_num = ''
        #         st.session_state.transfer_amount = 0
        #         st.session_state.wrong_password_count = 0
        #         st.session_state.transfer_state = 0
        #         st.session_state.signup_state = False
        #         st.session_state.available_id_list = []
        #         st.session_state.logout_state = True
        #         if st.session_state.current_page != 'pages/home.py':
        #             st.session_state.previous_page.append(st.session_state.current_page)
        #             st.switch_page('pages/home.py')

pg.run()