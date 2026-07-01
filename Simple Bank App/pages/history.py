import streamlit as st
import pandas as pd
from datetime import date, timedelta
from helpers import transactions_init, ALL_TX_TYPES, TX_POSITIVE_TYPES, TX_NEGATIVE_TYPES

if not st.session_state.login_state:
    st.switch_page('pages/home.py')

text = st.session_state.text
stk = st.session_state.acc_num
PER_PAGE = 15

st.header(text['history_title'].upper(), anchor=False)

_, tx_df = transactions_init()
my_tx = tx_df[tx_df['Account_ID'] == stk].copy()

if my_tx.empty:
    st.info(text['history_no_records'])
    st.stop()

my_tx['Timestamp'] = pd.to_datetime(my_tx['Timestamp'])
my_tx = my_tx.sort_values('Timestamp', ascending=False).reset_index()

# ==============================================================================
# BỘ LỌC
# ==============================================================================
col1, col2, col3 = st.columns(3)
with col1:
    type_options = ['all'] + ALL_TX_TYPES
    selected_type = st.selectbox(
        text['history_filter_type'],
        type_options,
        format_func=lambda t: text['history_all_types'] if t == 'all' else text.get(f'tx_{t}', t),
        key='history_type_filter'
    )
with col2:
    from_date = st.date_input(text['history_filter_from'],
                            value=date.today() - timedelta(days=30),
                            key='history_from_date')
with col3:
    to_date = st.date_input(text['history_filter_to'],
                            value=date.today(),
                            key='history_to_date')

# Reset về trang 1 mỗi khi filter thay đổi
filter_state = (selected_type, str(from_date), str(to_date))
if st.session_state.get('_history_last_filter') != filter_state:
    st.session_state.history_page = 1
    st.session_state['_history_last_filter'] = filter_state

# Áp bộ lọc
filtered = my_tx.copy()
if selected_type != 'all':
    filtered = filtered[filtered['Type'] == selected_type]
filtered = filtered[
    (filtered['Timestamp'].dt.date >= from_date) &
    (filtered['Timestamp'].dt.date <= to_date)
]

total = len(filtered)
if total == 0:
    st.info(text['history_no_records'])
    st.stop()

total_pages = max((total + PER_PAGE - 1) // PER_PAGE, 1)
current_page = min(st.session_state.get('history_page', 1), total_pages)

# ==============================================================================
# HIỂN THỊ GIAO DỊCH
# ==============================================================================
st.caption(f"{total} giao dịch | {text['history_page']} {current_page}/{total_pages}")

start_idx = (current_page - 1) * PER_PAGE
page_tx = filtered.iloc[start_idx:start_idx + PER_PAGE]

for _, row in page_tx.iterrows():
    type_key = f'tx_{row["Type"]}'
    type_label = text.get(type_key, row['Type'])
    amount = int(row['Amount'])
    tx_type = row['Type']

    if tx_type in TX_POSITIVE_TYPES:
        amount_str = f'+{format(amount, ",")}'
        amount_color = 'green'
    elif tx_type in TX_NEGATIVE_TYPES:
        amount_str = f'-{format(amount, ",")}'
        amount_color = 'red'
    else:
        # Trung tính (tái tục tiết kiệm - số dư không đổi)
        amount_str = f'~{format(amount, ",")}'
        amount_color = 'blue'

    with st.container(border=True):
        st.markdown('<div class="finance-card-marker"></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            st.write(f"**{type_label}**")
            if row['Description']:
                st.caption(str(row['Description']))
        with c2:
            st.markdown(f":{amount_color}[**{amount_str} VNĐ**]")
        with c3:
            st.caption(row['Timestamp'].strftime('%d/%m/%Y %H:%M'))

# ==============================================================================
# ĐIỀU HƯỚNG PHÂN TRANG
# ==============================================================================
if total_pages > 1:
    p1, p2, p3 = st.columns([1, 3, 1])
    with p1:
        if st.button('◀', disabled=current_page == 1, key='history_prev'):
            st.session_state.history_page = current_page - 1
            st.rerun()
    with p2:
        st.write(f"{text['history_page']} **{current_page}** / {total_pages}")
    with p3:
        if st.button('▶', disabled=current_page == total_pages, key='history_next'):
            st.session_state.history_page = current_page + 1
            st.rerun()