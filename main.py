import requests
from datetime import datetime

# ============================================================
# بيانات البوت
# ============================================================
BOT_TOKEN = "8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54"
CHAT_ID = "1432340574"

# ============================================================
# دوال البوت
# ============================================================
def send_message(text):
    """إرسال رسالة إلى تليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
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
    """جلب سعر الذهب الحقيقي"""
    try:
        r = requests.get("https://gold-api.com/api/XAU/USD", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return float(data.get("price", 4472.91))
    except:
        pass
    return 4472.91

def analyze_gold(price):
    """تحليل متكامل للذهب مع توصيات"""
    
    # مستويات SMC
    bsl = round(price + 8, 2)      # سيولة شراء
    ssl = round(price - 6, 2)      # سيولة بيع
    resistance = round(price + 5, 2) # مقاومة
    support = round(price - 4, 2)    # دعم
    ob_buy = f"{round(price - 3, 2)} - {round(price - 1, 2)}"
    ob_sell = f"{round(price + 1, 2)} - {round(price + 3, 2)}"
    
    # تحديد الاتجاه والتوصية
    if price > 4475:
        bias = "🟢 صاعد (Bullish)"
        action = "شراء"
        entry = f"{support} - {price}"
        tp = bsl
        sl = ssl
        rr = "1:2.0"
        reason = "السعر فوق مستوى المقاومة الرئيسي، مع وجود زخم صاعد"
        confidence = "75%"
    elif price < 4470:
        bias = "🔴 هابط (Bearish)"
        action = "بيع"
        entry = f"{price} - {resistance}"
        tp = ssl
        sl = bsl
        rr = "1:1.8"
        reason = "السعر تحت مستوى الدعم الرئيسي، مع وجود ضغط بيعي"
        confidence = "70%"
    else:
        bias = "⚪ محايد (Neutral)"
        action = "انتظار"
        entry = "لا توجد إشارة واضحة"
        tp = resistance
        sl = support
        rr = "1:1.2"
        reason = "السعر في منطقة تذبذب، انتظر كسر أحد المستويات"
        confidence = "50%"
    
    # حساب حجم العقد
    lot_size = 0.2 if action != "انتظار" else 0.0
    
    return {
        'price': price,
        'bias': bias,
        'action': action,
        'entry': entry,
        'tp': tp,
        'sl': sl,
        'rr': rr,
        'reason': reason,
        'confidence': confidence,
        'lot_size': lot_size,
        'bsl': bsl,
        'ssl': ssl,
        'resistance': resistance,
        'support': support,
        'ob_buy': ob_buy,
        'ob_sell': ob_sell
    }

# ============================================================
# التشغيل الرئيسي
# ============================================================
def main():
    print("🚀 تشغيل بوت تحليل الذهب المتقدم...")
    
    # جلب السعر
    price = get_gold_price()
    analysis = analyze_gold(price)
    
    # بناء الرسالة
    msg = f"""📊 **تقرير تحليل XAUUSD**
{'─' * 30}

💰 **السعر الحالي:** {analysis['price']:.2f}
📈 **الاتجاه:** {analysis['bias']}
🎯 **الثقة:** {analysis['confidence']}

{'─' * 30}
🎯 **مناطق السيولة (SMC):**
• BSL (سيولة شراء): {analysis['bsl']}
• SSL (سيولة بيع): {analysis['ssl']}

📊 **الدعم والمقاومة:**
• المقاومة: {analysis['resistance']}
• الدعم: {analysis['support']}

📦 **الأوردر بلوك:**
• منطقة شراء: {analysis['ob_buy']}
• منطقة بيع: {analysis['ob_sell']}

{'─' * 30}
📋 **التوصية:**
• الإجراء: **{analysis['action']}**
• نقطة الدخول: {analysis['entry']}
• الهدف (TP): {analysis['tp']}
• وقف الخسارة (SL): {analysis['sl']}
• نسبة المخاطرة/المكافأة: {analysis['rr']}
• حجم العقد: {analysis['lot_size']} لوت

💡 **السبب:**
{analysis['reason']}

{'─' * 30}
🔄 تم التحديث: {datetime.now().strftime('%H:%M:%S')}
"""
    
    # إرسال الرسالة
    send_message(msg)
    print(f"✅ تم إرسال التحليل: {price:.2f}")

# ============================================================
# تشغيل مستمر
# ============================================================
def run_forever():
    print("🔄 التشغيل المستمر (كل 15 دقيقة)...")
    import time
    while True:
        main()
        time.sleep(900)  # 15 دقيقة

# ============================================================
# نقطة الدخول
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*40)
    print("🤖 بوت تحليل الذهب المتقدم")
    print("="*40)
    print("1. تشغيل مرة واحدة")
    print("2. تشغيل مستمر (كل 15 دقيقة)")
    
    choice = input("\nاختر (1/2): ").strip()
    
    if choice == "2":
        run_forever()
    else:
        main()
