import streamlit as st
from gspread.exceptions import APIError
from helpers import (available_balance, login_check, settle_matured_loans,
                    settle_monthly_interest, open_loan, open_split_loan,
                    repay_loan_early, partial_repay_loan, repay_all_loans,
                    pay_loan_interest, loans_init, get_loan_limit,
                    get_total_active_loans, get_monthly_interest_summary,
                    pay_interest_now, toggle_loan_auto_pay, is_account_locked,
                    get_current_loan_rate, check_loan_split,
                    calc_monthly_interest, today_vn, get_interest_due_date,
                    to_bool, is_interest_paid_this_month, is_all_interest_paid_this_month,
                    LOAN_MIN_AMOUNT, LOAN_RATE_TABLE,
                    LOAN_PREFERENTIAL_RATE, LOAN_RATE_FLOOR, LOAN_PENALTY_RATE,
                    ON_TIME_FOR_TIER_2, ON_TIME_FOR_TIER_3,
                    LOAN_TIER2_REDUCTION, LOAN_TIER3_REDUCTION,
                    flash_success, show_flash_message,
                    OptimisticLockError, TransactionFailedError, run_safely)

if not st.session_state.login_state:
    st.switch_page('pages/home.py')

text = st.session_state.text
stk = st.session_state.acc_num

ok1, _ = run_safely(settle_matured_loans, stk)
ok2, _ = run_safely(settle_monthly_interest, stk)
show_flash_message()
if not (ok1 and ok2):
    st.info(text['sys_err_quota_settle'])

if is_account_locked(stk):
    st.header(text['withdraw_title'].upper(), anchor=False)
    st.error(text['account_locked_notice'])
    st.stop()

st.header(text['withdraw_title'].upper(), anchor=False)

# --- Trạng thái khóa: khi có BẤT KỲ thao tác trả nợ/vay/trả lãi nào đang diễn ra thì khóa
#     TẤT CẢ nút khác (khoản vay khác, mở vay mới, trả tất cả...) để tránh chồng chéo. ---
def _any_loan_form_open():
    for key in list(st.session_state.keys()):
        if isinstance(key, str) and (
            key.startswith('show_repay_full_') or
            key.startswith('show_repay_partial_') or
            key.startswith('show_repay_min_')
        ) and st.session_state.get(key):
            return True
    return False

loans_locked = bool(
    st.session_state.get('confirm_repay_all') or
    st.session_state.get('show_pay_interest_confirm') or
    st.session_state.get('loan_split_pending') or
    _any_loan_form_open()
)

bal = available_balance(stk)
loan_limit     = get_loan_limit(stk)
current_debt   = get_total_active_loans(stk)
available_borrow = max(loan_limit - current_debt, 0)

st.write(f'{text["available_balance"]}: :green[{format(bal, ",")} VNĐ]')
st.write(f'{text["loan_lbl_current_limit"]}: '
        f':blue[{format(available_borrow, ",")} VNĐ] / {format(loan_limit, ",")} VNĐ')

# Monthly interest summary + Pay now
summary = get_monthly_interest_summary(stk)
if summary:
    today = today_vn()
    due   = summary['due_date']
    days_left = (due - today).days
    color = 'red' if days_left <= 3 else ('orange' if days_left <= 7 else 'blue')
    st.markdown(
        f":{color}[**{text['loan_monthly_interest']}: "
        f"{format(summary['total'], ',')} VNĐ · "
        f"{text['loan_interest_due_date']}: {due.strftime('%d/%m/%Y')}**]"
    )

    if summary['all_paid']:
        st.success(text['loan_interest_already_paid'])
    else:
        show_pay_key = 'show_pay_interest_confirm'
        if st.session_state.get(show_pay_key):
            with st.form('form_pay_interest_confirm', clear_on_submit=True):
                st.warning(f"{text['loan_monthly_interest']}: "
                        f"**{format(summary['total'], ',')} VNĐ**")
                pass_interest = st.text_input(text['savings_lbl_pass_confirm'],
                                            type='password', max_chars=24)
                pi1, pi2 = st.columns(2)
                with pi1:
                    if st.form_submit_button(f"**:green[{text['common_confirm']}]**"):
                        if pass_interest == '' or login_check(stk, pass_interest) != 2:
                            st.error(text['savings_err_pass_wrong'])
                        else:
                            try:
                                ok, total = pay_interest_now(stk)
                                del st.session_state[show_pay_key]
                                flash_success(
                                    text['loan_interest_paid_success'].format(format(total, ',')),
                                    is_key=False
                                ) if ok else flash_success(text['loan_interest_insufficient'], is_key=False)
                                st.rerun()
                            except (APIError, OptimisticLockError):
                                st.error(text['sys_err_quota'])
                with pi2:
                    if st.form_submit_button(f"**:red[{text['common_cancel']}]**"):
                        del st.session_state[show_pay_key]
                        st.rerun()
        elif not loans_locked:
            if st.button(text['loan_pay_now'], icon='💳', key='btn_pay_interest'):
                st.session_state[show_pay_key] = True
                st.rerun()

