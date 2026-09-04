# data_layer/scraping/smart_scraper.py
import random
import json
import os
from datetime import datetime
import logging
from .proxy_manager import ProxyManager
from .session_manager import SessionManager
from .monitor import ScrapingMonitor

logger = logging.getLogger(__name__)

class SmartScraper:
    """كاشط ذكي"""
    
    def __init__(self, headless=False, use_proxy=True):
        self.headless = headless
        self.use_proxy = use_proxy
        self.proxy_manager = ProxyManager() if use_proxy else None
        self.session_manager = SessionManager()
        self.monitor = ScrapingMonitor()
        self.current_session_id = None
        os.makedirs('backups', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        logger.info("🕷️ تم تهيئة الكاشط الذكي")
    
    def start_session(self, session_id=None):
        self.current_session_id = self.session_manager.start_session(session_id)
        return self.current_session_id
    
    def end_session(self):
        if self.current_session_id:
            self.session_manager.end_session(self.current_session_id)
        self.current_session_id = None
    
    def scrape_gold_data(self):
        """محاكاة كشط البيانات"""
        # محاكاة الحصول على سعر الذهب
        price = 4472.91 + random.uniform(-5, 5)
        
        data = {
            'price': round(price, 2),
            'timestamp': datetime.now().isoformat(),
            'source': 'simulated'
        }
        
        self.monitor.log_request(True)
        self._create_backup(data)
        logger.info(f"💰 تم كشط السعر: {data['price']}")
        return data
    
    def _create_backup(self, data):
        try:
            backup_file = os.path.join(
                'backups',
                f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ فشل النسخ الاحتياطي: {e}")
    
    def cleanup(self):
        self.end_session()
        logger.info("🧹 تم التنظيف")
