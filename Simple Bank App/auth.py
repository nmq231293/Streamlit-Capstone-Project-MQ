# ==============================================================================
# AUTH.PY - AUTHENTICATION AND SESSION MANAGEMENT MODULE
# ==============================================================================
import streamlit as st
import time
from itsdangerous import URLSafeSerializer, BadSignature

from helpers import df_init, update_accounts_safely, OptimisticLockError

# --- Hàm đăng xuất người dùng, xóa trạng thái đăng nhập và chuyển hướng về trang chủ hoặc trang đăng nhập ---
def logout(cause: str = 'manual'):
    if cause == 'manual':
        def invalidate_session(current_df):
            current_df.loc[st.session_state.acc_num, 'Session'] = '0'
        try:
            update_accounts_safely([st.session_state.acc_num], invalidate_session)
        except OptimisticLockError:
            pass

    st.session_state.login_state = False
    st.session_state.login_noti = False
    st.session_state.acc_num = ''
    st.session_state.acc_name = ''
    st.session_state.session_token = ''
    st.session_state.power_level = 0
    st.session_state.receiver_num = ''
    st.session_state.transfer_amount = 0
    st.session_state.wrong_password_count = 0
    st.session_state.transfer_state = 0
    st.session_state.signup_state = False
    st.session_state.available_id_list = []

    if cause == 'manual':
        st.query_params.clear()
        st.session_state.logout_state = True
        if st.session_state.current_page != 'pages/home.py':
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/home.py')
    else:
        st.query_params['session_expired'] = cause
        st.session_state.auth_token = st.query_params['auth_token']
        st.session_state.logout_state = False
        st.rerun()

# --- Hộp thoại cảnh báo khi phiên đăng nhập hết hạn (60p), không hoạt động (10p) hoặc bị đăng nhập từ thiết bị khác ---
@st.dialog('**:yellow[Cảnh Báo / Warning]**', width='medium', dismissible=False)
def session_expired(reason: str = 'expired'):
    text = st.session_state.text

    if reason == 'expired':
        session_expired_dialog_title = text['dialog_session_expired']
        session_expired_dialog_text = text['dialog_session_expired_info']
    elif reason == 'timeout':
        session_expired_dialog_title = text['dialog_session_timeout']
        session_expired_dialog_text = text['dialog_session_timeout_info']
    else:
        session_expired_dialog_title = text['dialog_session_hijacked']
        session_expired_dialog_text = text['dialog_session_hijacked_info']

    st.markdown(f"<h1 style='text-align: center; color: #ff5555; margin-top:0;'>⚠️ {session_expired_dialog_title.upper()} ⚠️</h3>", unsafe_allow_html=True)
    st.markdown('<div class="dialog-divider"></div>', unsafe_allow_html=True)
    st.info(session_expired_dialog_text)
    st.markdown('<div class="dialog-divider"></div>', unsafe_allow_html=True)

    def invalidate_all_sessions(current_df):
        if reason == 'expired' or reason == 'timeout':
            current_df.loc[st.session_state.acc_num, 'Session'] = '0'
        else:
            current_df.loc[st.session_state.acc_num, 'Session'] = '0'
            current_df.loc[st.session_state.acc_num, 'Previous_Session'] = '0'

    c1, c2, c3 = st.columns([3, 3, 2])
    with c1:
        if st.button(f'**:green[{text["relogin_button"]}]**', icon='🔑', key="btn_sess_login"):
            update_accounts_safely([st.session_state.acc_num], invalidate_all_sessions)
            del st.session_state.session_expired
            del st.session_state.acc_num
            del st.session_state.auth_token
            st.query_params.clear()
            st.session_state.previous_page.append(st.session_state.current_page)
            st.switch_page('pages/login.py')

    with c2:
        if reason == 'hijacked':
            if st.button(f'**:green[{text["change_password_button"]}]**', icon='🔓', key="btn_hj_change_pass"):
                update_accounts_safely([st.session_state.acc_num], invalidate_all_sessions)
                del st.session_state.session_expired
                del st.session_state.auth_token
                st.query_params.clear()
                st.session_state.password_change_need = True
                st.session_state.previous_page.append(st.session_state.current_page)
                st.switch_page('pages/account_settings.py')

    with c3:
        if st.button(f'**:red[{text.get("dialog_stay_btn", "Ở lại trang này")}]**', icon='❗', key="btn_sess_stay"):
            update_accounts_safely([st.session_state.acc_num], invalidate_all_sessions)
            del st.session_state.session_expired
            del st.session_state.acc_num
            del st.session_state.auth_token
            st.query_params.clear()
            st.rerun()

