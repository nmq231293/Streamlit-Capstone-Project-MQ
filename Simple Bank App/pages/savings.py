import streamlit as st
from helpers import (available_balance, login_check, settle_matured_savings,
                    open_savings_deposit, withdraw_savings_early,
                    partial_withdraw_savings, withdraw_all_savings,
                    toggle_savings_auto_renew, get_forced_paydown_info,
                    savings_init, SAVINGS_MIN_AMOUNT, RATE_TABLE, to_bool,
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
        unit   = text['common_month_unit']
        label  = f":green[**{term} {unit}**]" if is_sel else f"{term} {unit}"
        if st.button(label, key=f"sav_term_{term}"):
            st.session_state.savings_selected_term = term
            st.rerun()

if st.session_state.savings_selected_term:
    rate = RATE_TABLE[st.session_state.savings_selected_term]['savings']
    st.info(f"{text['common_rate_label']}: **{rate*100:.2f}%{text['common_per_year']}**")

with st.form('form_open_savings', clear_on_submit=True):
    amount = st.number_input(text['savings_lbl_amount'], min_value=SAVINGS_MIN_AMOUNT,
                            step=100000, format='%d')
    auto_renew   = st.checkbox(text['savings_lbl_auto_renew'], value=False)
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
            open_savings_deposit(stk, int(amount),
                                st.session_state.savings_selected_term, auto_renew)
            st.session_state.savings_selected_term = None
            flash_success('savings_success_opened')
            st.rerun()

st.markdown('---')

# ==============================================================================
# SỔ TIẾT KIỆM ĐANG HOẠT ĐỘNG
# ==============================================================================
_, savings_df = savings_init()
my_deposits = savings_df[(savings_df['Account_ID'] == stk) & (savings_df['Status'] == 'active')]

hc1, hc2 = st.columns([3, 1])
with hc1:
    st.markdown(f"**:violet[{text['savings_section_active']}]**")
with hc2:
    if not my_deposits.empty:
        if st.button(text['savings_btn_withdraw_all_deposits'], key='btn_withdraw_all'):
            st.session_state['confirm_withdraw_all'] = True
            st.rerun()

if st.session_state.get('confirm_withdraw_all'):
    st.warning(text['savings_confirm_withdraw_all'])
    wa1, wa2 = st.columns(2)
    with wa1:
        pass_all = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                max_chars=24, key='pass_withdraw_all')
        if st.button(f"**:green[{text['common_confirm']} ✓]**", key='btn_cfm_withdraw_all'):
            if pass_all == '' or login_check(stk, pass_all) != 2:
                st.error(text['savings_err_pass_wrong'])
            else:
                total_p, total_fp = withdraw_all_savings(stk)
                del st.session_state['confirm_withdraw_all']
                if total_fp > 0:
                    flash_success(text['savings_forced_paydown_notice'].format(
                        format(total_fp, ',')), is_key=False)
                else:
                    flash_success('savings_success_early_withdrawn')
                st.rerun()
    with wa2:
        if st.button(f"**:red[{text['common_cancel']}]**", key='btn_cancel_withdraw_all'):
            del st.session_state['confirm_withdraw_all']
            st.rerun()

if my_deposits.empty:
    st.info(text['savings_no_active'])
