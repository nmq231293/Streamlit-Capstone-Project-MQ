import streamlit as st
import pandas as pd
import plotly.express as px
from helpers import (
    admin_get_system_stats, admin_get_user_summary,
    admin_lock_account, admin_unlock_account,
    admin_adjust_balance, admin_change_power_level,
    admin_soft_delete_account, admin_get_recent_transactions,
    admin_get_tx_timeline, savings_init, loans_init,
    to_bool, ALL_TX_TYPES, TX_POSITIVE_TYPES, TX_NEGATIVE_TYPES,
    POWER_LEVEL_LABELS, login_check
)

if st.session_state.power_level == 0:
    st.switch_page('pages/home.py')

# Không cho vào admin khi đang giả lập
if st.session_state.get('impersonating'):
    st.switch_page('pages/home.py')

text = st.session_state.text
pl = st.session_state.power_level  # 1=viewer, 2=moderator, 3=superadmin

st.header(text["admin_power_title"].upper(), anchor=False)
st.caption(f"Quyền hiện tại: **{POWER_LEVEL_LABELS.get(pl, 'Unknown')}** (Level {pl})")

# Tabs chính
tab_overview, tab_users, tab_tx = st.tabs([
    f"📊 {text['admin_tab_overview']}",
    f"👥 {text['admin_tab_users']}",
    f"📋 {text['admin_tab_transactions']}"
])

# ==============================================================================
# TAB 1: TỔNG QUAN
# ==============================================================================
with tab_overview:
    stats = admin_get_system_stats()

    # KPI row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric(text['admin_kpi_total_users'], stats['total_users'])
    k2.metric(text['admin_kpi_total_balance'],
               f"{format(stats['total_balance'] // 1_000_000, ',')}M VNĐ")
    k3.metric(text['admin_kpi_total_savings'],
               f"{format(stats['total_savings'] // 1_000_000, ',')}M VNĐ")
    k4.metric(text['admin_kpi_total_loans'],
               f"{format(stats['total_loans'] // 1_000_000, ',')}M VNĐ")
    k5.metric(text['admin_kpi_locked'],
               f"{'🔴' if stats['locked_count'] > 0 else '🟢'} {stats['locked_count']}")
    k6.metric(text['admin_kpi_overdue'],
               f"{'🔴' if stats['overdue_count'] > 0 else '🟢'} {stats['overdue_count']}")

    st.markdown('---')

    # Charts row 1: Balance distribution | Savings vs Loans pie
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"**{text['admin_chart_balance_dist']}**")
        user_df, _ = admin_get_user_summary()
        non_zero = user_df[user_df['Balance'] > 0]
        if not non_zero.empty:
            fig_hist = px.histogram(
                non_zero, x='Balance', nbins=15,
                color_discrete_sequence=['#9b5de5'],
                labels={'Balance': 'Số dư (VNĐ)', 'count': 'Số tài khoản'}
            )
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0', margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_hist, width='stretch')
        else:
            st.info("Chưa có dữ liệu số dư")

    with c2:
        st.markdown(f"**{text['admin_chart_savings_loans']}**")
        pie_data = {
            'Tiết kiệm': stats['total_savings'],
            'Dư nợ': stats['total_loans'],
            'Số dư tự do': max(0, stats['total_balance'] - stats['total_loans'] - stats['total_savings'])
        }
        fig_pie = px.pie(
            values=list(pie_data.values()),
            names=list(pie_data.keys()),
            color_discrete_sequence=['#00ff66', '#ff4757', '#9b5de5'],
            hole=0.4
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0',
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_pie, width='stretch')

    # Transaction timeline
    st.markdown(f"**{text['admin_chart_tx_timeline']}**")
    timeline_df = admin_get_tx_timeline()
    if not timeline_df.empty:
        fig_line = px.line(
            timeline_df, x='Date', y='Count',
            color_discrete_sequence=['#9b5de5'],
            labels={'Date': 'Ngày', 'Count': 'Số giao dịch'}
        )
        fig_line.update_traces(
            line_color='#9b5de5', fill='tozeroy',
            fillcolor='rgba(155,93,229,0.15)'
        )
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_line, width='stretch')
    else:
        st.info("Chưa có dữ liệu giao dịch")

    # Alerts section
    st.markdown('---')
    st.markdown(f"**:violet[{text['admin_locked_overdue_title']}]**")
    user_df2, overdue_ids = admin_get_user_summary()

    locked_df = user_df2[user_df2['Is_Locked_Bool'] == True]
    overdue_df = user_df2[user_df2['Has_Overdue'] == True]

    if locked_df.empty and overdue_df.empty:
        st.success(text['admin_no_issues'])
    else:
        al1, al2 = st.columns(2)
        with al1:
            if not locked_df.empty:
                st.error(f"🔒 Tài khoản bị khóa ({len(locked_df)})")
                for _, r in locked_df.iterrows():
                    st.caption(f"· `{r['ID']}` — {r['Name']}")
        with al2:
            if not overdue_df.empty:
                st.warning(f"⚠️ Nợ quá hạn ({len(overdue_df)})")
                for _, r in overdue_df.iterrows():
                    st.caption(f"· `{r['ID']}` — {r['Name']} — {format(int(r['Total_Loans']), ',')} VNĐ")