# Rate info dialog
@st.dialog(f"📋 :red[Loan Rate Policy / Chính Sách Lãi Suất]", width='large')
def loan_rate_info_dialog():
    d = st.session_state.text

    st.markdown(f"**:violet[{d['loan_rate_info_base']}]**")
    for term, rate in LOAN_RATE_TABLE.items():
        st.markdown(f"- {term} {d['common_month_unit']}: "
                    f"**{rate*100:.1f}%{d['common_per_year']}**")

    st.divider()
    st.markdown(f"**:violet[{d['loan_rate_info_tiers_header']}]**:")
    st.markdown(f"- {d['loan_rate_info_tiers_1']}")
    st.markdown(f"- {d['loan_rate_info_tiers_2']}")
    st.markdown(f"- {d['loan_rate_info_tiers_3']}")

    st.divider()
    st.markdown(f"**:violet[{d['loan_rate_info_penalty_header']}]**")
    st.markdown(f"- {d['loan_rate_info_penalty_1']}")
    st.markdown(f"- {d['loan_rate_info_penalty_2']}")
    st.markdown(f"- {d['loan_rate_info_penalty_3']}")

    st.divider()
    st.markdown(f"**:violet[{d['loan_rate_info_overdue_header']}]**")
    st.markdown(f"- {d['loan_rate_info_overdue_1']}")
    st.markdown(f"- {d['loan_rate_info_overdue_2']}")
    st.markdown(f"- {d['loan_rate_info_overdue_3']}")

if st.button(f"**:orange[{text['loan_rate_info_btn']}]**", key='btn_rate_info'):
    loan_rate_info_dialog()

st.markdown(f"**:violet[{text['loan_section_open']}]**")

# Term selection
term_options = list(LOAN_RATE_TABLE.keys())
if 'loan_selected_term' not in st.session_state:
    st.session_state.loan_selected_term = None

st.write(f"**{text['loan_lbl_term']}**")
cols = st.columns(len(term_options))
for idx, term in enumerate(term_options):
    with cols[idx]:
        is_sel = st.session_state.loan_selected_term == term
        unit   = text['common_month_unit']
        label  = f":green[**{term} {unit}**]" if is_sel else f"{term} {unit}"
        if st.button(label, key=f"loan_term_{term}", disabled=loans_locked):
            st.session_state.loan_selected_term = term
            st.rerun()

# Pending split confirmation (after password already verified)
if st.session_state.get('loan_split_pending'):
    sp = st.session_state.loan_split_pending
    st.warning(text['loan_split_notice'])
    st.write(text['loan_split_pref_part'].format(
        format(sp['pref_amount'], ','), sp['pref_rate'] * 100))
    st.write(text['loan_split_standard_part'].format(
        format(sp['standard_amount'], ','), f"{sp['standard_rate']*100:.1f}"))
    sa, sb, sc = st.columns(3)
    with sa:
        if st.button(f"**:green[{text['loan_split_confirm']}]**", key='btn_confirm_split'):
            try:
                open_split_loan(stk, sp['pref_amount'], sp['standard_amount'],
                                sp['term_months'])
                del st.session_state['loan_split_pending']
                st.session_state.loan_selected_term = None
                flash_success('loan_success_opened')
                st.rerun()
            except ValueError:
                st.error(text['loan_err_limit_exceeded'])
            except TransactionFailedError as e:
                st.error(text['tx_failed_recovered'] if e.recovered else text['tx_failed_unrecovered'])
            except (APIError, OptimisticLockError):
                st.error(text['sys_err_quota'])
    with sb:
        if st.button(text['loan_split_adjust'], key='btn_adjust_split'):
            del st.session_state['loan_split_pending']
            st.rerun()
    with sc:
        if st.button(f"**:red[{text['common_cancel']}]**", key='btn_cancel_split'):
            del st.session_state['loan_split_pending']
            st.rerun()
    st.info(text['loan_split_max_pref'].format(format(sp['max_pref_amount'], ',')))

