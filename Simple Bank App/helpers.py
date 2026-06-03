import streamlit as st 
import pandas as pd
import os
import re
import random
from datetime import date, datetime

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

account_file = 'Simple Bank App/bank_account.csv'

if os.path.exists(account_file):
    df = pd.read_csv(account_file, dtype={'ID':str,'Phone':str,'Balance':int}, index_col='ID')
else:
    df = pd.DataFrame(columns= ['ID', 'Name', 'DoB', 'Phone', 'Email', 'Password', 'Balance'])
    df = df.astype({
        'ID':'string',
        'Name':'string',
        'DoB':'string',
        'Phone':'string',
        'Email':'string',
        'Password':'string',
        'Balance':'int64'
        })
    df.set_index('ID', inplace=True)

df.sort_index(inplace=True)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
    
def validate_phone(phone):
    pattern = r'^\+?(0|84)\d{9,10}$'
    return bool(re.match(pattern, phone))

def calculate_age(birth_date):
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def new_id_check(id):
    global df
    if id not in df.index:
        return id
    else:
        for i in range(1, 100000000):
            if f'{i:08}' not in df.index:
                return f'{i:08}'
                break
                        
def id_available_check(num):
    return True if num not in df.index else False

def id_num_generate(init_num, choices=['6', '8', '9']):
    i_str = str(init_num)
    init_len = len(i_str)
    spaces_count = 8 - init_len
    

    def filler_generate(length):
        if length == 0:
            return [[]]
        sub_combos = filler_generate(length - 1)
        return [combo + [digit] for combo in sub_combos for digit in choices]


    filler_list = filler_generate(spaces_count)
    
    kq = set()

    for filler in filler_list:
        for i in range(spaces_count + 1):

            temp = filler.copy()

            temp.insert(i, i_str)

            whole_num = "".join(temp)
            kq.add(whole_num)
            
    return sorted(list(kq))

def new_id_suggest(init_id, rs_num):
    good_id = id_num_generate(init_id)
    available_good_id = list(filter(id_available_check, good_id))
    
    if len(available_good_id) <= rs_num:
        return available_good_id
    
    random_good_id = []
    while len(random_good_id) < rs_num:
        chosen_random_id = random.choice(available_good_id)
        random_good_id.append(chosen_random_id)
        available_good_id.remove(chosen_random_id)
        
    random_good_id.sort()
    
    return random_good_id
            
def signup(stk, ten, ngay_sinh, sdt, email, matkhau, sodu):
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
    df.to_csv(account_file)



def signup_form():
    with st.form('form_dang_ky', clear_on_submit=False):
        ten = st.text_input('Vui lòng nhập tên của bạn', value='Nguyễn Văn A', placeholder='Không được để trống')
        ngay_sinh = st.date_input('Chọn ngày sinh: ', value= datetime.today(), min_value= date(1920,1,1), max_value= datetime.today(), format='DD/MM/YYYY')
        sdt = st.text_input('Nhập SĐT của bạn')
        email = st.text_input('Nhập email của bạn: ')
        mat_khau = st.text_input('Vui lòng nhập mật khẩu', type='password', max_chars=24, placeholder='Không được để trống')
        sodu = st.number_input('Nhập số tiền khi tạo tài khoản', value= 2000000, min_value=500000, max_value=100000000000, step=100000, placeholder='Không được để trống', format= '%d')
        stk_mac_dinh = new_id_check('00000001')
        st.markdown('')
        st.markdown('**:violet[PHẦN TỰ CHỌN]**')
        if st.session_state.available_id_list == []:
            stk = st.text_input('Điền dãy số mà quý khách mong muốn có trong số tài khoản, bỏ trống nếu quý khách muốn nhận số tài khoản mặc định từ hệ thống'
                                ,placeholder=stk_mac_dinh, max_chars=8
                                )
        else:
            stk = st.pills('Dưới đây là một vài số tài khoản có chứa dãy số yêu thích của quý khách, vui lòng chọn một số để làm số tài khoản. Quý khách có thể chọn Mặc định để nhận số tài khoản ngẫu nhiên hoặc Đổi dãy số khác'
                                , st.session_state.available_id_list,
                            )
            stk_modify = st.radio('Chọn stk theo', ['Mặc định', 'Đổi dãy số khác'], index=None, label_visibility='hidden')
            st.info('Quý khách hãy chọn một số tài khoản trong danh sách gợi ý')
        if st.form_submit_button('Đăng ký'):
            form_check = True
            if ten == '':
                st.error('Tên không được để trống')
                form_check = False
            elif ' ' not in ten:
                st.error('Phải có đủ họ và tên')
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
            if st.session_state.available_id_list != [] and stk_modify != None:
                stk = stk_modify
            if stk == None:
                st.error('Bạn phải chọn một dãy số làm số tài khoản. Nếu không hãy chọn Mặc định hoặc Đổi dãy số khác')
                form_check = False
            elif stk == '' or stk == 'Mặc định':
                stk = stk_mac_dinh
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
            if form_check == True:
                if stk == 'Đổi dãy số khác':                    
                    st.rerun()
                elif not id_available_check(stkc) or len(stk) < 8:
                    st.session_state.available_id_list = new_id_suggest(int(stk),28)
                    if st.session_state.available_id_list == []:
                        st.error('Không còn số tài khoản nào chứa dãy số này, hãy chọn số khác hoặc bỏ trống')
                        form_check = False
                    else:
                        st.rerun()

            if form_check:
                st.session_state.previous_page.append(st.session_state.current_page)
                signup(stk, ten, ngay_sinh, sdt, email, mat_khau, sodu)
                st.session_state.available_id_list = []
                st.session_state.acc_num = stk
                st.session_state.signup_state = True
                st.switch_page('pages/signup_success.py')
            else:
                st.error('Vui lòng kiểm tra và nhập lại')
                
def login_check(stk:str, mat_khau:str):
    if stk in df.index:
        if mat_khau == df.loc[stk, 'Password']:
            return 2
        else:
            return 1
    else:
        return 0

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

def available_balance(stk:str):
    return df.loc[stk, 'Balance']

def transfer_check(stk:str, tien_ck:int):
    if stk in df.index:
        if tien_ck <= df.loc[stk, 'Balance']:
            return 2
        else:
            return 1
    else:
        return 0    

def money_transfer(sender:str, receiver:str, transfer_amount:int):
    global df
    df.loc[sender, 'Balance'] -= transfer_amount
    df.loc[receiver, 'Balance'] += transfer_amount
    df.to_csv('bank_account.csv', index=False)

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