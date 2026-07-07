# 🏦 REYNOLD BANK - SIMPLE BANK APP

An advanced, interactive digital banking simulation application built with Python and Streamlit, utilizing Google Sheets as a database secure storage layer with multi-language support (English & Vietnamese).

*Ứng dụng mô phỏng ngân hàng số tương tác nâng cao được xây dựng bằng Python và Streamlit, sử dụng Google Sheets làm cơ sở dữ liệu bảo mật, hỗ trợ song ngữ hoàn chỉnh (Tiếng Anh & Tiếng Việt).*

---

## 📌 TABLE OF CONTENTS / MỤC LỤC
1. [English Version](#english-version)
   - [Key Features](#key-features)
   - [Project Structure](#project-structure)
   - [How to Install & Run](#how-to-install--run)
   - [Important Notes & Safeguards](#important-notes--safeguards)
2. [Phiên Bản Tiếng Việt](#phiên-bản-tiếng-việt)
   - [Các Tính Năng Chính](#các-tính-năng-chính)
   - [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
   - [Hướng Dẫn Cài Đặt & Khởi Chạy](#hướng-dẫn-cài-đặt--khởi-chạy)
   - [Lưu Ý Quan Trọng & Cơ Chế Bảo Vệ](#lưu-ý-quan-trọng--cơ-chế-bảo-vệ)

---

# 🇬🇧 ENGLISH VERSION

## 🚀 Key Features

### 1. Authentication & Security
* **Smart Registration (Signup):** Users can register an account with a secure password hashed via bcrypt. Features a smart numeric generator to look up and suggest lucky account numbers matching user input or date of birth.
* **Secure Login & Session Management:** Utilizes encrypted auth_token query parameters on URLs to automatically restore state safely via URLSafeSerializer.
* **Session Protection Dialogs:** Implements automated strict session invalidation (60-minute absolute session expiration and 10-minute inactive idle timeout).
* **Anti-Hijacking Security:** Instantly triggers an alert dialog if a concurrent login attempt is detected from another device/browser session.

### 2. Core Financial Transactions
* **Fund Transfer:** Transfer funds safely between accounts with standard transaction amount guardrails (Min: 10,000 VND, Max: 500,000,000 VND per transaction). Includes an automated amount-to-words generator and custom text descriptions.
* **Beneficiary Management:** Save accounts into a personalized beneficiary list with nicknames for recurring quick transfers.
* **Flexible Fixed Savings Deposits:** Open multi-term fixed deposits. Supports automated interest compound/payout renewals at maturity, partial withdrawals, or premature liquidation (early withdrawal with interest forfeiture).
* **Credit Loan Approvals:** Dynamic borrow eligibility and borrowing caps evaluated on asset limits. Supports multi-tier interest rate deductions for consecutive on-time payments, special promotional rates, or multi-part loan splits for excess loans.

### 3. Account Dashboard & History
* **Summary Dashboard:** High-level metrics visualization showing a comprehensive snapshot of free balance, active savings books, total debt liabilities, and recent activity.
* **Advanced Transaction History:** Historical transaction statement viewer with structural page navigation and filters (transaction types, custom dates).
* **Data Export:** Generate and export tailored audit trails down into structured CSV spreadsheets natively.

### 4. Admin Management Dashboard
* **KPI Matrix Indicators:** System-wide diagnostics monitoring total user counts, combined asset pools, total system deposits, and active default loans.
* **User Control Center:** Perform balance adjustments, toggle full access suspension (Lock/Unlock accounts), update security privileges, or wipe accounts.
* **Live Impersonation Tool:** Securely shadow-login to debug individual client profiles directly with atomic transaction backup states.

### 5. Seamless Multi-Language & AI Integrations
* Full dynamic translation binding via an localized internal dictionary system.
* Sticky embedded responsive AI Assistance overlay powered by OpenAI/Gemini models to help guide clients through financial tasks.

---

## 📂 Project Structure

    .
    ├── .devcontainer/
    │   └── devcontainer.json       # Visual Studio Code development container configurations
    ├── .vscode/
    │   └── settings.json           # IDE layout constraints and editor configurations
    ├── Simple Bank App/
    │   ├── .streamlit/
    │   │   ├── config.toml         # Custom user UI interface branding options
    │   │   └── secrets.toml.example# Example secret credentials file structure
    │   ├── auth.py                 # Core Session Lifecycle, timeout validation, and cryptography
    │   ├── dictionary_data.py      # Dual-language localization source translation bindings
    │   ├── helpers.py              # Google Sheets API integrations, business algorithms, and safety layers
    │   ├── main.py                 # App entry-point orchestration panel
    │   ├── styles.py               # Futuristic glassmorphism theme and custom styles injection
    │   ├── pages/                  # Multipage navigation module
    │   │   ├── account_settings.py # Profile settings, password modifications, and credential updates
    │   │   ├── admin_power.py      # Back-office admin diagnostics overview controls
    │   │   ├── history.py          # Paginated transaction explorer with CSV exporter
    │   │   ├── home.py             # Main routing portal and automated scheduled tasks processor
    │   │   ├── loans.py            # Credit requests, structured payouts, and manual repayments
    │   │   ├── login.py            # Security login view
    │   │   ├── login_success.py    # Redirect route upon validation success
    │   │   ├── password_wrong.py   # Security penalty routing page
    │   │   ├── re_submit.py        # Fallback navigation handler
    │   │   ├── savings.py          # Fixed deposit configuration asset manager
    │   │   ├── signup.py           # Account enrollment wizard
    │   │   ├── signup_success.py   # Account creation celebration page
    │   │   ├── summary.py          # Central account metrics summary tab
    │   │   ├── transfer.py         # Interbank remittance dashboard
    │   │   ├── transfer_rehearsal.py # Transaction verification and password check
    │   │   └── transfer_success.py # E-receipt presentation page
    │   └── wallpaper/              # Brand theme wallpaper assets
    └── requirements.txt            # Main Python dependency environment manifests

---

## 🛠️ How to Install & Run

1. **Clone the repository:**
   `git clone <repository_url>`
   `cd <repository_directory>`

2. **Install Dependencies:**
   Make sure you have Python 3.10+ installed, then run:
   `pip install -r requirements.txt`

3. **Configure Environment Secrets:**
   - Navigate to `Simple Bank App/.streamlit/`
   - Copy `secrets.toml.example` and rename it to `secrets.toml`
   - Fill out the required parameters, including Google Sheets configuration credentials, OpenAI/Gemini API keys, and a strong application encryption SECRET_KEY.

4. **Launch the Application:**
   Execute the run script from the root directory:
   `streamlit run "Simple Bank App/main.py"`

---

## ⚠️ Important Notes & Safeguards

- **Data Consistency Protection:** The application utilizes a custom optimistic concurrency locking strategy (update_accounts_safely) to prevent data corruption when multiple transactions happen at the same time.
- **Failure Compensation Handling:** Critical transactional operations utilize a robust _run_with_compensation safety mechanism. If a balance updates successfully but a subsequent database row update fails, the system triggers an automatic roll-back to restore the user's previous balance state safely.
- **Google Sheets API Quotas:** Because Google Sheets imposes strict minute-based query caps, certain automated operations (like deposit renewals or interest payouts) may fail or delay during peak usage. The app handles this gracefully with an automatic retry routine on subsequent page refreshes.
* **Session Persistence & Streamlit Route Bug:** The application utilizes URL query parameters to seamlessly restore and persist user sessions upon a page refresh (F5). Please note that there is a confirmed native Streamlit bug (tracked under GitHub issue #9050) where query parameters are automatically stripped from the visible URL bar immediately following any `st.switch_page()` routing invocation. The application self-heals by instantly rewriting the encrypted auth token back into the URL during the very next render cycle. Consequently, session data loss would only occur if a user manually refreshes the browser within that extremely narrow fraction-of-a-second window.

---

# 🇻🇳 PHIÊN BẢN TIẾNG VIỆT

## 🚀 Các Tính Năng Chính

### 1. Xác Thực & Bảo Mật Hệ Thống
* **Đăng Ký Thông Minh:** Cho phép người dùng mở tài khoản với mật khẩu băm bảo mật bằng bcrypt. Hệ thống tự động gợi ý chọn số tài khoản đẹp theo ngày sinh hoặc dãy số mong muốn.
* **Phục Hồi Phiên Đăng Nhập:** Sử dụng tham số mã hóa auth_token trên URL giúp lưu giữ và phục hồi phiên làm việc một cách an toàn thông qua URLSafeSerializer.
* **Cảnh Báo Hết Hạn Phiên:** Tự động giám sát thời gian thực để kích hoạt hộp thoại cảnh báo khi phiên làm việc hết hiệu lực (tuyệt đối 60 phút) hoặc không hoạt động (quá 10 phút).
* **Bảo Vệ Đăng Nhập Kép (Anti-Hijacking):** Nếu tài khoản được đăng nhập từ một trình duyệt hoặc thiết bị khác, hệ thống sẽ phát hiện ngay lập tức và yêu cầu đổi mật khẩu bảo mật.

### 2. Nghiệp Vụ Tài Chính Cốt Lõi
* **Chuyển Khoản An Toàn:** Hạn mức giao dịch chặt chẽ (Tối thiểu: 10.000 VNĐ, Tối đa: 500.000.000 VNĐ/giao dịch). Đi kèm bộ lọc chuyển tiền bằng chữ tự động và nội dung tùy chỉnh.
* **Quản Lý Thụ Hưởng:** Lưu và quản lý danh bạ người nhận kèm biệt danh nhằm tối ưu thời gian thao tác cho các giao dịch định kỳ.
* **Gửi Tiết Kiệm Kỳ Hạn:** Mở sổ tiết kiệm linh hoạt với cơ chế tự động tái tục (gộp lãi vào gốc) khi đến hạn, rút một phần, hoặc tất toán trước hạn (hưởng lãi suất không kỳ hạn).
* **Quản Lý Khoản Vay (Tín Dụng):** Hạn mức vay được tính toán linh hoạt dựa trên tài sản đảm bảo và sổ tiết kiệm. Tích hợp chính sách giảm lãi suất cho tài khoản thanh toán đúng hạn và cơ chế tự động tách khoản vay ưu đãi.

### 3. Tổng Quan & Lịch Sử Giao Dịch
* **Trang Tổng Quan (Dashboard):** Giao diện thống kê trực quan hiển thị số dư khả dụng, tổng số dư sổ tiết kiệm, tổng dư nợ khoản vay, và lịch sử giao dịch gần đây.
* **Tra Cứu Lịch Sử Nâng Cao:** Bộ lọc giao dịch thông minh theo loại nghiệp vụ, mốc thời gian, kết hợp tính năng phân trang mượt mà.
* **Xuất Dữ Liệu:** Hỗ trợ kết xuất báo cáo sao kê tài khoản trực tiếp thành định dạng file CSV.

### 4. Công Cụ Quản Trị (Admin Panel)
* **Bảng KPI Thống Kê:** Cung cấp số liệu tổng quan toàn hệ thống về lượng người dùng, tổng dòng tiền lưu thông, tổng lượng tiền gửi và nợ xấu quá hạn.
* **Trung Tâm Điều Khiển Người Dùng:** Cho phép Admin điều chỉnh số dư, khóa/mở khóa tài khoản, thay đổi cấp độ quyền hạn, hoặc xóa tài khoản.
* **Chế Độ Giả Lập (Impersonation Mode):** Admin có thể đăng nhập giả lập dưới quyền của một người dùng bất kỳ để kiểm tra lỗi hệ thống, có hỗ trợ cơ chế backup/restore trạng thái tài khoản.

### 5. Địa Phương Hóa & Trợ Lý AI
* Hệ thống quản lý ngôn ngữ tập trung chuyển đổi tức thì giữa Tiếng Việt và Tiếng Anh.
* Tích hợp khung Chatbot Trợ Lý AI (OpenAI/Gemini) đặt cố định tại góc màn hình để hỗ trợ giải đáp thắc mắc tài chính.

---

## 📂 Cấu Trúc Thư Mục
*(Vui lòng xem chi tiết tại sơ đồ cây cấu trúc file ở mục [Project Structure](#project-structure) phía trên).*

---

## 🛠️ Hướng Dẫn Cài Đặt & Khởi Chạy

1. **Tải mã nguồn về máy máy tính:**
   `git clone <repository_url>`
   `cd <repository_directory>`

2. **Cài đặt các thư viện phụ thuộc:**
   Đảm bảo máy tính đã cài đặt Python phiên bản 3.10 trở lên, sau đó thực thi:
   `pip install -r requirements.txt`

3. **Cấu hình tệp bảo mật (Secrets):**
   - Truy cập thư mục `Simple Bank App/.streamlit/`
   - Sao chép file `secrets.toml.example` và đổi tên thành `secrets.toml`
   - Điền đầy đủ các thông tin kết nối API Google Sheets, API Key của OpenAI/Gemini và một khóa ứng dụng SECRET_KEY đủ mạnh.

4. **Khởi chạy ứng dụng Streamlit:**
   Chạy lệnh sau tại thư mục gốc của dự án:
   `streamlit run "Simple Bank App/main.py"`

---

## ⚠️ Lưu Ý Quan Trọng & Cơ Chế Bảo Vệ

- **Đồng Bộ Hóa Dữ tiếp liệu:** Ứng dụng áp dụng cơ chế khóa lạc quan (update_accounts_safely) để ngăn chặn xung đột ghi đè dữ liệu khi có nhiều giao dịch xảy ra đồng thời.
- **Cơ Chế Bù Trừ Lỗi (Compensation):** Các tác vụ tài chính cốt lõi được bảo vệ bằng hàm kiểm soát lỗi hệ thống _run_with_compensation. Nếu bước cập nhật dữ liệu sau bị thất bại, hệ thống sẽ tự động thực hiện lệnh bù trừ để hoàn trả lại số dư trước đó cho khách hàng.
- **Giới Hạn Tần Suất API Google Sheets:** Do Google giới hạn số lượt truy vấn/phút đối với tài khoản Sheets thông thường, một số tiến trình chạy ngầm như tính toán lãi suất hoặc đáo hạn sổ tiết kiệm có thể bị trễ. Hệ thống sẽ tự động kiểm tra và thực hiện bù ở lần tải trang tiếp theo của người dùng.
* **Cơ Chế Giữ Phiên Đăng Nhập & Lỗi Điều Hướng Streamlit:** Ứng dụng sử dụng tham số truy vấn (URL query parameters) nhằm tự động khôi phục và duy trì phiên đăng nhập của người dùng sau khi tải lại trang (F5). Hiện tại, Streamlit đang có một lỗi hệ thống đã được đội ngũ phát triển xác nhận (GitHub issue #9050), khiến các tham số query bị xóa khỏi thanh địa chỉ hiển thị của trình duyệt ngay sau mỗi lần thực thi lệnh chuyển trang `st.switch_page()`. Ứng dụng đã tự động khắc phục bằng cách ghi đè mã hóa token trở lại URL ngay trong lượt render kế tiếp. Do đó, việc mất phiên đăng nhập chỉ có thể xảy ra nếu người dùng cố tình nhấn F5 đúng vào khoảng thời gian cực kỳ ngắn ngủi (vài phần mười giây) trước khi token kịp ghi lại.