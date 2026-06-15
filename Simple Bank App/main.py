import streamlit as st
import time
from itsdangerous import URLSafeSerializer, BadSignature
from helpers import df, df_init, on_language_change, switch_page_check, embed_chatbot, logout, session_expired
from dictionary_data import DICTIONARY

# Quy định bắt buộc: Thiết lập cấu hình trang nằm ở dòng đầu tiên
st.set_page_config(layout='wide')


if "lang" not in st.session_state:
    st.session_state.lang = st.query_params.get("lang", "vi")


st.query_params["lang"] = st.session_state.lang


st.session_state.text = DICTIONARY[st.session_state.lang]


LANG_LABELS = {
    "vi": "Tiếng Việt",
    "en": "English"
}


col1, col2, col3, col4 = st.columns(4)
with col4:
    
    current_index = 1 if st.session_state.lang == 'en' else 0
    
    st.selectbox(
        f'{st.session_state.text['language']}',
        options=["vi", "en"],
        index=current_index,
        format_func=lambda x: LANG_LABELS[x],
        key="temp_lang_key",
        on_change=on_language_change,
        width=125
    )


# ==============================================================================
# BỘ QUÉT KHÔI PHỤC ĐĂNG NHẬP THEO LUỒNG BẢO MẬT BẠN GỢI Ý
# ==============================================================================
if 'session_expired' not in st.session_state:
    if 'session_expired' in st.query_params:
        st.session_state.session_expired = st.query_params['session_expired']

if 'session_expired' in st.session_state:
    url_token = st.query_params.get("auth_token", None)
    if url_token:
        try:
            auth_serializer = URLSafeSerializer(st.secrets["SECRET_KEY"])
            timestamped_id = auth_serializer.loads(url_token)
            login_timestamp, stk_decrypted = timestamped_id.split("|", 1)
            
            st.session_state.acc_num = stk_decrypted
            st.session_state.login_state = False
            session_expired(st.session_state.session_expired)
            
        except BadSignature:
            st.query_params.clear()
            st.session_state.login_state = False     
    else:
        st.query_params.clear()
        st.session_state.login_state = False     

else:
    if "login_state" not in st.session_state:
        url_token = st.query_params.get("auth_token", None)
        if url_token:
            try:
                auth_serializer = URLSafeSerializer(st.secrets["SECRET_KEY"])
                timestamped_id = auth_serializer.loads(url_token)
                last_activity_time, stk_decrypted = timestamped_id.split("|", 1)
                
                if stk_decrypted in df.index:
                    worksheet, df = df_init()
                    session_value = str(df.loc[stk_decrypted, 'Session'])
                    previous_session_value = str(df.loc[stk_decrypted, 'Previous_Session'])                
                    if "|" in session_value:
                        # Tách chuỗi: lấy mốc thời gian và thông tin trình duyệt đã lưu trên Sheet
                        sheet_time, sheet_browser = session_value.split("|", 1) # Sử dụng split("|", 1) để tránh lỗi nếu chuỗi trình duyệt có dấu |
                        # Lấy thông tin trình duyệt hiện thời của thiết bị đang F5
                        current_browser = st.context.headers.get("User-Agent", "UnknownBrowser")

                        
                        # KIỂM TRA CHÉO: Thời gian < 1 tiếng VÀ Thông tin trình duyệt phải TRÙNG KHỚP 100%
                        if current_browser == sheet_browser:
                            CURRENT_TIME = time.time()
                            if CURRENT_TIME - float(sheet_time) <= 3600:
                                if 'last_activity_time' not in st.session_state:
                                    st.session_state.last_activity_time = float(last_activity_time)                                
                                st.session_state.login_state = True
                                st.session_state.acc_num = stk_decrypted
                                st.session_state.acc_name = df.loc[stk_decrypted, 'Name']

                                match stk_decrypted:
                                    case 'creator': st.session_state.power_level = 3
                                    case 'tester': st.session_state.power_level = 2
                                    case 'viewer': st.session_state.power_level = 1
                                    case _: st.session_state.power_level = 0

                            else:
                                st.session_state.session_expired = 'expired'
                                logout('expired')
                    if "login_state" not in st.session_state: 
                        if "|" in previous_session_value:
                            # Lấy thông tin trình duyệt hiện thời của thiết bị đang F5
                            current_browser = st.context.headers.get("User-Agent", "UnknownBrowser")                         
                            previous_sheet_time, previous_sheet_browser = previous_session_value.split("|", 1)
                            if current_browser == previous_sheet_browser:
                                st.session_state.session_expired = 'hijacked'
                                logout('hijacked')
                            else:
                                st.query_params.clear()
                                st.session_state.login_state = False
                        else:
                            # Sai trình duyệt (Kẻ xấu copy link sang thiết bị khác) hoặc hết hạn -> Đá văng
                            st.query_params.clear()
                            st.session_state.login_state = False
                else:
                    st.query_params.clear()
                    st.session_state.login_state = False
                    
            except BadSignature:
                st.query_params.clear()
                st.session_state.login_state = False
        else:
            st.session_state.login_state = False

# Đảm bảo URL luôn giữ Token này khi người dùng chuyển qua lại các menu navbar mặc định
if st.session_state.get("login_state"):
    CURRENT_TIME = time.time()
    if "auth_token" not in st.query_params:
        last_activity_timestamp = str(int(CURRENT_TIME))
        new_timestamped_id = f"{last_activity_timestamp}|{st.session_state.acc_num}"
        auth_serializer = URLSafeSerializer(st.secrets["SECRET_KEY"])
        st.query_params["auth_token"] = auth_serializer.dumps(new_timestamped_id)
    if CURRENT_TIME - st.session_state.last_activity_time <= 600:
        st.session_state.last_activity_time = CURRENT_TIME
    else:
        st.session_state.session_expired = 'timeout'
        del st.session_state.last_activity_time
        logout('timeout')       





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
                logout()

pg.run()