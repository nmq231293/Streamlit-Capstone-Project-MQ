import streamlit as st
from helpers import (available_balance, login_check, settle_matured_savings,
                    open_savings_deposit, withdraw_savings_early, toggle_savings_auto_renew,
                    savings_init, SAVINGS_MIN_AMOUNT, RATE_TABLE,
                    flash_success, show_flash_message)

if st.session_state.login_state == False:
    st.switch_page('pages/home.py')

text = st.session_state.text
stk = st.session_state.acc_num

settle_matured_savings(stk)
show_flash_message()

st.header(text["deposit_title"].upper(), anchor=False)
st.write(f'{text["available_balance"]}: :green[{format(available_balance(stk), ",")} VNĐ]')

st.markdown(f"**:violet[{text['savings_section_open']}]**")

st.write(f"**{text['savings_lbl_term']}**")
term_options = list(RATE_TABLE.keys())
if 'savings_selected_term' not in st.session_state:
    st.session_state.savings_selected_term = None

cols = st.columns(len(term_options))
for idx, term in enumerate(term_options):
    with cols[idx]:
        is_selected = st.session_state.savings_selected_term == term
        label = f":green[{term} tháng]" if is_selected else f"{term} tháng"
        if st.button(label, key=f"term_btn_{term}"):
            st.session_state.savings_selected_term = term
            st.rerun()

if st.session_state.savings_selected_term:
    rate = RATE_TABLE[st.session_state.savings_selected_term]['savings']
    st.info(f"Lãi suất: **{rate*100:.2f}%/năm**")

with st.form('form_open_savings', clear_on_submit=True):
    amount = st.number_input(text['savings_lbl_amount'], min_value=SAVINGS_MIN_AMOUNT,
                            step=100000, format='%d')
    auto_renew = st.checkbox(text['savings_lbl_auto_renew'], value=False)
    pass_confirm = st.text_input(text['savings_lbl_pass_confirm'], type='password', max_chars=24)

    if st.form_submit_button(text['savings_btn_open']):
        if st.session_state.savings_selected_term is None:
            st.error(text['savings_err_amount_min'])  # chưa chọn kỳ hạn
        elif amount < SAVINGS_MIN_AMOUNT:
            st.error(text['savings_err_amount_min'])
        elif amount > available_balance(stk):
            st.error(text['savings_err_insufficient'])
        elif pass_confirm == '' or login_check(stk, pass_confirm) != 2:
            st.error(text['savings_err_pass_wrong'])
        else:
            open_savings_deposit(stk, int(amount), st.session_state.savings_selected_term, auto_renew)
            st.session_state.savings_selected_term = None
            flash_success('savings_success_opened')
            st.rerun()

st.markdown('---')
st.markdown(f"**:violet[{text['savings_section_active']}]**")

_, savings_df = savings_init()
my_deposits = savings_df[(savings_df['Account_ID'] == stk) & (savings_df['Status'] == 'active')]

if my_deposits.empty:
    st.info(text['savings_no_active'])
else:
    for deposit_id, row in my_deposits.iterrows():
        with st.container(border=True):
            st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"{text['savings_lbl_principal']}: :green[{format(int(row['Principal']), ',')} VNĐ]")
                st.write(f"{row['Term_Months']} tháng - {row['Annual_Rate']*100:.2f}%/năm")
            with c2:
                st.write(f"{text['savings_lbl_start_date']}: {row['Start_Date']}")
                st.write(f"{text['savings_lbl_maturity_date']}: {row['Maturity_Date']}")
                new_auto_renew = st.checkbox(text['savings_lbl_auto_renew'], value=bool(row['Auto_Renew']),
                                            key=f"auto_renew_{deposit_id}")
                if new_auto_renew != bool(row['Auto_Renew']):
                    toggle_savings_auto_renew(deposit_id, new_auto_renew)
                    st.rerun()
            with c3:
                show_confirm_key = f"show_confirm_withdraw_{deposit_id}"
                if st.button(text['savings_btn_early_withdraw'], key=f"btn_withdraw_{deposit_id}"):
                    st.session_state[show_confirm_key] = True
                if st.session_state.get(show_confirm_key):
                    st.warning(text['savings_warning_early_withdraw'])
                    pass_early = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                                max_chars=24, key=f"pass_input_withdraw_{deposit_id}")
                    if st.button(f"**:green[{text['common_confirm']} ✓]**", key=f"btn_confirm_withdraw_{deposit_id}"):
                        if pass_early == '' or login_check(stk, pass_early) != 2:
                            st.error(text['savings_err_pass_wrong'])
                        else:
                            principal, forced_paydown = withdraw_savings_early(stk, deposit_id)
                            del st.session_state[show_confirm_key]
                            if forced_paydown > 0:
                                flash_success(text['savings_forced_paydown_notice'].format(format(forced_paydown, ',')), is_key=False)
                            else:
                                flash_success('savings_success_early_withdrawn')
                            st.rerun()