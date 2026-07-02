import streamlit as st
from helpers import (available_balance, login_check, settle_matured_savings,
                    open_savings_deposit, renew_savings_deposit,
                    withdraw_savings_early, toggle_savings_auto_renew,
                    get_forced_paydown_info, savings_init,
                    SAVINGS_MIN_AMOUNT, RATE_TABLE, to_bool,
                    flash_success, show_flash_message)

if not st.session_state.login_state:
    st.switch_page('pages/home.py')

text = st.session_state.text
stk = st.session_state.acc_num

settle_matured_savings(stk)
show_flash_message()

st.header(text["deposit_title"].upper(), anchor=False)
st.write(f'{text["available_balance"]}: :green[{format(available_balance(stk), ",")} VNĐ]')

# ==============================================================================
# MỞ SỔ TIẾT KIỆM MỚI
# ==============================================================================
st.markdown(f"**:violet[{text['savings_section_open']}]**")

term_options = list(RATE_TABLE.keys())
if 'savings_selected_term' not in st.session_state:
    st.session_state.savings_selected_term = None

st.write(f"**{text['savings_lbl_term']}**")
cols = st.columns(len(term_options))
for idx, term in enumerate(term_options):
    with cols[idx]:
        is_sel = st.session_state.savings_selected_term == term
        unit = text['common_month_unit']
        label = f":green[**{term} {unit}**]" if is_sel else f"{term} {unit}"
        if st.button(label, key=f"sav_term_{term}"):
            st.session_state.savings_selected_term = term
            st.rerun()

if st.session_state.savings_selected_term:
    rate = RATE_TABLE[st.session_state.savings_selected_term]['savings']
    st.info(f"Lãi suất: **{rate*100:.2f}%{text['common_per_year']}**")

with st.form('form_open_savings', clear_on_submit=True):
    amount = st.number_input(text['savings_lbl_amount'], min_value=SAVINGS_MIN_AMOUNT,
                            step=100000, format='%d')
    auto_renew = st.checkbox(text['savings_lbl_auto_renew'], value=False)
    pass_confirm = st.text_input(text['savings_lbl_pass_confirm'], type='password', max_chars=24)

    if st.form_submit_button(text['savings_btn_open']):
        if st.session_state.savings_selected_term is None:
            st.error(text['savings_err_no_term'])
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

# ==============================================================================
# SỔ TIẾT KIỆM ĐANG HOẠT ĐỘNG
# ==============================================================================
st.markdown(f"**:violet[{text['savings_section_active']}]**")

_, savings_df = savings_init()
my_deposits = savings_df[(savings_df['Account_ID'] == stk) & (savings_df['Status'] == 'active')]

if my_deposits.empty:
    st.info(text['savings_no_active'])
