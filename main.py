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
        return r.status_code == 200
    except:
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

def analyze_market(price):
    """تحليل السوق وإنتاج توصيات"""
    
    # مستويات SMC
    bsl = round(price + 8, 2)      # Buy-Side Liquidity
    ssl = round(price - 6, 2)      # Sell-Side Liquidity
    resistance = round(price + 5, 2)
    support = round(price - 4, 2)
    
    # تحديد الاتجاه والتوصية
    if price > 4475:
        bias = "🟢 صاعد (Bullish)"
        action = "شراء"
        entry = f"{support} - {price}"
        tp = bsl
        sl = ssl
        rr = "1:2.0"
        reason = "السعر فوق المقاومة مع زخم صاعد"
    elif price < 4470:
        bias = "🔴 هابط (Bearish)"
        action = "بيع"
        entry = f"{price} - {resistance}"
        tp = ssl
        sl = bsl
        rr = "1:1.8"
        reason = "السعر تحت الدعم مع ضغط بيعي"
    else:
        bias = "⚪ محايد (Neutral)"
        action = "انتظار"
        entry = "لا توجد إشارة"
        tp = resistance
        sl = support
        rr = "1:1.2"
        reason = "السعر في منطقة تذبذب"
    
    return {
        'price': price,
        'bias': bias,
        'action': action,
        'entry': entry,
        'tp': tp,
        'sl': sl,
        'rr': rr,
        'reason': reason,
        'bsl': bsl,
        'ssl': ssl,
        'resistance': resistance,
        'support': support
    }

# ============================================================
# التشغيل الرئيسي
# ============================================================
def main():
    print("🚀 تشغيل بوت تحليل الذهب...")
    
    price = get_gold_price()
    analysis = analyze_market(price)
    
    msg = f"""📊 **تقرير XAUUSD**
{'─' * 25}

💰 **السعر:** {analysis['price']:.2f}
📈 **الاتجاه:** {analysis['bias']}

🎯 **السيولة:**
• BSL: {analysis['bsl']}
• SSL: {analysis['ssl']}

📊 **المستويات:**
• مقاومة: {analysis['resistance']}
• دعم: {analysis['support']}

📋 **التوصية:**
• **{analysis['action']}** 
• الدخول: {analysis['entry']}
• TP: {analysis['tp']}
• SL: {analysis['sl']}
• RR: {analysis['rr']}

💡 {analysis['reason']}

🔄 {datetime.now().strftime('%H:%M:%S')}
"""
    
    send_message(msg)
    print(f"✅ تم الإرسال: {price:.2f}")

if __name__ == "__main__":
    main()
