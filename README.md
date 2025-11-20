# AWS Billing Notifier (Lambda + Telegram)

## 📌 Giới thiệu
Đây là hàm **AWS Lambda** dùng để tự động gửi báo cáo chi phí AWS hàng ngày qua **Telegram BotFather**.  
Hàm sẽ chạy theo lịch định sẵn (08:00 và 22:00 giờ Việt Nam) và gửi thông tin chi phí, budget, cùng top dịch vụ tiêu tốn nhiều nhất.

## ⚙️ Cấu hình cần thiết
1. **AWS Services**
   - Lambda (Python 3.12)
   - AWS Cost Explorer
   - AWS Budgets
   - IAM Role với quyền:
     - `ce:GetCostAndUsage`
     - `budgets:DescribeBudget`
     - `kms:Decrypt` (nếu dùng KMS cho secrets)

2. **Biến môi trường Lambda**
   - `TELEGRAM_API_TOKEN` : Token của Telegram Bot
   - `TELEGRAM_CHAT_ID` : Chat ID để gửi báo cáo
   - `AWS_REGION` : Vùng AWS (ví dụ `ap-southeast-1`)
   - `YOUR_AWS_ACCOUNT_ID` : ID tài khoản AWS
   - `BUDGET_NAME` : Tên budget cần theo dõi
   - `TEST_MODE` : `True` để chạy giả lập, `False` để chạy thật

3. **Test Mode**
   - Khi `TEST_MODE=True`, hàm sẽ dùng dữ liệu giả lập:
     ```python
     TEST_YESTERDAY_COST = 2.3
     TEST_MONTH_COST = 45.7
     TEST_YEAR_COST = 320.5
     ```

## 📝 Cách triển khai
1. Tạo Lambda function mới (Python 3.12).
2. Copy toàn bộ code trong `lambda_function.py` vào Lambda.
3. Cấu hình biến môi trường như trên.
4. Tạo **CloudWatch Event Rule** để trigger Lambda lúc 08:00 và 22:00 (giờ VN).
5. Kiểm tra log trong CloudWatch để đảm bảo báo cáo được gửi thành công.

## 📊 Nội dung báo cáo
Ví dụ báo cáo gửi qua Telegram:


