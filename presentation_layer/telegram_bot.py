# presentation_layer/telegram_bot.py
import requests
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class TelegramBot:
    """بوت التليجرام للإشعارات والتقارير"""
    
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.enabled = Config.TELEGRAM_ENABLED
        
        if self.enabled and self.token and self.chat_id:
            logger.info("✅ تم تفعيل بوت التليجرام")
            # إرسال رسالة بدء التشغيل
            self.send_message("🚀 **تم تشغيل بوت تحليل XAUUSD بنجاح!**")
        else:
            logger.warning("⚠️ بوت التليجرام غير مفعل")
    
    def send_message(self, message, parse_mode='Markdown'):
        """إرسال رسالة نصية"""
        if not self.enabled or not self.token or not self.chat_id:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ تم إرسال الرسالة إلى تليجرام")
                return True
            else:
                logger.error(f"❌ فشل إرسال الرسالة: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال التليجرام: {e}")
            return False
    
    def send_analysis_report(self, analysis_data):
        """إرسال تقرير تحليل كامل"""
        if not self.enabled:
            return False
        
        price = analysis_data.get('price', 0)
        smc = analysis_data.get('smc_analysis', {})
        bias = smc.get('bias', 'NEUTRAL')
        structure = smc.get('structure', 'N/A')
        session = smc.get('session', 'UNKNOWN')
        ai = analysis_data.get('ai_prediction', {})
        smart = analysis_data.get('smart_money', {})
        
        trend_icon = {
            'BULLISH': '🟢',
            'BEARISH': '🔴',
            'NEUTRAL': '⚪'
        }.get(bias, '⚪')
        
        msg = f"📊 **تقرير تحليل XAUUSD**\n"
        msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
        msg += f"{'─' * 25}\n"
        msg += f"💰 **السعر:** {price:.2f}\n"
        msg += f"📈 **الاتجاه:** {trend_icon} {bias}\n"
        msg += f"📊 **الهيكل:** {structure}\n"
        msg += f"🏛️ **الجلسة:** {session}\n\n"
        
        if ai:
            ai_signal = ai.get('signal', 'N/A')
            ai_icon = {'BULLISH': '🟢', 'BEARISH': '🔴', 'NEUTRAL': '⚪'}.get(ai_signal, '⚪')
            msg += f"🤖 **الذكاء الاصطناعي:**\n"
            msg += f"   • الإشارة: {ai_icon} {ai_signal}\n"
            msg += f"   • الثقة: {ai.get('confidence', 0)}%\n"
            msg += f"   • السعر المتوقع: {ai.get('predicted_price', 0):.2f}\n\n"
        
        if smart:
            smart_icon = {
                'BULLISH': '🟢',
                'BEARISH': '🔴',
                'NEUTRAL': '⚪'
            }.get(smart.get('activity', 'NEUTRAL'), '⚪')
            msg += f"💡 **المال الذكي:**\n"
            msg += f"   • النشاط: {smart_icon} {smart.get('activity', 'N/A')}\n"
            msg += f"   • النقاط: {smart.get('score', 0)}\n"
            msg += f"   • الرؤية: {smart.get('insight', 'N/A')}\n\n"
        
        liq = smc.get('liquidity_zones', {})
        if liq:
            msg += f"🎯 **مناطق السيولة:**\n"
            msg += f"   • BSL: {liq.get('bsl', 'N/A')}\n"
            msg += f"   • SSL: {liq.get('ssl', 'N/A')}\n"
            if liq.get('ssl_swept'):
                msg += f"   ✅ تم صيد SSL\n"
            if liq.get('bsl_swept'):
                msg += f"   ✅ تم صيد BSL\n"
        
        report = analysis_data.get('report', {})
        if report:
            msg += f"\n📋 **التوصية:**\n"
            msg += f"   • {report.get('recommendation', 'N/A')}\n"
            risk = report.get('risk_assessment', {})
            if risk:
                risk_icon = {'منخفضة': '🟢', 'متوسطة': '🟡', 'مرتفعة': '🔴'}.get(risk.get('level', ''), '⚪')
                msg += f"   • المخاطر: {risk_icon} {risk.get('description', 'N/A')}"
        
        msg += f"\n\n{'-' * 25}"
        msg += f"\n🔄 تم التحديث: {datetime.now().strftime('%H:%M:%S')}"
        
        return self.send_message(msg)
    
    def send_alert(self, alert_type, message, level='INFO'):
        """إرسال تنبيه فوري"""
        if not self.enabled:
            return False
        
        emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '🚨',
            'SUCCESS': '✅',
            'BREAKOUT': '🚀',
            'LIQUIDITY': '🎯'
        }.get(level, 'ℹ️')
        
        msg = f"{emoji} **{alert_type}**\n"
        msg += f"📌 {message}\n"
        msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
        
        return self.send_message(msg)
    
    def send_test_message(self):
        """إرسال رسالة اختبار"""
        msg = f"✅ **اختبار الاتصال ناجح!**\n"
        msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        msg += f"📡 البوت يعمل بشكل طبيعي."
        return self.send_message(msg)
