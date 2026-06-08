import streamlit as st
from openai import OpenAI
# Lấy API Key an toàn từ mục Secrets của Streamlit
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

st.title(":violet[🤖 Trợ Lý Ảo - Simple Bank Support]")
st.write("**:orange[Hãy hỏi tôi bất kỳ điều gì về cách sử dụng ứng dụng này!]**")

# Khởi tạo client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Định nghĩa vai trò cho mô hình (System Prompt)
system_instruction = {
    "role": "system",
    "content": "Bạn là trợ lý ảo hỗ trợ ứng dụng Simple Bank App. Hãy hướng dẫn người dùng đăng ký, đăng nhập, gửi tiền, rút tiền và xem lịch sử giao dịch một cách ngắn gọn, lịch sự bằng tiếng Việt."
}

SYSTEM_PROMPT = """
Bạn là một trợ lý ảo thông minh được tích hợp trong ứng dụng "Simple Bank App".
Nhiệm vụ của bạn là hỗ trợ, giải đáp và hướng dẫn người dùng cách sử dụng các tính năng của app.

Thông tin về ứng dụng gồm các tính năng chính sau:
1. Đăng nhập / Đăng ký tài khoản hệ thống.
2. Xem số dư tài khoản trực tuyến.
3. Gửi tiền (Deposit) và Rút tiền (Withdraw).
4. Chuyển khoản nội bộ hoặc liên ngân hàng bảo mật.
5. Xem lịch sử giao dịch gần đây.

Quy tắc ứng xử:
- Luôn trả lời bằng tiếng Việt, lịch sự, ngắn gọn và dễ hiểu.
- Chỉ tập trung trả lời các câu hỏi liên quan đến dịch vụ ngân hàng hoặc cách thao tác trên ứng dụng này.
- Nếu người dùng hỏi các vấn đề ngoài phạm vi ứng dụng, hãy khéo léo từ chối và hướng họ quay lại chủ đề chính.
"""

# Khởi tạo bộ nhớ lưu trữ lịch sử chat nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = [system_instruction]

# Hiển thị lại các tin nhắn cũ trong phiên làm việc (ẩn tin nhắn hệ thống)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Xử lý khi người dùng nhập câu hỏi mới
if user_query := st.chat_input("Bạn cần trợ giúp gì về tính năng của app?"):
    
    # Hiển thị câu hỏi của người dùng lên màn hình
    with st.chat_message("user", avatar='🙎🏻‍♂️'):
        st.write(f':green[{user_query}]')
    
    # Lưu câu hỏi vào lịch sử bộ nhớ
    st.session_state.messages.append({"role": "user", "content": f':green[{user_query}]'})

    # Gọi API của OpenAI để nhận phản hồi từ GPT-4o-mini
    with st.chat_message("assistant", avatar='🤖'):
        message_placeholder = st.empty()
        full_response = ""
        
        # Sử dụng stream=True để tạo hiệu ứng gõ chữ thời gian thực
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            stream=True,
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.write(f':orange[{full_response + "▌"}]')
                
        message_placeholder.write(f':orange[{full_response}]')
        
    # Lưu câu trả lời của AI vào lịch sử bộ nhớ
    st.session_state.messages.append({"role": "assistant", "content": f':orange[{full_response}]'})