else:
    # Loan form
    with st.form('form_open_loan', clear_on_submit=True):
        amount = st.number_input(
            text['loan_lbl_amount'],
            min_value=LOAN_MIN_AMOUNT,
            max_value=max(available_borrow, LOAN_MIN_AMOUNT),
            step=100000, format='%d'
        )
        if amount >= LOAN_MIN_AMOUNT and st.session_state.loan_selected_term:
            split_info = check_loan_split(stk, int(amount),
                                        st.session_state.loan_selected_term,
                                        current_debt)
            if split_info['fully_preferential']:
                st.success(text['loan_rate_preferential'])
            elif split_info['needs_split']:
                st.warning(text['loan_split_notice'])
                st.caption(text['loan_split_max_pref'].format(
                    format(split_info['max_pref_amount'], ',')))
            else:
                st.info(f"{text['common_rate_label']}: "
                        f"**{split_info['pref_rate']*100:.1f}%{text['common_per_year']}**")

        pass_confirm = st.text_input(text['savings_lbl_pass_confirm'],
                                    type='password', max_chars=24)

        if st.form_submit_button(text['loan_btn_open'], disabled=loans_locked):
            if st.session_state.loan_selected_term is None:
                st.error(text['loan_err_no_term'])
            elif amount < LOAN_MIN_AMOUNT or amount > available_borrow:
                st.error(text['loan_err_limit_exceeded'])
            elif pass_confirm == '' or login_check(stk, pass_confirm) != 2:
                st.error(text['savings_err_pass_wrong'])
            else:
                split_info = check_loan_split(stk, int(amount),
                                            st.session_state.loan_selected_term,
                                            current_debt)
                if split_info['needs_split']:
                    st.session_state['loan_split_pending'] = {
                        'pref_amount':    split_info['pref_amount'],
                        'standard_amount':split_info['standard_amount'],
                        'max_pref_amount':split_info['max_pref_amount'],
                        'pref_rate':      split_info['pref_rate'],
                        'standard_rate':  split_info['standard_rate'],
                        'term_months':    st.session_state.loan_selected_term,
                    }
                    st.rerun()
                else:
                    try:
                        open_loan(stk, int(amount), st.session_state.loan_selected_term)
                        st.session_state.loan_selected_term = None
                        flash_success('loan_success_opened')
                        st.rerun()
                    except ValueError:
                        st.error(text['loan_err_limit_exceeded'])
                    except TransactionFailedError as e:
                        st.error(text['tx_failed_recovered'] if e.recovered else text['tx_failed_unrecovered'])
                    except (APIError, OptimisticLockError):
                        st.error(text['sys_err_quota'])

st.markdown('---')

# ==============================================================================
# KHOẢN VAY ĐANG HOẠT ĐỘNG
# ==============================================================================
_, loans_df = loans_init()
my_loans = loans_df[
    (loans_df['Account_ID'] == stk) &
    (loans_df['Status'].isin(['active', 'overdue']))
]

lh1, lh2 = st.columns([3, 1])
with lh1:
    st.markdown(f"**:violet[{text['loan_section_active']}]**")
with lh2:
    if not my_loans.empty and not loans_locked:
        if st.button(text['loan_btn_repay_all_loans'], key='btn_repay_all'):
            st.session_state['confirm_repay_all'] = True
            st.rerun()

if st.session_state.get('confirm_repay_all'):
    st.warning(text['loan_confirm_repay_all'])
    pass_repay_all = st.text_input(text['savings_lbl_pass_confirm'], type='password',
                                max_chars=24, key='pass_repay_all')
    ra1, ra2 = st.columns(2)
    with ra1:
        if st.button(f"**:green[{text['common_confirm']}]**", key='btn_cfm_repay_all'):
            if pass_repay_all == '' or login_check(stk, pass_repay_all) != 2:
                st.error(text['savings_err_pass_wrong'])
            else:
                try:
                    cnt_ok, total, cnt_fail, had_critical = repay_all_loans(stk)
                    del st.session_state['confirm_repay_all']
                    msg = text['loan_repay_all_result'].format(cnt_ok, format(total, ','), cnt_fail)
                    if had_critical:
                        msg += ' ' + text['tx_failed_unrecovered']
                    flash_success(msg, is_key=False)
                    st.rerun()
                except (APIError, OptimisticLockError):
                    st.error(text['sys_err_quota'])
    with ra2:
        if st.button(f"**:red[{text['common_cancel']}]**", key='btn_cancel_repay_all'):
            del st.session_state['confirm_repay_all']
            st.rerun()

