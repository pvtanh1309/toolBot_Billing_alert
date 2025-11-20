# AWS Billing Notifier (Lambda + EventBridge + API Gateway + Budgets)

## 📌 Giới thiệu
Hệ thống này giúp tự động gửi báo cáo chi phí AWS qua Telegram.  
Có thể chạy theo lịch (EventBridge) hoặc gọi thủ công qua API Gateway.

## ⚙️ Thành phần
- **AWS Budgets**: Theo dõi chi phí và ngưỡng cảnh báo.
- **AWS Lambda**: Hàm Python xử lý dữ liệu chi phí.
- **Amazon EventBridge**: Trigger Lambda theo lịch (07:00 và 22:00 VN).
- **Amazon API Gateway**: Endpoint HTTP để gọi Lambda thủ công.
- **Telegram Bot**: Nhận báo cáo chi phí.

## 🔧 Cấu hình
1. Tạo Lambda function (Python 3.12).
2. Copy code từ `lambda_function.py`.
3. Cấu hình biến môi trường:
   - `TELEGRAM_API_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `AWS_REGION`
   - `YOUR_AWS_ACCOUNT_ID`
4. Tạo EventBridge Rule để trigger Lambda theo lịch.
5. (Tuỳ chọn) Tạo API Gateway để gọi Lambda qua HTTP.

## Ví dụ báo cáo
🔔 BÁO CÁO CHI PHÍ AWS

📅 Ngày 2025-11-19 💵 Chi phí: $2.3 📈 +53.3% vs hôm kia

📆 Tháng này (từ 2025-11-01) 💰 Tổng chi: $45.7

✅ Budget MyBudget: • Đã dùng: $45.7 / $100 • Tỷ lệ: 45.7%

📊 Top dịch vụ:

Amazon EC2: $3.5

AWS Lambda: $1.2

Amazon S3: $0.8

━━━━━━━━━━━━━━━━━━ 📈 Năm 2025 (từ 2025-01-01) 💎 Tổng chi: $320.5
