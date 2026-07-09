-- ==============================================================================
-- SCHEMA.SQL — REYNOLD BANK (Simple Bank App)
-- Thiết kế PostgreSQL thay thế hoàn toàn lớp dữ liệu Google Sheets hiện tại
-- (helpers.py: df_init, savings_init, loans_init, transactions_init, beneficiaries_init)
--
-- Tuần 1 / Lộ trình 6 tuần — Reynold
-- ==============================================================================


-- ------------------------------------------------------------------------------
-- 0. EXTENSION CẦN THIẾT
-- ------------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- cho gen_random_uuid()
-- CREATE EXTENSION IF NOT EXISTS "vector";  -- sẽ bật ở Tuần 4 khi làm pgvector


-- ------------------------------------------------------------------------------
-- 1. CÁC KIỂU ENUM — thay cho các cột string tự do trong Google Sheets
--    ('active'/'closed'/'overdue'/'void'... hiện đang gõ tay, dễ gõ sai chính tả
--    và Google Sheets không hề kiểm tra được giá trị hợp lệ)
-- ------------------------------------------------------------------------------
CREATE TYPE savings_status AS ENUM ('active', 'closed', 'void');
CREATE TYPE loan_status AS ENUM ('active', 'overdue', 'closed', 'void');
CREATE TYPE beneficiary_status AS ENUM ('active', 'deleted');

-- Lấy đúng nguyên văn từ ALL_TX_TYPES trong helpers.py
CREATE TYPE transaction_type AS ENUM (
    'transfer_out',
    'transfer_in',
    'savings_open',
    'savings_matured',
    'savings_auto_renew',
    'savings_early_withdraw',
    'savings_partial_withdraw',
    'loan_open',
    'loan_repay_early',
    'loan_partial_repay',
    'loan_repay_matured',
    'loan_forced_paydown',
    'loan_interest_paid',
    'loan_interest_penalty'
);


-- ------------------------------------------------------------------------------
-- 2. HÀM TRIGGER DÙNG CHUNG — tự động cập nhật cột updated_at
--    (Google Sheets không có khái niệm này, muốn biết "sửa lần cuối lúc nào"
--    phải tự ghi cột và tự cập nhật bằng tay ở mọi hàm — rất dễ quên)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ==============================================================================
-- 3. BẢNG accounts — thay thế worksheet "bank_account"
-- ==============================================================================
-- Ghi chú thiết kế:
--   • account_id giữ nguyên là số tài khoản 8 chữ số dạng chuỗi (VARCHAR,
--     KHÔNG dùng UUID) vì đây là nghiệp vụ thật: người dùng được chọn/gợi ý
--     số đẹp lúc đăng ký (xem new_id_suggest, id_num_generate trong helpers.py).
--     Đổi sang UUID sẽ làm mất hẳn tính năng "số tài khoản đẹp" này.
--   • balance dùng BIGINT (đơn vị: đồng VNĐ nguyên, KHÔNG thập phân) để
--     tránh sai số float — nguyên tắc bắt buộc cho mọi cột tiền tệ.
--   • Cột Session ("timestamp|token" ghép chuỗi) trong Sheet cũ được tách
--     thành 2 cột session_token + session_created_at, đúng kiểu dữ liệu
--     (TIMESTAMPTZ thay vì string epoch phải tự parse).
--   • version dùng cho optimistic locking — xem ghi chú cuối file.
CREATE TABLE accounts (
    account_id                   VARCHAR(8)    PRIMARY KEY,
    name                         VARCHAR(255)  NOT NULL,
    date_of_birth                DATE          NOT NULL,
    phone                        VARCHAR(15)   NOT NULL UNIQUE,
    email                        VARCHAR(255)  NOT NULL UNIQUE,
    password_hash                VARCHAR(60)   NOT NULL,     -- bcrypt hash luôn dài 60 ký tự

    balance                      BIGINT        NOT NULL DEFAULT 0,

    session_token                VARCHAR(128),
    session_created_at           TIMESTAMPTZ,
    previous_session_token       VARCHAR(128),
    previous_session_created_at  TIMESTAMPTZ,

    power_level                  SMALLINT      NOT NULL DEFAULT 0,
    is_locked                    BOOLEAN       NOT NULL DEFAULT FALSE,

    version                      INTEGER       NOT NULL DEFAULT 0,
    created_at                   TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at                   TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT chk_accounts_balance_non_negative CHECK (balance >= 0),
    CONSTRAINT chk_accounts_power_level_range CHECK (power_level BETWEEN 0 AND 3),
    CONSTRAINT chk_accounts_id_format CHECK (account_id ~ '^[0-9]{8}$')
);

