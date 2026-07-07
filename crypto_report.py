import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

# ================== تنظیمات ==================
EMAIL = os.getenv("EMAIL")          # ایمیل دریافت‌کننده
PASSWORD = os.getenv("EMAIL_PASS")  # App Password گوگل
TO_EMAIL = os.getenv("TO_EMAIL")    # همون ایمیل خودت

COINS = {
    "bitcoin": "بیت‌کوین (BTC)",
    "ethereum": "اتریوم (ETH)",
    "binancecoin": "BNB",
    "cardano": "کاردانو (ADA)",
    "ripple": "ریپل (XRP)"
}

def get_prices():
    ids = ",".join(COINS.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url)
    return response.json()

def analyze_coin(data, name):
    price = data['usd']
    change = data.get('usd_24h_change', 0)
    
    if change > 5:
        suggestion = "🟢 فرصت خرید خوب (روند صعودی قوی)"
    elif change > 0:
        suggestion = "🟡 روند مثبت - مناسب خرید یا نگه‌داری"
    elif change > -5:
        suggestion = "🟠 احتیاط - ممکن است اصلاح کند"
    else:
        suggestion = "🔴 ریسک بالا - بهتره فعلاً خرید نکنی"
    
    return f"""
{name}:
   • قیمت: ${price:,.2f}
   • تغییر ۲۴ ساعت: {change:.2f}%
   • پیشنهاد: {suggestion}
"""

def send_email(report):
    msg = MIMEText(report)
    msg['Subject'] = f"گزارش روزانه کریپتو - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = EMAIL
    msg['To'] = TO_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, TO_EMAIL, msg.as_string())

# ================== اجرا ==================
data = get_prices()
report = "📊 گزارش روزانه قیمت کریپتوکارنسی‌ها\n\n"

for coin_id, name in COINS.items():
    if coin_id in data:
        report += analyze_coin(data[coin_id], name)

report += f"\n\nگزارش ساخته شده در: {datetime.now()}"

print(report)  # برای تست در GitHub
send_email(report)