else:
    pending = st.session_state.get('_pending_withdraw')

    for deposit_id, row in my_deposits.iterrows():
        with st.container(border=True):
            st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)

            with c1:
                st.write(f"{text['savings_lbl_principal']}: "
                        f":green[**{format(int(row['Principal']), ',')} VNĐ**]")
                st.write(f"{row['Term_Months']} {text['common_month_unit']} "
                        f"· {float(row['Annual_Rate'])*100:.2f}%{text['common_per_year']}")

            with c2:
                st.write(f"{text['savings_lbl_start_date']}: {row['Start_Date']}")
                st.write(f"{text['savings_lbl_maturity_date']}: {row['Maturity_Date']}")
                cur_ar = to_bool(row['Auto_Renew'])
                new_ar = st.checkbox(text['savings_lbl_auto_renew'], value=cur_ar,
                                    key=f"ar_{deposit_id}")
                if new_ar != cur_ar:
                    toggle_savings_auto_renew(deposit_id, new_ar)
                    st.rerun()

            with c3:
                show_key        = f"show_wd_{deposit_id}"
                show_partial_key= f"show_partial_{deposit_id}"

                # Ẩn nút khi đang xử lý pending paydown hoặc đang mở form khác
                if not pending and not st.session_state.get(show_key) \
                                and not st.session_state.get(show_partial_key):
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(text['savings_btn_withdraw_full'],
                                    key=f"btn_full_{deposit_id}"):
                            info = get_forced_paydown_info(stk, deposit_id)
                            if info['needs_paydown']:
                                st.session_state['_pending_withdraw'] = {
                                    'deposit_id': deposit_id, 'info': info,
                                    'mode': 'full'
                                }
                            else:
                                st.session_state[show_key] = True
                            st.rerun()
                    with btn_col2:
                        if st.button(text['savings_btn_withdraw_partial'],
                                    key=f"btn_partial_{deposit_id}"):
                            st.session_state[show_partial_key] = True
                            st.rerun()

                # Form rút hết
                if st.session_state.get(show_key):
                    st.warning(text['savings_warning_early_withdraw'])
                    pass_wd = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                            max_chars=24, key=f"pass_wd_{deposit_id}")
                    btn_cfm, btn_cancel = st.columns(2)
                    with btn_cfm:
                        if st.button(f"**:green[{text['common_confirm']} ✓]**",
                                    key=f"btn_cfm_wd_{deposit_id}"):
                            if pass_wd == '' or login_check(stk, pass_wd) != 2:
                                st.error(text['savings_err_pass_wrong'])
                            else:
                                p, fp = withdraw_savings_early(stk, deposit_id)
                                del st.session_state[show_key]
                                if fp > 0:
                                    flash_success(text['savings_forced_paydown_notice'].format(
                                        format(fp, ',')), is_key=False)
                                else:
                                    flash_success('savings_success_early_withdrawn')
                                st.rerun()
                    with btn_cancel:
                        if st.button(f"**:red[{text['common_cancel']}]**",
                                    key=f"btn_cancel_wd_{deposit_id}"):
                            del st.session_state[show_key]
                            st.rerun()

                # Form rút một phần
                if st.session_state.get(show_partial_key):
                    max_partial = int(row['Principal']) - 1
                    with st.form(f"form_partial_{deposit_id}"):
                        partial_amt = st.number_input(
                            text['savings_lbl_partial_amount'],
                            min_value=1, max_value=max_partial,
                            step=100000, format='%d',
                            key=f"partial_amt_{deposit_id}"
                        )
                        pass_partial = st.text_input(
                            text['savings_lbl_pass_confirm'], type='password',
                            max_chars=24, key=f"pass_partial_{deposit_id}"
                        )
                        pfc1, pfc2 = st.columns(2)
                        with pfc1:
                            if st.form_submit_button(f"**:green[{text['common_confirm']} ✓]**"):
                                if pass_partial == '' or login_check(stk, pass_partial) != 2:
                                    st.error(text['savings_err_pass_wrong'])
                                elif partial_amt <= 0 or partial_amt >= int(row['Principal']):
                                    st.error(text['savings_err_partial_invalid'])
                                else:
                                    try:
                                        amt, fp = partial_withdraw_savings(
                                            stk, deposit_id, int(partial_amt))
                                        del st.session_state[show_partial_key]
                                        if fp > 0:
                                            flash_success(
                                                text['savings_forced_paydown_notice'].format(
                                                    format(fp, ',')), is_key=False)
                                        else:
                                            flash_success('savings_success_early_withdrawn')
                                        st.rerun()
                                    except ValueError:
                                        st.error(text['savings_err_partial_invalid'])
                        with pfc2:
                            if st.form_submit_button(f"**:red[{text['common_cancel']}]**"):
                                del st.session_state[show_partial_key]
                                st.rerun()

    # ==============================================================================
    # FORCED PAYDOWN DIALOG
    # ==============================================================================
    if pending:
        deposit_id = pending['deposit_id']
        info       = pending['info']
        st.markdown('---')
        st.warning(text['loan_paydown_needed'])
        st.write(text['loan_paydown_total_needed'].format(format(info['excess_debt'], ',')))

        mode = st.radio('', [text['loan_paydown_auto'], text['loan_paydown_manual']],
                        key='paydown_mode')
        loans_to_paydown = {}

        if mode == text['loan_paydown_auto']:
            # Lãi cao nhất trước, ưu đãi cuối cùng
            sorted_loans = sorted(info['loans'],
                                key=lambda x: x['rate'], reverse=True)
            remaining = info['excess_debt']
            for loan in sorted_loans:
                if remaining <= 0:
                    break
                pay = min(remaining, loan['principal'])
                loans_to_paydown[loan['loan_id']] = pay
                remaining -= pay
            for loan in sorted_loans:
                if loan['loan_id'] in loans_to_paydown:
                    amt = loans_to_paydown[loan['loan_id']]
                    st.caption(text['loan_paydown_caption'].format(
                        format(loan['principal'], ','), loan['start'], format(amt, ',')
                    ))
        else:
            total_sel = 0
            for loan in info['loans']:
                ca, cb = st.columns([3, 2])
                with ca:
                    rate_pct = loan['rate'] * 100
                    st.write(f"{format(loan['principal'], ',')} VNĐ · "
                            f"{rate_pct:.1f}%{text['common_per_year']} · {loan['maturity']}")
                with cb:
                    sel = st.number_input(
                        text['loan_paydown_manual_label'],
                        min_value=0, max_value=loan['principal'],
                        step=100000, format='%d', key=f"pd_{loan['loan_id']}"
                    )
                    if sel > 0:
                        loans_to_paydown[loan['loan_id']] = sel
                        total_sel += sel
            if total_sel < info['excess_debt']:
                st.warning(text['loan_paydown_insufficient'].format(
                    format(total_sel, ','), format(info['excess_debt'], ',')
                ))

        pass_pd = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                max_chars=24, key='pass_paydown')
        pa, pb = st.columns(2)
        with pa:
            if st.button(f"**:green[{text['loan_paydown_confirm']} ✓]**",
                        key='btn_cfm_pd'):
                total_sel_final = sum(loans_to_paydown.values())
                if (mode == text['loan_paydown_manual'] and
                        total_sel_final < info['excess_debt']):
                    st.error(text['loan_paydown_insufficient'].format(
                        format(total_sel_final, ','), format(info['excess_debt'], ',')
                    ))
                elif pass_pd == '' or login_check(stk, pass_pd) != 2:
                    st.error(text['savings_err_pass_wrong'])
                else:
                    manual = loans_to_paydown if mode == text['loan_paydown_manual'] else None
                    p, fp = withdraw_savings_early(stk, deposit_id, manual)
                    del st.session_state['_pending_withdraw']
                    flash_success(text['savings_forced_paydown_notice'].format(
                        format(fp, ',')), is_key=False)
                    st.rerun()
        with pb:
            if st.button(f"**:red[{text['common_cancel']}]**", key='btn_cancel_pd'):
                del st.session_state['_pending_withdraw']
                st.rerun()