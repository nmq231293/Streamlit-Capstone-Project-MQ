# ==============================================================================
# STYLES.PY - CUSTOM CSS STYLING FOR STREAMLIT APP
# ==============================================================================
import base64
import streamlit as st

MAIN_CSS = """
    <style>
    /* ==============================================================================
        CYBERPUNK DESIGN SYSTEM - MAIN STYLING FOR STREAMLIT APP
       ============================================================================== */
    
    /* A. TIÊU ĐỀ CHÍNH (H1) - GIỮ DẢI MÀU CẦU VỒNG RỰC RỠ*/
    h1:has(span),
    h1 span {
        background: linear-gradient(
            90deg, 
            #ff3366 0%,   /* Hồng Neon */
            #ff9933 25%,  /* Cam Neon */
            #00ffcc 50%,  /* Xanh Mint */
            #33ccff 75%,  /* Xanh Lơ */
            #a855f7 100%  /* Tím Neon */
        ) !important;
        background-size: 100% auto !important;               /* Cố định dải màu vừa khít với chữ */
        -webkit-background-clip: text !important;            /* Cắt dải màu ôm khít vào viền chữ */
        -webkit-text-fill-color: transparent !important;     /* Làm rỗng ruột chữ để hiện dải màu nền */
        color: transparent !important;
        font-weight: 900 !important;
        font-size: 42px !important;                          /* Giữ nguyên kích thước to lớn uy nghi */
        letter-spacing: 2px !important;                      /* Giãn chữ phong cách công nghệ tương lai */
        text-transform: uppercase !important;                /* Viết hoa toàn bộ tiêu đề chính */
        text-shadow: none !important;                        /* Chặn hoàn toàn bóng chữ màu đỏ cam từ dưới đè lên */
        animation: none !important;                          /* Tắt bỏ hoàn toàn hiệu ứng chạy màu để nhẹ máy */
        
        /* Tạo quầng sáng Neon mờ phát sáng nhẹ bao quanh cụm chữ cầu vồng */
        filter: drop-shadow(0 0 12px rgba(168, 85, 247, 0.45)) !important; 
    }

    /* ------------------------------------------------------------------------------ */

    /* B. TIÊU ĐỀ CÁC TRANG CON (H2) - MÀU ĐỎ CAM NEON CỐ ĐỊNH (GIỮ NGUYÊN ĐANG CHẠY TỐT) */
    h2, h2 span {
        background: none !important;                         /* Cắt bỏ hoàn toàn hiệu ứng cầu vồng của h1 */
        -webkit-text-fill-color: #ff4757 !important;         /* Ép chữ về màu đỏ cam đặc rực rỡ */
        color: #ff4757 !important;                           
        font-weight: 800 !important;                         
        font-size: 32px !important;                          
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        filter: none !important;                             /* Bỏ quầng sáng mờ drop-shadow của h1 */
        animation: none !important;                          
        
        /* Hiệu ứng phát sáng kép (Double Glow) màu đỏ cam cực mạnh */
        text-shadow: 0 0 10px rgba(255, 71, 87, 0.8),        
                    0 0 25px rgba(255, 71, 87, 0.45) !important; 
    }


    /* ==============================================================================
        HIỆU ỨNG SỐ DƯ PHÁT SÁNG MATRIX / HACKER (GREEN NEON GLOW)
       ============================================================================== */
    
    .balance-glow {
        color: #00ff66 !important; /* Màu xanh lá cây rực rỡ hệ Matrix */
        font-family: 'Courier New', Courier, monospace !important; /* Font chữ số điện tử chuyên dụng */
        font-size: 15px !important;
        letter-spacing: 0.5px !important;
        display: inline-block !important;
        
        /* Hiệu ứng đổ bóng kép tạo quầng sáng bao quanh số tiền */
        text-shadow: 0 0 6px rgba(0, 255, 102, 0.6),  
                    0 0 15px rgba(0, 255, 102, 0.3) !important;
                    
        animation: pulseGlow 2.5s infinite ease-in-out !important; /* Kích hoạt nhịp thở nhấp nháy mượt */
    }

    /* Chu kỳ co giãn quầng sáng Neon của số tiền */
    @keyframes pulseGlow {
        0%, 100% {
            text-shadow: 0 0 6px rgba(0, 255, 102, 0.6), 0 0 15px rgba(0, 255, 102, 0.3);
        }
        50% {
            text-shadow: 0 0 12px rgba(0, 255, 102, 0.9), 0 0 25px rgba(0, 255, 102, 0.5);
            color: #12ff7b !important; /* Sáng rực rỡ hơn ở đỉnh chu kỳ */
        }
    }

    /* ==============================================================================
        ĐỊNH DẠNG MẶC ĐỊNH CHO TẤT CẢ NÚT BẤM (MÀU TÍM NEON CHỦ ĐẠO)
       ============================================================================== */
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;               
        border-radius: 12px !important;          
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.3) !important; 
        transition: all 0.3s ease-in-out !important;
    }
    
    div[data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%) !important;
        color: #ffffff !important;               
        box-shadow: 0 6px 20px rgba(147, 51, 234, 0.5) !important; 
        transform: translateY(-2px) !important;  
    }
    
    /* Nút Chatbot Trợ lý AI */
    div[data-testid="stButton"] button[py-click*="toggle_chat_btn"] {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important; 
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4) !important;
    }

    /* ==============================================================================
        HỆ THỐNG ĐÓNG KHỐI ĐỒNG BỘ CHO TẤT CẢ LABEL WIDGETS (TONE TÍM NEON)
       ============================================================================== */
    
    /* Gom tất cả các thẻ label của mọi loại widget thông dụng trong Streamlit */
    div[data-testid="stTextInput"] label, 
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stTimeInput"] label,
    div[data-testid="stRadio"] > label,
    div[data-testid="stCheckbox"] > label {
        background: rgba(255, 255, 255, 0.04) !important; /* Nền kính mờ đồng bộ */
        border: 1px solid rgba(168, 85, 247, 0.25) !important; /* Viền tím neon nhẹ */
        border-radius: 8px !important;                       /* Bo góc khối */
        padding: 4px 12px !important;                        /* Khoảng cách trong khối */
        margin-bottom: 8px !important;                       /* Khoảng cách xuống ô nhập liệu */
        display: inline-flex !important;                     /* Ô ôm vừa khít chiều dài chữ */
        align-items: center !important;
        backdrop-filter: blur(4px) !important;
        box-shadow: 0 2px 8px rgba(147, 51, 234, 0.15) !important; /* Đổ bóng tím */
        transition: all 0.3s ease-in-out !important;
    }

    /* Hiệu ứng phát sáng nhẹ khi di chuột vào bất kỳ vùng widget nào */
    div[data-testid="stTextInput"]:hover label, 
    div[data-testid="stNumberInput"]:hover label,
    div[data-testid="stSelectbox"]:hover label,
    div[data-testid="stMultiSelect"]:hover label,
    div[data-testid="stTextArea"]:hover label,
    div[data-testid="stSlider"]:hover label,
    div[data-testid="stRadio"]:hover > label,
    div[data-testid="stCheckbox"]:hover > label {
        border-color: rgba(168, 85, 247, 0.6) !important;    /* Viền tím sáng rực hơn */
        background: rgba(255, 255, 255, 0.08) !important;   /* Nền trong hơn */
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3) !important; /* Tăng shadow neon */
    }

    /* Định dạng đồng bộ cho font chữ bên trong các khối label */
    div[data-testid="stTextInput"] label p, 
    div[data-testid="stNumberInput"] label p,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stMultiSelect"] label p,
    div[data-testid="stTextArea"] label p,
    div[data-testid="stSlider"] label p,
    div[data-testid="stRadio"] > label p,
    div[data-testid="stCheckbox"] > label p {
        color: #e2e8f0 !important;                           /* Màu chữ trắng xám công nghệ */
        font-weight: 600 !important;
        font-size: 13.5px !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 0 6px rgba(226, 232, 240, 0.2) !important; /* Chữ tự phát sáng nhẹ */
        margin: 0 !important;
    }

    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.08) !important; 
        border: 1px solid rgba(255, 255, 255, 0.2) !important;  
        border-radius: 12px !important;                          
        backdrop-filter: blur(8px) !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #a855f7 !important;                         
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.5) !important;
    }

    /* ==============================================================================
        ĐỊNH DẠNG NÚT CHỌN NGÔN NGỮ (MENU_BUTTON) - TONE MÀU HỒNG NEON CHỦ ĐẠO
       ============================================================================== */
    
    /* 1. Trạng thái mặc định của nút Chọn ngôn ngữ */
    div.st-key-lang_menu_btn button {
        background: linear-gradient(135deg, #db2777 0%, #f43f5e 100%) !important; /* Hồng cánh sen đậm chuyển sang Hồng cam rực rỡ */
        color: #ffffff !important;               
        border-radius: 12px !important;          
        border: 1px solid rgba(244, 63, 94, 0.25) !important; /* Viền hồng mờ */
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(219, 39, 119, 0.4) !important; /* Đổ bóng phát sáng màu hồng neon */
        transition: all 0.3s ease-in-out !important;
    }
    
    /* 2. Hiệu ứng Hover rực rỡ khi di chuột vào nút Chọn ngôn ngữ */
    div.st-key-lang_menu_btn button:hover {
        background: linear-gradient(135deg, #be185d 0%, #e11d48 100%) !important; /* Tông hồng sẫm sâu sắc và quyến rũ hơn */
        color: #ffffff !important;               
        box-shadow: 0 6px 20px rgba(225, 29, 72, 0.6) !important; /* Tăng cường độ phát sáng Cyber */
        transform: translateY(-2px) !important;  /* Nút nảy nhẹ lên trên 2px */
    }

    /* 3. Hiệu ứng đặc biệt dành cho hộp danh sách lựa chọn ngôn ngữ xổ xuống (nếu có chung class) */
    div.st-key-lang_menu_btn + div ul[role="menu"],
    div.st-key-lang_menu_btn + div div[role="listbox"] {
        border-color: rgba(244, 63, 94, 0.3) !important; /* Đồng bộ viền hộp thoại màu hồng */
    }

    /* ==============================================================================
        ĐỊNH DẠNG NÚT MENU_BUTTON QUA CLASS KEY - ĐỘC LẬP NGÔN NGỮ (TONE XANH LƠ ĐẬM)
       ============================================================================== */
    
    /* 1. Trạng thái mặc định của nút (Bắt chính xác theo Class st-key) */
    div.st-key-settings_menu_btn button {
        background: linear-gradient(135deg, #005f73 0%, #0a9396 100%) !important; /* Tông màu Deep Teal chuyển sang Cyan đậm */
        color: #ffffff !important;               
        border-radius: 12px !important;          
        border: 1px solid rgba(0, 255, 204, 0.25) !important; /* Viền xanh lơ mờ */
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(0, 95, 115, 0.4) !important; /* Đổ bóng phát sáng xanh lơ biển sâu */
        transition: all 0.3s ease-in-out !important;
    }
    
    /* 2. Hiệu ứng Hover rực rỡ khi di chuột vào nút */
    div.st-key-settings_menu_btn button:hover {
        background: linear-gradient(135deg, #004b5c 0%, #00b4d8 100%) !important; /* Sáng bừng lên sắc xanh lơ neon của Ethereum */
        color: #ffffff !important;               
        box-shadow: 0 6px 20px rgba(0, 180, 216, 0.6) !important; /* Tăng cường độ bóng phát sáng Cyber */
        transform: translateY(-2px) !important;  /* Nút nảy nhẹ lên trên */
    }

    /* ==============================================================================
        HIỆU ỨNG POP-OVER CHO CẢ MENU CÀI ĐẶT & NGÔN NGỮ
       ============================================================================== */
    
    /* 1. Định dạng khung nền tối và viền mờ cho TẤT CẢ các danh sách xổ xuống */
    ul[role="menu"], 
    div[role="listbox"],
    [data-presentation="popover"] ul {
        background-color: #0f172a !important;                /* Nền tối sâu sâu thẳm giống background ngân hàng */
        border: 1px solid rgba(168, 85, 247, 0.3) !important; /* Viền tím mờ làm ranh giới hộp */
        border-radius: 12px !important;
        padding: 6px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7) !important;
    }

    /* 2. Định dạng chữ và khoảng cách của từng dòng tùy chọn mặc định */
    ul[role="menu"] li,
    div[role="listbox"] [role="option"],
    [data-presentation="popover"] ul li {
        color: #cbd5e1 !important;                           /* Ép chữ về màu trắng xám công nghệ (không lo bị đen chữ) */
        font-weight: 500 !important;
        font-size: 13.5px !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        transition: all 0.25s ease-in-out !important;
    }

    /* 3. HIỆU ỨNG HOVER RỰC RỠ: Tự động phân chia màu theo nội dung cụ thể */
    
    /* A. Các phần tử thuộc Menu Ngôn ngữ (Sẽ lướt sáng màu Hồng Neon) */
    ul[role="menu"] li:has(span:contains("Tiếng")),
    ul[role="menu"] li:has(span:contains("English")),
    div[role="listbox"] [role="option"]:contains("Tiếng"),
    div[role="listbox"] [role="option"]:contains("English"),
    ul[role="menu"] li:contains("Tiếng Việt"),
    ul[role="menu"] li:contains("English") {
        /* Thiết lập hover riêng cho ngôn ngữ */
    }
    ul[role="menu"] li:contains("Tiếng"):hover,
    ul[role="menu"] li:contains("English"):hover,
    div[role="listbox"] [role="option"]:hover:has(span:contains("Tiếng")),
    [data-presentation="popover"] ul li:contains("Tiếng"):hover,
    [data-presentation="popover"] ul li:contains("English"):hover {
        background: rgba(244, 63, 94, 0.15) !important;      /* Nền hồng mỏng */
        color: #f43f5e !important;                           /* Chữ đổi sang hồng rực */
        padding-left: 20px !important;                       /* Trượt nhẹ sang phải */
        box-shadow: inset 3px 0 0 0 #db2777 !important;      /* Vạch dọc màu hồng bên trái */
    }
    
    /* B. Các phần tử thuộc Menu Cài đặt (Sẽ lướt sáng màu Xanh Lơ Đậm) */
    ul[role="menu"] li:hover,
    div[role="listbox"] [role="option"]:hover,
    [data-presentation="popover"] ul li:hover {
        background: rgba(0, 206, 209, 0.15) !important;      /* Mặc định các menu khác là xanh lơ */
        color: #00ffff !important;                           /* Chữ màu Cyan phát sáng giống lõi Ethereum */
        padding-left: 20px !important;                       /* Trượt nhẹ sang phải */
        box-shadow: inset 3px 0 0 0 #00ced1 !important;      /* Vạch dọc xanh lơ bên trái */
    }


    
    /* ==============================================================================
        HỆ THỐNG KÍCH SÁNG NEON CHO MÃ MÀU CHỮ CỦA STREAMLIT TRONG DIALOG
       ============================================================================== */
    
    /* 1. Kích sáng màu ĐỎ (:red) thành Đỏ Neon rực rỡ và đổ bóng chữ */
    div[data-testid="stDialog"] div[data-testid="stMarkdownContainer"] span[style*="color: rgb(255, 75, 75)"] p,
    div[data-testid="stDialog"] div[data-testid="stMarkdownContainer"] span[style*="color: #ff4b4b"] p,
    div[data-testid="stDialog"] p style[style*="color:red"] {
        color: #ff3333 !important; /* Đổi sang tông đỏ lửa rực sáng */
        font-weight: 800 !important;
        font-size: 15px !important;
        text-shadow: 0 0 8px rgba(255, 51, 51, 0.6) !important; /* Tạo hiệu ứng chữ phát sáng */
    }

    /* 2. Kích sáng màu XANH LÁ (:green) thành Xanh Mint phát sáng cực mạnh */
    div[data-testid="stDialog"] div[data-testid="stMarkdownContainer"] span[style*="color: rgb(9, 171, 59)"] p,
    div[data-testid="stDialog"] div[data-testid="stMarkdownContainer"] span[style*="color: #09ab3b"] p {
        color: #00ffcc !important; /* Đổi sang màu xanh ngọc Mint Neon cực kỳ bắt mắt */
        font-weight: 800 !important;
        font-size: 15px !important;
        text-shadow: 0 0 8px rgba(0, 255, 204, 0.7) !important; /* Tạo hiệu ứng chữ phát sáng */
    }
    
    /* Điều chỉnh nhẹ để nền nút bên trong Dialog trong suốt hơn, giúp chữ phát sáng nổi lên */
    div[data-testid="stDialog"] div[data-testid="stForm"] div[data-testid="stButton"] button,
    div[data-testid="stDialog"] div[data-testid="column"] div[data-testid="stButton"] button {
        background: rgba(255, 255, 255, 0.05) !important; /* Đổi nền nút thành kính mờ trong suốt */
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: none !important;
    }
    div[data-testid="stDialog"] div[data-testid="stForm"] div[data-testid="stButton"] button:hover,
    div[data-testid="stDialog"] div[data-testid="column"] div[data-testid="stButton"] button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Nền kính mờ cho các khung sổ tiết kiệm / khoản vay - đọc chữ dễ hơn trên nền ảnh */
    div[data-testid="stVerticalBlock"] > div:has(div.finance-card-marker) {
        background-color: rgba(15, 10, 30, 0.65) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px;
    }    
    </style>
"""

# Mã hóa ảnh nền thành base64 để nhúng trực tiếp vào CSS, tránh việc đọc từ đĩa nhiều lần
@st.cache_data
def _get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Ảnh nền mặc định của app
def apply_background_image(image_path: str) -> bool:
    """
    Đọc + encode base64 CHỈ 1 LẦN nhờ cache (thay vì mỗi lần rerun đọc lại từ đĩa
    - đây chính là nguyên nhân chính khiến app giật mỗi lần bấm nút).
    """
    try:
        img_base64 = _get_base64_image(image_path)
    except FileNotFoundError:
        return False

    st.markdown(f"""
        <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/png;base64,{img_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            [data-testid="stHeader"] {{
                background: rgba(0,0,0,0);
            }}
        </style>
    """, unsafe_allow_html=True)
    return True

# Hàm tiện ích để áp dụng CSS chính cho toàn bộ app
def apply_main_styles():
    st.markdown(MAIN_CSS, unsafe_allow_html=True)