import streamlit as st
import pandas as pd
from helpers import (available_balance, savings_init, loans_init,
                      transactions_init, TX_TRANSFER_IN, TX_TRANSFER_OUT,
                      TX_POSITIVE_TYPES, TX_NEGATIVE_TYPES)

if not st.session_state.login_state:
    st.switch_page('pages/home.py')

text = st.session_state.text
stk = st.session_state.acc_num

st.header(text['summary_title'].upper(), anchor=False)

# ==============================================================================
# KHUNG THÔNG TIN TÀI KHOẢN
# ==============================================================================
balance = available_balance(stk)
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(168,85,247,0.25) 100%);
    border: 1px solid rgba(168, 85, 247, 0.4);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(147, 51, 234, 0.2);
">
    <div style="color: rgba(226,232,240,0.6); font-size: 13px; letter-spacing: 2px;
                text-transform: uppercase; margin-bottom: 6px;">
        {text['summary_acc_info']}
    </div>
    <div style="color: #e2e8f0; font-size: 22px; font-weight: 700; margin-bottom: 4px;">
        {st.session_state.acc_name}
    </div>
    <div style="color: rgba(226,232,240,0.5); font-size: 14px; letter-spacing: 3px;
                margin-bottom: 28px; font-family: 'Courier New', monospace;">
        {stk}
    </div>
    <div style="color: rgba(226,232,240,0.6); font-size: 12px; letter-spacing: 1.5px;
                text-transform: uppercase; margin-bottom: 6px;">
        {text['available_balance']}
    </div>
    <div style="
        color: #00ff66;
        font-size: 36px;
        font-weight: 900;
        font-family: 'Courier New', monospace;
        letter-spacing: 1px;
        text-shadow: 0 0 12px rgba(0, 255, 102, 0.5);
    ">
        {format(balance, ',')} <span style="font-size: 18px; opacity: 0.7;">VNĐ</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# TIẾT KIỆM VÀ VAY - 2 CỘT SONG SONG
# ==============================================================================
col_sav, col_loan = st.columns(2)

_, savings_df = savings_init()
my_savings = savings_df[(savings_df['Account_ID'] == stk) & (savings_df['Status'] == 'active')]

_, loans_df = loans_init()
my_loans = loans_df[(loans_df['Account_ID'] == stk) & (loans_df['Status'].isin(['active', 'overdue']))]

with col_sav:
    st.markdown(f"**:violet[{text['summary_active_savings']}]**")
    if my_savings.empty:
        st.info(text['summary_no_savings'])
    else:
        for _, row in my_savings.iterrows():
            with st.container(border=True):
                st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
                st.markdown(f":green[**{format(int(row['Principal']), ',')} VNĐ**]")
                st.caption(f"{row['Term_Months']} tháng · {row['Annual_Rate']*100:.2f}%/năm")
                st.caption(f"📅 {row['Start_Date']} → {row['Maturity_Date']}")
                if bool(row['Auto_Renew']):
                    st.caption("🔄 Tự động tái tục")

with col_loan:
    st.markdown(f"**:violet[{text['summary_active_loans']}]**")
    if my_loans.empty:
        st.info(text['summary_no_loans'])
    else:
        for _, row in my_loans.iterrows():
            with st.container(border=True):
                st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
                is_overdue = row['Status'] == 'overdue'
                color = 'orange' if is_overdue else 'red'
                st.markdown(f":{color}[**{format(int(row['Principal']), ',')} VNĐ**]")
                st.caption(f"{row['Term_Months']} tháng · {row['Annual_Rate']*100:.2f}%/năm")
                st.caption(f"📅 {row['Start_Date']} → {row['Maturity_Date']}")
                if is_overdue:
                    st.caption("⚠️ Quá hạn")

st.markdown('---')

# ==============================================================================
# 5 GIAO DỊCH GẦN NHẤT (chỉ transfer_in và transfer_out)
# ==============================================================================
header_c1, header_c2 = st.columns([3, 1])
with header_c1:
    st.markdown(f"**:violet[{text['summary_recent_tx']}]**")
with header_c2:
    if st.button(f"{text['summary_view_all_history']} →", key='btn_view_all_history'):
        st.session_state.previous_page.append(st.session_state.current_page)
        st.switch_page('pages/history.py')

_, tx_df = transactions_init()
my_tx = tx_df[
    (tx_df['Account_ID'] == stk) &
    (tx_df['Type'].isin([TX_TRANSFER_IN, TX_TRANSFER_OUT]))
].copy()

if my_tx.empty:
    st.info(text['summary_no_tx'])
else:
    my_tx['Timestamp'] = pd.to_datetime(my_tx['Timestamp'])
    recent_5 = my_tx.sort_values('Timestamp', ascending=False).head(5)

    for _, row in recent_5.iterrows():
        tx_type = row['Type']
        amount = int(row['Amount'])
        type_label = text.get(f'tx_{tx_type}', tx_type)

        if tx_type in TX_POSITIVE_TYPES:
            amount_str = f'+{format(amount, ",")}'
            amount_color = 'green'
        else:
            amount_str = f'-{format(amount, ",")}'
            amount_color = 'red'

        with st.container(border=True):
            st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
            tc1, tc2, tc3 = st.columns([3, 2, 2])
            with tc1:
                st.write(f"**{type_label}**")
                if row['Description']:
                    st.caption(str(row['Description']))
            with tc2:
                st.markdown(f":{amount_color}[**{amount_str} VNĐ**]")
            with tc3:
                st.caption(row['Timestamp'].strftime('%d/%m/%Y %H:%M'))