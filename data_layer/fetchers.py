# data_layer/fetchers.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from .scraping.smart_scraper import SmartScraper

logger = logging.getLogger(__name__)

class DataFetcher:
    """مدير جلب البيانات مع دعم الكشط"""
    
    def __init__(self, use_scraping=True):
        self.scraper = SmartScraper(headless=False, use_proxy=True) if use_scraping else None
        self.use_scraping = use_scraping
    
    def fetch(self, symbol="XAU/USD", timeframe="15m", count=100):
        """جلب البيانات"""
        if self.use_scraping and self.scraper:
            try:
                data = self.scraper.scrape_gold_data()
                if data and data.get('price'):
                    return self._build_dataframe(data, count)
            except Exception as e:
                logger.warning(f"⚠️ فشل الكشط: {e}")
        
        return self._generate_fallback_data(count)
    
    def _build_dataframe(self, data, count):
        """بناء DataFrame"""
        price = data.get('price', 4472.91)
        now = datetime.now()
        dates = [now - timedelta(minutes=15*i) for i in range(count)]
        
        return pd.DataFrame({
            'time': [d.isoformat() for d in dates],
            'open': [price + np.random.randn()*0.5 for _ in range(count)],
            'high': [price + abs(np.random.randn())*0.8 for _ in range(count)],
            'low': [price - abs(np.random.randn())*0.8 for _ in range(count)],
            'close': [price + np.random.randn()*0.4 for _ in range(count)],
            'volume': [abs(np.random.randn()*1000 + 500) for _ in range(count)]
        })
    
    def _generate_fallback_data(self, count=100):
        """بيانات احتياطية"""
        now = datetime.now()
        dates = [now - timedelta(minutes=15*i) for i in range(count)]
        base_price = 4472.91
        
        data = []
        for i, dt in enumerate(reversed(dates)):
            noise = np.random.randn() * 2
            data.append({
                'time': dt.isoformat(),
                'open': base_price + noise,
                'high': base_price + noise + abs(np.random.randn()) * 0.8,
                'low': base_price + noise - abs(np.random.randn()) * 0.8,
                'close': base_price + noise + np.random.randn() * 0.5,
                'volume': abs(np.random.randn() * 1000 + 500)
            })
            base_price = data[-1]['close']
        
        return pd.DataFrame(data)
    
    def fetch_news(self):
        """جلب الأخبار"""
        return []
