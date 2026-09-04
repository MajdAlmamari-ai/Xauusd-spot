# # config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """إعدادات المنصة"""

    # إعدادات الكشط
    SCRAPING_HEADLESS = os.getenv('SCRAPING_HEADLESS', 'false').lower() == 'true'
    SCRAPING_USE_PROXY = os.getenv('SCRAPING_USE_PROXY', 'true').lower() == 'true'
    SCRAPING_MIN_DELAY = float(os.getenv('SCRAPING_MIN_DELAY', 2.0))
    SCRAPING_MAX_DELAY = float(os.getenv('SCRAPING_MAX_DELAY', 7.0))

    # إدارة المخاطر
    ACCOUNT_BALANCE = float(os.getenv('ACCOUNT_BALANCE', 10000.0))
    RISK_PERCENT = float(os.getenv('RISK_PERCENT', 0.01))

    # ============================================================
    # ✅ إعدادات التليجرام (داخل الكلاس)
    # ============================================================
    TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'true').lower() == 'true'
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8651437637:AAF4rEY8bTdYrP7_A0ZI1lCH1I92Aijkm54')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '1432340574')
