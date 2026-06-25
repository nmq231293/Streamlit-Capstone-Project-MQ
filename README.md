Ứng dụng dùng URL query params để khôi phục session sau F5.
Streamlit có 1 bug đã được team xác nhận (GitHub issue #9050) khiến query params bị xóa khỏi URL hiển thị sau mỗi lần st.switch_page().
App đã tự khắc phục bằng cách ghi lại token ngay ở lượt render kế tiếp, nên ảnh hưởng chỉ xảy ra nếu người dùng F5 đúng vào khung thời gian rất hẹp đó.