if my_loans.empty:
    st.info(text['loan_no_active'])
else:
    if (my_loans['Status'] == 'overdue').any():
        st.warning(text['loan_notice_overdue'])

    for loan_id, row in my_loans.iterrows():
        with st.container(border=True):
            st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            rate = float(row['Current_Rate'])
            term = int(row['Term_Months'])
            principal = int(row['Principal'])
            is_overdue_loan = row['Status'] == 'overdue'
            is_pref = (rate == LOAN_PREFERENTIAL_RATE)
            on_time = int(row['On_Time_Payments'])
            base_rate = LOAN_RATE_TABLE.get(term, 0.10)

            with c1:
                color = 'orange' if is_overdue_loan else 'red'
                st.write(f"{text['loan_lbl_principal']}: "
                        f":{color}[**{format(principal, ',')} VNĐ**]")
                st.write(f"{term} {text['common_month_unit']} "
                        f"· {rate*100:.2f}%{text['common_per_year']}")
                if is_overdue_loan:
                    st.caption(f":red[{text['loan_penalty_notice']}]")
                elif is_pref:
                    st.caption("🌟 Ưu đãi 6%")
                elif rate <= base_rate - LOAN_TIER3_REDUCTION:
                    st.caption(text['loan_rate_tier3_reached'])
                elif rate <= base_rate - LOAN_TIER2_REDUCTION:
                    remain = ON_TIME_FOR_TIER_3 - on_time
                    st.caption(text['loan_rate_tier3_hint'].format(remain))
                else:
                    remain = ON_TIME_FOR_TIER_2 - on_time
                    st.caption(text['loan_rate_tier2_hint'].format(remain))
                monthly = calc_monthly_interest(principal, rate)
                st.caption(f"{text['loan_lbl_monthly_interest_short']}: "
                        f"{format(monthly, ',')} VNĐ")

            with c2:
                status_label = (text['loan_lbl_status_overdue'] if is_overdue_loan
                                else text['loan_lbl_status_active'])
                st.write(f"{text['common_status']}: {status_label}")
                st.write(f"{text['savings_lbl_maturity_date']}: {row['Maturity_Date']}")
                auto_pay = to_bool(row['Auto_Pay'])
                new_auto = st.checkbox(text['loan_auto_pay'], value=auto_pay,
                                    key=f"ap_{loan_id}", disabled=loans_locked)
                if new_auto != auto_pay and not loans_locked:
                    try:
                        toggle_loan_auto_pay(loan_id, new_auto)
                        st.rerun()
                    except (APIError, OptimisticLockError):
                        st.error(text['sys_err_quota'])

            with c3:
                show_full    = f"show_repay_full_{loan_id}"
                show_partial = f"show_repay_partial_{loan_id}"
                show_min     = f"show_repay_min_{loan_id}"

                if not loans_locked:
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button(text['loan_btn_repay_full'],
                                    key=f"btn_full_{loan_id}"):
                            st.session_state[show_full] = True
                            st.rerun()
                    with b2:
                        if st.button(text['loan_btn_repay_minimum'],
                                    key=f"btn_min_{loan_id}"):
                            st.session_state[show_min] = True
                            st.rerun()
                    with b3:
                        if st.button(text['loan_btn_repay_partial'],
                                    key=f"btn_partial_{loan_id}"):
                            st.session_state[show_partial] = True
                            st.rerun()

                # Form trả hết
                if st.session_state.get(show_full):
                    pass_f = st.text_input(text['savings_lbl_pass_confirm'],
                                            type='password', max_chars=24,
                                            key=f"pass_full_{loan_id}")
                    cf1, cf2 = st.columns(2)
                    with cf1:
                        if st.button(f"**:green[{text['common_confirm']}]**",
                                    key=f"btn_cfm_full_{loan_id}"):
                            if pass_f == '' or login_check(stk, pass_f) != 2:
                                st.error(text['savings_err_pass_wrong'])
                            else:
                                try:
                                    repay_loan_early(stk, loan_id)
                                    del st.session_state[show_full]
                                    flash_success('loan_success_repaid')
                                    st.rerun()
                                except ValueError as e:
                                    if str(e) == "LOAN_NOT_ACTIVE":
                                        st.error(text['loan_err_not_active'])
                                        del st.session_state[show_full]
                                        st.rerun()
                                    else:
                                        st.error(text['loan_err_insufficient_repay'])
                                except TransactionFailedError as e:
                                    st.error(text['tx_failed_recovered'] if e.recovered else text['tx_failed_unrecovered'])
                                    del st.session_state[show_full]
                                    st.rerun()
                                except (APIError, OptimisticLockError):
                                    st.error(text['sys_err_quota'])
                    with cf2:
                        if st.button(f"**:red[{text['common_cancel']}]**",
                                    key=f"btn_cancel_full_{loan_id}"):
                            del st.session_state[show_full]
                            st.rerun()

                # Form trả tối thiểu (lãi tháng)
                if st.session_state.get(show_min):
                    if summary and summary['per_loan_paid'].get(loan_id, False):
                        st.success(text['loan_interest_this_loan_paid'])
                        if st.button(f"**:red[{text['common_cancel']}]**",
                                    key=f"btn_cancel_min_{loan_id}"):
                            del st.session_state[show_min]
                            st.rerun()
                    else:
                        monthly = calc_monthly_interest(principal, rate)
                        st.info(f"{text['loan_minimum_interest_label']}: "
                                f"**{format(monthly, ',')} VNĐ**")
                        st.caption(text['loan_minimum_interest_hint'])
                        pass_m = st.text_input(text['savings_lbl_pass_confirm'],
                                                type='password', max_chars=24,
                                                key=f"pass_min_{loan_id}")
                        cm1, cm2 = st.columns(2)
                        with cm1:
                            if st.button(f"**:green[{text['common_confirm']}]**",
                                        key=f"btn_cfm_min_{loan_id}"):
                                if pass_m == '' or login_check(stk, pass_m) != 2:
                                    st.error(text['savings_err_pass_wrong'])
                                else:
                                    try:
                                        ok, paid, already = pay_loan_interest(stk, loan_id)
                                        del st.session_state[show_min]
                                        if already:
                                            flash_success(text['loan_interest_this_loan_paid'], is_key=False)
                                        elif ok:
                                            flash_success(
                                                text['loan_interest_paid_success'].format(format(paid, ',')),
                                                is_key=False)
                                        else:
                                            flash_success(text['loan_interest_insufficient'], is_key=False)
                                        st.rerun()
                                    except (APIError, OptimisticLockError):
                                        st.error(text['sys_err_quota'])
                        with cm2:
                            if st.button(f"**:red[{text['common_cancel']}]**",
                                        key=f"btn_cancel_min_{loan_id}"):
                                del st.session_state[show_min]
                                st.rerun()

                # Form trả một phần
                if st.session_state.get(show_partial):
                    with st.form(f"form_partial_loan_{loan_id}"):
                        partial_p = st.number_input(
                            text['loan_lbl_partial_principal'],
                            min_value=1, max_value=principal - 1,
                            step=100000, format='%d',
                            key=f"partial_loan_amt_{loan_id}"
                        )
                        pass_p = st.text_input(
                            text['savings_lbl_pass_confirm'],
                            type='password', max_chars=24,
                            key=f"pass_partial_loan_{loan_id}"
                        )
                        pp1, pp2 = st.columns(2)
                        with pp1:
                            if st.form_submit_button(
                                    f"**:green[{text['common_confirm']}]**"):
                                if pass_p == '' or login_check(stk, pass_p) != 2:
                                    st.error(text['savings_err_pass_wrong'])
                                elif partial_p <= 0 or partial_p >= principal:
                                    st.error(text['loan_err_partial_invalid'])
                                else:
                                    try:
                                        paid = partial_repay_loan(
                                            stk, loan_id, int(partial_p))
                                        del st.session_state[show_partial]
                                        flash_success(
                                            text['loan_interest_paid_success'].format(
                                                format(paid, ',')), is_key=False)
                                        st.rerun()
                                    except ValueError as e:
                                        err = str(e)
                                        if err == 'LOAN_NOT_ACTIVE':
                                            st.error(text['loan_err_not_active'])
                                            del st.session_state[show_partial]
                                            st.rerun()
                                        elif 'INSUFFICIENT' in err:
                                            st.error(text['loan_err_insufficient_repay'])
                                        else:
                                            st.error(text['loan_err_partial_invalid'])
                                    except TransactionFailedError as e:
                                        st.error(text['tx_failed_recovered'] if e.recovered else text['tx_failed_unrecovered'])
                                        del st.session_state[show_partial]
                                        st.rerun()
                                    except (APIError, OptimisticLockError):
                                        st.error(text['sys_err_quota'])
                        with pp2:
                            if st.form_submit_button(
                                    f"**:red[{text['common_cancel']}]**"):
                                del st.session_state[show_partial]
                                st.rerun()