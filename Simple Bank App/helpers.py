import streamlit as st 
import gspread
import pandas as pd
import os
import re
import random
from datetime import date, datetime

# Tạo màu cho widget label:
st.markdown(
    """
    <style>
    [data-testid="stWidgetLabel"] p {
        color: #FF5733 !important; /* Màu cam đỏ */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# account_file = 'Simple Bank App/bank_account.csv'

# if os.path.exists(account_file):
#     df = pd.read_csv(account_file, dtype={'ID':str,'Phone':str,'Balance':int}, index_col='ID')
# else:
#     df = pd.DataFrame(columns= ['ID', 'Name', 'DoB', 'Phone', 'Email', 'Password', 'Balance'])
#     df = df.astype({
#         'ID':'string',
#         'Name':'string',
#         'DoB':'string',
#         'Phone':'string',
#         'Email':'string',
#         'Password':'string',
#         'Balance':'int64'
#         })
#     df.set_index('ID', inplace=True)

# Hàm lấy secrets để đọc file google sheet
def get_gspread_client():

    credentials_dict = dict(st.secrets["connections"]["gsheets"])

    gc = gspread.service_account_from_dict(credentials_dict)
    return gc


# Đọc file vào dataframe

gc = get_gspread_client()

spreadsheet_url = st.secrets["connections"]["gsheets"]["toplevel_url"]
sh = gc.open_by_url(spreadsheet_url)

worksheet = sh.worksheet("bank_account")

data = worksheet.get_all_records()
df = pd.DataFrame(data)


df = df.astype({
                'Name' : 'str',
                'Phone' : 'str',
                'Email' : 'str',
                'Password' : 'str',
                'Balance' : 'int64'
                })

# Xử lý dataframe

df['ID'] = pd.Series(f'{x:08}' for x in list(df['ID']))
df['Phone'] = '0' + df['Phone']
pd.to_datetime(df['DoB'])
df.set_index('ID', inplace=True)
df.sort_index(inplace=True)

# Hộp thoại báo khi rời những trang điền form
@st.dialog('Xác nhận rời trang')
def switch_page_confirm(page_path, page_trace = True):
    st.warning('Nếu rời khỏi trang, nội dung bạn đã điền sẽ không được lưu. Bạn có chắc muốn rời khỏi trang này chứ?')
    if st.button('**:red[Rời khỏi trang này]**'):
        if page_trace:
            st.session_state.previous_page.append(st.session_state.current_page)
        else:
            st.session_state.previous_page.pop(-1)
        st.switch_page(page_path)
    if st.button('**:green[Ở lại trang này]**'):
        st.rerun()

# Hàm kiểm tra các trang có form điền để mở hộp thoại thông báo khi rời đi
def switch_page_check(page_path, page_trace = True):
    check = True
    for i in ['login.py','signup.py','transfer.py','transfer_rehearsal.py']:
        if i in str(st.session_state.current_page):
            check = False
            switch_page_confirm(page_path, page_trace)
    if check:
        if not page_trace:
            st.session_state.previous_page.pop(-1)
        st.switch_page(page_path)


# Các hàm xử lý dữ liệu nhập form

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
    global df
    if id not in df.index:
        return id
    else:
        for i in range(1, 100000000):
            if f'{i:08}' not in df.index:
                return f'{i:08}'
                break

# Nhóm hàm tạo list ID số đẹp

# Hàm kiểm tra ID khả dụng hay không
def id_available_check(num):
    return True if num not in df.index else False

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

# Hàm xuất df ra lại google sheet
def work_sheet_update():
    global df, worksheet

    worksheet.clear()

    df['DoB'] = df['DoB'].astype(str)
    df.reset_index(drop=False, inplace=True)
    
    header = df.columns.values.tolist()
    rows = df.values.tolist()
    data_to_upload = [header] + rows

    worksheet.update(range_name='A1', values=data_to_upload)

    pd.to_datetime(df['DoB'])
    df.set_index('ID')

# Hàm tạo tài khoản mới
def account_signup(stk, ten, ngay_sinh, sdt, email, matkhau, sodu):
    global df
    df.loc[stk] = pd.Series({
                            'Name':ten,
                            'DoB':ngay_sinh,
                            'Phone':sdt,
                            'Email':email,
                            'Password':matkhau,
                            'Balance':sodu
                            })
    df.sort_index(inplace=True)
    # df.to_csv(account_file)
    work_sheet_update()

# Hàm hỗ trợ gợi ý ID là số ngày sinh nếu khả dụng khi nhập vào form đăng ký
def process_temp_DoB():
    st.session_state.pr_temp_DoB = st.session_state.temp_DoB.strftime('%d/%m/%Y').replace('/', '')

# Form đăng ký tài khoản mới
def signup_form():
    ten = st.text_input('Vui lòng nhập tên của bạn', value='Nguyễn Văn A', placeholder='Không được để trống')
    ngay_sinh = st.date_input('Chọn ngày sinh: ', value= datetime.today(), min_value= date(1920,1,1), max_value= datetime.today(), format='DD/MM/YYYY', key= 'temp_DoB', on_change=process_temp_DoB)
    sdt = st.text_input('Nhập SĐT của bạn')
    email = st.text_input('Nhập email của bạn: ')
    mat_khau = st.text_input('Vui lòng nhập mật khẩu', type='password', max_chars=24, placeholder='Không được để trống')
    xn_mat_khau = st.text_input('Vui lòng xác nhận lại mật khẩu', type='password', max_chars=24, placeholder='Không được để trống')
    sodu = st.number_input('Nhập số tiền khi tạo tài khoản', value= 2000000, min_value=500000, max_value=100000000000, step=100000, placeholder='Không được để trống', format= '%d')
    stk_mac_dinh = new_id_check(st.session_state.pr_temp_DoB)
    st.markdown('')
    st.markdown('**:violet[PHẦN TỰ CHỌN]**')
    if st.session_state.available_id_list == []:
        stk = st.text_input('Điền dãy số mà quý khách mong muốn có trong số tài khoản, bỏ trống nếu quý khách muốn nhận số tài khoản mặc định từ hệ thống'
                            ,placeholder=stk_mac_dinh + ' đang khả dụng', max_chars=8
                            )
        if stk_mac_dinh == st.session_state.pr_temp_DoB and calculate_age(ngay_sinh) >= 16:
            st.info('Dãy số ngày sinh của quý khách đang khả dụng để làm số tài khoản, quý khách có thể bấm đăng ký để chọn dãy số này')
    elif len(st.session_state.available_id_list) == 1:
        stk_modify = st.radio('Dãy số quý khách đã chọn khả dụng để làm số tài khoản, quý khách hãy xác nhận dùng dãy số này. Nếu không hãy chọn mặc định để lấy một số ngẫu nhiên hoặc chọn một dãy số khác',
                    [f'Xác nhận dùng {st.session_state.available_id_list[0]} làm số tài khoản'] + ['Mặc định', 'Đổi dãy số khác'], index=0)
    else:
        stk = st.pills('Dưới đây là một vài số tài khoản có chứa dãy số yêu thích của quý khách, vui lòng chọn một số để làm số tài khoản. Quý khách có thể chọn mặc định để nhận số tài khoản ngẫu nhiên hoặc đổi dãy số khác'
                            , st.session_state.available_id_list,
                        )
        stk_modify = st.radio('Chọn stk theo', ['Mặc định', 'Đổi dãy số khác'], index=None, label_visibility='hidden')
        st.info('Quý khách hãy chọn một số tài khoản trong danh sách gợi ý')
    if st.button('Đăng ký'):
        form_check = True
        if ten == '':
            st.error('Tên không được để trống')
            form_check = False
        elif ' ' not in ten:
            st.error('Phải có đủ họ và tên')
            form_check = False
        elif ten.isdigit():
            st.error('Tên không được có số')
            form_check = False            
        if calculate_age(ngay_sinh) < 16:
            st.error('Bạn phải trên 16 tuổi mới được tạo tài khoản')
            form_check = False
        if not validate_phone(sdt):
            st.error('Số điện thoại phải bắt đầu là 0 hoặc 84 và kèm theo 9-10 chữ số')
            form_check = False
        elif sdt in list(df['Phone']):
            st.error('Số điện thoại đã được đăng ký cho tài khoản khác')
            form_check = False
        if not validate_email(email):
            st.error('Email sai cú pháp')
            form_check = False
        elif email.upper() in list(df['Email'].str.upper()):
            st.error('Email đã được đăng ký cho tài khoản khác')
            form_check = False
        if mat_khau == '':
            st.error('Mật khẩu không được để trống')
            form_check = False
        elif len(mat_khau) < 8:
            st.error('Mật khẩu phải chứa từ 8-24 ký tự')
            form_check = False
        elif mat_khau != xn_mat_khau:
            st.error('Xác nhận mật khẩu không trùng khớp')
            form_check = False            
        if st.session_state.available_id_list != [] and stk_modify != None:
            if 'Xác nhận' in stk_modify:
                stk = st.session_state.available_id_list[0]
            elif stk == None:
                stk = stk_modify
        if stk == None:
            st.error('Bạn phải chọn một dãy số làm số tài khoản. Nếu không hãy chọn Mặc định hoặc Đổi dãy số khác')
            form_check = False
        elif stk == '' or stk == 'Mặc định':
            stk = stk_mac_dinh
            stkc = stk_mac_dinh
        elif stk == 'Đổi dãy số khác':
            st.session_state.available_id_list = []
        elif not stk.isdigit():
            st.error('Số tài khoản không được chứa chữ cái')
            form_check = False
        elif len(stk) > 8:
            st.error('Số tài khoản không được quá 8 chữ số')
            form_check = False
        else:
            stkc = f'{int(stk):08}'
        if form_check:
            if stk == 'Đổi dãy số khác':           
                st.rerun()
            if not id_available_check(stkc) or len(stk) < 8:
                st.session_state.available_id_list = new_id_suggest(stk,28)
                if st.session_state.available_id_list == []:
                    st.error('Không còn số tài khoản khả dụng nào chứa dãy số này, hãy chọn số khác hoặc bỏ trống')
                    form_check = False
                else:
                    st.rerun()
            elif st.session_state.available_id_list == []:
                st.session_state.available_id_list = [stk]
                st.rerun()

        if form_check:
            st.session_state.previous_page.append(st.session_state.current_page)
            account_signup(stk, ten, ngay_sinh, sdt, email, mat_khau, sodu)
            st.session_state.available_id_list = []
            st.session_state.acc_num = stk
            st.session_state.signup_state = True
            st.switch_page('pages/signup_success.py')
        else:
            st.error('Vui lòng kiểm tra và nhập lại')

# Hàm kiểm tra đăng nhập. KQ trả về 2 là thành công, 1 là sai mật khẩu, 0 là không tồn tại tài khoản
def login_check(stk:str, mat_khau:str):
    if stk in df.index:
        if mat_khau == df.loc[stk, 'Password']:
            return 2
        else:
            return 1
    else:
        return 0

# Form đăng nhập
def login_form():
    with st.form('form_dang_nhap', clear_on_submit=False):
        stk = st.text_input('Số tài khoản', value=st.session_state.acc_num, max_chars=8, placeholder='Nhập số tài khoản của quý khách')        
        mat_khau = st.text_input('Mật khẩu', type='password', max_chars=24, placeholder='Nhập mật khẩu đăng nhập')
        if st.form_submit_button('Đăng nhập'):
            if stk == '':
                st.error('Số tài khoản không được bỏ trống')
            elif mat_khau == '':
                st.error('Vui lòng điền mật khẩu')
            else:
                match login_check(stk, mat_khau):
                    case 0:
                        st.error('Không tìm thấy tài khoản')
                    case 1:
                        st.session_state.dem_sai_mk += 1
                        st.error(f'Sai mật khẩu. Quý khách sẽ bị chuyển về trang chủ sau **:red[{3-st.session_state.dem_sai_mk}]** lần nữa')
                    case 2:
                        st.session_state.previous_page.append(st.session_state.current_page)
                        st.session_state.login_state = True
                        st.session_state.login_noti = True
                        st.session_state.acc_name = df.loc[stk, 'Name']
                        st.session_state.acc_num = stk
                        st.switch_page('pages/login_success.py')
    if st.session_state.dem_sai_mk > 2:
        st.session_state.dem_sai_mk = 0
        st.switch_page('pages/password_wrong.py')

# Hàm lấy số dư tài khoản
def available_balance(stk:str):
    return df.loc[stk, 'Balance']

# Hàm kiểm tra chuyển tiền được hay không. KQ trả về 2 là được, 1 là tk ko đủ, 0 là ko tồn tại tài khoản nhận
def transfer_check(stk:str, tien_ck:int):
    if stk in df.index:
        if tien_ck <= df.loc[stk, 'Balance']:
            return 2
        else:
            return 1
    else:
        return 0    

# Hàm chuyển tiền
def money_transfer(sender:str, receiver:str, transfer_amount:int):
    global df
    df.loc[sender, 'Balance'] -= transfer_amount
    df.loc[receiver, 'Balance'] += transfer_amount
    df.to_csv('bank_account.csv', index=False)

# Form chuyển tiền
def money_transfer_form():
    stkc = st.session_state.receiver_num
    tien_ckc = st.session_state.transfer_amount
    with st.form('form_chuyen_khoan', clear_on_submit=False):
        stk = st.text_input('Số tài khoản cần chuyển', value=stkc, max_chars=8, placeholder='Nhập số tài khoản người nhận')        
        tien_ck = st.number_input('Số tiền cần chuyển', value=tien_ckc, max_value=500000000, step=100000, placeholder='Nhập số tiền cần chuyển', format= '%u')
        st.write('Chuyển khoản ít nhất 10.000 đồng và nhiều nhất 500.000.000 đồng trong một lần chuyển')
        noi_dung = st.text_input('Nội dung', max_chars= 99, placeholder='Nhập nội dung chuyển khoản')
        if st.form_submit_button('Chuyển khoản'):
            if stk == '':
                st.error('Số tài khoản không được bỏ trống')
            elif stk == st.session_state.acc_num:
                st.error('Đây là số tài khoản của quý khách, vui lòng điền số tài khoản khác')
            elif tien_ck < 10000:
                st.error('Số tiền chuyển không được nhỏ hơn 10.000 đồng')
            elif noi_dung == '':
                st.error('Nội dung không được bỏ trống')
            else:
                match transfer_check(stk, tien_ck):
                    case 0:
                        st.error('Không tìm thấy tài khoản')
                    case 1:
                        st.error('Không đủ tiền để chuyển')
                    case 2:
                        st.session_state.previous_page.append(st.session_state.current_page)
                        st.session_state.receiver_num = stk
                        st.session_state.transfer_amount = tien_ck
                        st.session_state.transfer_state = 1
                        st.switch_page('pages/transfer_rehearsal.py')

# Hàm chuyển số tiền từ số thành chữ
def doc_so_tien(n):
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
    
    while n > 0:
        so_phan_chia = n % 1000
        n = n // 1000
        
        if so_phan_chia > 0:
            chuoi_3_so = doc_3_so(so_phan_chia)
            chuoi_tien = f"{chuoi_3_so} {don_vi[vi_tri]} {chuoi_tien}".strip()
        vi_tri += 1
    
    if chuoi_tien[0:11] == 'Không trăm ':
        chuoi_tien = chuoi_tien[11:]
    
    return chuoi_tien.capitalize() + " đồng"

# Form xác nhận chuyển tiền
def transfer_rehearsal():
    with st.form('form_kiem_tra_ck', clear_on_submit=True):
        st.write(f'Số tiền chuyển khoản: **:green[{format(st.session_state.transfer_amount, ',')} VNĐ]**')
        st.write(f'Số tiền bằng chữ: **:green[{doc_so_tien(st.session_state.transfer_amount)}]**')
        st.write(f'Người gửi: **:green[{df.loc[st.session_state.acc_num, 'Name']}]**')
        st.write(f'Số tài khoản: **:green[{st.session_state.acc_num}]**')
        st.write(f'Người nhận: **:green[{df.loc[st.session_state.receiver_num, 'Name']}]**')
        st.write(f'Số tài khoản: **:green[{st.session_state.receiver_num}]**')
        mat_khau = st.text_input('Mật khẩu', type='password', max_chars=24, placeholder='Nhập lại mật khẩu để xác nhận chuyển khoản')
        if st.form_submit_button('Xác nhận chuyển tiền'):
            if mat_khau == '':
                st.error('Vui lòng điền mật khẩu')
            else:
                match login_check(st.session_state.acc_num, mat_khau):
                    case 1:
                        st.session_state.dem_sai_mk += 1
                        st.error(f'Sai mật khẩu. Quý khách sẽ bị chuyển về trang chủ sau **:red[{3-st.session_state.dem_sai_mk}]** lần nữa')
                    case 2:
                        money_transfer(st.session_state.acc_num, st.session_state.receiver_num, st.session_state.transfer_amount)
                        st.session_state.receiver_num = ''
                        st.session_state.transfer_amount = 0
                        st.session_state.dem_sai_mk = 0
                        st.session_state.transfer_state = 2
                        st.switch_page('pages/transfer_success.py')
    if st.session_state.dem_sai_mk > 2:
        st.session_state.receiver_num = ''
        st.session_state.transfer_amount = 0     
        st.session_state.dem_sai_mk = 0
        st.session_state.transfer_state = 0
        st.switch_page('pages/password_wrong.py')