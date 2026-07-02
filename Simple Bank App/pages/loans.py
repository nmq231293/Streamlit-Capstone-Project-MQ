import streamlit as st
from helpers import (available_balance, login_check, settle_matured_loans,
                    settle_monthly_interest, open_loan, repay_loan_early,
                    loans_init, get_loan_limit, get_total_active_loans,
                    get_monthly_interest_summary, pay_interest_now,
                    toggle_loan_auto_pay, is_account_locked,
                    get_current_loan_rate, calc_monthly_interest,
                    today_vn, get_interest_due_date, to_bool,
                    LOAN_MIN_AMOUNT, LOAN_BASE_RATE, LOAN_PREFERENTIAL_RATE,
                    LOAN_RATE_TIER_2, LOAN_RATE_TIER_3,
                    ON_TIME_FOR_TIER_2, ON_TIME_FOR_TIER_3,
                    RATE_TABLE, flash_success, show_flash_message)

if not st.session_state.login_state:
    st.switch_page('pages/home.py')

text = st.session_state.text
stk = st.session_state.acc_num

settle_matured_loans(stk)
settle_monthly_interest(stk)
show_flash_message()

if is_account_locked(stk):
    st.header(text['withdraw_title'].upper(), anchor=False)
    st.error(text['account_locked_notice'])
    st.stop()

st.header(text['withdraw_title'].upper(), anchor=False)

bal = available_balance(stk)
loan_limit = get_loan_limit(stk)
current_debt = get_total_active_loans(stk)
available_to_borrow = max(loan_limit - current_debt, 0)

st.write(f'{text["available_balance"]}: :green[{format(bal, ",")} VNĐ]')
st.write(f'{text["loan_lbl_current_limit"]}: :blue[{format(available_to_borrow, ",")} VNĐ] / {format(loan_limit, ",")} VNĐ')

# Monthly interest summary
summary = get_monthly_interest_summary(stk)
if summary:
    today = today_vn()
    due = summary['due_date']
    days_left = (due - today).days
    color = 'red' if days_left <= 3 else 'orange' if days_left <= 7 else 'blue'
    st.markdown(f":{color}[**{text['loan_monthly_interest']}: {format(summary['total'], ',')} VNĐ · {text['loan_interest_due_date']}: {due.strftime('%d/%m/%Y')}**]")
    show_pay_key = 'show_pay_interest_confirm'
    if not st.session_state.get(show_pay_key):
        if st.button(text['loan_pay_now'], icon='💳', key='btn_pay_interest'):
            st.session_state[show_pay_key] = True
            st.rerun()
    else:
        with st.form('form_pay_interest_confirm', clear_on_submit=True):
            st.warning(f"{text['loan_monthly_interest']}: **{format(summary['total'], ',')} VNĐ**")
            pass_interest = st.text_input(text['savings_lbl_pass_confirm'],
                                        type='password', max_chars=24)
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button(f"**:green[{text['common_confirm']} ✓]**"):
                    if pass_interest == '' or login_check(stk, pass_interest) != 2:
                        st.error(text['savings_err_pass_wrong'])
                    else:
                        success, total = pay_interest_now(stk)
                        del st.session_state[show_pay_key]
                        if success:
                            flash_success(
                                text['loan_interest_paid_success'].format(format(total, ',')),
                                is_key=False
                            )
                        else:
                            flash_success(text['loan_interest_insufficient'], is_key=False)
                        st.rerun()
            with c2:
                if st.form_submit_button(f"**:red[{text['common_cancel']}]**"):
                    del st.session_state[show_pay_key]
                    st.rerun()

st.markdown(f"**:violet[{text['loan_section_open']}]**")

# Term buttons
term_options = list(RATE_TABLE.keys())
if 'loan_selected_term' not in st.session_state:
    st.session_state.loan_selected_term = None

st.write(f"**{text['loan_lbl_term']}**")
cols = st.columns(len(term_options))
for idx, term in enumerate(term_options):
    with cols[idx]:
        is_sel = st.session_state.loan_selected_term == term
        unit = text['common_month_unit']
        label = f":green[**{term} {unit}**]" if is_sel else f"{term} {unit}"
        if st.button(label, key=f"loan_term_{term}"):
            st.session_state.loan_selected_term = term
            st.rerun()