CREATE TRIGGER trg_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMENT ON COLUMN accounts.power_level IS
    '0=User, 1=Viewer, 2=Moderator, 3=Super Admin (xem POWER_LEVEL_LABELS trong helpers.py)';


-- ==============================================================================
-- 4. BẢNG savings_deposits — thay thế worksheet "savings"
-- ==============================================================================
CREATE TABLE savings_deposits (
    deposit_id      UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      VARCHAR(8)      NOT NULL REFERENCES accounts(account_id),

    principal       BIGINT          NOT NULL,
    annual_rate     NUMERIC(6,4)    NOT NULL,      -- vd 0.0700 = 7%/năm
    term_months     SMALLINT        NOT NULL,

    start_date      DATE            NOT NULL,
    maturity_date   DATE            NOT NULL,
    status          savings_status  NOT NULL DEFAULT 'active',
    auto_renew      BOOLEAN         NOT NULL DEFAULT FALSE,

    version         INTEGER         NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),

    CONSTRAINT chk_savings_principal_positive CHECK (principal > 0),
    CONSTRAINT chk_savings_rate_range CHECK (annual_rate >= 0 AND annual_rate < 1),
    CONSTRAINT chk_savings_term_positive CHECK (term_months > 0),
    CONSTRAINT chk_savings_dates CHECK (maturity_date > start_date)
);

CREATE TRIGGER trg_savings_updated_at
    BEFORE UPDATE ON savings_deposits
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Index bắt buộc: savings.py / summary.py luôn query theo
-- (account_id, status='active') — đây là truy vấn nóng nhất của bảng này.
CREATE INDEX idx_savings_account_status ON savings_deposits (account_id, status);


-- ==============================================================================
-- 5. BẢNG loans — thay thế worksheet "loans"
-- ==============================================================================
CREATE TABLE loans (
    loan_id             UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          VARCHAR(8)    NOT NULL REFERENCES accounts(account_id),

    principal           BIGINT        NOT NULL,
    current_rate        NUMERIC(6,4)  NOT NULL,
    term_months         SMALLINT      NOT NULL,

    start_date          DATE          NOT NULL,
    maturity_date       DATE          NOT NULL,
    status              loan_status   NOT NULL DEFAULT 'active',

    on_time_payments    INTEGER       NOT NULL DEFAULT 0,
    last_interest_date  DATE,                       -- NULL = chưa trả lãi lần nào
    auto_pay            BOOLEAN       NOT NULL DEFAULT FALSE,

    version             INTEGER       NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT chk_loans_principal_positive CHECK (principal > 0),
    CONSTRAINT chk_loans_rate_range CHECK (current_rate >= 0 AND current_rate <= 1),
    CONSTRAINT chk_loans_term_positive CHECK (term_months > 0),
    CONSTRAINT chk_loans_dates CHECK (maturity_date > start_date)
);

CREATE TRIGGER trg_loans_updated_at
    BEFORE UPDATE ON loans
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX idx_loans_account_status ON loans (account_id, status);


-- ==============================================================================
-- 6. BẢNG transactions — thay thế worksheet "transactions"
-- ==============================================================================
-- Ghi chú: reference_id KHÔNG đặt FOREIGN KEY vì nó mang tính "đa hình"
-- (polymorphic) — tùy loại giao dịch mà nó trỏ tới loans.loan_id,
-- savings_deposits.deposit_id, hoặc accounts.account_id khác (vd transfer_out
-- lưu account_id người nhận). Ràng buộc FK cứng ở đây sẽ vướng loại này chặn
-- loại kia. Đây là đánh đổi hợp lý, bình thường cho một bảng log/lịch sử.
CREATE TABLE transactions (
    transaction_id  UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      VARCHAR(8)          NOT NULL REFERENCES accounts(account_id),

    type            transaction_type    NOT NULL,
    amount          BIGINT              NOT NULL,
    reference_id    VARCHAR(64),
    description     TEXT,

    created_at      TIMESTAMPTZ         NOT NULL DEFAULT now(),

    CONSTRAINT chk_transactions_amount_non_negative CHECK (amount >= 0)
);

