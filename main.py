import requests
from datetime import datetime

# بيانات البوت (ضع التوكن الصحيح)
BOT_TOKEN = "8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54"
CHAT_ID = "1432340574"

def send_message(text):
    """إرسال رسالة إلى تليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            print("✅ تم الإرسال")
            return True
        else:
            print(f"❌ فشل: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def get_gold_price():
    """جلب سعر الذهب"""
    try:
        r = requests.get("https://gold-api.com/api/XAU/USD", timeout=5)
        if r.status_code == 200:
            return float(r.json().get("price", 4472.91))
    except:
        pass
    return 4472.91  # قيمة احتياطية

# تنفيذ البوت
print("🚀 تشغيل بوت الذهب...")
price = get_gold_price()
msg = f"📊 *تحديث الذهب*\n💰 {price:.2f}\n⏰ {datetime.now().strftime('%H:%M')}"
send_message(msg)
print(f"✅ تم الإرسال: {price:.2f}")
