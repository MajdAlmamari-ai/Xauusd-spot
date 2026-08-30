import pandas as pd
import numpy as np
import requests

# ==========================================
# 1. دالة جلب أسعار الذهب الحية
# ==========================================
def fetch_live_gold_data():
    """جلب سعر الذهب المباشر وبناء إطار بيانات للتحليل"""
    url = "https://gold-api.com/api/XAU/USD"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            price = float(response.json().get("price", 2650.0))
            # بناء هيكل حركة السعر استناداً للسعر المباشر
            data = {
                'High': [price + 1.5, price + 3.0, price + 4.5, price + 6.0],
                'Low':  [price - 3.0, price - 1.0, price + 0.5, price + 2.0],
                'Close':[price - 0.5, price + 2.0, price + 3.5, price + 5.0]
            }
            return pd.DataFrame(data)
    except Exception as e:
        print(f"⚠️ تعذر جلب السعر المباشر، جاري استخدام بيانات الاحتياط: {e}")
    
    # بيانات احتياطية في حال تعذر الاتصال بالمزود
    return pd.DataFrame({
        'High': [2645.0, 2648.0, 2655.0, 2658.0],
        'Low':  [2640.0, 2642.0, 2647.0, 2650.0],
        'Close':[2644.0, 2647.0, 2654.0, 2656.0]
    })

# ==========================================
# 2. مؤشر السيولة والحجم (Liquidity & Volume)
# ==========================================
class LiquidityVolumeAnalyzer:
    def __init__(self, high_col='High', low_col='Low', close_col='Close'):
        self.high = high_col
        self.low = low_col
        self.close = close_col

    def analyze(self, df):
        if len(df) < 3:
            return {'signal': 'NEUTRAL', 'reason': 'بيانات غير كافية'}
        
        last_close = df[self.close].iloc[-1]
        prev_high = df[self.high].iloc[-2]
        prev_low = df[self.low].iloc[-2]
        
        if last_close > prev_high:
            return {'signal': 'BUY', 'reason': 'كاسر سيولة شرائية (Buy-side Liquidity Swept)'}
        elif last_close < prev_low:
            return {'signal': 'SELL', 'reason': 'كاسر سيولة بيعية (Sell-side Liquidity Swept)'}
        
        return {'signal': 'NEUTRAL', 'reason': 'تذبذب داخل النطاق'}

# ==========================================
# 3. إدارة المخاطر وعقود التداول (Risk Management)
# ==========================================
class SmartRiskManager:
    def __init__(self, balance=10000.0, risk_per_trade=0.01):
        self.balance = balance
        self.risk_per_trade = risk_per_trade

    def calculate_position(self, entry_price, sl_price, tp_price):
        risk_amount = self.balance * self.risk_per_trade
        sl_pips = abs(entry_price - sl_price)
        
        if sl_pips == 0:
            return None
            
        # حساسية العقود للذهب (1 اللوت = 100 أونصة)
        lot_size = round(risk_amount / (sl_pips * 100), 2)
        lot_size = max(0.01, lot_size) # الحد الأدنى 0.01 لوت
        
        tp_pips = abs(tp_price - entry_price)
        rr_ratio = round(tp_pips / sl_pips, 2)
        
        return {
            'risk_amount': risk_amount,
            'lot_size': lot_size,
            'rr_ratio': rr_ratio
        }

# ==========================================
# 4. بوت تليجرام للتنبيهات (Telegram Bot)
# ==========================================
class TelegramNotifier:
    def __init__(self, token=None, chat_id=None):
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message):
        if not self.token or not self.chat_id:
            print("ℹ️ تنبيه التليجرام: لم يتم إدخال API Token أو Chat ID بعد.")
            return False
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            res = requests.post(url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            print(f"❌ خطأ في إرسال التليجرام: {e}")
            return False

# ==========================================
# 5. النظام الرئيسي للتداول (Trading System)
# ==========================================
class XAUUSD_Trading_System:
    def __init__(self, account_balance=10000.0, telegram_bot_token=None, telegram_chat_id=None):
        self.liquidity = LiquidityVolumeAnalyzer()
        self.risk_mgr = SmartRiskManager(balance=account_balance)
        self.notifier = TelegramNotifier(token=telegram_bot_token, chat_id=telegram_chat_id)

    def process(self, df_5m, mtf_trends):
        # 1. تحليل الاتجاه المتعدد (MTF)
        is_bullish = mtf_trends.get('1h') == 'BUY' and mtf_trends.get('4h') == 'BUY'
        is_bearish = mtf_trends.get('1h') == 'SELL' and mtf_trends.get('4h') == 'SELL'
        
        # 2. تحليل السيولة الحالية
        liq_res = self.liquidity.analyze(df_5m)
        
        current_price = df_5m['Close'].iloc[-1]
        
        # 3. اتخاذ القرار التداولي
        if is_bullish and liq_res['signal'] == 'BUY':
            action = 'BUY'
            sl = current_price - 5.0  # وقف الخسارة 50 نقطة
            tp = current_price + 10.0 # الهدف 100 نقطة
        elif is_bearish and liq_res['signal'] == 'SELL':
            action = 'SELL'
            sl = current_price + 5.0
            tp = current_price - 10.0
        else:
            msg = "⏳ لا توجد فرصة متوافقة مع شروط النظام حالياً."
            self.notifier.send_message(f"ℹ️ **تحديث سوق الذهب:**\n{msg}")
            return msg

        # 4. حساب إدارة المخاطر
        risk_data = self.risk_mgr.calculate_position(current_price, sl, tp)
        
        # 5. صياغة التوصية
        msg = (
            f"🚀 **توصية تداول جديدة على الذهب (XAUUSD)**\n"
            f"----------------------------------------\n"
            f"🔹 **النوع:** {action}\n"
            f"🔹 **سعر الدخول:** {current_price:.2f}\n"
            f"🛑 **وقف الخسارة (SL):** {sl:.2f}\n"
            f"🎯 **الهدف (TP):** {tp:.2f}\n"
            f"----------------------------------------\n"
            f"📊 **حجم العقد المقترح:** {risk_data['lot_size']} لوت\n"
            f"⚖️ **نسبة المخاطرة للمكافأة:** 1:{risk_data['rr_ratio']}\n"
            f"💡 **السبب:** {liq_res['reason']}"
        )
        
        # إرسال التوصية عبر تليجرام
        self.notifier.send_message(msg)
        return msg

# ==========================================
# 6. نقطة التشغيل الرئيسية (Execution)
# ==========================================
if __name__ == "__main__":
    BOT_TOKEN = "8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54"
    CHAT_ID = "1432340574"

    # تشغيل النظام
    system = XAUUSD_Trading_System(
        account_balance=10000.0,
        telegram_bot_token=BOT_TOKEN,
        telegram_chat_id=CHAT_ID
    )

    # 1. جلب البيانات المباشرة
    df_5m = fetch_live_gold_data()
    mtf_trends = {'1h': 'BUY', '4h': 'BUY'}

    # 2. تشغيل التحليل وطباعة التوصية
    recommendation = system.process(df_5m, mtf_trends)
    print(recommendation)
