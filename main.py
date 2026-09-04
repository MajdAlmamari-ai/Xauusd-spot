# main.py - النظام المتكامل
import sys
import os
import logging
from datetime import datetime
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data_layer.fetchers import DataFetcher
from data_layer.cleaner import DataCleaner

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
    """المنصة المتكاملة"""
    
    def __init__(self):
        logger.info("🏗️ تهيئة منصة XAUUSD...")
        
        for folder in ['backups', 'sessions', 'logs']:
            os.makedirs(folder, exist_ok=True)
        
        self.fetcher = DataFetcher(use_scraping=True)
        self.cleaner = DataCleaner()
        logger.info("✅ تم تهيئة المنصة")
    
    def run_analysis_cycle(self):
        """دورة تحليل"""
        logger.info("🔄 بدء دورة التحليل...")
        
        df = self.fetcher.fetch()
        if df is None or df.empty:
            logger.error("❌ فشل في جلب البيانات")
            return None
        
        df = self.cleaner.clean(df)
        price = df.iloc[-1]['close']
        
        logger.info(f"💰 السعر الحالي: {price:.2f}")
        logger.info("✅ اكتملت دورة التحليل")
        return {'price': price}

def main():
    platform = XAUUSDPlatform()
    
    print("\nاختر طريقة التشغيل:")
    print("1. دورة تحليل واحدة")
    print("2. تشغيل مستمر (كل 5 دقائق)")
    
    choice = input("أدخل الرقم (1/2): ").strip()
    
    if choice == '1':
        platform.run_analysis_cycle()
    elif choice == '2':
        while True:
            platform.run_analysis_cycle()
            time.sleep(300)
    else:
        platform.run_analysis_cycle()

if __name__ == "__main__":
    main()