with st.form('form_open_loan', clear_on_submit=True):
    amount = st.number_input(text['loan_lbl_amount'], min_value=LOAN_MIN_AMOUNT,
                            max_value=max(available_to_borrow, LOAN_MIN_AMOUNT),
                            step=100000, format='%d')
    # Preview rate
    if amount >= LOAN_MIN_AMOUNT:
        preview_rate, is_pref = get_current_loan_rate(stk, amount, current_debt)
        if is_pref:
            st.success(text['loan_rate_preferential'])
        else:
            st.info(text['loan_rate_base'])

    pass_confirm = st.text_input(text['savings_lbl_pass_confirm'], type='password', max_chars=24)

    if st.form_submit_button(text['loan_btn_open']):
        if st.session_state.loan_selected_term is None:
            st.error(text['loan_err_no_term'])
        elif amount < LOAN_MIN_AMOUNT or amount > available_to_borrow:
            st.error(text['loan_err_limit_exceeded'])
        elif pass_confirm == '' or login_check(stk, pass_confirm) != 2:
            st.error(text['savings_err_pass_wrong'])
        else:
            try:
                loan_id, _ = open_loan(stk, int(amount), st.session_state.loan_selected_term)
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
                rate_pct = float(row['Current_Rate']) * 100
                st.write(f"{text['loan_lbl_principal']}: :red[**{format(int(row['Principal']), ',')} VNĐ**]")
                st.write(f"{row['Term_Months']} {text['common_month_unit']} · {rate_pct:.1f}%{text['common_per_year']}")
                on_time = int(row['On_Time_Payments'])
                rate = float(row['Current_Rate'])
                if rate == LOAN_PREFERENTIAL_RATE:
                    st.caption(f"🌟 {text['loan_rate_promotion']}")
                elif rate <= LOAN_RATE_TIER_3:
                    st.caption(text['loan_rate_tier3_reached'])
                elif rate <= LOAN_RATE_TIER_2:
                    st.caption(text['loan_rate_tier3_hint'].format(ON_TIME_FOR_TIER_3 - on_time))
                else:
                    st.caption(text['loan_rate_tier2_hint'].format(ON_TIME_FOR_TIER_2 - on_time))
                st.caption(f"{text['loan_lbl_monthly_interest_short']}: {format(calc_monthly_interest(int(row['Principal']), rate), ',')} VNĐ")
            with c2:
                status_label = text['loan_lbl_status_overdue'] if row['Status'] == 'overdue' else text['loan_lbl_status_active']
                st.write(f"{text['common_status']}: {status_label}")
                st.write(f"{text['savings_lbl_maturity_date']}: {row['Maturity_Date']}")
                auto_pay = to_bool(row['Auto_Pay'])
                new_auto_pay = st.checkbox(text['loan_auto_pay'], value=auto_pay, key=f"ap_{loan_id}")
                if new_auto_pay != auto_pay:
                    toggle_loan_auto_pay(loan_id, new_auto_pay)
                    st.rerun()
            with c3:
                show_key = f"show_repay_{loan_id}"
                if not st.session_state.get(show_key):
                    if st.button(text['loan_btn_early_repay'], key=f"btn_repay_{loan_id}"):
                        st.session_state[show_key] = True
                        st.rerun()
                else:
                    pass_repay = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                                max_chars=24, key=f"pass_rp_{loan_id}")
                    if st.button(f"**:green[{text['common_confirm']} ✓]**", key=f"btn_cfm_rp_{loan_id}"):
                        if pass_repay == '' or login_check(stk, pass_repay) != 2:
                            st.error(text['savings_err_pass_wrong'])
                        else:
                            try:
                                repay_loan_early(stk, loan_id)
                                del st.session_state[show_key]
                                flash_success('loan_success_repaid')
                                st.rerun()
                            except ValueError:
                                st.error(text['loan_err_insufficient_repay'])