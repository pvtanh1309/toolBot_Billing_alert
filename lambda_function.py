import os
import json
import boto3
import requests
from datetime import datetime, timedelta, timezone

TELEGRAM_API_TOKEN = "8058574955:AAESzChg0Cv_GGmmErIYvvWugUQqWprgVl8"
TELEGRAM_CHAT_ID = "6568421005"
AWS_REGION = "ap-southeast-1"  # Change to your AWS region
BUDGET_NAME = "LearningBudget"  # Only if you have already created a budget
YOUR_AWS_ACCOUNT_ID = "792023348046"


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("❌ Lỗi gửi Telegram:", response.text)
    else:
        print("✅ Gửi Telegram thành công")

def get_all_costs(ce_client, today):
    """Lấy toàn bộ dữ liệu chi phí chỉ với 1 request CE."""
    current_date = today.strftime('%Y-%m-%d')
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    day_before = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    start_of_year = today.replace(month=1, day=1).strftime('%Y-%m-%d')

    response = ce_client.get_cost_and_usage(
        TimePeriod={'Start': start_of_year, 'End': current_date},
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
    )

    results = response["ResultsByTime"]

    # DAILY 
    def get_day_cost(day_str):
        total = 0
        for day in results:
            if day["TimePeriod"]["Start"] == day_str:
                for g in day["Groups"]:
                    total += float(g["Metrics"]["BlendedCost"]["Amount"])
        return total

    yesterday_cost = get_day_cost(yesterday)
    day_before_cost = get_day_cost(day_before)

    # MONTH 
    month_cost = sum(
        float(g["Metrics"]["BlendedCost"]["Amount"])
        for day in results
        if day["TimePeriod"]["Start"] >= start_of_month
        for g in day["Groups"]
    )

    # YEAR
    year_cost = sum(
        float(g["Metrics"]["BlendedCost"]["Amount"])
        for day in results
        for g in day["Groups"]
    )

    # TOP SERVICES
    service_totals = {}
    for day in results:
        for g in day["Groups"]:
            service = g["Keys"][0]
            amt = float(g["Metrics"]["BlendedCost"]["Amount"])
            service_totals[service] = service_totals.get(service, 0) + amt

    top_services = sorted(service_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    top_services = [{"service": s, "cost": round(c, 2)} for s, c in top_services]

    return {
        "yesterday_cost": round(yesterday_cost, 2),
        "day_before_cost": round(day_before_cost, 2),
        "month_cost": round(month_cost, 2),
        "year_cost": round(year_cost, 2),
        "top_services": top_services
    }

def get_budget_info(budgets_client):
    try:
        r = budgets_client.describe_budget(
            AccountId=YOUR_AWS_ACCOUNT_ID,
            BudgetName=BUDGET_NAME
        )
        budget = r["Budget"]
        limit = float(budget["BudgetLimit"]["Amount"])
        actual = float(budget["CalculatedSpend"]["ActualSpend"]["Amount"])
        percent = round(actual / limit * 100, 1) if limit > 0 else 0

        return {
            "limit": limit,
            "actual": actual,
            "percent": percent
        }
    except Exception as e:
        print("⚠️ Budget error:", e)
        return None

def lambda_handler(event, context):
    print("🚀 Lambda AWS Cost Report running...")

    # Giờ VN = UTC+7
    now_utc = datetime.now(timezone.utc)
    now_vn = now_utc + timedelta(hours=7)

    # Chỉ gửi vào 07:00 và 22:00 VN
    if now_vn.hour not in [7, 22]:
        print(f"⏱ Không phải giờ gửi báo cáo ({now_vn.hour}h VN)")
        return {"statusCode": 200, "body": "Not scheduled hour"}

    today = datetime.utcnow()

    ce_client = boto3.client("ce", region_name=AWS_REGION)
    budgets_client = boto3.client("budgets", region_name=AWS_REGION)

    # Extract
    y_cost = cost_data["yesterday_cost"]
    d_cost = cost_data["day_before_cost"]
    m_cost = cost_data["month_cost"]
    ytd_cost = cost_data["year_cost"]
    top_svc = cost_data["top_services"]

    # % CHANGE
    if d_cost > 0:
        diff = ((y_cost - d_cost) / d_cost) * 100
        diff_txt = f"{'📈' if diff > 0 else '📉'} {abs(diff):.1f}% vs hôm kia"
    else:
        diff_txt = "➖ Không có dữ liệu so sánh"

    budget = get_budget_info(budgets_client)

    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    start_of_year = today.replace(month=1, day=1).strftime('%Y-%m-%d')

    msg = [
        "🔔 *BÁO CÁO CHI PHÍ AWS*",
        "",
        f"📅 *Ngày {yesterday}*",
        f"💵 Chi phí: *${y_cost}*",
        f"   {diff_txt}",
        "",
        f"📆 *Tháng này* (từ {start_of_month})",
        f"💰 Tổng chi: *${m_cost}*",
        ""
    ]

    if budget:
        emoji = "✅" if budget["percent"] < 80 else "⚠️" if budget["percent"] < 100 else "🚨"
        msg += [
            f"{emoji} *Budget {BUDGET_NAME}:*",
            f"   • Đã dùng: ${budget['actual']} / ${budget['limit']}",
            f"   • Tỷ lệ: {budget['percent']}%",
            ""
        ]

    if top_svc:
        msg.append("📊 *Top dịch vụ:*")
        for i, svc in enumerate(top_svc, 1):
            msg.append(f"   {i}. {svc['service']}: ${svc['cost']}")
        msg.append("")

    msg += [
        "━━━━━━━━━━━━━━━━━━",
        f"📈 *Năm {today.year}* (từ {start_of_year})",
        f"💎 Tổng chi: *${ytd_cost}*",
        "",
        f"_Cập nhật lúc {now_vn.strftime('%H:%M:%S')} (VN)_"
    ]

    message = "\n".join(msg)

    print(message)
    send_telegram_message(message)

    return {"statusCode": 200, "body": "Report sent!"}