-- Index bắt buộc: history.py luôn query theo (account_id, created_at DESC)
-- kèm phân trang — thiếu index này, bảng càng lớn trang lịch sử càng chậm dần.
CREATE INDEX idx_tx_account_time ON transactions (account_id, created_at DESC);

-- Hỗ trợ bộ lọc theo loại giao dịch trong history.py / admin_power.py
CREATE INDEX idx_tx_account_type ON transactions (account_id, type);


-- ==============================================================================
-- 7. BẢNG beneficiaries — thay thế worksheet "beneficiaries"
-- ==============================================================================
CREATE TABLE beneficiaries (
    beneficiary_id            UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_account_id          VARCHAR(8)          NOT NULL REFERENCES accounts(account_id),
    beneficiary_account_id    VARCHAR(8)          NOT NULL REFERENCES accounts(account_id),

    nickname                  VARCHAR(50),
    status                    beneficiary_status  NOT NULL DEFAULT 'active',

    version                   INTEGER             NOT NULL DEFAULT 0,
    created_at                TIMESTAMPTZ         NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ         NOT NULL DEFAULT now(),

    CONSTRAINT chk_beneficiaries_not_self
        CHECK (owner_account_id <> beneficiary_account_id)
);

CREATE TRIGGER trg_beneficiaries_updated_at
    BEFORE UPDATE ON beneficiaries
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX idx_beneficiary_owner ON beneficiaries (owner_account_id, status);

-- Quan trọng: is_beneficiary_saved() trong helpers.py chỉ kiểm tra trùng lặp
-- trong số các dòng ĐANG active (soft-delete không tính). Một UNIQUE constraint
-- thường sẽ chặn luôn cả trường hợp thêm lại sau khi đã xóa (status='deleted') —
-- sai với nghiệp vụ gốc. Partial unique index dưới đây tái hiện đúng logic đó
-- ở tầng database: chỉ chặn trùng khi CẢ HAI dòng đều đang active.
CREATE UNIQUE INDEX uq_beneficiaries_active_pair
    ON beneficiaries (owner_account_id, beneficiary_account_id)
    WHERE status = 'active';


-- ==============================================================================
-- 8. GHI CHÚ THIẾT KẾ — ĐỌC TRƯỚC KHI VIẾT FASTAPI Ở TUẦN 2
-- ==============================================================================
-- 1. OPTIMISTIC LOCKING: cột `version` vẫn giữ lại, nhưng cách dùng khác hẳn
--    Google Sheets. Thay vì đọc-toàn-bộ-df rồi ghi-đè-cả-dòng như
--    update_accounts_safely() hiện tại, bạn viết MỘT câu UPDATE atomic:
--
--      UPDATE accounts
--         SET balance = balance - :amount,
--             version = version + 1
--       WHERE account_id = :id
--         AND version = :expected_version;
--
--    Nếu rowcount trả về = 0 -> có người khác đã ghi trước (xung đột) ->
--    tầng FastAPI tự đọc lại + thử lại, y hệt tinh thần OptimisticLockError
--    hiện tại nhưng không cần vòng lặp đọc-so sánh-ghi thủ công nữa, vì
--    WHERE version = :expected đã gộp "kiểm tra + ghi" thành 1 thao tác
--    nguyên tử. SQLAlchemy còn có sẵn cơ chế version_id_col làm việc này
--    tự động — sẽ dùng ở Tuần 3.
--
-- 2. CHUYỂN TIỀN ATOMIC THẬT: money_transfer() sẽ không còn cần
--    _run_with_compensation nữa. Bọc 2 UPDATE (trừ sender, cộng receiver)
--    trong 1 transaction Postgres (BEGIN...COMMIT) — nếu 1 bước lỗi, toàn
--    bộ tự rollback, không còn khoảng hở kiểu "đã trừ tiền nhưng chưa ghi
--    nhận" nữa. Nếu dùng SELECT ... FOR UPDATE để khóa 2 dòng account, luôn
--    khóa theo thứ tự account_id tăng dần để tránh deadlock giữa 2 giao
--    dịch chuyển tiền ngược chiều nhau cùng lúc.
--
-- 3. _sheet_row KHÔNG CÒN CẦN THIẾT: Postgres định vị dòng bằng PRIMARY KEY,
--    nên soft-delete (cột `status`) giờ chỉ còn ý nghĩa nghiệp vụ/audit,
--    không còn ràng buộc kỹ thuật nào bắt bạn phải giữ nó như khi ghi đè
--    theo _sheet_row trong Google Sheets nữa.
-- ==============================================================================
