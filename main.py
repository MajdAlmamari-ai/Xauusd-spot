# main.py - النظام المتكامل (للاستخدام الشخصي)
import sys
import os
import logging
from datetime import datetime
import time

# إضافة المسارات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد الإعدادات
from config import Config

# استيراد الطبقة الأولى: البيانات
from data_layer.fetchers import DataFetcher
from data_layer.scheduler import DataScheduler
from data_layer.cleaner import DataCleaner

# استيراد الطبقة الثانية: التحليل
from analysis_layer.technical.smc_analyzer import SMCAnalyzer
from analysis_layer.fundamental.news_analyzer import NewsAnalyzer
from analysis_layer.ai_engine.predictor import AIPredictor
from analysis_layer.smart_money.tracker import SmartMoneyTracker

# استيراد الطبقة الثالثة: العرض
from presentation_layer.app import app
from presentation_layer.alerts import AlertSystem
from presentation_layer.reports import ReportGenerator
from presentation_layer.telegram_bot import TelegramBot

# إعداد التسجيل
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class XAUUSDPlatform:
    """المنصة المتكاملة (للاستخدام الشخصي)"""
    
    def __init__(self):
        logger.info("🏗️ تهيئة منصة XAUUSD SMC (شخصية)...")
        
        # إنشاء المجلدات
        for folder in ['backups', 'sessions', 'logs']:
            os.makedirs(folder, exist_ok=True)
        
        # الطبقة الأولى: البيانات
        self.fetcher = DataFetcher(use_scraping=True)
        self.cleaner = DataCleaner()
        
        # الطبقة الثانية: التحليل
        self.smc = SMCAnalyzer()
        self.news_analyzer = NewsAnalyzer()
        self.ai_predictor = AIPredictor()
        self.smart_tracker = SmartMoneyTracker(self.smc)
        
        # الطبقة الثالثة: العرض
        self.alert_system = AlertSystem()
        self.report_generator = ReportGenerator()
        self.telegram = TelegramBot()
        
        self.current_data = None
        self.current_analysis = None
        
        logger.info("✅ تم تهيئة المنصة الشخصية بنجاح")
    
    def run_analysis_cycle(self):
        """دورة تحليل كاملة"""
        logger.info("\n" + "="*60)
        logger.info(f"🔄 دورة التحليل - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        logger.info("="*60)
        
        # 1. جلب البيانات
        df = self.fetcher.fetch()
        if df is None or df.empty:
            logger.error("❌ فشل في جلب البيانات")
            return None
        
        # 2. تنظيف البيانات
        df = self.cleaner.clean(df)
        self.current_data = df
        
        # 3. التحليل الفني (SMC)
        smc_result = self.smc.analyze(df)
        logger.info(f"📊 SMC: {smc_result.get('bias', 'NEUTRAL')} | هيكل: {smc_result.get('structure', 'N/A')}")
        
        # 4. تحليل الأخبار
        news = self.fetcher.fetch_news()
        news_analysis = self.news_analyzer.analyze(news) if news else {'impact': 'LOW', 'summary': 'لا أخبار'}
        logger.info(f"📰 الأخبار: {news_analysis.get('summary', 'N/A')}")
        
        # 5. التنبؤ بالذكاء الاصطناعي
        ai_prediction = self.ai_predictor.predict(df)
        if ai_prediction:
            logger.info(f"🤖 الذكاء الاصطناعي: {ai_prediction.get('signal', 'N/A')} | ثقة: {ai_prediction.get('confidence', 0)}%")
        
        # 6. تتبع المال الذكي
        smart_result = self.smart_tracker.analyze(df)
        logger.info(f"💡 المال الذكي: {smart_result.get('activity', 'NEUTRAL')} | نقاط: {smart_result.get('score', 0)}")
        
        # 7. تحديث النموذج
        self.ai_predictor.update(df)
        
        # 8. توليد التقرير
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'price': round(df.iloc[-1]['close'], 2),
            'smc_analysis': smc_result,
            'news_analysis': news_analysis,
            'ai_prediction': ai_prediction,
            'smart_money': smart_result
        }
        self.current_analysis = analysis_data
        
        # 9. فحص التنبيهات
        alerts = self.alert_system.check_alerts(df, smc_result, news_analysis)
        if alerts:
            logger.info(f"🔔 تنبيهات: {len(alerts)}")
            for alert in alerts[:3]:
                logger.info(f"   - {alert['message']}")
        
        # 10. توليد التقرير النهائي
        report = self.report_generator.generate_report(analysis_data)
        analysis_data['report'] = report
        logger.info(f"✅ التوصية: {report.get('recommendation', 'N/A')}")
        logger.info(f"⚖️ المخاطر: {report.get('risk_assessment', {}).get('description', 'N/A')}")
        
        # 11. إرسال التقرير عبر تليجرام
        if self.telegram.enabled:
            try:
                self.telegram.send_analysis_report(analysis_data)
                logger.info("📱 تم إرسال التقرير إلى تليجرام")
            except Exception as e:
                logger.error(f"❌ فشل إرسال التقرير إلى تليجرام: {e}")
        
        return analysis_data
    
    def run_continuously(self, interval_minutes=5):
        """تشغيل التحليل بشكل مستمر"""
        logger.info(f"⏳ تشغيل التحليل كل {interval_minutes} دقيقة...")
        
        try:
            while True:
                self.run_analysis_cycle()
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            logger.info("\n🛑 إيقاف التشغيل...")

def main():
    """نقطة التشغيل الرئيسية"""
    platform = XAUUSDPlatform()
    
    print("\nاختر طريقة التشغيل:")
    print("1. دورة تحليل واحدة")
    print("2. تشغيل مستمر (كل 5 دقائق)")
    print("3. تشغيل خادم الويب")
    
    choice = input("أدخل الرقم (1/2/3): ").strip()
    
    if choice == '1':
        platform.run_analysis_cycle()
    elif choice == '2':
        platform.run_continuously()
    elif choice == '3':
        from presentation_layer.app import run_server
        run_server()
    else:
        print("خيار غير صحيح، تشغيل دورة واحدة")
        platform.run_analysis_cycle()

if __name__ == "__main__":
    main()