# ==============================================================================
# TAB 2: NGƯỜI DÙNG
# ==============================================================================
with tab_users:
    user_df, _ = admin_get_user_summary()

    search = st.text_input(text['admin_search_user'], key='admin_search')
    if search:
        mask = (
            user_df['ID'].str.contains(search, case=False, na=False) |
            user_df['Name'].str.contains(search, case=False, na=False)
        )
        user_df = user_df[mask]

    if user_df.empty:
        st.info("Không tìm thấy người dùng nào.")
    else:
        for _, row in user_df.iterrows():
            target_id = row['ID']
            target_pl = int(row['Power_Level'])
            is_locked = to_bool(row['Is_Locked'])
            has_overdue = row['Has_Overdue']
            is_self = target_id == st.session_state.acc_num
            can_act = (pl >= 2) and (target_pl < pl) and not is_self

            with st.container(border=True):
                st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
                uc1, uc2, uc3 = st.columns([3, 2, 3])

                with uc1:
                    icon = "🔒" if is_locked else ("⚠️" if has_overdue else "✅")
                    st.write(f"{icon} **{row['Name']}** — `{target_id}`")
                    pl_label = POWER_LEVEL_LABELS.get(target_pl, str(target_pl))
                    st.caption(f"Quyền: {pl_label} (Level {target_pl})")
                    if is_self:
                        st.caption("_(tài khoản của bạn)_")

                with uc2:
                    st.write(f":green[**{format(int(row['Balance']), ',')} VNĐ**]")
                    if row['Total_Savings'] > 0:
                        st.caption(f"🏦 {format(int(row['Total_Savings']), ',')} VNĐ")
                    if row['Total_Loans'] > 0:
                        st.caption(f"💳 {format(int(row['Total_Loans']), ',')} VNĐ")

                with uc3:
                    btn_cols = st.columns(2)

                    # Giả lập (all pl > 0, target phải có pl thấp hơn)
                    if target_pl < pl and not is_self:
                        if btn_cols[0].button(f"👤 {text['admin_action_impersonate']}",
                                               key=f"imp_{target_id}"):
                            st.session_state.real_acc_num = st.session_state.acc_num
                            st.session_state.real_acc_name = st.session_state.acc_name
                            st.session_state.real_power_level = pl
                            st.session_state.impersonating = True
                            st.session_state.acc_num = target_id
                            st.session_state.acc_name = row['Name']
                            st.session_state.power_level = target_pl
                            st.session_state.previous_page.append(st.session_state.current_page)
                            st.switch_page('pages/home.py')

                    # Lock/unlock (pl >= 2)
                    if can_act:
                        lock_label = f"🔓 {text['admin_action_unlock']}" if is_locked else f"🔒 {text['admin_action_lock']}"
                        if btn_cols[1].button(lock_label, key=f"lock_{target_id}"):
                            if is_locked:
                                admin_unlock_account(target_id)
                            else:
                                admin_lock_account(target_id)
                            st.rerun()

                    # Adjust balance (pl >= 2)
                    if can_act:
                        expand_adj = f"_adj_{target_id}"
                        if st.button(f"💰 {text['admin_action_adjust_balance']}",
                                     key=f"adj_btn_{target_id}"):
                            st.session_state[expand_adj] = not st.session_state.get(expand_adj, False)
                            st.rerun()

                        if st.session_state.get(expand_adj):
                            with st.form(f"form_adj_{target_id}"):
                                adj_amount = st.number_input(
                                    text['admin_balance_adjust_label'],
                                    step=100000, format='%d', key=f"adj_val_{target_id}"
                                )
                                pass_adj = st.text_input("Mật khẩu xác nhận", type='password',
                                                          max_chars=24, key=f"adj_pass_{target_id}")
                                ca, cb = st.columns(2)
                                with ca:
                                    if st.form_submit_button(f"**:green[{text['common_confirm']} ✓]**"):
                                        if pass_adj == '' or login_check(st.session_state.acc_num, pass_adj) != 2:
                                            st.error("Sai mật khẩu")
                                        else:
                                            try:
                                                admin_adjust_balance(target_id, int(adj_amount))
                                                del st.session_state[expand_adj]
                                                st.rerun()
                                            except ValueError:
                                                st.error("Số dư không thể âm")
                                with cb:
                                    if st.form_submit_button(f"**:red[{text['common_cancel']}]**"):
                                        del st.session_state[expand_adj]
                                        st.rerun()

                    # Change power level + Delete (pl == 3 only)
                    if pl == 3 and not is_self and target_pl < 3:
                        expand_pl = f"_pl_{target_id}"
                        if st.button(f"⚡ {text['admin_action_change_power']}",
                                     key=f"pl_btn_{target_id}"):
                            st.session_state[expand_pl] = not st.session_state.get(expand_pl, False)
                            st.rerun()

                        if st.session_state.get(expand_pl):
                            # Chỉ có thể gán quyền thấp hơn quyền của chính mình
                            allowed_levels = [i for i in range(3) if i != target_pl]
                            new_pl_val = st.selectbox(
                                "Quyền mới",
                                options=allowed_levels,
                                format_func=lambda x: POWER_LEVEL_LABELS.get(x, str(x)),
                                key=f"pl_sel_{target_id}"
                            )
                            pc1, pc2 = st.columns(2)
                            with pc1:
                                if st.button(f"**:green[{text['common_confirm']} ✓]**",
                                             key=f"pl_cfm_{target_id}"):
                                    admin_change_power_level(target_id, new_pl_val)
                                    del st.session_state[expand_pl]
                                    st.rerun()
                            with pc2:
                                if st.button(f"**:red[{text['common_cancel']}]**",
                                             key=f"pl_cancel_{target_id}"):
                                    del st.session_state[expand_pl]
                                    st.rerun()

                        # Delete
                        del_key = f"_del_{target_id}"
                        if st.button(f"🗑️ {text['admin_action_delete']}",
                                     key=f"del_btn_{target_id}"):
                            st.session_state[del_key] = True
                            st.rerun()

                        if st.session_state.get(del_key):
                            st.warning(text['admin_confirm_delete'].format(target_id))
                            dc1, dc2 = st.columns(2)
                            with dc1:
                                if st.button(f"**:red[✓ Xóa]**", key=f"del_cfm_{target_id}"):
                                    admin_soft_delete_account(target_id)
                                    del st.session_state[del_key]
                                    st.rerun()
                            with dc2:
                                if st.button(f"**:green[{text['common_cancel']}]**",
                                             key=f"del_cancel_{target_id}"):
                                    del st.session_state[del_key]
                                    st.rerun()