else:
    pending = st.session_state.get('_pending_withdraw')

    for deposit_id, row in my_deposits.iterrows():
        with st.container(border=True):
            st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"{text['savings_lbl_principal']}: :green[**{format(int(row['Principal']), ',')} VNĐ**]")
                st.write(f"{row['Term_Months']} {text['common_month_unit']} · {float(row['Annual_Rate'])*100:.2f}%{text['common_per_year']}")
            with c2:
                st.write(f"{text['savings_lbl_start_date']}: {row['Start_Date']}")
                st.write(f"{text['savings_lbl_maturity_date']}: {row['Maturity_Date']}")
                cur_ar = to_bool(row['Auto_Renew'])
                new_ar = st.checkbox(text['savings_lbl_auto_renew'], value=cur_ar, key=f"ar_{deposit_id}")
                if new_ar != cur_ar:
                    toggle_savings_auto_renew(deposit_id, new_ar)
                    st.rerun()
            with c3:
                show_key = f"show_wd_{deposit_id}"
                if not pending and not st.session_state.get(show_key):
                    if st.button(text['savings_btn_early_withdraw'], key=f"btn_wd_{deposit_id}"):
                        info = get_forced_paydown_info(stk, deposit_id)
                        if info['needs_paydown']:
                            st.session_state['_pending_withdraw'] = {
                                'deposit_id': deposit_id, 'info': info
                            }
                        else:
                            st.session_state[show_key] = True
                        st.rerun()
                if st.session_state.get(show_key):
                    st.warning(text['savings_warning_early_withdraw'])
                    pass_wd = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                            max_chars=24, key=f"pass_wd_{deposit_id}")
                    if st.button(f"**:green[{text['common_confirm']} ✓]**", key=f"btn_cfm_wd_{deposit_id}"):
                        if pass_wd == '' or login_check(stk, pass_wd) != 2:
                            st.error(text['savings_err_pass_wrong'])
                        else:
                            principal, paid = withdraw_savings_early(stk, deposit_id)
                            del st.session_state[show_key]
                            if paid > 0:
                                flash_success(text['savings_forced_paydown_notice'].format(format(paid, ',')), is_key=False)
                            else:
                                flash_success('savings_success_early_withdrawn')
                            st.rerun()

    # ==============================================================================
    # FORCED PAYDOWN SELECTION
    # ==============================================================================
    if pending:
        deposit_id = pending['deposit_id']
        info = pending['info']
        st.markdown('---')
        st.warning(text['loan_paydown_needed'])
        st.write(text['loan_paydown_total_needed'].format(format(info['excess_debt'], ',')))

        mode = st.radio('', [text['loan_paydown_auto'], text['loan_paydown_manual']],
                        key='paydown_mode')
        loans_to_paydown = {}

        if mode == text['loan_paydown_auto']:
            remaining = info['excess_debt']
            for loan in info['loans']:
                if remaining <= 0:
                    break
                pay = min(remaining, loan['principal'])
                loans_to_paydown[loan['loan_id']] = pay
                remaining -= pay
            for loan in info['loans']:
                if loan['loan_id'] in loans_to_paydown:
                    amt = loans_to_paydown[loan['loan_id']]
                    st.caption(text['loan_paydown_caption'].format(format(loan['principal'], ','), loan['start'], format(amt, ',')))
        else:
            total_sel = 0
            for loan in info['loans']:
                ca, cb = st.columns([3, 2])
                with ca:
                    st.write(f"Vay {format(loan['principal'], ',')} VNĐ · {loan['term']} tháng · đến {loan['maturity']}")
                with cb:
                    sel = st.number_input(text['loan_paydown_manual_label'], min_value=0, max_value=loan['principal'],
                                        step=100000, format='%d', key=f"pd_{loan['loan_id']}")
                    if sel > 0:
                        loans_to_paydown[loan['loan_id']] = sel
                        total_sel += sel
            if total_sel < info['excess_debt']:
                st.warning(text['loan_paydown_insufficient'].format(format(total_sel, ','), format(info['excess_debt'], ',')))

        pass_pd = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                max_chars=24, key='pass_paydown')
        ca, cb = st.columns(2)
        with ca:
            if st.button(f"**:green[{text['loan_paydown_confirm']} ✓]**", key='btn_cfm_pd'):
                total_sel_final = sum(loans_to_paydown.values())
                if mode == text['loan_paydown_manual'] and total_sel_final < info['excess_debt']:
                    st.error(text['loan_paydown_insufficient'].format(
                        format(total_sel_final, ','), format(info['excess_debt'], ',')))
                elif pass_pd == '' or login_check(stk, pass_pd) != 2:
                    st.error(text['savings_err_pass_wrong'])
                else:
                    manual = loans_to_paydown if mode == text['loan_paydown_manual'] else None
                    principal, paid = withdraw_savings_early(stk, deposit_id, manual)
                    del st.session_state['_pending_withdraw']
                    flash_success(text['savings_forced_paydown_notice'].format(format(paid, ',')), is_key=False)
                    st.rerun()
        with cb:
            if st.button(f"**:red[{text['common_cancel']}]**", key='btn_cancel_pd'):
                del st.session_state['_pending_withdraw']
                st.rerun()