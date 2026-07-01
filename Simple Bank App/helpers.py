import streamlit as st 
import gspread
import pandas as pd
import time
import os
import re
import random
from datetime import date, datetime, timedelta
import secrets
from gspread.exceptions import WorksheetNotFound, APIError
from openai import OpenAI
import bcrypt


# Chương trình chatbot trợ lý ảo:
def embed_chatbot():
    text = st.session_state.text
    
    # 1. Cập nhật System Prompt cho OpenAI (Giữ nguyên logic hôm qua)
    SYSTEM_PROMPT = text['system_prompt']
    system_instruction = {"role": "system", "content": SYSTEM_PROMPT}

    if "messages" not in st.session_state:
        st.session_state.messages = [system_instruction]
    else:
        if len(st.session_state.messages) > 0 and st.session_state.messages[0]["role"] == "system":
            st.session_state.messages[0]["content"] = SYSTEM_PROMPT
    
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    # 2. Định nghĩa hàm Callback xử lý việc Đóng/Mở chat nhanh gọn
    def toggle_chat():
        st.session_state.chat_open = not st.session_state.chat_open

    # 3. Tạo nút bấm trước để lấy label động dựa trên trạng thái
    button_label = f"❌ {text['AI_chatbot_close_button']}" if st.session_state.chat_open else f"💬 {text['AI_chatbot_title']}"

    # 4. Tính toán thông số CSS dựa trên trạng thái ĐÃ ĐƯỢC CHUẨN HÓA
    is_open = st.session_state.chat_open
    bg_color = "rgba(30, 20, 60, 0.95)" if is_open else "transparent"
    box_shadow = "0px 8px 32px rgba(0, 0, 0, 0.5)" if is_open else "none"
    border_style = "1px solid rgba(255, 255, 255, 0.15)" if is_open else "none"
    padding_style = "10px" if is_open else "0px"
    width_style = "360px" if is_open else "auto"

    # 5. Bơm CSS cố định vị trí (Fix lỗi giật lag giao diện)
    st.markdown(
        f"""
        <style>
        div[data-testid="stVerticalBlock"] > div:has(div.custom-floating-chat) {{
            position: fixed !important;
            bottom: 70px !important;
            right: 0px !important;
            width: {width_style} !important;
            background-color: {bg_color} !important;
            border-radius: 16px !important;
            box-shadow: {box_shadow} !important;
            padding: {padding_style} !important;
            z-index: 999999 !important;
            border: {border_style} !important;
            backdrop-filter: blur(8px);
            transition: all 0.2s ease-in-out;
        }}
        .chat-title-text {{
            color: #e2e8f0 !important;
            font-weight: bold !important;
            margin-bottom: 8px !important;
            font-size: 14px !important;
            letter-spacing: 0.5px;
        }}
        .floating-btn-container {{
            display: flex;
            justify-content: flex-end;
            margin-top: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # 6. Render giao diện khung chat
    chat_wrapper = st.container()
    with chat_wrapper:
        st.markdown('<div class="custom-floating-chat"></div>', unsafe_allow_html=True)
        
        if st.session_state.chat_open:
            st.markdown(f'**:red[🤖 {text["AI_chatbot_title"]}]**')
            chat_history_box = st.container(height=300)
            
            with chat_history_box:
                for message in st.session_state.messages:
                    if message["role"] != "system":
                        with st.chat_message(message["role"]):
                            st.write(message["content"])

            if user_query := st.chat_input(f"{text['AI_chatbot_input_placeholder']}", key="chat_input_unique"):
                with chat_history_box:
                    with st.chat_message("user"):
                        st.write(f':green[{user_query.capitalize()}]')
                st.session_state.messages.append({"role": "user", "content": f':green[{user_query.capitalize()}]'})

                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                with chat_history_box:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=st.session_state.messages,
                            stream=True,
                        )
                        for chunk in response:
                            if chunk.choices and len(chunk.choices) > 0:
                                delta_content = chunk.choices[0].delta.content
                                if delta_content:
                                    full_response += delta_content
                                    message_placeholder.write(full_response + "▌")
                        
                        message_placeholder.write(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        # 7. Render nút bấm ở cuối container nhưng đã được xử lý callback từ trước
        st.markdown('<div class="floating-btn-container">', unsafe_allow_html=True)
        # Sử dụng on_click giúp trạng thái thay đổi ngay trước khi file rerun, không cần gọi st.rerun() thủ công
        st.button(button_label, key="toggle_chat_btn", type="primary", on_click=toggle_chat)
        st.markdown('</div>', unsafe_allow_html=True)




@st.cache_resource
def get_gspread_client():
    credentials_dict = dict(st.secrets["connections"]["gsheets"])
    return gspread.service_account_from_dict(credentials_dict)


@st.cache_resource
def get_spreadsheet():
    gc = get_gspread_client()
    spreadsheet_url = st.secrets["connections"]["gsheets"]["toplevel_url"]
    return gc.open_by_url(spreadsheet_url)

# Khởi tạo đọc dữ liệu bank accounts
@st.cache_resource
def get_bank_account_worksheet():
    sh = get_spreadsheet()
    return sh.worksheet("bank_account")

def with_quota_retry(func, max_attempts=4, base_delay=2):
    """Tự động chờ và thử lại khi gặp lỗi quota tạm thời (HTTP 429) từ Google Sheets API."""
    for attempt in range(max_attempts):
        try:
            return func()
        except APIError as e:
            is_quota_error = '429' in str(e) or 'Quota exceeded' in str(e)
            if is_quota_error and attempt < max_attempts - 1:
                time.sleep(base_delay * (attempt + 1))
            else:
                raise

def df_init():
    worksheet = get_bank_account_worksheet()
    data = with_quota_retry(lambda: worksheet.get_all_records())
    df = pd.DataFrame(data)


    df = df.astype({
                    'Name' : 'str',
                    'Phone' : 'str',
                    'Email' : 'str',
                    'Password' : 'str',
                    'Balance' : 'int64',
                    'Session' : 'str',
                    'Previous_Session' : 'str',
                    'Version' : 'int64',
                    'Power_Level' : 'int64'
                    })

    # Xử lý dataframe

    df['ID'] = pd.Series(f'{x:08}' if str(x).isdigit() else x for x in list(df['ID']))
    df['Phone'] = '0' + df['Phone']
    pd.to_datetime(df['DoB'])

    # Ghi nhớ vị trí dòng THẬT trên Google Sheet (trước khi sắp xếp lại trong bộ nhớ) -
    # để các lần ghi sau biết đúng dòng cần sửa, không cần ghi đè cả sheet.
    df['_sheet_row'] = range(2, len(df) + 2)

    df.set_index('ID', inplace=True)
    df.sort_index(inplace=True)
    return worksheet, df

@st.cache_data(ttl=5)
def get_display_snapshot():
    """
    Đọc nhanh dữ liệu sheet, dùng cho HIỂN THỊ/KIỂM TRA NHẸ (chấp nhận trễ tối đa 5 giây).
    KHÔNG dùng cho login, chuyển tiền, đổi mật khẩu - những nơi đó luôn gọi df_init() trực tiếp.
    """
    _, snapshot_df = df_init()
    return snapshot_df

worksheet, df = df_init()


# CÁC LOẠI HỘP THOẠI:
# ==============================================================================
# 1. HỘP THOẠI BÁO ĐÃ ĐĂNG NHẬP NƠI KHÁC HOẶC HẾT PHIÊN ĐĂNG NHẬP
# ==============================================================================
@st.dialog('**:yellow[Cảnh Báo / Warning]**', width='medium', dismissible=False)
def session_expired(reason:str = 'expired'):
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
            # hijacked -> đăng xuất CẢ máy đang chiếm (Session) và xóa luôn dấu vết cũ (Previous_Session)
            current_df.loc[st.session_state.acc_num, 'Session'] = '0'
            current_df.loc[st.session_state.acc_num, 'Previous_Session'] = '0'

    c1, c2, c3 = st.columns([3,3,2])
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
                del st.session_state.acc_num
                del st.session_state.auth_token
                st.query_params.clear()
                st.session_state.password_change_need = True
                st.session_state.previous_page.append(st.session_state.current_page)
                st.switch_page('pages/account_settings.py')        
    
    with c3:
        if st.button(f'**:red[{text.get('dialog_stay_btn', 'Ở lại trang này')}]**', icon='❗', key="btn_sess_stay"):
            update_accounts_safely([st.session_state.acc_num], invalidate_all_sessions)

            del st.session_state.session_expired
            del st.session_state.acc_num
            del st.session_state.auth_token
            st.query_params.clear()
            st.rerun()


# ==============================================================================
# 2. HỘP THOẠI BÁO KHI RỜI NHỮNG TRANG ĐIỀN FORM
# ==============================================================================
def switch_page_dialog_title():
    if 'text' in st.session_state:
        result = st.session_state.text.get('dialog_leave_title', 'Xác nhận rời trang')
    else:
        result = 'Xác nhận rời trang'
    return result

@st.dialog('**:yellow[Thông Báo / Notification]**')
def switch_page_confirm(page_path, page_trace = True):
    text = st.session_state.text
    
    st.markdown(f"<h1 style='text-align: center; color: #ff9f43; margin-top:0;'>⚠️ {switch_page_dialog_title().upper()} ⚠️</h3>", unsafe_allow_html=True)
    st.markdown('<div class="dialog-divider"></div>', unsafe_allow_html=True)
    st.warning(text.get('dialog_leave_warning', 'Nếu rời khỏi trang...'))
    st.markdown('<div class="dialog-divider"></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    
    with c1:
        leave_label = text.get('dialog_leave_btn', 'Rời khỏi trang này')
        # Lồng in đậm ngoài mã màu :red[...] để nét chữ dày và sáng hơn
        if st.button(f'**:red[{leave_label}]**'):
            if page_trace:
                st.session_state.previous_page.append(st.session_state.current_page)
            else:
                st.session_state.previous_page.pop(-1)
            st.switch_page(page_path)
            
    with c2:
        stay_label = text.get('dialog_stay_btn', 'Ở lại trang này')
        # Lồng in đậm ngoài mã màu :green[...] để nét chữ dày và sáng hơn
        if st.button(f'**:green[{stay_label}]**'):
            st.rerun()



# Hàm kiểm tra các trang có form điền để mở hộp thoại thông báo khi rời đi
def switch_page_check(page_path, page_trace = True):
    check = True
    for i in ['login.py','signup.py']:
        if i in str(st.session_state.current_page) and not st.session_state.login_state:
            check = False
            switch_page_confirm(page_path, page_trace)
    for i in ['transfer.py','transfer_rehearsal.py']:
        if i in str(st.session_state.current_page) and st.session_state.login_state:
            check = False
            switch_page_confirm(page_path, page_trace)
    if check:
        if not page_trace:
            st.session_state.previous_page.pop(-1)
        st.switch_page(page_path)


# Các hàm xử lý dữ liệu nhập form

# Hàm hash mật khẩu mới
def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Hàm kiểm tra xem 1 chuỗi có phải là bcrypt hash hay không (để phân biệt với password cũ dạng plaintext)
def is_bcrypt_hash(value: str) -> bool:
    return isinstance(value, str) and value.startswith(('$2b$', '$2a$', '$2y$')) and len(value) == 60

# Hàm kiểm tra mail
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Hàm kiểm tra sđt
def validate_phone(phone):
    pattern = r'^\+?(0|84)\d{9,10}$'
    return bool(re.match(pattern, phone))

# Hàm kiểm tra tuổi
def calculate_age(birth_date):
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Hàm trả về cùng tham số nếu ID này khả dụng, nếu không sẽ trả một số ID khả dụng nhỏ nhất có thể
def new_id_check(id):
    snapshot_df = get_display_snapshot()
    if id not in snapshot_df.index:
        return id

    max_random_attempts = 1000
    for _ in range(max_random_attempts):
        candidate = f'{random.randint(1, 99999999):08}'
        if candidate not in snapshot_df.index:
            return candidate

    for i in range(1, 100000000):
        if f'{i:08}' not in snapshot_df.index:
            return f'{i:08}'

    raise RuntimeError("Không còn số tài khoản nào khả dụng trong hệ thống.")

# Nhóm hàm tạo list ID số đẹp

# Hàm kiểm tra ID khả dụng hay không
def id_available_check(num):
    snapshot_df = get_display_snapshot()
    return num not in snapshot_df.index

# Hàm tạo các tổ hợp số đẹp chứa dãy số cho trước
def id_num_generate(init_num:str, init_choices = [6,8,9]):
    
    init_len = len(init_num)
    spaces_count = 8 - init_len
    choices = [str(x) for x in init_choices]
    
    # Đệ quy khởi tạo bộ số đẹp từ các chữ số trong choices
    def filler_generate(length):
        if length == 0:
            return [[]]
        sub_combos = filler_generate(length - 1)
        return [combo + [digit] for combo in sub_combos for digit in choices]


    filler_list = filler_generate(spaces_count)
    
    # Nhét dãy số cho trước vào các bộ số đã tạo
    kq = set()

    for filler in filler_list:
        for i in range(spaces_count + 1):

            temp = filler.copy()

            temp.insert(i, init_num)

            whole_num = "".join(temp)
            kq.add(whole_num)
            
    # Dùng set để lọc số trùng, sau đó chuyển lại thành list và sắp xếp lại
    return sorted(list(kq))

# Hàm kiểm tra và trả ra list ID số đẹp từ dãy số cho trước, kết quả là list gồm nhiều nhất suggest_num được lấy ngẫu nhiên từ các ID khả dụng
def new_id_suggest(init_id:str, suggest_num:int):
    if len(init_id) > 4:
        good_id = id_num_generate(init_id,[0,1,2,3,4,5,6,7,8,9])
    else:
        good_id = id_num_generate(init_id)
    available_good_id = list(filter(id_available_check, good_id))
    
    if len(available_good_id) <= suggest_num:
        return available_good_id
    
    random_good_id = []
    while len(random_good_id) < suggest_num:
        chosen_random_id = random.choice(available_good_id)
        random_good_id.append(chosen_random_id)
        available_good_id.remove(chosen_random_id)
        
    random_good_id.sort()
    
    return random_good_id

# ==============================================================================
# CÁC HÀM XUẤT DỮ LIỆU VÀO GOOGLE SHEET
# ==============================================================================

SHEET_COLUMNS = ['ID', 'Name', 'DoB', 'Phone', 'Email', 'Password', 'Balance',
                'Session', 'Previous_Session', 'Version', 'Power_Level']

# Hàm chỉnh sửa ô trong google sheet:
def update_account_rows(worksheet, df, account_ids):
    for acc_id in account_ids:
        row_series = df.loc[acc_id, [c for c in SHEET_COLUMNS if c != 'ID']].copy()
        row_series['DoB'] = str(row_series['DoB'])
        row_values = [acc_id] + [v.item() if hasattr(v, 'item') else v for v in row_series.tolist()]
        sheet_row_number = int(df.loc[acc_id, '_sheet_row'])
        with_quota_retry(lambda rn=f"A{sheet_row_number}", rv=row_values: worksheet.update(range_name=rn, values=[rv]))
        
# Hàm xuất df ra lại google sheet:
def work_sheet_update(worksheet, df = df_init()):
    
    worksheet.clear()

    df['DoB'] = df['DoB'].astype(str)
    df.reset_index(drop=False, inplace=True)
    
    header = df.columns.values.tolist()
    rows = df.values.tolist()
    data_to_upload = [header] + rows

    worksheet.update(range_name='A1', values=data_to_upload)

    pd.to_datetime(df['DoB'])
    df.set_index('ID', inplace=True)

# Hàm tạo tài khoản mới
class AccountIdTakenError(Exception):
    """Báo hiệu việc tạo tài khoản thất bại vì số tài khoản vừa bị người khác đăng ký trước trong tích tắc."""
    pass


def account_signup(stk, ten, ngay_sinh, sdt, email, matkhau, sodu):
    worksheet, fresh_df = df_init()

    if stk in fresh_df.index:
        raise AccountIdTakenError(stk)

    new_row_values = [stk, ten, str(ngay_sinh), sdt, email, hash_password(matkhau),
                        sodu, '0', '0', 0, 0]
    with_quota_retry(lambda: worksheet.append_row(new_row_values))
    
# Các thông số cho hàm chuyển khoản:
MAX_RETRY_ATTEMPTS = 5
RETRY_BASE_DELAY = 0.2  # giây, tăng dần mỗi lần retry (backoff)

# Tạo lỗi khi ghi nhận thay đổi số dư chuyển khoản thất bại:
class OptimisticLockError(Exception):
    """Báo hiệu việc ghi thất bại vì version đã bị người khác thay đổi trước."""
    pass

# Hàm kiểm tra phiên bản dòng để tạo giao dịch:
def update_accounts_safely(account_ids: list, mutation_function):
    """
    Cập nhật 1 hoặc nhiều dòng tài khoản một cách an toàn dùng optimistic locking.

    account_ids: list các ID tài khoản sẽ bị thay đổi (vd: [sender_id, receiver_id])
    mutation_function: hàm nhận df mới nhất, thực hiện thay đổi TRỰC TIẾP lên df đó
                        (vd: trừ tiền A, cộng tiền B), không cần return gì.

    Trả về: df mới nhất sau khi ghi thành công.
    Raise OptimisticLockError nếu thử hết số lần mà vẫn xung đột.
    """
    for attempt in range(MAX_RETRY_ATTEMPTS):
        worksheet, fresh_df = df_init()

        # Ghi nhớ version hiện tại của các dòng liên quan, TRƯỚC khi sửa
        versions_before = {acc_id: fresh_df.loc[acc_id, 'Version'] for acc_id in account_ids}

        # Áp logic nghiệp vụ (sửa balance, v.v...) lên df mới nhất này
        mutation_function(fresh_df)

        # Tăng version của các dòng bị sửa lên 1
        for acc_id in account_ids:
            fresh_df.loc[acc_id, 'Version'] = versions_before[acc_id] + 1

        # Trước khi ghi thật, đọc lại 1 lần nữa để chắc chắn version vẫn chưa đổi
        # (Đây là bước "check" cuối cùng ngay sát thời điểm ghi, giảm tối đa race window)
        _, check_df = df_init()
        conflict = any(
            check_df.loc[acc_id, 'Version'] != versions_before[acc_id]
            for acc_id in account_ids
        )

        if not conflict:
            update_account_rows(worksheet, fresh_df, account_ids)
            return fresh_df

        # Có xung đột -> chờ một chút (backoff) rồi thử lại toàn bộ từ đầu
        time.sleep(RETRY_BASE_DELAY * (attempt + 1))

    raise OptimisticLockError(f"Failed to update accounts {account_ids} after {MAX_RETRY_ATTEMPTS} attempts")

@st.cache_resource
def get_or_create_worksheet(sheet_name, all_columns_tuple):
    """Lấy worksheet theo tên, tự tạo kèm header nếu chưa tồn tại.
    Cache theo (sheet_name, all_columns_tuple) - chỉ gọi API 'mở sheet' 1 lần duy nhất
    cho mỗi tên sheet, thay vì mỗi lần đọc/ghi đều gọi lại."""
    sh = get_spreadsheet()
    try:
        return sh.worksheet(sheet_name)
    except WorksheetNotFound:
        worksheet = sh.add_worksheet(title=sheet_name, rows=100, cols=len(all_columns_tuple))
        worksheet.append_row(list(all_columns_tuple))
        return worksheet


def generic_sheet_init(sheet_name, index_col, dtype_map, all_columns):
    """Phiên bản tổng quát của df_init() - dùng cho sheet phụ (savings, loans...)."""
    worksheet = get_or_create_worksheet(sheet_name, tuple(all_columns))
    data = with_quota_retry(lambda: worksheet.get_all_records())
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=all_columns)
    df = df.astype(dtype_map)
    df['_sheet_row'] = range(2, len(df) + 2)
    df.set_index(index_col, inplace=True)
    return worksheet, df


def generic_update_rows(worksheet, df, row_ids, all_columns, index_col):
    for row_id in row_ids:
        row_series = df.loc[row_id, [c for c in all_columns if c != index_col]].copy()
        row_values = [row_id] + [v.item() if hasattr(v, 'item') else v for v in row_series.tolist()]
        sheet_row_number = int(df.loc[row_id, '_sheet_row'])
        with_quota_retry(lambda rn=f"A{sheet_row_number}", rv=row_values: worksheet.update(range_name=rn, values=[rv]))


def update_rows_safely(init_function, all_columns, index_col, row_ids, mutation_function):
    """Phiên bản tổng quát của update_accounts_safely() - dùng optimistic locking
    cho bất kỳ sheet nào (savings, loans...), không chỉ bank_account."""
    for attempt in range(MAX_RETRY_ATTEMPTS):
        worksheet, fresh_df = init_function()
        versions_before = {row_id: fresh_df.loc[row_id, 'Version'] for row_id in row_ids}
        mutation_function(fresh_df)
        for row_id in row_ids:
            fresh_df.loc[row_id, 'Version'] = versions_before[row_id] + 1
        _, check_df = init_function()
        conflict = any(check_df.loc[row_id, 'Version'] != versions_before[row_id] for row_id in row_ids)
        if not conflict:
            generic_update_rows(worksheet, fresh_df, row_ids, all_columns, index_col)
            return fresh_df
        time.sleep(RETRY_BASE_DELAY * (attempt + 1))
    raise OptimisticLockError(f"Failed to update rows {row_ids} after {MAX_RETRY_ATTEMPTS} attempts")

# ==============================================================================
# GỬI TIẾT KIỆM & VAY TIỀN
# ==============================================================================

SAVINGS_COLUMNS = ['Deposit_ID', 'Account_ID', 'Principal', 'Annual_Rate', 'Term_Months',
                    'Start_Date', 'Maturity_Date', 'Status', 'Auto_Renew', 'Version']
SAVINGS_DTYPES = {'Account_ID': 'str', 'Principal': 'int64', 'Annual_Rate': 'float64',
                'Term_Months': 'int64', 'Start_Date': 'str', 'Maturity_Date': 'str',
                'Status': 'str', 'Auto_Renew': 'bool', 'Version': 'int64'}

LOAN_COLUMNS = ['Loan_ID', 'Account_ID', 'Principal', 'Annual_Rate', 'Term_Months',
                'Start_Date', 'Maturity_Date', 'Status', 'Version']
LOAN_DTYPES = {'Account_ID': 'str', 'Principal': 'int64', 'Annual_Rate': 'float64',
                'Term_Months': 'int64', 'Start_Date': 'str', 'Maturity_Date': 'str',
                'Status': 'str', 'Version': 'int64'}

RATE_TABLE = {
    1:  {'savings': 0.03,  'loan': 0.045},
    3:  {'savings': 0.04,  'loan': 0.06},
    6:  {'savings': 0.05,  'loan': 0.075},
    12: {'savings': 0.06,  'loan': 0.09},
    18: {'savings': 0.065, 'loan': 0.0975},
    24: {'savings': 0.07,  'loan': 0.105},
    36: {'savings': 0.075, 'loan': 0.1125},
}

SAVINGS_MIN_AMOUNT = 500000
LOAN_MIN_AMOUNT = 500000
LOAN_BASE_MAX_AMOUNT = 200000000
LOAN_MAX_RATIO_OF_SAVINGS = 0.7
DAYS_PER_MONTH = 30

def savings_init():
    return generic_sheet_init('savings', 'Deposit_ID', SAVINGS_DTYPES, SAVINGS_COLUMNS)


def loans_init():
    return generic_sheet_init('loans', 'Loan_ID', LOAN_DTYPES, LOAN_COLUMNS)

def flash_success(message_or_key, is_key=True):
    """Lưu 1 thông báo để hiển thị NGAY SAU rerun - vì st.success()+st.rerun() liên tiếp
    sẽ làm mất thông báo (rerun xóa UI cũ trước khi người dùng kịp thấy)."""
    st.session_state['_flash_message'] = {'type': 'key' if is_key else 'raw', 'value': message_or_key}


def show_flash_message():
    text = st.session_state.text
    flash = st.session_state.pop('_flash_message', None)
    if flash:
        st.success(text[flash['value']] if flash['type'] == 'key' else flash['value'])

def open_savings_deposit(stk, amount, term_months, auto_renew=False, start_date=None):
    """start_date=None (gửi mới từ người dùng) -> bắt đầu hôm nay, TRỪ Balance.
    start_date có giá trị (tái tục nội bộ) -> bắt đầu đúng từ ngày đó, KHÔNG trừ Balance."""
    rate = RATE_TABLE[term_months]['savings']
    is_new_deposit = start_date is None
    actual_start = start_date if start_date else date.today()
    maturity = actual_start + timedelta(days=DAYS_PER_MONTH * term_months)
    deposit_id = secrets.token_hex(8)

    worksheet = get_or_create_worksheet('savings', tuple(SAVINGS_COLUMNS))
    with_quota_retry(lambda: worksheet.append_row([deposit_id, stk, amount, rate, term_months,
                        str(actual_start), str(maturity), 'active', auto_renew, 0]))

    if is_new_deposit:
        def deduct_balance(current_df):
            current_df.loc[stk, 'Balance'] -= amount
        update_accounts_safely([stk], deduct_balance)
        
    if is_new_deposit:
        def deduct_balance(current_df):
            current_df.loc[stk, 'Balance'] -= amount
        update_accounts_safely([stk], deduct_balance)
        log_transaction(stk, TX_SAVINGS_OPEN, amount, reference_id=deposit_id)

    return deposit_id

    return deposit_id

def toggle_savings_auto_renew(deposit_id, new_value):
    def apply_toggle(current_df):
        current_df.loc[deposit_id, 'Auto_Renew'] = new_value
    update_rows_safely(savings_init, SAVINGS_COLUMNS, 'Deposit_ID', [deposit_id], apply_toggle)

def settle_matured_savings(stk):
    """Xử lý các sổ tiết kiệm đã đến hạn. Nếu nhiều kỳ đã trôi qua (vd lâu không mở app),
    tính lãi gộp qua TỪNG kỳ đã hoàn thành, không chỉ 1 kỳ."""
    _, savings_df = savings_init()
    my_deposits = savings_df[(savings_df['Account_ID'] == stk) & (savings_df['Status'] == 'active')]
    today = date.today()
    matured_count = 0

    for deposit_id, row in my_deposits.iterrows():
        maturity = datetime.strptime(row['Maturity_Date'], '%Y-%m-%d').date()
        if maturity <= today:
            term_months = int(row['Term_Months'])
            rate = float(row['Annual_Rate'])
            principal = int(row['Principal'])
            auto_renew = bool(row['Auto_Renew'])

            def close_deposit(current_df):
                current_df.loc[deposit_id, 'Status'] = 'closed'
            try:
                update_rows_safely(savings_init, SAVINGS_COLUMNS, 'Deposit_ID', [deposit_id], close_deposit)
            except OptimisticLockError:
                continue

            if auto_renew:
                current_principal = principal
                current_maturity = maturity
                current_start = maturity
                while current_maturity <= today:
                    current_principal = int(current_principal + current_principal * rate * term_months / 12)
                    current_start = current_maturity
                    current_maturity = current_start + timedelta(days=DAYS_PER_MONTH * term_months)

                open_savings_deposit(stk, current_principal, term_months, auto_renew=True, start_date=current_start)
                log_transaction(stk, TX_SAVINGS_AUTO_RENEW, current_principal, reference_id=deposit_id)
                matured_count += 1
            else:
                payout = int(principal + principal * rate * term_months / 12)
                def credit_balance(current_df):
                    current_df.loc[stk, 'Balance'] += payout
                try:
                    update_accounts_safely([stk], credit_balance)
                    log_transaction(stk, TX_SAVINGS_MATURED, payout, reference_id=deposit_id)
                    matured_count += 1
                except OptimisticLockError:
                    pass

    return matured_count


def withdraw_savings_early(stk, deposit_id):
    """Rút tiết kiệm trước hạn - chỉ nhận lại đúng số tiền gốc, mất toàn bộ lãi.
    Nếu việc rút khiến hạn mức vay (70% tổng tiết kiệm) giảm xuống dưới dư nợ hiện tại,
    tự động trích từ số tiền rút được để trả bớt nợ (FIFO - khoản vay cũ nhất trả trước)
    cho đến khi dư nợ về lại trong hạn mức mới."""
    _, savings_df = savings_init()
    principal = int(savings_df.loc[deposit_id, 'Principal'])

    def close_deposit(current_df):
        current_df.loc[deposit_id, 'Status'] = 'closed'
    update_rows_safely(savings_init, SAVINGS_COLUMNS, 'Deposit_ID', [deposit_id], close_deposit)

    # Tính hạn mức vay MỚI sau khi sổ này đã đóng (get_loan_limit tự đọc lại data mới nhất)
    new_loan_limit = get_loan_limit(stk)
    current_total_debt = get_total_active_loans(stk)

    forced_paydown_amount = 0
    if current_total_debt > new_loan_limit:
        excess_debt = current_total_debt - new_loan_limit
        forced_paydown_amount = min(excess_debt, principal)

        _, loans_df = loans_init()
        my_loans = loans_df[(loans_df['Account_ID'] == stk) & (loans_df['Status'].isin(['active', 'overdue']))]
        my_loans = my_loans.sort_values('Start_Date')  # FIFO - khoản vay cũ nhất trả trước

        remaining_to_pay = forced_paydown_amount
        for loan_id, loan_row in my_loans.iterrows():
            if remaining_to_pay <= 0:
                break
            loan_principal = int(loan_row['Principal'])
            pay_this_loan = min(remaining_to_pay, loan_principal)
            new_principal = loan_principal - pay_this_loan

            if new_principal <= 0:
                def close_this_loan(current_df, lid=loan_id):
                    current_df.loc[lid, 'Status'] = 'closed'
                try:
                    update_rows_safely(loans_init, LOAN_COLUMNS, 'Loan_ID', [loan_id], close_this_loan)
                except OptimisticLockError:
                    continue
            else:
                def reduce_this_loan(current_df, lid=loan_id, new_p=new_principal):
                    current_df.loc[lid, 'Principal'] = new_p
                try:
                    update_rows_safely(loans_init, LOAN_COLUMNS, 'Loan_ID', [loan_id], reduce_this_loan)
                except OptimisticLockError:
                    continue

            remaining_to_pay -= pay_this_loan

        forced_paydown_amount -= remaining_to_pay  # phần thực sự đã trừ được

    amount_to_credit = principal - forced_paydown_amount

    def credit_balance(current_df):
        current_df.loc[stk, 'Balance'] += amount_to_credit
    update_accounts_safely([stk], credit_balance)
    
    log_transaction(stk, TX_SAVINGS_EARLY, principal, reference_id=deposit_id)
    if forced_paydown_amount > 0:
        log_transaction(stk, TX_LOAN_FORCED_PAYDOWN, forced_paydown_amount)

    return principal, forced_paydown_amount

def get_total_active_savings(stk):
    """Tổng số tiền gốc đang gửi tiết kiệm (chỉ tính sổ còn active) - dùng để tính hạn mức vay."""
    _, savings_df = savings_init()
    my_active = savings_df[(savings_df['Account_ID'] == stk) & (savings_df['Status'] == 'active')]
    return int(my_active['Principal'].sum()) if not my_active.empty else 0


def get_loan_limit(stk):
    """Hạn mức vay tối đa = lớn hơn giữa mức sàn cố định và 70% tổng tiết kiệm đang có."""
    total_savings = get_total_active_savings(stk)
    return max(LOAN_BASE_MAX_AMOUNT, int(total_savings * LOAN_MAX_RATIO_OF_SAVINGS))


def get_total_active_loans(stk):
    """Tổng dư nợ gốc đang vay (active + overdue)."""
    _, loans_df = loans_init()
    my_loans = loans_df[(loans_df['Account_ID'] == stk) & (loans_df['Status'].isin(['active', 'overdue']))]
    return int(my_loans['Principal'].sum()) if not my_loans.empty else 0

def open_loan(stk, amount, term_months):
    loan_limit = get_loan_limit(stk)
    current_debt = get_total_active_loans(stk)
    if current_debt + amount > loan_limit:
        raise ValueError("LOAN_LIMIT_EXCEEDED")

    rate = RATE_TABLE[term_months]['loan']
    today = date.today()
    maturity = today + timedelta(days=DAYS_PER_MONTH * term_months)
    loan_id = secrets.token_hex(8)

    worksheet = get_or_create_worksheet('loans', tuple(LOAN_COLUMNS))
    with_quota_retry(lambda: worksheet.append_row([loan_id, stk, amount, rate, term_months,
                        str(today), str(maturity), 'active', 0]))

    def add_balance(current_df):
        current_df.loc[stk, 'Balance'] += amount
    update_accounts_safely([stk], add_balance)
    log_transaction(stk, TX_LOAN_OPEN, amount, reference_id=loan_id)
    return loan_id


def settle_matured_loans(stk):
    """Tự động trả nợ các khoản vay đã đến hạn (nếu đủ tiền) - trừ gốc+lãi từ Balance.
    Nếu không đủ tiền, chuyển 'overdue' và tiếp tục tự thử ở lần đăng nhập sau."""
    _, loans_df = loans_init()
    my_loans = loans_df[(loans_df['Account_ID'] == stk) & (loans_df['Status'].isin(['active', 'overdue']))]
    today = date.today()

    for loan_id, row in my_loans.iterrows():
        maturity = datetime.strptime(row['Maturity_Date'], '%Y-%m-%d').date()
        if maturity <= today:
            repay_amount = int(row['Principal'] + row['Principal'] * row['Annual_Rate'] * row['Term_Months'] / 12)
            _, fresh_acc_df = df_init()
            current_balance = int(fresh_acc_df.loc[stk, 'Balance'])

            if current_balance >= repay_amount:
                def repay(current_df):
                    current_df.loc[stk, 'Balance'] -= repay_amount
                try:
                    update_accounts_safely([stk], repay)
                    log_transaction(stk, TX_LOAN_REPAY_MATURED, repay_amount, reference_id=loan_id)
                except OptimisticLockError:
                    continue

                def close_loan(current_df):
                    current_df.loc[loan_id, 'Status'] = 'closed'
                try:
                    update_rows_safely(loans_init, LOAN_COLUMNS, 'Loan_ID', [loan_id], close_loan)
                except OptimisticLockError:
                    pass
            else:
                if row['Status'] != 'overdue':
                    def mark_overdue(current_df):
                        current_df.loc[loan_id, 'Status'] = 'overdue'
                    try:
                        update_rows_safely(loans_init, LOAN_COLUMNS, 'Loan_ID', [loan_id], mark_overdue)
                    except OptimisticLockError:
                        pass


def repay_loan_early(stk, loan_id):
    """Trả nợ trước hạn - lãi tính theo số ngày thực vay (ít hơn lãi đủ kỳ hạn)."""
    _, loans_df = loans_init()
    loan_row = loans_df.loc[loan_id]
    start = datetime.strptime(loan_row['Start_Date'], '%Y-%m-%d').date()
    actual_days = max((date.today() - start).days, 1)
    actual_months = actual_days / DAYS_PER_MONTH
    repay_amount = int(loan_row['Principal'] + loan_row['Principal'] * loan_row['Annual_Rate'] * actual_months / 12)

    def deduct_balance(current_df):
        if current_df.loc[stk, 'Balance'] < repay_amount:
            raise ValueError("INSUFFICIENT_FUNDS")
        current_df.loc[stk, 'Balance'] -= repay_amount
    update_accounts_safely([stk], deduct_balance)

    def close_loan(current_df):
        current_df.loc[loan_id, 'Status'] = 'closed'
    update_rows_safely(loans_init, LOAN_COLUMNS, 'Loan_ID', [loan_id], close_loan)
    
    log_transaction(stk, TX_LOAN_REPAY_EARLY, repay_amount, reference_id=loan_id)
    return repay_amount


# ==============================================================================
# LỊCH SỬ GIAO DỊCH
# ==============================================================================
TRANSACTION_COLUMNS = ['Transaction_ID', 'Account_ID', 'Type', 'Amount',
                        'Reference_ID', 'Description', 'Timestamp']
TRANSACTION_DTYPES = {
    'Account_ID': 'str', 'Type': 'str', 'Amount': 'int64',
    'Reference_ID': 'str', 'Description': 'str', 'Timestamp': 'str'
}

# Hằng số loại giao dịch - dùng trong code logic, KHÔNG đổi theo ngôn ngữ
TX_TRANSFER_OUT        = 'transfer_out'
TX_TRANSFER_IN         = 'transfer_in'
TX_SAVINGS_OPEN        = 'savings_open'
TX_SAVINGS_MATURED     = 'savings_matured'
TX_SAVINGS_AUTO_RENEW  = 'savings_auto_renew'
TX_SAVINGS_EARLY       = 'savings_early_withdraw'
TX_LOAN_OPEN           = 'loan_open'
TX_LOAN_REPAY_EARLY    = 'loan_repay_early'
TX_LOAN_REPAY_MATURED  = 'loan_repay_matured'
TX_LOAN_FORCED_PAYDOWN = 'loan_forced_paydown'

ALL_TX_TYPES = [
    TX_TRANSFER_OUT, TX_TRANSFER_IN,
    TX_SAVINGS_OPEN, TX_SAVINGS_MATURED, TX_SAVINGS_AUTO_RENEW, TX_SAVINGS_EARLY,
    TX_LOAN_OPEN, TX_LOAN_REPAY_EARLY, TX_LOAN_REPAY_MATURED, TX_LOAN_FORCED_PAYDOWN
]

# Loại nào thì số tiền là dương (cộng vào số dư)
TX_POSITIVE_TYPES = {TX_TRANSFER_IN, TX_SAVINGS_MATURED, TX_SAVINGS_EARLY, TX_LOAN_OPEN}
# Loại nào thì số tiền là âm (trừ khỏi số dư)
TX_NEGATIVE_TYPES = {TX_TRANSFER_OUT, TX_SAVINGS_OPEN, TX_LOAN_REPAY_EARLY,
                    TX_LOAN_REPAY_MATURED, TX_LOAN_FORCED_PAYDOWN}
# Còn lại (TX_SAVINGS_AUTO_RENEW) là trung tính (số dư không đổi, chỉ ghi nhận sự kiện)

def transactions_init():
    return generic_sheet_init('transactions', 'Transaction_ID', TRANSACTION_DTYPES, TRANSACTION_COLUMNS)


def log_transaction(acc_id, tx_type, amount, reference_id='', description=''):
    """Ghi 1 dòng lịch sử giao dịch vào sheet transactions.
    Fire-and-forget: nếu thất bại, bắt exception im lặng - không được để log crash giao dịch chính."""
    try:
        worksheet = get_or_create_worksheet('transactions', tuple(TRANSACTION_COLUMNS))
        tx_id = secrets.token_hex(8)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with_quota_retry(lambda: worksheet.append_row(
            [tx_id, acc_id, tx_type, int(amount), str(reference_id), str(description), timestamp]
        ))
    except Exception:
        pass


# Hàm chức năng chuyển tiền:
def money_transfer(sender:str, receiver:str, transfer_amount:int):
    global worksheet, df

    def apply_transfer(current_df):
        if current_df.loc[sender, 'Balance'] < transfer_amount:
            raise ValueError("INSUFFICIENT_FUNDS")
        current_df.loc[sender, 'Balance'] -= transfer_amount
        current_df.loc[receiver, 'Balance'] += transfer_amount

    df = update_accounts_safely([sender, receiver], apply_transfer)

    receiver_name = df.loc[receiver, 'Name']
    sender_name = df.loc[sender, 'Name']
    log_transaction(sender, TX_TRANSFER_OUT, transfer_amount, reference_id=receiver, description=receiver_name)
    log_transaction(receiver, TX_TRANSFER_IN, transfer_amount, reference_id=sender, description=sender_name)


# Hàm hỗ trợ gợi ý ID là số ngày sinh nếu khả dụng khi nhập vào form đăng ký
def process_temp_DoB():
    temp_DoB = st.session_state.temp_DoB
    st.session_state.pr_temp_DoB = temp_DoB.strftime('%d/%m/%Y').replace('/', '')


# Hằng số nội bộ cho lựa chọn số tài khoản khi đăng ký - KHÔNG đổi theo ngôn ngữ, dùng để so sánh logic an toàn
ACC_ID_OPTION_USE_SUGGESTED = '__acc_opt_use_suggested__'
ACC_ID_OPTION_DEFAULT = '__acc_opt_default__'
ACC_ID_OPTION_CHANGE = '__acc_opt_change__'

# Form đăng ký tài khoản mới
def signup_form():

    text = st.session_state.text

    ten = st.text_input(text['su_lbl_name'], value='Nguyễn Văn A', placeholder=text['su_placeholder_required'])
    ngay_sinh = st.date_input(text['su_lbl_dob'], value= datetime.today(), min_value= date(1920,1,1), max_value= datetime.today(), format='DD/MM/YYYY', key= 'temp_DoB', on_change=process_temp_DoB)
    sdt = st.text_input(text['su_lbl_phone'])
    email = st.text_input(text['su_lbl_email'])
    mat_khau = st.text_input(text['su_lbl_pass'], type='password', max_chars=24, placeholder=text['su_placeholder_required'])
    xn_mat_khau = st.text_input(text['su_lbl_confirm_pass'], type='password', max_chars=24, placeholder=text['su_placeholder_required'])
    sodu = st.number_input(text['su_lbl_balance'], value= 2000000, min_value=500000, max_value=100000000000, step=100000, placeholder=text['su_placeholder_required'], format= '%d')
    stk_mac_dinh = new_id_check(st.session_state.pr_temp_DoB)
    st.markdown('')
    st.markdown(f"**:violet[{text['su_section_optional']}]**")

    stk_modify = None

    if st.session_state.available_id_list == []:
        stk = st.text_input(text['su_lbl_custom_id']
                            ,placeholder=stk_mac_dinh + ' ' + text['su_placeholder_id_avail'], max_chars=8
                            )
        if stk_mac_dinh == st.session_state.pr_temp_DoB and calculate_age(ngay_sinh) >= 16:
            st.info(text['su_info_dob_avail'])
            
    elif len(st.session_state.available_id_list) == 1:
        single_option_labels = {
            ACC_ID_OPTION_USE_SUGGESTED: text['su_radio_single_avail'].format(f':green[{st.session_state.available_id_list[0]}]'),
            ACC_ID_OPTION_DEFAULT: text['su_opt_default'],
            ACC_ID_OPTION_CHANGE: text['su_opt_change_id'],
        }
        stk_modify = st.radio(f':red[{text["su_radio_single_desc"]}]',
                    [ACC_ID_OPTION_USE_SUGGESTED, ACC_ID_OPTION_DEFAULT, ACC_ID_OPTION_CHANGE],
                    format_func=lambda x: single_option_labels[x],
                    index=0, key='acc_no')
        if 'acc_no' in st.session_state:
            stk = st.session_state.acc_no
        else:
            stk = None
                    
    else:
        # Lấy danh sách số tài khoản đẹp đang có
        account_list = st.session_state.available_id_list

        if account_list:
            st.write(f"**{text['su_lbl_choose_suggested']}**")
            if 'acc_no' not in st.session_state:
                st.session_state.acc_no = None
            # Chia thành lưới 5 cột để xếp các số tài khoản thẳng hàng nằm ngang như st.pills
            cols = st.columns(5) 
            txt_color = ':orange['            
            for idx, acc_no in enumerate(account_list):
                # Chia đều các số vào các cột tuần hoàn
                with cols[idx % 5]:
                    if 'acc_no' in st.session_state:
                        if acc_no == st.session_state.acc_no:
                            txt_color = ':green['
                    # Mỗi số tài khoản biến thành một nút st.button tuyệt đẹp theo CSS main.py của bạn
                    if st.button(f"{txt_color}{acc_no}]", key=f"acc_{acc_no}"):
                        st.session_state.acc_no = acc_no
                        st.session_state.acc_no_radio = None  # bỏ chọn radio nếu đang chọn
                        st.rerun()
                    txt_color = ':orange['
        stk = st.session_state.acc_no
        if stk is not None:
            st.markdown(f'{text["su_lbl_chosen_acc"]}: :green[{stk}]')

        multi_option_labels = {
            ACC_ID_OPTION_DEFAULT: text['su_opt_default'],
            ACC_ID_OPTION_CHANGE: text['su_opt_change_id'],
        }

        def reset_grid_selection():
            st.session_state.acc_no = None

        stk_modify = st.radio(text['su_radio_multi_lbl'],
                    [ACC_ID_OPTION_DEFAULT, ACC_ID_OPTION_CHANGE],
                    format_func=lambda x: multi_option_labels[x],
                    index=None, label_visibility='hidden', key='acc_no_radio',
                    on_change=reset_grid_selection)
        st.info(text['su_info_choose_suggest'])
        
    if st.button(text['su_btn_signup']):
        
        form_check = True
        
        if ten == '':
            st.error(text['su_err_name_empty'])
            form_check = False
        elif ' ' not in ten:
            st.error(text['su_err_name_fullname'])
            form_check = False
        elif ten.isdigit():
            st.error(text['su_err_name_digit'])
            form_check = False
            
        if calculate_age(ngay_sinh) < 16:
            st.error(text['su_err_age_limit'])
            form_check = False
            
        snapshot_df = get_display_snapshot()
        
        if not validate_phone(sdt):
            st.error(text['su_err_phone_format'])
            form_check = False
        elif sdt in list(snapshot_df['Phone']):
            st.error(text['su_err_phone_exist'])
            form_check = False
            
        if not validate_email(email):
            st.error(text['su_err_email_format'])
            form_check = False
        elif email.upper() in list(snapshot_df['Email'].str.upper()):
            st.error(text['su_err_email_exist'])
            form_check = False
            
        if mat_khau == '':
            st.error(text['su_err_pass_empty'])
            form_check = False
        elif len(mat_khau) < 8:
            st.error(text['su_err_pass_length'])
            form_check = False
        elif mat_khau != xn_mat_khau:
            st.error(text['su_err_pass_mismatch'])
            form_check = False            
            
        if st.session_state.available_id_list != [] and stk_modify != None:
            if stk_modify == ACC_ID_OPTION_USE_SUGGESTED:
                stk = st.session_state.available_id_list[0]
            elif stk == None:
                stk = stk_modify
                
        if stk == None:
            st.error(text['su_err_must_choose_id'])
            form_check = False
        elif stk == '' or stk == ACC_ID_OPTION_DEFAULT:
            stk = stk_mac_dinh
            stkc = stk_mac_dinh
        elif stk == ACC_ID_OPTION_CHANGE:
            st.session_state.available_id_list = []
        elif not stk.isdigit():
            st.error(text['su_err_id_digit'])
            form_check = False
        elif len(stk) > 8:
            st.error(text['su_err_id_length'])
            form_check = False
        else:
            stkc = f'{int(stk):08}'
            
        if form_check:
            if stk == ACC_ID_OPTION_CHANGE:           
                st.rerun()
            if not id_available_check(stkc) or len(stk) < 8:
                st.session_state.available_id_list = new_id_suggest(stk,30)
                if st.session_state.available_id_list == []:
                    st.error(text['su_err_no_avail_id'])
                    form_check = False
                else:
                    st.rerun()
            elif st.session_state.available_id_list == []:
                st.session_state.available_id_list = [stk]
                st.rerun()

        if form_check:
            try:
                account_signup(stk, ten, ngay_sinh, sdt, email, mat_khau, sodu)
                st.session_state.previous_page.append(st.session_state.current_page)
                st.session_state.available_id_list = []
                st.session_state.acc_num = stk
                st.session_state.signup_state = True
                st.switch_page('pages/signup_success.py')
            except AccountIdTakenError:
                st.session_state.available_id_list = []
                st.error(text['su_err_id_taken'])
        else:
            st.error(text['su_err_recheck'])


# Hàm kiểm tra đăng nhập. KQ trả về 2 là thành công, 1 là sai mật khẩu, 0 là không tồn tại tài khoản
def login_check(stk:str, mat_khau:str):
    global worksheet, df
    if stk in df.index:
        stored_password = df.loc[stk, 'Password']

        if is_bcrypt_hash(stored_password):
            # Tài khoản đã hash -> so sánh bằng bcrypt
            password_correct = bcrypt.checkpw(mat_khau.encode('utf-8'), stored_password.encode('utf-8'))
        else:
            # Tài khoản cũ dạng plaintext -> so sánh trực tiếp
            password_correct = (mat_khau == stored_password)
            if password_correct:
                # Đăng nhập đúng -> tự động nâng cấp mật khẩu cũ lên hash ngay lúc này
                def apply_password_upgrade(current_df):
                    current_df.loc[stk, 'Password'] = hash_password(mat_khau)

                try:
                    update_accounts_safely([stk], apply_password_upgrade)
                except OptimisticLockError:
                    pass  # Không nâng cấp được lần này thì thôi, lần đăng nhập sau sẽ thử lại

        return 2 if password_correct else 1
    else:
        return 0

def generate_session_token() -> str:
    """Sinh ra 1 chuỗi ngẫu nhiên an toàn để làm session token"""
    return secrets.token_hex(32)  # 64 ký tự hex, 256 bit entropy

# Form đăng nhập
def login_form():
    global worksheet, df
    
    worksheet, df = df_init()
    
    text = st.session_state.text
    with st.form('form_dang_nhap', clear_on_submit=False):
        stk = st.text_input(text['lg_lbl_acc'], value=st.session_state.acc_num, max_chars=8, placeholder=text['lg_placeholder_acc'])        
        mat_khau = st.text_input(text['lg_lbl_pass'], type='password', max_chars=24, placeholder=text['lg_placeholder_pass'])

        if st.form_submit_button(text['lg_btn_submit'], type='primary'):
            if stk == '':
                st.error(text['lg_err_acc_empty'])
            elif mat_khau == '':
                st.error(text['lg_err_pass_empty'])
            else:
                if not stk.isdigit():
                    stk = stk.lower()
                match login_check(stk, mat_khau):
                    case 0:
                        st.error(text['lg_err_not_found'])
                    case 1:
                        st.session_state.wrong_password_count += 1
                        remaining_attempts = 3 - st.session_state.wrong_password_count
                        st.error(text['lg_err_wrong_pass'].format(remaining_attempts))
                    case 2:
                        st.session_state.previous_page.append(st.session_state.current_page)
                        st.session_state.login_state = True
                        st.session_state.login_noti = True
                        st.session_state.acc_name = df.loc[stk, 'Name']
                        st.session_state.acc_num = stk
                        
                        CURRENT_TIME = time.time()
                        st.session_state.last_activity_time = CURRENT_TIME
                        
                        login_timestamp = str(int(CURRENT_TIME))
                        new_session_token = generate_session_token()

                        def apply_new_session(current_df):
                            old_session_value = str(current_df.loc[stk, 'Session'])
                            if "|" in old_session_value:
                                current_df.loc[stk, 'Previous_Session'] = old_session_value
                            current_df.loc[stk, 'Session'] = f"{login_timestamp}|{new_session_token}"

                        update_accounts_safely([stk], apply_new_session)
                        st.session_state.session_token = new_session_token
                        
                        st.session_state.power_level = int(df.loc[stk, 'Power_Level'])
                        st.switch_page('pages/login_success.py')
                        
    if st.session_state.wrong_password_count > 2:
        st.session_state.wrong_password_count = 0                            
        st.switch_page('pages/password_wrong.py')

# Hàm đăng xuất:
def logout(cause:str = 'manual'):
    worksheet, df = df_init()

    if cause == 'manual':
        # Trả giá trị phiên làm việc trên Google Sheet về '0' để vô hiệu hóa Token cũ vĩnh viễn.
        df.loc[st.session_state.acc_num, 'Session'] = '0'
        work_sheet_update(worksheet, df)
        
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
    st.session_state.password_change_need = False
    
    if cause == 'manual':
        # Làm sạch hoàn toàn thanh URL và điều hướng về trang chủ
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



# Hàm lấy số dư tài khoản
def available_balance(stk:str):
    _, fresh_df = df_init()
    return fresh_df.loc[stk, 'Balance']

# Form tạo yêu cầu chuyển tiền
def money_transfer_form():
    global df
    
    text = st.session_state.text 
    stkc = st.session_state.receiver_num
    tien_ckc = st.session_state.transfer_amount
    
    stk = st.text_input(text['tf_lbl_receiver'], value=stkc, max_chars=8, placeholder=text['tf_placeholder_receiver'])
    snapshot_df = get_display_snapshot()
    if stk in snapshot_df.index:
        st.write(f':blue[{format(snapshot_df.loc[stk, 'Name'])}]')
        
    tien_ck = st.number_input(text['tf_lbl_amount'], value=tien_ckc, max_value=500000000, step=100000, placeholder=text['tf_placeholder_amount'], format='%u')
    if 100000 <= tien_ck <= 500000000:
        st.write(f':blue[{format(money_number_to_text(tien_ck))}]')
    else:
        st.write(f":red[{text['tf_limit_hint']}]")
    noi_dung = st.text_input(text['tf_lbl_content'], max_chars=99, placeholder=text['tf_placeholder_content'])
    
    if st.button(text['tf_btn_submit']):
        if stk == '':
            st.error(text['tf_err_acc_empty'])
        elif stk == st.session_state.acc_num:
            st.error(text['tf_err_self_transfer'])
        elif tien_ck < 10000:
            st.error(text['tf_err_min_limit'])
        elif noi_dung == '':
            st.error(text['tf_err_content_empty'])
        elif stk not in snapshot_df.index:
            st.error(text['tf_err_not_found'])
        else:
            st.session_state.previous_page.append(st.session_state.current_page)
            st.session_state.receiver_num = stk
            st.session_state.transfer_amount = tien_ck
            st.session_state.transfer_state = 1
            st.session_state.transfer_content = noi_dung
            st.switch_page('pages/transfer_rehearsal.py')

# Hàm chính chuyển số tiền thành chữ (Tự động nhận diện Tiếng Việt / Tiếng Anh)
def money_number_to_text(n):
    # ==============================================================================
    # TRƯỜNG HỢP 1: ĐỌC TIẾNG ANH
    # ==============================================================================
    if st.session_state.get('lang') == 'en':
        if n == 0:
            return "Zero Vietnamese Dong"
        
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
                "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        thousands = ["", "Thousand", "Million", "Billion"]

        def convert_three_digits_en(num):
            res = ""
            hundred = num // 100
            rem = num % 100
            if hundred > 0:
                res += ones[hundred] + " Hundred "
            if rem > 0:
                if rem < 20:
                    res += ones[rem]
                else:
                    res += tens[rem // 10] + (" " + ones[rem % 10] if rem % 10 > 0 else "")
            return res.strip()

        res_words = ""
        curr_idx = 0
        temp_n = n
        while temp_n > 0:
            if temp_n % 1000 != 0:
                res_words = convert_three_digits_en(temp_n % 1000) + " " + thousands[curr_idx] + " " + res_words
            temp_n //= 1000
            curr_idx += 1
            
        return res_words.strip() + " Vietnamese Dong"

    # ==============================================================================
    # TRƯỜNG HỢP 2: ĐỌC TIẾNG VIỆT
    # ==============================================================================
    if n == 0:
        return "Không đồng"
    
    chu_so = ["Không", "Một", "Hai", "Ba", "Bốn", "Năm", "Sáu", "Bảy", "Tám", "Chín"]
    don_vi = ["", "Nghìn", "Triệu", "Tỷ", "Nghìn tỷ", "Triệu tỷ"]
    
    def doc_3_so(num):
        tram = num // 100
        chuc = (num % 100) // 10
        don_vi_le = num % 10
        
        ket_qua = ""
        if tram == 0 and chuc == 0 and don_vi_le == 0:
            return ""
        else:    
            ket_qua += f" {chu_so[tram]} trăm"

        if chuc > 1:
            ket_qua += f" {chu_so[chuc]} mươi"
        elif chuc == 1:
            ket_qua += " mười"
        elif tram > 0 and chuc == 0 and don_vi_le > 0:
            ket_qua += " lẻ"
            
        if chuc > 0 and don_vi_le == 5:
            ket_qua += " lăm"
        elif (tram > 0 and chuc == 0) or don_vi_le > 0:
            if don_vi_le == 1 and chuc > 1:
                ket_qua += " mốt"
            elif don_vi_le > 0:
                ket_qua += f" {chu_so[don_vi_le]}"
                
        return ket_qua.strip()

    chuoi_tien = ""
    vi_tri = 0
    temp_n_vi = n
    
    while temp_n_vi > 0:
        so_phan_chia = temp_n_vi % 1000
        temp_n_vi = temp_n_vi // 1000
        
        if so_phan_chia > 0:
            chuoi_3_so = doc_3_so(so_phan_chia)
            chuoi_tien = f"{chuoi_3_so} {don_vi[vi_tri]} {chuoi_tien}".strip()
        vi_tri += 1
    
    if chuoi_tien[0:11] == 'Không trăm ':
        chuoi_tien = chuoi_tien[11:]
    
    return chuoi_tien.capitalize() + " đồng"


# Form xác nhận chuyển tiền
def transfer_rehearsal():
    global worksheet, df
    
    text = st.session_state.text 
    
    # Định dạng dấu phẩy phân tách hàng nghìn cho số tiền
    formatted_money = format(st.session_state.transfer_amount, ',')
    
    # Xác định đơn vị tiền tệ dựa trên ngôn ngữ
    unit = "VND" if st.session_state.lang == 'en' else "VNĐ"
    
    # Tạo danh sách các cặp thông tin (Nhãn trái, Giá trị phải) để lặp cho gọn code
    receipt_data = [
        (text['rh_amount'].replace(': **:green[{} VNĐ]**', '').replace(': **:green[{} VND]**', ''), f"{formatted_money} {unit}"),
        (text['rh_words'].replace(': **:green[{}]**', ''), money_number_to_text(st.session_state.transfer_amount)),
        (text['rh_sender'].replace(': **:green[{}]**', ''), df.loc[st.session_state.acc_num, 'Name']),
        (text['rh_sender_acc'].replace(': **:green[{}]**', ''), st.session_state.acc_num),
        (text['rh_receiver'].replace(': **:green[{}]**', ''), df.loc[st.session_state.receiver_num, 'Name']),
        (text['rh_receiver_acc'].replace(': **:green[{}]**', ''), st.session_state.receiver_num),
        (text['rh_content'].replace(': **:green[{}]**', ''), st.session_state.transfer_content)
    ]
    
    with st.form('form_kiem_tra_ck', clear_on_submit=True, width='stretch'):
        # Vòng lặp vẽ giao diện biên lai bám 2 lề trái/phải
        for label, value in receipt_data:
            c1, c2 = st.columns([2, 3])
            with c1:
                st.write(label)
            with c2:
                # Canh lề phải và tô màu xanh lá cho phần dữ liệu biến
                st.markdown(f'<div style="text-align: right; color: #2ecc71; font-weight: bold;">{value}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        mat_khau = st.text_input(text['rh_lbl_pass'], type='password', max_chars=24, placeholder=text['rh_placeholder_pass'])
        
        if st.form_submit_button(f'**:green[{text['rh_btn_submit']}]**'):
            if mat_khau == '':
                st.error(text['rh_err_pass_empty'])
            else:
                match login_check(st.session_state.acc_num, mat_khau):
                    case 1:
                        st.session_state.wrong_password_count += 1
                        remaining_attempts = 3 - st.session_state.wrong_password_count
                        st.error(text['rh_err_wrong_pass'].format(remaining_attempts))
                    case 2:
                        try:
                            money_transfer(st.session_state.acc_num, st.session_state.receiver_num, st.session_state.transfer_amount)
                            st.session_state.receiver_num = ''
                            st.session_state.transfer_amount = 0
                            st.session_state.wrong_password_count = 0
                            st.session_state.transfer_state = 2
                            st.switch_page('pages/transfer_success.py')
                        except ValueError:
                            st.error(text['rh_err_insufficient'])
                            st.session_state.wrong_password_count = 0
                        except OptimisticLockError:
                            st.error(text['rh_err_system_busy'])                     
                        
    if st.session_state.wrong_password_count > 2:
        st.session_state.receiver_num = ''
        st.session_state.transfer_amount = 0     
        st.session_state.wrong_password_count = 0
        st.session_state.transfer_state = 0
        st.switch_page('pages/password_wrong.py')

# Form thông tin tài khoản và chỉnh sửa:
def account_info(stk):
    global worksheet, df
    worksheet, df = df_init()
    text = st.session_state.text

    snapshot_df = get_display_snapshot()
    if stk not in snapshot_df.index:
        st.error(text['lg_err_not_found'])
        return

    current_info = snapshot_df.loc[stk]
    is_privileged = st.session_state.power_level > 0  # tài khoản quản trị/kiểm thử -> chỉ xem

    if st.session_state.get('password_change_need'):
        st.warning(text['as_warning_forced_change'])

    if is_privileged:
        st.info(text['as_notice_privileged_view_only'])
    else:
        st.text_input(text['as_lbl_acc_num'], value=stk, disabled=True)

    # ============================================================
    # PHẦN 1: THÔNG TIN CÁ NHÂN
    # ============================================================
    st.markdown(f"**:violet[{text['as_section_profile']}]**")
    with st.form('form_account_info', clear_on_submit=False):
        st.text_input(text['su_lbl_name'], value=current_info['Name'], disabled=True)
        st.date_input(text['su_lbl_dob'], value=pd.to_datetime(current_info['DoB']).date(),
                    min_value=date(1920, 1, 1), max_value=datetime.today(), format='DD/MM/YYYY',
                    disabled=True)
        sdt = st.text_input(text['su_lbl_phone'], value=current_info['Phone'], disabled=is_privileged)
        email = st.text_input(text['su_lbl_email'], value=current_info['Email'], disabled=is_privileged)
        current_pass_for_info = st.text_input(text['as_lbl_current_pass'], type='password', max_chars=24,
                                                placeholder=text['su_placeholder_required'], disabled=is_privileged)

        if st.form_submit_button(text['as_btn_save_profile'], disabled=is_privileged):
            form_check = True
            if not validate_phone(sdt):
                st.error(text['su_err_phone_format']); form_check = False
            else:
                other_accounts_df = get_display_snapshot().drop(index=stk, errors='ignore')
                if sdt in list(other_accounts_df['Phone']):
                    st.error(text['su_err_phone_exist']); form_check = False
            if not validate_email(email):
                st.error(text['su_err_email_format']); form_check = False
            else:
                other_accounts_df = get_display_snapshot().drop(index=stk, errors='ignore')
                if email.upper() in list(other_accounts_df['Email'].str.upper()):
                    st.error(text['su_err_email_exist']); form_check = False
            if current_pass_for_info == '':
                st.error(text['lg_err_pass_empty']); form_check = False
            elif login_check(stk, current_pass_for_info) != 2:
                st.error(text['as_err_current_pass_wrong']); form_check = False

            if form_check:
                def apply_profile_update(current_df):
                    current_df.loc[stk, 'Phone'] = sdt
                    current_df.loc[stk, 'Email'] = email
                update_accounts_safely([stk], apply_profile_update)
                st.success(text['as_success_profile_updated'])
                st.rerun()

    st.markdown('---')

    # ============================================================
    # PHẦN 2: ĐỔI MẬT KHẨU
    # ============================================================
    st.markdown(f"**:violet[{text['as_section_change_pass']}]**")
    with st.form('form_change_password', clear_on_submit=True):
        current_pass = st.text_input(text['as_lbl_current_pass'], type='password', max_chars=24,
                                    placeholder=text['su_placeholder_required'], key='current_pass_for_change',
                                    disabled=is_privileged)
        new_pass = st.text_input(text['as_lbl_new_pass'], type='password', max_chars=24,
                                placeholder=text['su_placeholder_required'], disabled=is_privileged)
        confirm_new_pass = st.text_input(text['as_lbl_confirm_new_pass'], type='password', max_chars=24,
                                        placeholder=text['su_placeholder_required'], disabled=is_privileged)

        if st.form_submit_button(text['as_btn_change_pass'], disabled=is_privileged):
            form_check = True
            if current_pass == '':
                st.error(text['lg_err_pass_empty']); form_check = False
            elif login_check(stk, current_pass) != 2:
                st.error(text['as_err_current_pass_wrong']); form_check = False
            if new_pass == '':
                st.error(text['su_err_pass_empty']); form_check = False
            elif len(new_pass) < 8:
                st.error(text['su_err_pass_length']); form_check = False
            elif new_pass != confirm_new_pass:
                st.error(text['su_err_pass_mismatch']); form_check = False

            if form_check:
                def apply_password_change(current_df):
                    current_df.loc[stk, 'Password'] = hash_password(new_pass)
                update_accounts_safely([stk], apply_password_change)
                st.session_state.password_change_need = False
                st.success(text['as_success_pass_changed'])