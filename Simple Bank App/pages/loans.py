import streamlit as st
from helpers import (available_balance, login_check, settle_matured_loans,
                    open_loan, repay_loan_early, loans_init, get_loan_limit,
                    get_total_active_loans, LOAN_MIN_AMOUNT, RATE_TABLE,
                    flash_success, show_flash_message)

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text
stk = st.session_state.acc_num

settle_matured_loans(stk)
show_flash_message()

st.header(text['withdraw_title'].upper(), anchor=False)
st.write(f'{text["available_balance"]}: :green[{format(available_balance(stk), ",")} VNĐ]')

loan_limit = get_loan_limit(stk)
current_debt = get_total_active_loans(stk)
available_to_borrow = max(loan_limit - current_debt, 0)
st.write(f'{text["loan_lbl_current_limit"]}: :blue[{format(available_to_borrow, ",")} VNĐ] / {format(loan_limit, ",")} VNĐ')

st.markdown(f"**:violet[{text['loan_section_open']}]**")

st.write(f"**{text['loan_lbl_term']}**")
term_options = list(RATE_TABLE.keys())
if 'loan_selected_term' not in st.session_state:
    st.session_state.loan_selected_term = None

cols = st.columns(len(term_options))
for idx, term in enumerate(term_options):
    with cols[idx]:
        is_selected = st.session_state.loan_selected_term == term
        label = f":green[{term} tháng]" if is_selected else f"{term} tháng"
        if st.button(label, key=f"loan_term_btn_{term}"):
            st.session_state.loan_selected_term = term
            st.rerun()

if st.session_state.loan_selected_term:
    rate = RATE_TABLE[st.session_state.loan_selected_term]['loan']
    st.info(f"Lãi suất: **{rate*100:.2f}%/năm**")

with st.form('form_open_loan', clear_on_submit=True):
    amount = st.number_input(text['loan_lbl_amount'], min_value=LOAN_MIN_AMOUNT,
                            max_value=max(available_to_borrow, LOAN_MIN_AMOUNT), step=100000, format='%d')
    pass_confirm = st.text_input(text['savings_lbl_pass_confirm'], type='password', max_chars=24)

    if st.form_submit_button(text['loan_btn_open']):
        if st.session_state.loan_selected_term is None:
            st.error(text['loan_err_amount_range'])
        elif amount < LOAN_MIN_AMOUNT or amount > available_to_borrow:
            st.error(text['loan_err_limit_exceeded'])
        elif pass_confirm == '' or login_check(stk, pass_confirm) != 2:
            st.error(text['savings_err_pass_wrong'])
        else:
            try:
                open_loan(stk, int(amount), st.session_state.loan_selected_term)
                st.session_state.loan_selected_term = None
                flash_success('loan_success_opened')
                st.rerun()
            except ValueError:
                st.error(text['loan_err_limit_exceeded'])

st.markdown('---')
st.markdown(f"**:violet[{text['loan_section_active']}]**")

_, loans_df = loans_init()
my_loans = loans_df[(loans_df['Account_ID'] == stk) & (loans_df['Status'].isin(['active', 'overdue']))]

if my_loans.empty:
    st.info(text['loan_no_active'])
else:
    if (my_loans['Status'] == 'overdue').any():
        st.warning(text['loan_notice_overdue'])

    for loan_id, row in my_loans.iterrows():
        with st.container(border=True):
            st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"{text['loan_lbl_principal']}: :red[{format(int(row['Principal']), ',')} VNĐ]")
                st.write(f"{row['Term_Months']} tháng - {row['Annual_Rate']*100:.2f}%/năm")
            with c2:
                status_label = text['loan_lbl_status_overdue'] if row['Status'] == 'overdue' else text['loan_lbl_status_active']
                st.write(f"Trạng thái: {status_label}")
                st.write(f"{text['savings_lbl_maturity_date']}: {row['Maturity_Date']}")
            with c3:
                show_confirm_key = f"show_confirm_repay_{loan_id}"
                if st.button(text['loan_btn_early_repay'], key=f"btn_repay_{loan_id}"):
                    st.session_state[show_confirm_key] = True
                if st.session_state.get(show_confirm_key):
                    pass_repay = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                                max_chars=24, key=f"pass_input_repay_{loan_id}")
                    if st.button(f"**:green[{text['common_confirm']} ✓]**", key=f"btn_confirm_repay_{loan_id}"):
                        if pass_repay == '' or login_check(stk, pass_repay) != 2:
                            st.error(text['savings_err_pass_wrong'])
                        else:
                            try:
                                repay_loan_early(stk, loan_id)
                                del st.session_state[show_confirm_key]
                                flash_success('loan_success_repaid')
                                st.rerun()
                            except ValueError:
                                st.error(text['loan_err_insufficient_repay'])