# =================================================================================
# Hàm khôi phục trạng thái đăng nhập từ auth_token trên URL, xác thực và xử lý
# các trường hợp hết hạn, không hoạt động hoặc bị đăng nhập từ thiết bị khác
# =================================================================================
def restore_login_session(df):
    """
    Đọc auth_token trên URL, xác thực, và khôi phục trạng thái đăng nhập vào session_state.
    Xử lý: session hết hạn, timeout do không hoạt động, và bị đăng nhập từ thiết bị khác.
    """
    if 'auth_token' in st.session_state:
        st.query_params['auth_token'] = st.session_state.auth_token
    if 'session_expired' in st.session_state:
        st.query_params['session_expired'] = st.session_state.session_expired

    if 'session_expired' not in st.session_state:
        if 'session_expired' in st.query_params:
            st.session_state.session_expired = st.query_params['session_expired']

    if 'session_expired' in st.session_state:
        url_token = st.query_params.get("auth_token", None)
        if url_token:
            try:
                auth_serializer = URLSafeSerializer(st.secrets["SECRET_KEY"])
                timestamped_id = auth_serializer.loads(url_token)
                login_timestamp, stk_decrypted, _ = timestamped_id.split("|", 2)

                st.session_state.acc_num = stk_decrypted
                st.session_state.login_state = False
                session_expired(st.session_state.session_expired)

            except (BadSignature, ValueError):
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
                    last_activity_time, stk_decrypted, token_decrypted = timestamped_id.split("|", 2)

                    if stk_decrypted in df.index:
                        worksheet, df = df_init()
                        session_value = str(df.loc[stk_decrypted, 'Session'])
                        previous_session_value = str(df.loc[stk_decrypted, 'Previous_Session'])
                        if "|" in session_value:
                            sheet_time, sheet_token = session_value.split("|", 1)

                            if token_decrypted == sheet_token:
                                CURRENT_TIME = time.time()
                                if CURRENT_TIME - float(sheet_time) <= 3600:
                                    if 'last_activity_time' not in st.session_state:
                                        st.session_state.last_activity_time = float(last_activity_time)
                                    st.session_state.login_state = True
                                    st.session_state.acc_num = stk_decrypted
                                    st.session_state.acc_name = df.loc[stk_decrypted, 'Name']
                                    st.session_state.session_token = token_decrypted
                                    st.session_state.power_level = int(df.loc[stk_decrypted, 'Power_Level'])

                                else:
                                    st.session_state.session_expired = 'expired'
                                    logout('expired')
                        if "login_state" not in st.session_state:
                            if "|" in previous_session_value:
                                previous_sheet_time, previous_sheet_token = previous_session_value.split("|", 1)
                                if token_decrypted == previous_sheet_token:
                                    st.session_state.session_expired = 'hijacked'
                                    logout('hijacked')
                                else:
                                    st.query_params.clear()
                                    st.session_state.login_state = False
                            else:
                                st.query_params.clear()
                                st.session_state.login_state = False
                    else:
                        st.query_params.clear()
                        st.session_state.login_state = False

                except BadSignature:
                    st.query_params.clear()
                    st.session_state.login_state = False
                except ValueError:
                    st.query_params.clear()
                    st.session_state.login_state = False
            else:
                st.session_state.login_state = False

    if st.session_state.get("login_state"):
        CURRENT_TIME = time.time()
        last_activity_timestamp = str(int(CURRENT_TIME))
        new_timestamped_id = f"{last_activity_timestamp}|{st.session_state.acc_num}|{st.session_state.session_token}"
        auth_serializer = URLSafeSerializer(st.secrets["SECRET_KEY"])
        st.query_params["auth_token"] = auth_serializer.dumps(new_timestamped_id)

        if CURRENT_TIME - st.session_state.last_activity_time <= 600:
            st.session_state.last_activity_time = CURRENT_TIME
        else:
            st.session_state.session_expired = 'timeout'
            del st.session_state.last_activity_time
            logout('timeout')