# ==============================================================================
# TAB 3: GIAO DỊCH TOÀN HỆ THỐNG
# ==============================================================================
with tab_tx:
    st.markdown(f"**{text['admin_recent_tx_title']}**")

    recent_tx = admin_get_recent_transactions(50)

    if recent_tx.empty:
        st.info("Chưa có giao dịch nào trong hệ thống.")
    else:
        type_filter = st.selectbox(
            text['history_filter_type'],
            ['all'] + ALL_TX_TYPES,
            format_func=lambda t: text['history_all_types'] if t == 'all' else text.get(f'tx_{t}', t),
            key='admin_tx_type_filter'
        )
        display_tx = recent_tx if type_filter == 'all' else recent_tx[recent_tx['Type'] == type_filter]

        for _, row in display_tx.iterrows():
            tx_type = row['Type']
            amount = int(row['Amount'])
            type_label = text.get(f'tx_{tx_type}', tx_type)

            if tx_type in TX_POSITIVE_TYPES:
                amount_str, amount_color = f'+{format(amount, ",")}', 'green'
            elif tx_type in TX_NEGATIVE_TYPES:
                amount_str, amount_color = f'-{format(amount, ",")}', 'red'
            else:
                amount_str, amount_color = f'~{format(amount, ",")}', 'blue'

            with st.container(border=True):
                st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
                tc1, tc2, tc3, tc4 = st.columns([2, 2, 2, 2])
                with tc1:
                    st.write(f"**{type_label}**")
                    st.caption(f"`{row['Account_ID']}`")
                with tc2:
                    st.markdown(f":{amount_color}[**{amount_str} VNĐ**]")
                with tc3:
                    if str(row['Description']) not in ('', 'nan', 'None'):
                        st.caption(str(row['Description']))
                with tc4:
                    st.caption(row['Timestamp'].strftime('%d/%m/%Y %H:%M'))