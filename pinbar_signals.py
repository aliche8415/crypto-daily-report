import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")

COINS = {
    "bitcoin": "بیت‌کوین (BTC)",
    "ethereum": "اتریوم (ETH)",
    "binancecoin": "BNB",
    "ripple": "ریپل (XRP)"
}

def get_1h_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=7"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return []

def is_pinbar(o, h, l, c):
    body = abs(c - o)
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l
    total_range = h - l if h > l else 1
    
    if body / total_range < 0.3:  # بدنه کوچک
        if lower_wick > 2 * body:   # Pin Bar صعودی
            return "🟢 Bullish Pin Bar - سیگنال خرید"
        elif upper_wick > 2 * body: # Pin Bar نزولی
            return "🔴 Bearish Pin Bar - سیگنال فروش"
    return None

def analyze():
    report = "📍 سیگنال Pin Bar (تایم فریم ۱ ساعته)\n\n"
    found_signal = False
    
    for coin_id, name in COINS.items():
        data = get_1h_data(coin_id)
        if len(data) < 5:
            continue
        o, h, l, c = data[-1][1], data[-1][2], data[-1][3], data[-1][4]
        signal = is_pinbar(o, h, l, c)
        
        report += f"{name}:\n"
        report += f"   قیمت: ${c:,.2f}\n"
        if signal:
            report += f"   **{signal}**\n"
            sl = l if "Bullish" in signal else h
            tp = c + (c - sl)*1.5 if "Bullish" in signal else c - (sl - c)*1.5
            report += f"   ورود: ${c:,.2f} | حد ضرر: ${sl:,.2f} | حد سود: ${tp:,.2f}\n\n"
            found_signal = True
        else:
            report += "   سیگنال Pin Bar مشاهده نشد\n\n"
    
    if not found_signal:
        report += "در حال حاضر سیگنال Pin Bar قوی در ۴ ارز اصلی مشاهده نشد."
    
    return report

# Run
report_text = analyze()
report_text += f"\nزمان چک: {datetime.now()}"

print(report_text)

# Send Email
msg = MIMEText(report_text)
msg['Subject'] = f"سیگنال Pin Bar - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
msg['From'] = EMAIL
msg['To'] = TO_EMAIL

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
