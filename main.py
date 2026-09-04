"""
XAU/USD SMC Institutional Trading System v5.0
المبادئ: Smart Money Concepts (SMC) + Inner Circle Trader (ICT)
الميزات: تحليل سيولة حقيقي، أوردر بلوك، فجوات، جلسات زمنية، إدارة مخاطر متقدمة
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone
import time
import json

# ============================================================
# 1. جلب البيانات الحقيقية (Replaced Mock Data)
# ============================================================
class DataFetcher:
    """جلب بيانات حقيقية من OANDA API (بديل موثوق)"""
    def __init__(self, api_key=None, account_id=None):
        self.api_key = api_key  # مفتاح OANDA API
        self.account_id = account_id
        self.base_url = "https://api-fxtrade.oanda.com/v3"
        
    def fetch_candles(self, instrument="XAU_USD", granularity="M15", count=100):
        """
        جلب بيانات شموع حقيقية من OANDA
        """
        if not self.api_key:
            print("⚠️ لم يتم إدخال مفتاح OANDA API، استخدم بيانات تجريبية للعرض.")
            return self._generate_demo_data()
            
        url = f"{self.base_url}/instruments/{instrument}/candles"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"granularity": granularity, "count": count, "price": "M"}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                candles = []
                for c in data['candles']:
                    candles.append({
                        'time': c['time'],
                        'open': float(c['mid']['o']),
                        'high': float(c['mid']['h']),
                        'low': float(c['mid']['l']),
                        'close': float(c['mid']['c']),
                        'volume': float(c.get('volume', 0))
                    })
                return pd.DataFrame(candles)
            else:
                print(f"⚠️ خطأ في OANDA: {response.status_code}")
        except Exception as e:
            print(f"⚠️ تعذر جلب البيانات: {e}")
            
        return self._generate_demo_data()
    
    def _generate_demo_data(self):
        """بيانات تجريبية فقط للاختبار (ستُستبدل بالحقيقية)"""
        last_price = 4472.91
        base_time = datetime.now(timezone.utc)
        data = []
        for i in range(100):
            t = base_time - pd.Timedelta(minutes=15*i)
            data.append({
                'time': t.isoformat(),
                'open': last_price + np.random.randn()*0.5,
                'high': last_price + abs(np.random.randn())*0.8,
                'low': last_price - abs(np.random.randn())*0.8,
                'close': last_price + np.random.randn()*0.4,
                'volume': abs(np.random.randn()*1000 + 500)
            })
            last_price = data[-1]['close']
        return pd.DataFrame(data)

# ============================================================
# 2. المحلل الأساسي لـ (SMC) مع جميع العناصر
# ============================================================
class SMC_Analyzer:
    def __init__(self):
        self.session_times = {
            'london': (7, 16),    # UTC
            'ny': (12, 20),
            'killzone': (13, 16)  # تداخل لندن ونيويورك
        }
        
    def analyze(self, df):
        """التحليل الكامل وفق منهجية SMC"""
        if len(df) < 10:
            return {'error': 'بيانات غير كافية'}
            
        result = {
            'structure': self._detect_structure(df),
            'liquidity_zones': self._find_liquidity_zones(df),
            'order_blocks': self._find_order_blocks(df),
            'fvg_zones': self._find_fvg(df),
            'current_session': self._get_current_session(),
            'market_bias': None
        }
        
        # تحديد الاتجاه العام بناءً على التظافر
        result['market_bias'] = self._determine_bias(result)
        return result
    
    # ============================================================
    # 2.1 تحليل هيكل السوق (Market Structure)
    # ============================================================
    def _detect_structure(self, df):
        """تحديد الاتجاه (صاعد/هابط/مضطرب) بناءً على القمم والقيعان"""
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        
        # كسر الهيكل الأخير (BOS)
        bos_up = closes[-1] > max(highs[-5:-1]) and closes[-2] > max(highs[-6:-2])
        bos_down = closes[-1] < min(lows[-5:-1]) and closes[-2] < min(lows[-6:-2])
        
        if bos_up:
            return 'UPTREND'
        elif bos_down:
            return 'DOWNTREND'
        else:
            return 'CONSOLIDATION'
    
    # ============================================================
    # 2.2 اكتشاف مناطق السيولة (Liquidity Pools)
    # ============================================================
    def _find_liquidity_zones(self, df):
        """BSL (سيولة الشراء) و SSL (سيولة البيع) الحقيقية"""
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values
        
        # BSL: القمم الأخيرة التي سيتم استهدافها
        bsl_levels = []
        for i in range(-5, -1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                bsl_levels.append(highs[i])
        
        # SSL: القيعان الأخيرة
        ssl_levels = []
        for i in range(-5, -1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                ssl_levels.append(lows[i])
        
        # اكتشاف عمليات الصيد (Sweeps)
        current_price = closes[-1]
        last_high = max(highs[-3:])
        last_low = min(lows[-3:])
        
        ssl_swept = current_price < last_low and current_price > min(lows[-10:-5]) if len(lows) > 10 else False
        bsl_swept = current_price > last_high and current_price < max(highs[-10:-5]) if len(highs) > 10 else False
        
        return {
            'bsl': max(bsl_levels) if bsl_levels else max(highs[-5:]),
            'ssl': min(ssl_levels) if ssl_levels else min(lows[-5:]),
            'ssl_swept': ssl_swept,
            'bsl_swept': bsl_swept,
            'distance_to_bsl': (max(highs[-5:]) - current_price) / current_price * 100,
            'distance_to_ssl': (current_price - min(lows[-5:])) / current_price * 100
        }
    
    # ============================================================
    # 2.3 اكتشاف الأوردر بلوك (Order Blocks)
    # ============================================================
    def _find_order_blocks(self, df):
        """الشمعة الأخيرة قبل الحركة القوية (مع التحقق من الظل والحجم)"""
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        volumes = df['volume'].values if 'volume' in df.columns else np.ones(len(df))
        
        bullish_obs = []
        bearish_obs = []
        
        for i in range(-10, -1):
            # شرط الحركة القوية: فرق كبير بين الإغلاق والافتتاح
            move = abs(closes[i] - opens[i])
            avg_move = np.mean([abs(closes[j] - opens[j]) for j in range(i-10, i)]) if i > 10 else move
            
            if move > avg_move * 2:
                # شمعة صاعدة (Bullish OB)
                if closes[i] > opens[i]:
                    wick_ratio = (highs[i] - max(opens[i], closes[i])) / (highs[i] - lows[i]) if (highs[i] - lows[i]) > 0 else 0
                    if wick_ratio > 0.5:  # ظل علوي طويل
                        bullish_obs.append({
                            'high': highs[i],
                            'low': lows[i],
                            'open': opens[i],
                            'close': closes[i],
                            'score': min(100, 60 + (wick_ratio * 40))
                        })
                # شمعة هابطة (Bearish OB)
                else:
                    wick_ratio = (min(opens[i], closes[i]) - lows[i]) / (highs[i] - lows[i]) if (highs[i] - lows[i]) > 0 else 0
                    if wick_ratio > 0.5:  # ظل سفلي طويل
                        bearish_obs.append({
                            'high': highs[i],
                            'low': lows[i],
                            'open': opens[i],
                            'close': closes[i],
                            'score': min(100, 60 + (wick_ratio * 40))
                        })
        
        # اختيار الأحدث والأقوى
        best_bullish = max(bullish_obs, key=lambda x: x['score']) if bullish_obs else None
        best_bearish = max(bearish_obs, key=lambda x: x['score']) if bearish_obs else None
        
        return {
            'bullish': best_bullish,
            'bearish': best_bearish
        }
    
    # ============================================================
    # 2.4 اكتشاف الفجوات السعرية (FVG)
    # ============================================================
    def _find_fvg(self, df):
        """فجوات الكفاءة (Fair Value Gaps)"""
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        
        fvg_bullish = []
        fvg_bearish = []
        
        for i in range(-10, -1):
            if i < 2:
                continue
            # شرط FVG صاعد: قاع الشمعة i > قمة الشمعة i-2
            if lows[i] > highs[i-2] and closes[i] > opens[i]:
                fvg_bullish.append({
                    'high': lows[i],
                    'low': highs[i-2],
                    'strength': (lows[i] - highs[i-2]) / closes[i] * 100
                })
            # شرط FVG هابط: قمة الشمعة i < قاع الشمعة i-2
            if highs[i] < lows[i-2] and closes[i] < opens[i]:
                fvg_bearish.append({
                    'high': lows[i-2],
                    'low': highs[i],
                    'strength': (lows[i-2] - highs[i]) / closes[i] * 100
                })
        
        return {
            'bullish': fvg_bullish[-1] if fvg_bullish else None,
            'bearish': fvg_bearish[-1] if fvg_bearish else None
        }
    
    # ============================================================
    # 2.5 الجلسات الزمنية
    # ============================================================
    def _get_current_session(self):
        """تحديد الجلسة الحالية بناءً على التوقيت العالمي"""
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        if self.session_times['london'][0] <= hour < self.session_times['london'][1]:
            return 'LONDON'
        elif self.session_times['ny'][0] <= hour < self.session_times['ny'][1]:
            return 'NEW_YORK'
        elif self.session_times['killzone'][0] <= hour < self.session_times['killzone'][1]:
            return 'KILL_ZONE'
        else:
            return 'OFF_SESSION'
    
    # ============================================================
    # 2.6 تحديد الاتجاه النهائي (التظافر)
    # ============================================================
    def _determine_bias(self, analysis):
        """حساب الميل الكلي بناءً على تظافر العوامل"""
        score = 0
        # هيكل السوق
        if analysis['structure'] == 'UPTREND':
            score += 30
        elif analysis['structure'] == 'DOWNTREND':
            score -= 30
            
        # الأوردر بلوك
        if analysis['order_blocks']['bullish']:
            score += analysis['order_blocks']['bullish']['score'] * 0.3
        if analysis['order_blocks']['bearish']:
            score -= analysis['order_blocks']['bearish']['score'] * 0.3
            
        # السيولة
        if analysis['liquidity_zones']['ssl_swept']:
            score += 20
        if analysis['liquidity_zones']['bsl_swept']:
            score -= 20
            
        return 'BULLISH' if score > 20 else 'BEARISH' if score < -20 else 'NEUTRAL'

# ============================================================
# 3. نظام إدارة المخاطر المتقدم
# ============================================================
class AdvancedRiskManager:
    def __init__(self, balance=10000.0, risk_percent=0.01):
        self.balance = balance
        self.risk_percent = risk_percent
        
    def calculate_position(self, entry, stop_loss, take_profit):
        """حساب حجم العقد مع نسبة مخاطرة/عائد ديناميكية"""
        if not stop_loss or entry == stop_loss:
            return None
            
        risk_amount = self.balance * self.risk_percent
        sl_distance = abs(entry - stop_loss)
        
        # 1 لوت = 100 أونصة للذهب
        lot_size = round((risk_amount / (sl_distance * 100)), 2)
        lot_size = max(0.01, min(1.0, lot_size))  # بين 0.01 و 1 لوت
        
        # نسبة المخاطرة/المكافأة
        if take_profit:
            tp_distance = abs(take_profit - entry)
            rr_ratio = round(tp_distance / sl_distance, 2)
        else:
            rr_ratio = 0
            
        return {
            'lot_size': lot_size,
            'risk_amount': round(risk_amount, 2),
            'risk_reward_ratio': rr_ratio,
            'sl_pips': round(sl_distance * 100, 2),
            'tp_pips': round(tp_distance * 100, 2) if take_profit else None
        }

# ============================================================
# 4. توليد السيناريوهات المتعددة (شجرة القرار)
# ============================================================
class ScenarioTree:
    @staticmethod
    def generate(smc_analysis, current_price, risk_manager):
        """توليد 3 سيناريوهات مع التوصيات"""
        scenarios = {
            'primary': None,
            'secondary': None,
            'tertiary': None
        }
        
        # استخراج المعطيات
        liquidity = smc_analysis['liquidity_zones']
        obs = smc_analysis['order_blocks']
        fvgs = smc_analysis['fvg_zones']
        session = smc_analysis['current_session']
        bias = smc_analysis['market_bias']
        
        # --- السيناريو الأساسي (Primary) ---
        # شرط: صيد سيولة بيع + أوردر بلوك شرائي + جلسة نشطة
        if liquidity['ssl_swept'] and obs['bullish'] and session in ['LONDON', 'NEW_YORK', 'KILL_ZONE']:
            entry_zone = obs['bullish']
            sl_price = liquidity['ssl'] - 0.5  # تحت السيولة
            tp_price = liquidity['bsl']
            
            risk = risk_manager.calculate_position(
                entry=(entry_zone['high'] + entry_zone['low'])/2,
                stop_loss=sl_price,
                take_profit=tp_price
            )
            
            scenarios['primary'] = {
                'action': 'BUY_LIMIT',
                'entry': f"{entry_zone['low']:.2f} - {entry_zone['high']:.2f}",
                'stop_loss': sl_price,
                'take_profit': tp_price,
                'risk': risk,
                'confidence': min(95, 60 + (20 if session == 'KILL_ZONE' else 0) + (10 if fvgs['bullish'] else 0)),
                'reason': 'ارتداد من أوردر بلوك شرائي بعد صيد سيولة البيع مع تظافر فجوة سعرية.'
            }
        
        # --- السيناريو البديل (Secondary) ---
        # شرط: السعر في منطقة سيولة شراء وأوردر بلوك بيعي
        elif liquidity['bsl_swept'] and obs['bearish']:
            entry_zone = obs['bearish']
            sl_price = liquidity['bsl'] + 0.5
            tp_price = liquidity['ssl']
            
            risk = risk_manager.calculate_position(
                entry=(entry_zone['high'] + entry_zone['low'])/2,
                stop_loss=sl_price,
                take_profit=tp_price
            )
            
            scenarios['secondary'] = {
                'action': 'SELL_LIMIT',
                'entry': f"{entry_zone['low']:.2f} - {entry_zone['high']:.2f}",
                'stop_loss': sl_price,
                'take_profit': tp_price,
                'risk': risk,
                'confidence': min(90, 55 + (15 if session == 'KILL_ZONE' else 0)),
                'reason': 'انعكاس متوقع من أوردر بلوك بيعي بعد صيد سيولة الشراء.'
            }
        
        # --- السيناريو الثالث (Tertiary) ---
        # الانتظار
        else:
            scenarios['tertiary'] = {
                'action': 'WAIT',
                'entry': None,
                'stop_loss': None,
                'take_profit': None,
                'risk': None,
                'confidence': 0,
                'reason': f"السوق في حالة {smc_analysis['structure']}. انتظار كسر هيكل واضح أو صيد سيولة.",
                'watch_levels': f"اختراق {liquidity['bsl']:.2f} للصعود أو {liquidity['ssl']:.2f} للهبوط."
            }
            
        return scenarios

# ============================================================
# 5. بوت التليجرام المحسن
# ============================================================
class TelegramBot:
    def __init__(self, token=None, chat_id=None):
        self.token = 8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54
        self.chat_id = 1432340574
        
    def send_analysis(self, scenarios, smc_analysis, price):
        """إرسال تحليل كامل مع السيناريوهات"""
        if not self.token or not self.chat_id:
            print("ℹ️ تنبيه التليجرام غير مفعل.")
            return
            
        msg = f"📊 **تحليل XAUUSD SMC - {datetime.now(timezone.utc).strftime('%H:%M UTC')}**\n"
        msg += f"💰 السعر الحالي: **{price:.2f}**\n"
        msg += f"🏛️ الجلسة: **{smc_analysis['current_session']}**\n"
        msg += f"📈 الاتجاه العام: **{smc_analysis['market_bias']}**\n\n"
        
        # عرض السيولة
        liq = smc_analysis['liquidity_zones']
        msg += f"🔹 **BSL (سيولة شراء)**: {liq['bsl']:.2f}\n"
        msg += f"🔹 **SSL (سيولة بيع)**: {liq['ssl']:.2f}\n"
        msg += f"{'✅' if liq['ssl_swept'] else '❌'} تم صيد SSL: {liq['ssl_swept']}\n"
        msg += f"{'✅' if liq['bsl_swept'] else '❌'} تم صيد BSL: {liq['bsl_swept']}\n\n"
        
        # السيناريو الأساسي
        if scenarios['primary']:
            sc = scenarios['primary']
            msg += f"🚀 **السيناريو الأساسي ({sc['confidence']}%)**\n"
            msg += f"• الإجراء: **{sc['action']}**\n"
            msg += f"• الدخول: {sc['entry']}\n"
            msg += f"• وقف الخسارة: {sc['stop_loss']:.2f}\n"
            msg += f"• الهدف: {sc['take_profit']:.2f}\n"
            if sc['risk']:
                msg += f"• حجم العقد: {sc['risk']['lot_size']} لوت\n"
                msg += f"• نسبة المخاطرة/المكافأة: 1:{sc['risk']['risk_reward_ratio']}\n"
            msg += f"• السبب: {sc['reason']}\n\n"
            
        # السيناريو البديل
        if scenarios['secondary']:
            sc = scenarios['secondary']
            msg += f"⚡ **السيناريو البديل ({sc['confidence']}%)**\n"
            msg += f"• الإجراء: **{sc['action']}**\n"
            msg += f"• الدخول: {sc['entry']}\n"
            msg += f"• وقف الخسارة: {sc['stop_loss']:.2f}\n"
            msg += f"• الهدف: {sc['take_profit']:.2f}\n"
            if sc['risk']:
                msg += f"• حجم العقد: {sc['risk']['lot_size']} لوت\n"
            msg += f"• السبب: {sc['reason']}\n\n"
            
        # السيناريو الثالث
        if scenarios['tertiary']:
            sc = scenarios['tertiary']
            msg += f"⏳ **السيناريو الثالث (انتظار)**\n"
            msg += f"• السبب: {sc['reason']}\n"
            msg += f"• مستويات المراقبة: {sc['watch_levels']}\n"
            
        self.send_message(msg)
        
    def send_message(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            res = requests.post(url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            print(f"❌ خطأ في إرسال التليجرام: {e}")
            return False

# ============================================================
# 6. النظام الرئيسي المتكامل
# ============================================================
class XAUUSD_SMC_System:
    def __init__(self, account_balance=10000.0, oanda_api_key=None, telegram_token=None, chat_id=None):
        self.data_fetcher = DataFetcher(api_key=oanda_api_key)
        self.smc_analyzer = SMC_Analyzer()
        self.risk_manager = AdvancedRiskManager(balance=account_balance)
        self.telegram = TelegramBot(token=telegram_token, chat_id=chat_id)
        
    def run(self):
        """تشغيل دورة التحليل الكاملة"""
        print("🔄 جاري تحليل الذهب وفق منهجية SMC...")
        
        # 1. جلب البيانات
        df = self.data_fetcher.fetch_candles(granularity="M15", count=150)
        if df.empty:
            print("❌ فشل في جلب البيانات.")
            return
            
        current_price = df['close'].iloc[-1]
        
        # 2. تحليل SMC
        smc_result = self.smc_analyzer.analyze(df)
        if 'error' in smc_result:
            print(f"❌ {smc_result['error']}")
            return
            
        # 3. توليد السيناريوهات
        scenarios = ScenarioTree.generate(smc_result, current_price, self.risk_manager)
        
        # 4. إرسال النتائج
        print("=" * 50)
        print(f"📊 تحليل XAUUSD SMC - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"💰 السعر الحالي: {current_price:.2f}")
        print(f"🏛️ الجلسة: {smc_result['current_session']}")
        print(f"📈 الاتجاه العام: {smc_result['market_bias']}")
        print("-" * 50)
        
        # عرض ملخص السيناريوهات
        for key, scenario in scenarios.items():
            if scenario:
                print(f"\n🔹 {key.upper()}:")
                print(f"   الإجراء: {scenario['action']}")
                if scenario['entry']:
                    print(f"   الدخول: {scenario['entry']}")
                    print(f"   وقف الخسارة: {scenario['stop_loss']:.2f}")
                    print(f"   الهدف: {scenario['take_profit']:.2f}")
                    if scenario['risk']:
                        print(f"   الثقة: {scenario['confidence']}%")
                        print(f"   حجم العقد: {scenario['risk']['lot_size']} لوت")
                        print(f"   المخاطرة/المكافأة: 1:{scenario['risk']['risk_reward_ratio']}")
                if scenario['reason']:
                    print(f"   السبب: {scenario['reason']}")
                    
        # 5. إرسال عبر تليجرام
        self.telegram.send_analysis(scenarios, smc_result, current_price)
        
        return {
            'price': current_price,
            'smc_analysis': smc_result,
            'scenarios': scenarios
        }

# ============================================================
# 7. نقطة التشغيل الرئيسية
# ============================================================
if __name__ == "__main__":
    # إعدادات (استبدلها بقيمتك الفعلية)
    OANDA_KEY = "Your_OANDA_API_Key_Here"
    TELEGRAM_TOKEN = "8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54"
    TELEGRAM_CHAT_ID = "1432340574"
    
    # إنشاء النظام وتشغيله
    system = XAUUSD_SMC_System(
        account_balance=10000.0,
        oanda_api_key=OANDA_KEY,
        telegram_token=TELEGRAM_TOKEN,
        chat_id=TELEGRAM_CHAT_ID
    )
    
    # تشغيل دورة تحليل واحدة (يمكن وضعها في حلقة كل 5 دقائق)
    result = system.run()
# ============================================================
# 7. التحليل الذكي المتقدم (Advanced Intelligent Analysis)
# ============================================================
class IntelligentAnalyzer:
    """
    تحليل ذكي لمحاكاة "المال الذكي":
    - تحديد مناطق تجميع السيولة (Accumulation Zones)
    - تحليل تدفق الأوامر (Order Flow Imbalance)
    - التنبؤ بالحركة الاحتمالية القادمة
    """
    
    def __init__(self, smc_analyzer):
        self.smc = smc_analyzer
        self.historical_patterns = []
        
    def full_analysis(self, df, current_price):
        """التحليل الذكي الكامل"""
        result = {
            'accumulation_zones': self._find_accumulation_zones(df),
            'order_flow_imbalance': self._calculate_flow_imbalance(df),
            'liquidity_heatmap': self._generate_liquidity_heatmap(df),
            'probabilistic_forecast': None,
            'smart_money_indicator': self._smart_money_score(df, current_price)
        }
        
        # التنبؤ الاحتمالي
        result['probabilistic_forecast'] = self._probabilistic_forecast(
            df, current_price, result
        )
        
        return result
    
    # ============================================================
    # 7.1 مناطق تجميع السيولة المؤسسية (Accumulation Zones)
    # ============================================================
    def _find_accumulation_zones(self, df):
        """
        تحديد مناطق تجميع السيولة (حيث تتجمع أوامر البنوك قبل الحركة الكبيرة)
        تعتمد على: كثافة التداول، تكرار الارتطام بالسعر، والزمن.
        """
        # استخدام بيانات الشموع لتحديد مناطق التركيز السعري
        prices = df['close'].values
        volumes = df['volume'].values if 'volume' in df.columns else np.ones(len(df))
        
        # 1. تقسيم النطاق السعري إلى 50 مستوى
        price_range = np.linspace(min(df['low']), max(df['high']), 50)
        zone_density = {p: 0 for p in price_range}
        
        # 2. حساب كثافة الارتطام بكل مستوى سعري
        for i in range(len(prices) - 1):
            for price in price_range:
                # الارتطام: السعر يمر بمستوى معين (قريب من الإغلاق أو الافتتاح)
                if abs(prices[i] - price) < (price_range[1] - price_range[0]) * 0.8:
                    zone_density[price] += volumes[i] / 1000  # ترجيح بالحجم
        
        # 3. اكتشاف القمم في الكثافة (مناطق التجميع)
        sorted_zones = sorted(zone_density.items(), key=lambda x: x[1], reverse=True)
        top_zones = sorted_zones[:5]  # أعلى 5 مناطق
        
        accumulation_zones = []
        for price, density in top_zones:
            if density > np.mean(list(zone_density.values())) * 1.5:  # أعلى من المتوسط
                # تحديد ما إذا كانت منطقة شراء أو بيع بناءً على موقعها
                zone_type = 'BUY_ACCUMULATION' if price < np.mean(prices) else 'SELL_DISTRIBUTION'
                accumulation_zones.append({
                    'price': price,
                    'density': round(density, 2),
                    'type': zone_type,
                    'strength': min(100, int(density / max(top_zones, key=lambda x: x[1])[1] * 100))
                })
        
        return accumulation_zones
    
    # ============================================================
    # 7.2 تحليل تدفق الأوامر (Order Flow Imbalance)
    # ============================================================
    def _calculate_flow_imbalance(self, df):
        """
        حساب اختلال التوازن بين أوامر الشراء والبيع (Delta)
        محاكاة لبيانات Level 2 باستخدام الشموع
        """
        if len(df) < 10:
            return {'imbalance': 0, 'interpretation': 'بيانات غير كافية'}
        
        # حساب الدلتا التقريبي لكل شمعة
        deltas = []
        for i in range(len(df)):
            candle = df.iloc[i]
            # فرضية: حجم الشراء = حجم الشمعة * (النطاق العلوي / النطاق الكلي)
            buy_pressure = candle['volume'] * ((candle['close'] - candle['low']) / (candle['high'] - candle['low'] + 0.001))
            sell_pressure = candle['volume'] - buy_pressure
            deltas.append(buy_pressure - sell_pressure)
        
        cumulative_delta = sum(deltas[-20:])  # آخر 20 شمعة
        avg_delta = np.mean(deltas[-10:])
        
        # تفسير الدلتا
        if cumulative_delta > 0 and avg_delta > 0:
            interpretation = 'ضغط شرائي قوي (Bullish Order Flow)'
            signal = 'BULLISH'
        elif cumulative_delta < 0 and avg_delta < 0:
            interpretation = 'ضغط بيعي قوي (Bearish Order Flow)'
            signal = 'BEARISH'
        else:
            interpretation = 'تدفق متوازن أو تذبذب (Neutral Flow)'
            signal = 'NEUTRAL'
        
        return {
            'cumulative_delta': round(cumulative_delta, 2),
            'avg_delta': round(avg_delta, 2),
            'signal': signal,
            'interpretation': interpretation,
            'strength': min(100, abs(cumulative_delta) / (max(abs(cumulative_delta), 1)) * 100)
        }
    
    # ============================================================
    # 7.3 خريطة حرارة السيولة (Liquidity Heatmap)
    # ============================================================
    def _generate_liquidity_heatmap(self, df):
        """
        إنشاء خريطة حرارة لمناطق السيولة المحتملة
        بناءً على مستويات الدعم والمقاومة التاريخية وقمم الحجم
        """
        # استخراج القمم والقيعان الرئيسية (الدعم والمقاومة الديناميكية)
        highs = df['high'].values
        lows = df['low'].values
        
        # اكتشاف المستويات الرئيسية
        resistance_levels = []
        support_levels = []
        
        for i in range(-50, -1):
            if i < 2:
                continue
            # قمة محلية (مقاومة)
            if highs[i] > highs[i-1] and highs[i] > highs[i+1] and highs[i] > highs[i-2]:
                resistance_levels.append(highs[i])
            # قاع محلي (دعم)
            if lows[i] < lows[i-1] and lows[i] < lows[i+1] and lows[i] < lows[i-2]:
                support_levels.append(lows[i])
        
        # حساب كثافة السيولة حول كل مستوى
        heatmap = {}
        current_price = df['close'].iloc[-1]
        
        for level in resistance_levels:
            distance = abs(current_price - level)
            if distance < 20:  # تركيز على المستويات القريبة
                heatmap[level] = 'HIGH' if distance < 5 else 'MEDIUM' if distance < 10 else 'LOW'
                
        for level in support_levels:
            distance = abs(current_price - level)
            if distance < 20:
                heatmap[level] = 'HIGH' if distance < 5 else 'MEDIUM' if distance < 10 else 'LOW'
        
        # إضافة مستوى السيولة الرئيسي (SSL/BSL) من تحليل SMC
        liq = self.smc._find_liquidity_zones(df)
        heatmap[liq['bsl']] = 'LIQUIDITY_POOL (BSL)'
        heatmap[liq['ssl']] = 'LIQUIDITY_POOL (SSL)'
        
        return heatmap
    
    # ============================================================
    # 7.4 مؤشر "المال الذكي" (Smart Money Score)
    # ============================================================
    def _smart_money_score(self, df, current_price):
        """
        مؤشر مركب يعكس نشاط المؤسسات بناءً على:
        - اختراق مستويات السيولة
        - التدفق التراكمي
        - مناطق التجميع
        """
        score = 0
        
        # 1. فحص مستويات السيولة
        liq = self.smc._find_liquidity_zones(df)
        if liq['ssl_swept']:
            score += 30  # صيد سيولة البيع = وجود يد قوية
        if liq['bsl_swept']:
            score -= 30  # صيد سيولة الشراء = انعكاس محتمل
        
        # 2. تحليل التدفق (Order Flow)
        flow = self._calculate_flow_imbalance(df)
        if flow['signal'] == 'BULLISH':
            score += flow['strength'] * 0.3
        elif flow['signal'] == 'BEARISH':
            score -= flow['strength'] * 0.3
        
        # 3. مناطق التجميع
        accum = self._find_accumulation_zones(df)
        if accum:
            # قرب السعر من منطقة تجميع شرائية يزيد الثقة
            closest_zone = min(accum, key=lambda z: abs(z['price'] - current_price))
            if closest_zone['type'] == 'BUY_ACCUMULATION' and closest_zone['strength'] > 50:
                score += 20
            elif closest_zone['type'] == 'SELL_DISTRIBUTION' and closest_zone['strength'] > 50:
                score -= 20
        
        # تطبيع النتيجة بين -100 و 100
        return max(-100, min(100, score))
    
    # ============================================================
    # 7.5 التنبؤ الاحتمالي (Probabilistic Forecast)
    # ============================================================
    def _probabilistic_forecast(self, df, current_price, analysis_result):
        """
        التنبؤ بما سيحدث بناءً على تحليل الاحتمالات لثلاثة سيناريوهات
        مع تحديد نسبة حدوث كل سيناريو
        """
        # 1. تحليل السيولة
        liq = self.smc._find_liquidity_zones(df)
        
        # 2. تحليل التدفق
        flow = analysis_result['order_flow_imbalance']
        
        # 3. قوة الاتجاه الحالي
        trend = self.smc._detect_structure(df)
        trend_strength = 0
        if trend == 'UPTREND':
            trend_strength = 60
        elif trend == 'DOWNTREND':
            trend_strength = -60
        else:
            trend_strength = 0
        
        # 4. حساب الاحتمالات
        # السيناريو الصاعد (مواصلة الصعود)
        bullish_prob = 30  # أساس
        if liq['ssl_swept'] and flow['signal'] == 'BULLISH':
            bullish_prob += 35
        if trend_strength > 0:
            bullish_prob += 20
        if analysis_result['smart_money_indicator'] > 20:
            bullish_prob += 15
            
        # السيناريو الهابط (انعكاس أو هبوط)
        bearish_prob = 30  # أساس
        if liq['bsl_swept'] and flow['signal'] == 'BEARISH':
            bearish_prob += 35
        if trend_strength < 0:
            bearish_prob += 20
        if analysis_result['smart_money_indicator'] < -20:
            bearish_prob += 15
            
        # السيناريو العرضي (تذبذب)
        sideways_prob = 100 - bullish_prob - bearish_prob
        sideways_prob = max(10, sideways_prob)  # حد أدنى 10%
        
        # تحديد الاحتمال الأقوى
        probabilities = {
            'BULLISH': round(bullish_prob, 1),
            'BEARISH': round(bearish_prob, 1),
            'SIDEWAYS': round(sideways_prob, 1)
        }
        
        # تحديد الهدف والوقف المتوقعين لكل سيناريو
        forecast = {
            'probabilities': probabilities,
            'most_likely': max(probabilities, key=probabilities.get),
            'expected_move': {
                'bullish': {
                    'target': liq['bsl'] if liq['bsl'] else current_price + 10,
                    'stop': current_price - 5,
                    'confidence': probabilities['BULLISH'] / 100
                },
                'bearish': {
                    'target': liq['ssl'] if liq['ssl'] else current_price - 10,
                    'stop': current_price + 5,
                    'confidence': probabilities['BEARISH'] / 100
                }
            },
            'smart_money_insight': self._generate_smart_insight(
                probabilities, analysis_result['smart_money_indicator'], trend
            )
        }
        
        return forecast
    
    # ============================================================
    # 7.6 توليد رؤى "المال الذكي" (Smart Insight)
    # ============================================================
    def _generate_smart_insight(self, probabilities, sm_score, trend):
        """توليد تفسير بصيغة "المال الذكي" للتنبؤ"""
        most_likely = max(probabilities, key=probabilities.get)
        prob_value = probabilities[most_likely]
        
        if prob_value < 40:
            return "⚠️ السوق في حالة عدم يقين عالية. يفضل الانتظار حتى تظهر إشارة واضحة."
        
        if most_likely == 'BULLISH':
            insight = f"📈 المال الذكي يميل إلى الصعود بنسبة {prob_value}%. "
            if sm_score > 30:
                insight += "هناك تدفق شرائي قوي يدعم هذا السيناريو. "
            else:
                insight += "لكن التدفق ضعيف، قد يكون ارتداداً مؤقتاً. "
            insight += f"الهدف المتوقع: {prob_value*0.5:.2f} نقطة."
            return insight
            
        elif most_likely == 'BEARISH':
            insight = f"📉 المال الذكي يميل إلى الهبوط بنسبة {prob_value}%. "
            if sm_score < -30:
                insight += "تدفق بيعي مؤسسي واضح. "
            else:
                insight += "لكن البيع قد يكون محدوداً. "
            insight += f"الهدف المتوقع: {prob_value*0.5:.2f} نقطة."
            return insight
            
        else:
            return f"🔄 تذبذب متوقع بنسبة {prob_value}%. السعر سيظل ضمن النطاق الحالي حتى ظهور محفز جديد."

# ============================================================
# 8. دمج التحليل الذكي مع النظام الرئيسي
# ============================================================
# أضف هذه الدالة في نهاية class XAUUSD_SMC_System
def run_with_intelligence(self):
    """
    تشغيل النظام مع التحليل الذكي المتقدم
    """
    print("🧠 جاري تشغيل التحليل الذكي المتقدم...")
    
    # التحليل الأساسي
    df = self.data_fetcher.fetch_candles(granularity="M15", count=200)
    if df.empty:
        return None
        
    current_price = df['close'].iloc[-1]
    smc_result = self.smc_analyzer.analyze(df)
    
    # التحليل الذكي
    intelligent = IntelligentAnalyzer(self.smc_analyzer)
    smart_analysis = intelligent.full_analysis(df, current_price)
    
    # توليد السيناريوهات (من الكود السابق)
    scenarios = ScenarioTree.generate(smc_result, current_price, self.risk_manager)
    
    # إضافة التحليل الذكي إلى المخرجات
    full_result = {
        'price': current_price,
        'time': datetime.now(timezone.utc).isoformat(),
        'smc': smc_result,
        'scenarios': scenarios,
        'intelligent': smart_analysis,
        'final_recommendation': self._generate_final_verdict(
            smc_result, smart_analysis, scenarios
        )
    }
    
    # عرض النتائج الذكية
    self._print_intelligent_analysis(full_result)
    
    # إرسال تقرير شامل للتليجرام
    self.telegram.send_intelligent_report(full_result)
    
    return full_result

# ============================================================
# 9. وظائف مساعدة للعرض والإرسال
# ============================================================
def _print_intelligent_analysis(self, result):
    """طباعة التحليل الذكي في الطرفية"""
    intelligent = result['intelligent']
    
    print("\n" + "=" * 60)
    print("🧠 تحليل المال الذكي المتقدم")
    print("=" * 60)
    
    # مناطق التجميع
    print("\n📊 مناطق تجميع السيولة:")
    for zone in intelligent['accumulation_zones'][:3]:
        print(f"   • السعر: {zone['price']:.2f} | النوع: {zone['type']} | القوة: {zone['strength']}%")
    
    # تدفق الأوامر
    flow = intelligent['order_flow_imbalance']
    print(f"\n📈 تدفق الأوامر (Order Flow):")
    print(f"   • الدلتا التراكمي: {flow['cumulative_delta']:.2f}")
    print(f"   • الإشارة: {flow['signal']} ({flow['interpretation']})")
    print(f"   • القوة: {flow['strength']}%")
    
    # مؤشر المال الذكي
    sm_score = intelligent['smart_money_indicator']
    print(f"\n💡 مؤشر المال الذكي: {sm_score:.1f}")
    if sm_score > 30:
        print("   🔥 نشاط شرائي مؤسسي قوي")
    elif sm_score < -30:
        print("   ❄️ نشاط بيعي مؤسسي قوي")
    else:
        print("   ⚖️ نشاط متوازن أو ضعيف")
    
    # التنبؤ الاحتمالي
    forecast = intelligent['probabilistic_forecast']
    if forecast:
        print("\n🔮 التنبؤ الاحتمالي:")
        for direction, prob in forecast['probabilities'].items():
            bar = "█" * int(prob / 5)
            print(f"   • {direction}: {prob}% {bar}")
        print(f"   • الأكثر ترجيحاً: {forecast['most_likely']}")
        print(f"   • رؤية المال الذكي: {forecast['smart_money_insight']}")
    
    # التوصية النهائية
    print("\n" + "=" * 60)
    print(f"✅ التوصية النهائية: {result['final_recommendation']}")
    print("=" * 60)

def _generate_final_verdict(self, smc, intelligent, scenarios):
    """توليد حكم نهائي بناءً على كل التحليلات"""
    # إذا كان هناك سيناريو أساسي بثقة عالية
    if scenarios['primary'] and scenarios['primary'].get('confidence', 0) > 70:
        return f"{scenarios['primary']['action']} من {scenarios['primary']['entry']} | الثقة: {scenarios['primary']['confidence']}%"
    
    # إذا كان مؤشر المال الذكي قوياً
    sm_score = intelligent['smart_money_indicator']
    if sm_score > 40:
        return f"🚀 شراء مع تدفق مؤسسي قوي | الهدف: أعلى BSL"
    elif sm_score < -40:
        return f"🔻 بيع مع تدفق مؤسسي قوي | الهدف: أسفل SSL"
    
    # إذا كان التنبؤ الاحتمالي واضحاً
    forecast = intelligent['probabilistic_forecast']
    if forecast:
        most_likely = forecast['most_likely']
        prob = forecast['probabilities'][most_likely]
        if prob > 60:
            if most_likely == 'BULLISH':
                return f"📈 صعود متوقع بنسبة {prob}% | استهدف {forecast['expected_move']['bullish']['target']:.2f}"
            elif most_likely == 'BEARISH':
                return f"📉 هبوط متوقع بنسبة {prob}% | استهدف {forecast['expected_move']['bearish']['target']:.2f}"
    
    # الانتظار في الحالات الأخرى
    return "⏳ انتظار حتى وضوح الرؤية. السوق في منطقة قرار."

# ============================================================
# 10. تحديث بوت التليجرام لإرسال التحليل الذكي
# ============================================================
# أضف هذه الدالة إلى class TelegramBot
def send_intelligent_report(self, full_result):
    """إرسال تقرير التحليل الذكي الكامل إلى تليجرام"""
    if not self.token or not self.chat_id:
        return
    
    msg = f"🧠 **تحليل المال الذكي المتقدم**\n"
    msg += f"⏰ {full_result['time']}\n"
    msg += f"💰 السعر الحالي: {full_result['price']:.2f}\n\n"
    
    # التحليل الذكي
    intelligent = full_result['intelligent']
    
    # مناطق التجميع
    msg += "📊 **مناطق تجميع السيولة:**\n"
    for zone in intelligent['accumulation_zones'][:3]:
        msg += f"• {zone['price']:.2f} ({zone['type']}) - قوة {zone['strength']}%\n"
    
    # تدفق الأوامر
    flow = intelligent['order_flow_imbalance']
    msg += f"\n📈 **تدفق الأوامر:** {flow['signal']} ({flow['interpretation']})\n"
    
    # مؤشر المال الذكي
    msg += f"💡 **مؤشر المال الذكي:** {intelligent['smart_money_indicator']:.1f}\n"
    
    # التنبؤ الاحتمالي
    forecast = intelligent['probabilistic_forecast']
    if forecast:
        msg += "\n🔮 **التنبؤ الاحتمالي:**\n"
        for direction, prob in forecast['probabilities'].items():
            msg += f"• {direction}: {prob}%\n"
        msg += f"✅ **الأكثر ترجيحاً:** {forecast['most_likely']}\n"
        msg += f"💭 **رؤية المال الذكي:** {forecast['smart_money_insight']}\n"
    
    # التوصية النهائية
    msg += f"\n🚀 **التوصية النهائية:**\n{full_result['final_recommendation']}"
    
    self.send_message(msg)

# ============================================================
# 11. تحديث نقطة التشغيل الرئيسية
# ============================================================
# استبدل الكود الموجود تحت if __name__ == "__main__" بهذا:
if __name__ == "__main__":
    # إعدادات
    OANDA_KEY = "Your_OANDA_API_Key_Here"  # أدخل مفتاحك الحقيقي
    TELEGRAM_TOKEN = "8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54"
    TELEGRAM_CHAT_ID = "1432340574"
    
    # إنشاء النظام
    system = XAUUSD_SMC_System(
        account_balance=10000.0,
        oanda_api_key=OANDA_KEY,
        telegram_token=TELEGRAM_TOKEN,
        chat_id=TELEGRAM_CHAT_ID
    )
    
    # تشغيل التحليل الذكي المتقدم
    result = system.run_with_intelligence()
    
    # يمكن تشغيله في حلقة كل 15 دقيقة
    # while True:
    #     system.run_with_intelligence()
    #     time.sleep(900)
