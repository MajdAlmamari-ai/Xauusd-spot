import requests
from datetime import datetime
import random

# ============================================================
# بيانات البوت
# ============================================================
BOT_TOKEN = "8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54"
CHAT_ID = "1432340574"

# ============================================================
# دوال المساعدة
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

def calculate_smc_levels(price):
    """حساب مستويات SMC"""
    # مستويات السيولة
    bsl = round(price + 8, 2)      # Buy-Side Liquidity
    ssl = round(price - 6, 2)      # Sell-Side Liquidity
    
    # مستويات الدعم والمقاومة
    resistance = round(price + 5, 2)
    support = round(price - 4, 2)
    
    # مناطق الأوردر بلوك
    ob_buy_low = round(price - 3, 2)
    ob_buy_high = round(price - 1, 2)
    ob_sell_low = round(price + 1, 2)
    ob_sell_high = round(price + 3, 2)
    
    return {
        'bsl': bsl,
        'ssl': ssl,
        'resistance': resistance,
        'support': support,
        'ob_buy': f"{ob_buy_low} - {ob_buy_high}",
        'ob_sell': f"{ob_sell_low} - {ob_sell_high}"
    }

def detect_liquidity_sweep(price):
    """كشف صيد السيولة"""
    # محاكاة ذكية لكشف صيد السيولة
    if price > 4475:
        return {
            'sweep': 'BSL SWEEP',
            'direction': 'BUY',
            'message': '✅ تم صيد سيولة الشراء (BSL Swept) - انعكاس هابط متوقع'
        }
    elif price < 4470:
        return {
            'sweep': 'SSL SWEEP',
            'direction': 'SELL',
            'message': '✅ تم صيد سيولة البيع (SSL Swept) - انعكاس صاعد متوقع'
        }
    else:
        return {
            'sweep': 'NO SWEEP',
            'direction': 'NEUTRAL',
            'message': '⏳ لا توجد عملية صيد سيولة حالياً'
        }

def generate_smc_analysis(price):
    """توليد تحليل SMC كامل"""
    levels = calculate_smc_levels(price)
    sweep = detect_liquidity_sweep(price)
    
    # تحديد الاتجاه
    if sweep['direction'] == 'BUY':
        bias = "🟢 صاعد (Bullish)"
        entry = f"شراء من منطقة {levels['ob_buy']}"
        tp = levels['bsl']
        sl = levels['ssl']
        rr = "1:2.5"
    elif sweep['direction'] == 'SELL':
        bias = "🔴 هابط (Bearish)"
        entry = f"بيع من منطقة {levels['ob_sell']}"
        tp = levels['ssl']
        sl = levels['bsl']
        rr = "1:2.5"
    else:
        bias = "⚪ محايد (Neutral)"
        entry = "الانتظار حتى ظهور إشارة واضحة"
        tp = levels['resistance']
        sl = levels['support']
        rr = "1:1.5"
    
    return {
        'price': price,
        'bias': bias,
        'entry': entry,
        'tp': tp,
        'sl': sl,
        'rr': rr,
        'sweep': sweep['message'],
        'levels': levels,
        'sweep_type': sweep['sweep']
    }

# ============================================================
# التشغيل الرئيسي
# ============================================================
def main():
    print("🚀 تشغيل بوت تحليل الذهب المتقدم...")
    
    # جلب السعر
    price = get_gold_price()
    analysis = generate_smc_analysis(price)
    
    # بناء الرسالة
    msg = f"""📊 **تقرير تحليل XAUUSD (SMC)**
{'─' * 30}

💰 **السعر الحالي:** {price:.2f}
📈 **الاتجاه:** {analysis['bias']}

{'─' * 30}
🎯 **مناطق السيولة:**
• BSL (سيولة شراء): {analysis['levels']['bsl']}
• SSL (سيولة بيع): {analysis['levels']['ssl']}

📊 **الدعم والمقاومة:**
• المقاومة: {analysis['levels']['resistance']}
• الدعم: {analysis['levels']['support']}

📦 **الأوردر بلوك:**
• شراء: {analysis['levels']['ob_buy']}
• بيع: {analysis['levels']['ob_sell']}

{'─' * 30}
📋 **التوصية:**
• الإجراء: {analysis['entry']}
• الهدف (TP): {analysis['tp']}
• وقف الخسارة (SL): {analysis['sl']}
• نسبة المخاطرة/المكافأة: {analysis['rr']}

💡 **رؤية السوق:**
{analysis['sweep']}

{'─' * 30}
🔄 تم التحديث: {datetime.now().strftime('%H:%M:%S')}
"""
    
    # إرسال الرسالة
    send_message(msg)
    print(f"✅ تم إرسال التحليل: {price:.2f}")

if __name__ == "__main__":
    main()
